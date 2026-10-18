"""The evaluation command, run end to end on the sample case file with a fake model (no network, no key)."""
import contextlib
import io
import json
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timezone
from pathlib import Path

from cases import SAMPLE_CASE_FILE, load_cases
from evaluate import main
from prompts import AGENTIC_TUTOR_PROMPT_VERSION, ROUTER_PROMPT_VERSION, TUTOR_PROMPT_VERSION
from tests.fakes import FakeChatModel, QuestionScriptedModel, reads

QUESTIONS = {case.id: case.question for case in load_cases(SAMPLE_CASE_FILE)}
FIXED_CLOCK = lambda: datetime(2026, 10, 9, 14, 30, 0, tzinfo=timezone.utc)  # noqa: E731


def route(course, evidence="phrase"):
    return json.dumps({"course": course, "evidence": evidence})


def well_behaved_script():
    """Every sample case gets the expected behaviour in every run."""
    return {
        QUESTIONS["SAMPLE-01"]: [route("PEID"), "Models predict plausible tokens [PEID-1.9]."],
        QUESTIONS["SAMPLE-02"]: [route("DTGS"), "There are five rungs [DTGS-3.7]."],
        QUESTIONS["SAMPLE-03"]: [route("GAIF"), "It updates weights on errors [GAIF-2.9]."],
        QUESTIONS["SAMPLE-04"]: [route("AITB"), "Name the task and give context [AITB-2.2]."],
        QUESTIONS["SAMPLE-05"]: [route("OUT_OF_SCOPE")],
        QUESTIONS["SAMPLE-06"]: [route("AITB"), "This is not covered in the AITB material."],
    }


