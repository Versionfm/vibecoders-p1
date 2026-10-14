"""Seam B: the Search, Path and Answer Steps and End-to-end Success, over hand-built cases and Traces."""
import unittest

from scoring import answer_step, path_step, score_run, score_trace, search_step
from tests.test_scoring import case
from tutor import TutorResult


def trace(read=(), **fields):
    return TutorResult(question="q", materials_read=list(read), read_count=len(read), **fields)


class SearchStepTest(unittest.TestCase):
    def test_reading_the_accepted_course_passes(self):
        verdict = search_step(case("p1", ["PEID"]), trace(["PEID"], course="PEID"))
        self.assertTrue(verdict.passed)
        self.assertEqual(verdict.recall, 1.0)
        self.assertEqual(verdict.extra_reads, ())

    def test_an_extra_course_fails_search_and_is_recorded(self):
        verdict = search_step(case("p1", ["PEID"]), trace(["PEID", "AITB"]))
        self.assertFalse(verdict.passed)
        self.assertEqual(verdict.recall, 1.0)
        self.assertEqual(verdict.extra_reads, ("AITB",))
        self.assertIn("AITB", verdict.reason)

    def test_another_course_instead_of_the_accepted_one_fails_search(self):
        verdict = search_step(case("p1", ["PEID"]), trace(["GAIF"], course="GAIF"))
        self.assertFalse(verdict.passed)
        self.assertEqual(verdict.recall, 0.0)

    def test_an_overlap_case_passes_with_either_accepted_course_or_both(self):
        overlap = case("o1", ["PEID", "AITB"], "overlap")
        for read, recall in ((["PEID"], 0.5), (["AITB"], 0.5), (["AITB", "PEID"], 1.0)):
            with self.subTest(read=read):
                verdict = search_step(overlap, trace(read))
                self.assertTrue(verdict.passed)
                self.assertEqual(verdict.recall, recall)

    def test_an_in_scope_case_with_nothing_read_fails_search(self):
        verdict = search_step(case("p1", ["PEID"]), trace(course="OUT_OF_SCOPE"))
        self.assertFalse(verdict.passed)
        self.assertEqual(verdict.recall, 0.0)

    def test_nothing_read_because_of_an_error_names_the_error(self):
        verdict = search_step(case("p1", ["PEID"]), trace(error="Router reply is not valid JSON: 'x'"))
        self.assertFalse(verdict.passed)
        self.assertIn("Router reply is not valid JSON", verdict.reason)

    def test_out_of_scope_passes_only_when_no_course_material_is_read(self):
        out_of_scope = case("x1", ["OUT_OF_SCOPE"], "out_of_scope")
        passed = search_step(out_of_scope, trace(course="OUT_OF_SCOPE"))
        self.assertTrue(passed.passed)
        self.assertIsNone(passed.recall)
        failed = search_step(out_of_scope, trace(["GAIF"], course="GAIF"))
        self.assertFalse(failed.passed)
        self.assertEqual(failed.extra_reads, ("GAIF",))


class PathStepTest(unittest.TestCase):
    def setUp(self):
        self.in_scope = case("p1", ["PEID"], expected_sections=["PEID-2.3"])

    def test_one_read_then_an_answer_passes(self):
        self.assertTrue(path_step(self.in_scope, trace(["PEID"], answer="A [PEID-2.3].")).passed)

    def test_routed_tutor_out_of_scope_with_no_read_passes(self):
        self.assertTrue(path_step(case("x1", ["OUT_OF_SCOPE"], "out_of_scope"), trace(course="OUT_OF_SCOPE")).passed)

    def test_each_path_rule_fails_on_its_own(self):
        failures = {
            "failed model call": trace(["PEID"], error="Course Tutor model call failed: TimeoutError: slow"),
            "invalid Router reply": trace(error="Router reply is not valid JSON: 'x'"),
            "repeated Read": trace(["PEID", "PEID"], answer="A [PEID-2.3]."),
            "invalid tool argument": trace(["PEID"], tool_arguments=["PEID", "../.env"], answer="A [PEID-2.3]."),
            "answer without a Read": trace(answer="A from memory."),
            "Refusal without a Read": trace(answer="This is not covered in the PEID material.", is_refusal=True),
            "Read limit reached": trace(["PEID"], read_limit_hit=True, answer="A [PEID-2.3]."),
        }
        for rule, result in failures.items():
            with self.subTest(rule=rule):
                verdict = path_step(self.in_scope, result)
                self.assertFalse(verdict.passed)
                self.assertTrue(verdict.reason)

    def test_the_reason_names_the_failure(self):
        self.assertIn("../.env", path_step(self.in_scope, trace(["PEID"], tool_arguments=["../.env"])).reason)
        self.assertIn("PEID", path_step(self.in_scope, trace(["PEID", "PEID"])).reason)
        self.assertIn("Router reply", path_step(self.in_scope, trace(error="Router reply is not valid JSON")).reason)


REFUSAL = "This is not covered in the PEID material."


class AnswerStepTest(unittest.TestCase):
    def setUp(self):
        self.answer_case = case("p1", ["PEID"], expected_sections=["PEID-2.3"])
        self.refusal_case = case("r1", ["PEID"], "refusal", expect_refusal=True)
        self.out_of_scope_case = case("x1", ["OUT_OF_SCOPE"], "out_of_scope")

    def test_an_answer_citing_an_expected_section_and_only_valid_sections_passes(self):
        result = trace(["PEID"], course="PEID", answer="A [PEID-2.3] [PEID-2.5].", citations=["PEID-2.3", "PEID-2.5"])
        self.assertTrue(answer_step(self.answer_case, result).passed)

    def test_an_answer_fails_without_an_expected_section_with_an_invalid_one_or_as_a_fixed_sentence(self):
        failures = {
            "no expected Section": trace(["PEID"], course="PEID", answer="A [PEID-2.5].", citations=["PEID-2.5"]),
            "invalid Section": trace(
                ["PEID"], course="PEID", answer="A", citations=["PEID-2.3", "GAIF-1.1"], invalid_citations=["GAIF-1.1"]
            ),
            "Refusal": trace(["PEID"], course="PEID", answer=REFUSAL, is_refusal=True),
            "Out of scope": trace(course="OUT_OF_SCOPE"),
            "failed call": trace(["PEID"], course="PEID", error="Course Tutor model call failed: TimeoutError: x"),
        }
        for kind, result in failures.items():
            with self.subTest(kind=kind):
                verdict = answer_step(self.answer_case, result)
                self.assertFalse(verdict.passed)
                self.assertTrue(verdict.reason)

    def test_the_expected_refusal_passes_and_an_answer_instead_fails(self):
        self.assertTrue(answer_step(self.refusal_case, trace(["PEID"], answer=REFUSAL, is_refusal=True)).passed)
        answered = trace(["PEID"], answer="An invented answer [PEID-2.3].", citations=["PEID-2.3"])
        self.assertFalse(answer_step(self.refusal_case, answered).passed)

    def test_out_of_scope_with_no_read_passes_and_anything_else_fails(self):
        self.assertTrue(answer_step(self.out_of_scope_case, trace(course="OUT_OF_SCOPE")).passed)
        answered = trace(["GAIF"], course="GAIF", answer="Pizza [GAIF-1.1].", citations=["GAIF-1.1"])
        self.assertFalse(answer_step(self.out_of_scope_case, answered).passed)
        refused = trace(["GAIF"], course="GAIF", answer="This is not covered in the GAIF material.", is_refusal=True)
        self.assertFalse(answer_step(self.out_of_scope_case, refused).passed)


class EndToEndSuccessTest(unittest.TestCase):
    def setUp(self):
        self.case = case("p1", ["PEID"], expected_sections=["PEID-2.3"])

    def good(self, **changes):
        fields = {"course": "PEID", "answer": "A [PEID-2.3].", "citations": ["PEID-2.3"], **changes}
        return trace(fields.pop("read", ["PEID"]), **fields)

    def test_a_trace_passing_all_three_steps_succeeds_and_has_no_failing_step(self):
        score = score_trace(self.case, self.good())
        self.assertTrue(score.success)
        self.assertIsNone(score.earliest_failure)

    def test_end_to_end_success_fails_on_each_step_and_names_the_earliest_failing_step(self):
        failing = {
            "Search": self.good(read=["PEID", "AITB"]),
            "Path": self.good(read_limit_hit=True),
            "Answer": self.good(answer="A [PEID-2.5].", citations=["PEID-2.5"]),
        }
        for step, result in failing.items():
            with self.subTest(step=step):
                score = score_trace(self.case, result)
                self.assertFalse(score.success)
                self.assertEqual(score.earliest_failure[0], step)
                self.assertTrue(score.earliest_failure[1])

    def test_search_is_named_before_path_and_answer_when_all_fail(self):
        result = trace(["GAIF", "GAIF"], course="GAIF", answer="A [GAIF-1.1].", citations=["GAIF-1.1"])
        self.assertEqual(score_trace(self.case, result).earliest_failure[0], "Search")

    def test_a_run_reports_each_step_pass_rate_and_end_to_end_success(self):
        cases = [self.case, self.case, case("x1", ["OUT_OF_SCOPE"], "out_of_scope")]
        results = [self.good(), self.good(read_limit_hit=True), trace(course="OUT_OF_SCOPE")]
        scores = score_run(cases, results)
        self.assertEqual(scores["Search Step"], 1.0)
        self.assertAlmostEqual(scores["Path Step"], 2 / 3)
        self.assertEqual(scores["Answer Step"], 1.0)
        self.assertAlmostEqual(scores["End-to-end Success"], 2 / 3)
        self.assertEqual(scores["Routing accuracy"], 1.0)  # existing metrics stay


if __name__ == "__main__":
    unittest.main()