class EvaluationCommandTest(unittest.TestCase):
    def run_command(self, script, extra_args=(), judge=None):
        self.model = QuestionScriptedModel(script, name="fake/app-model", thinking=False)
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        argv = [str(SAMPLE_CASE_FILE), "--out", self.folder.name, *extra_args]
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = main(argv, model=self.model, clock=FIXED_CLOCK, judge=judge)
        self.assertEqual(exit_code, 0)
        [run_dir] = Path(self.folder.name).iterdir()
        return run_dir

    def test_every_case_is_answered_three_times_and_each_run_is_stored(self):
        run_dir = self.run_command(well_behaved_script())

        for question in QUESTIONS.values():
            expected_calls = 3 if question == QUESTIONS["SAMPLE-05"] else 6  # Out of scope skips the tutor
            self.assertEqual(self.model.calls_for(question), expected_calls)
        stored = sorted(p.name for p in run_dir.glob("run_*.json"))
        self.assertEqual(stored, ["run_1.json", "run_2.json", "run_3.json"])

    def test_a_stored_run_records_timestamp_prompt_versions_model_names_and_per_case_outputs(self):
        run_dir = self.run_command(well_behaved_script())
        run = json.loads((run_dir / "run_2.json").read_text(encoding="utf-8"))

        self.assertEqual(run["run"], 2)
        self.assertTrue(run["timestamp"].startswith("2026-10-09T14:30:00"))
        self.assertEqual(run["prompt_versions"], {"router": ROUTER_PROMPT_VERSION, "tutor": TUTOR_PROMPT_VERSION})
        self.assertEqual(run["models"]["app"], "fake/app-model")
        self.assertIn("judge", run["models"])
        self.assertIs(run["thinking"], False)
        outputs = {o["case_id"]: o for o in run["outputs"]}
        self.assertEqual(set(outputs), set(QUESTIONS))
        self.assertEqual(outputs["SAMPLE-01"]["course"], "PEID")
        self.assertEqual(outputs["SAMPLE-01"]["citations"], ["PEID-1.9"])
        self.assertTrue(outputs["SAMPLE-06"]["is_refusal"])
        self.assertEqual(run["metrics"]["Routing accuracy"], 1.0)

    def test_the_report_shows_mean_and_range_across_runs_and_labels_the_macro_average(self):
        script = well_behaved_script()
        # SAMPLE-03 is routed to PEID in the second run only: routing accuracy 1, 5/6, 1 across the runs
        script[QUESTIONS["SAMPLE-03"]] = [
            route("GAIF"), "It updates weights on errors [GAIF-2.9].",
            route("PEID"), "This is not covered in the PEID material.",
            route("GAIF"), "It updates weights on errors [GAIF-2.9].",
        ]
        run_dir = self.run_command(script)
        report = (run_dir / "report.md").read_text(encoding="utf-8")

        self.assertIn("| Routing accuracy | 94.4% | 83.3% to 100.0% | 100.0% | 83.3% | 100.0% |", report)
        self.assertIn("| Recall GAIF | 66.7% | 0.0% to 100.0% | 100.0% | 0.0% | 100.0% |", report)
        self.assertIn("Recall (macro average)", report)
        self.assertIn("End-to-end Success", report)
        self.assertIn("App model (Router and Course Tutor): `fake/app-model`", report)
        self.assertIn("Thinking: off", report)
        self.assertIn(TUTOR_PROMPT_VERSION, report)

    def test_a_stored_run_records_the_tutor_and_each_trace_with_its_step_verdicts(self):
        run_dir = self.run_command(well_behaved_script(), ["--runs", "1"])
        run = json.loads((run_dir / "run_1.json").read_text(encoding="utf-8"))

        self.assertEqual(run["tutor"], "routed")
        outputs = {o["case_id"]: o for o in run["outputs"]}
        answered, out_of_scope = outputs["SAMPLE-01"], outputs["SAMPLE-05"]
        self.assertEqual(answered["materials_read"], ["PEID"])
        self.assertEqual(answered["read_arguments"], [])
        self.assertEqual(answered["read_count"], 1)
        self.assertIs(answered["read_limit_hit"], False)
        self.assertEqual(out_of_scope["materials_read"], [])
        self.assertEqual(
            answered["steps"]["search"], {"passed": True, "reason": "", "recall": 1.0, "extra_reads": []}
        )
        self.assertEqual(answered["steps"]["path"], {"passed": True, "reason": ""})
        self.assertEqual(answered["steps"]["answer"], {"passed": True, "reason": ""})
        self.assertIs(answered["steps"]["end_to_end_success"], True)
        self.assertIsNone(answered["steps"]["earliest_failing_step"])
        self.assertEqual(run["metrics"]["End-to-end Success"], 1.0)

    def test_the_report_shows_the_step_matrix_and_per_case_step_counts_with_the_earliest_failing_step(self):
        script = well_behaved_script()
        # SAMPLE-03 is routed to PEID and refused in the second run only: it fails Search (and Answer) once
        script[QUESTIONS["SAMPLE-03"]] = [
            route("GAIF"), "It updates weights on errors [GAIF-2.9].",
            route("PEID"), "This is not covered in the PEID material.",
            route("GAIF"), "It updates weights on errors [GAIF-2.9].",
        ]
        run_dir = self.run_command(script)
        report = (run_dir / "report.md").read_text(encoding="utf-8")

        self.assertIn("## Steps", report)
        self.assertIn("| Search Step | 94.4% | 83.3% to 100.0% | 100.0% | 83.3% | 100.0% |", report)
        self.assertIn("| Path Step | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |", report)
        self.assertIn("| **End-to-end Success** | 94.4% | 83.3% to 100.0% | 100.0% | 83.3% | 100.0% |", report)
        self.assertIn(
            "| SAMPLE-03 | near_miss | 2/3 | 3/3 | 2/3 | 2/3 | Search: read PEID, not an Accepted Course (1/3) |",
            report,
        )
        self.assertIn("| SAMPLE-01 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |", report)
        self.assertNotIn("End-to-end Success | pending", report)

    def test_an_html_report_is_written_beside_the_markdown_report_and_its_path_printed(self):
        model = QuestionScriptedModel(well_behaved_script(), name="fake/app-model")
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()) as output:
            main([str(SAMPLE_CASE_FILE), "--out", folder], model=model, clock=FIXED_CLOCK)
            [run_dir] = Path(folder).iterdir()
            html = (run_dir / "report.html").read_text(encoding="utf-8")

        self.assertIn(str(run_dir / "report.html"), output.getvalue())
        self.assertIn("100.0%", html)
        for case_id in QUESTIONS:
            self.assertIn(f'id="trace-3-{case_id}"', html)

    def test_a_model_failure_is_recorded_as_an_error_for_that_case_and_the_run_completes(self):
        script = well_behaved_script()
        script[QUESTIONS["SAMPLE-01"]] = [TimeoutError("service did not answer")]
        run_dir = self.run_command(script, ["--runs", "1"])
        run = json.loads((run_dir / "run_1.json").read_text(encoding="utf-8"))

        failed = next(o for o in run["outputs"] if o["case_id"] == "SAMPLE-01")
        self.assertIn("TimeoutError", failed["error"])
        self.assertAlmostEqual(run["metrics"]["Routing accuracy"], 5 / 6)

    def test_an_interrupted_evaluation_keeps_the_runs_that_finished(self):
        script = well_behaved_script()
        # SAMPLE-01 is interrupted in its second run (KeyboardInterrupt is not a model failure, it stops the command)
        script[QUESTIONS["SAMPLE-01"]] = [
            route("PEID"), "Models predict plausible tokens [PEID-1.9].", KeyboardInterrupt(),
        ]
        model = QuestionScriptedModel(script, name="fake/app-model")
        with tempfile.TemporaryDirectory() as folder:
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(KeyboardInterrupt):
                main([str(SAMPLE_CASE_FILE), "--out", folder], model=model, clock=FIXED_CLOCK)
            [run_dir] = Path(folder).iterdir()
            self.assertEqual([p.name for p in run_dir.glob("run_*.json")], ["run_1.json"])
            run = json.loads((run_dir / "run_1.json").read_text(encoding="utf-8"))
            self.assertEqual(len(run["outputs"]), len(QUESTIONS))

    def test_two_evaluations_started_in_the_same_second_get_separate_folders(self):
        with tempfile.TemporaryDirectory() as folder:
            for _ in range(2):
                model = QuestionScriptedModel(well_behaved_script(), name="fake/app-model")
                argv = [str(SAMPLE_CASE_FILE), "--out", folder, "--runs", "1"]
                with contextlib.redirect_stdout(io.StringIO()):
                    main(argv, model=model, clock=FIXED_CLOCK)
            folders = sorted(Path(folder).iterdir())
            self.assertEqual(len(folders), 2)
            for run_dir in folders:
                self.assertTrue((run_dir / "run_1.json").exists())
                self.assertTrue((run_dir / "report.md").exists())

    def test_cases_answered_in_parallel_are_stored_in_case_order_with_the_same_outputs(self):
        sequential = json.loads((self.run_command(well_behaved_script()) / "run_1.json").read_text(encoding="utf-8"))
        parallel_dir = self.run_command(well_behaved_script(), ["--workers", "4"])
        parallel = json.loads((parallel_dir / "run_1.json").read_text(encoding="utf-8"))

        self.assertEqual([o["case_id"] for o in parallel["outputs"]], list(QUESTIONS))
        self.assertEqual(parallel["outputs"], sequential["outputs"])
        self.assertEqual(parallel["metrics"], sequential["metrics"])

    def test_tutor_agentic_stores_runs_labelled_with_the_tutor_and_scored_by_the_steps(self):
        script = {
            QUESTIONS["SAMPLE-01"]: [reads("PEID"), "Models predict plausible tokens [PEID-1.9]."],
            QUESTIONS["SAMPLE-02"]: [reads("DTGS"), "There are five rungs [DTGS-3.7]."],
            QUESTIONS["SAMPLE-03"]: [reads("PEID"), "Not in what I read [GAIF-2.9]."],
            QUESTIONS["SAMPLE-04"]: [reads("AITB"), "Name the task and give context [AITB-2.2]."],
            QUESTIONS["SAMPLE-05"]: ["This question is outside the four Courses."],
            QUESTIONS["SAMPLE-06"]: [reads("AITB"), "This is not covered in the AITB material."],
        }
        run_dir = self.run_command(script, ["--tutor", "agentic"])
        run = json.loads((run_dir / "run_3.json").read_text(encoding="utf-8"))

        self.assertTrue(run_dir.name.endswith("_agentic"))
        self.assertEqual(run["tutor"], "agentic")
        self.assertEqual(run["prompt_versions"], {"agentic_tutor": AGENTIC_TUTOR_PROMPT_VERSION})
        self.assertEqual(self.model.calls_for(QUESTIONS["SAMPLE-01"]), 6)  # a Read and an answer, in each of 3 runs
        outputs = {o["case_id"]: o for o in run["outputs"]}
        self.assertEqual(outputs["SAMPLE-01"]["materials_read"], ["PEID"])
        self.assertEqual(outputs["SAMPLE-01"]["read_arguments"], ["PEID"])
        self.assertIs(outputs["SAMPLE-01"]["steps"]["end_to_end_success"], True)
        self.assertEqual(
            outputs["SAMPLE-03"]["steps"]["earliest_failing_step"],
            {"step": "Search", "reason": "read PEID, not an Accepted Course"},
        )
        report = (run_dir / "report.md").read_text(encoding="utf-8")
        self.assertIn("Tutor: `agentic`", report)
        self.assertIn("App model (Agentic Tutor): `fake/app-model`", report)
        self.assertNotIn("Router", report.split("## Steps")[0])

    def test_with_a_judge_only_expected_answers_are_judged_and_the_report_shows_the_judge_rates(self):
        # Four sample cases expect an answer; SAMPLE-05 (Out of scope) and SAMPLE-06 (Refusal) are never judged.
        # One Run: the first answer is judged not Supported, the other three pass both criteria.
        replies = [json.dumps({"evidence": "not in PEID-1.9", "verdict": "FAIL"})]
        replies += [json.dumps({"evidence": "ok", "verdict": "PASS"})] * 7
        judge = FakeChatModel(replies, name="fake/judge-model")
        run_dir = self.run_command(well_behaved_script(), ["--runs", "1"], judge=judge)
        run = json.loads((run_dir / "run_1.json").read_text(encoding="utf-8"))

        self.assertEqual(len(judge.calls), 8)  # two criteria for each of the four expected answers
        self.assertEqual(run["models"]["judge"], "fake/judge-model")
        self.assertIn("judge_supported", run["prompt_versions"])
        outputs = {o["case_id"]: o for o in run["outputs"]}
        self.assertIsNone(outputs["SAMPLE-05"]["judge"])
        self.assertIsNone(outputs["SAMPLE-06"]["judge"])
        judged = [o for o in run["outputs"] if o["judge"]]
        self.assertEqual(len(judged), 4)
        failed = [o for o in judged if o["judge"]["supported"]["verdict"] == "FAIL"]
        self.assertEqual(len(failed), 1)
        self.assertIn("not Supported", failed[0]["steps"]["earliest_failing_step"]["reason"])
        self.assertAlmostEqual(run["metrics"]["Supported rate"], 3 / 4)
        self.assertAlmostEqual(run["metrics"]["End-to-end Success"], 5 / 6)

        report = (run_dir / "report.md").read_text(encoding="utf-8")
        self.assertIn("Judge model: `fake/judge-model`", report)
        self.assertIn("| Supported rate | 75.0% |", report)
        self.assertIn("| Responsive rate | 100.0% |", report)
        html = (run_dir / "report.html").read_text(encoding="utf-8")
        self.assertIn("Supported rate", html)

    def test_without_a_judge_the_report_says_the_judge_rates_were_not_measured(self):
        run_dir = self.run_command(well_behaved_script(), ["--runs", "1"])
        report = (run_dir / "report.md").read_text(encoding="utf-8")
        self.assertIn("| Supported rate | not measured | no judge model set |", report)
        self.assertIn("code checks only", report)

    def test_the_command_refuses_to_run_without_a_judge_in_the_settings(self):
        app_model = QuestionScriptedModel(well_behaved_script(), name="fake/app-model")
        with (
            tempfile.TemporaryDirectory() as folder,
            mock.patch("llm.get_chat_model", return_value=app_model),
            mock.patch("llm.get_judge_model", return_value=None),
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaisesRegex(SystemExit, "LLM_JUDGE_MODEL"),
        ):
            main([str(SAMPLE_CASE_FILE), "--out", folder], clock=FIXED_CLOCK)
        self.assertEqual(app_model.calls_for(QUESTIONS["SAMPLE-01"]), 0)  # refused before any question was asked


if __name__ == "__main__":
    unittest.main()
