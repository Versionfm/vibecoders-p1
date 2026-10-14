"""compare.html, rendered from two folders of stored Runs of hand-built Traces: its numbers, rows and warnings."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from compare import main, render_compare
from evaluate import Run, run_record
from scoring import score_run
from tests.test_html_report import CASES, OUT_OF_SCOPE, answered

SEARCH_FAILS = answered(read=["PEID", "AITB"])


def stored_runs(per_run, case_file="cases.json", model="fake/app-model", thinking=False):
    return [
        run_record(Run(n, "2026-10-09T14:30:00+00:00", case_file, model, thinking, None, results,
                       score_run(CASES, results)), CASES)
        for n, results in enumerate(per_run, start=1)
    ]


def before():
    """p1 fails Search in every Run; x1 always succeeds."""
    return stored_runs([[SEARCH_FAILS, OUT_OF_SCOPE]] * 3)


def after(**settings):
    """p1 succeeds in Runs 1 and 2 and fails Path in Run 3; x1 always succeeds."""
    return stored_runs(
        [[answered(), OUT_OF_SCOPE], [answered(), OUT_OF_SCOPE], [answered(read_limit_hit=True), OUT_OF_SCOPE]],
        **settings,
    )


class RenderCompareTest(unittest.TestCase):
    def test_both_evaluations_step_rates_are_shown_side_by_side_as_mean_and_range(self):
        html = render_compare(before(), after(), "tutor_v1", "tutor_v2")
        self.assertIn("tutor_v1", html)
        self.assertIn("tutor_v2", html)
        self.assertIn("50.0% <small>50.0% to 50.0%</small>", html)  # A: Search and End-to-end Success
        self.assertIn("83.3% <small>50.0% to 100.0%</small>", html)  # B: Path and End-to-end Success
        self.assertIn("100.0% <small>100.0% to 100.0%</small>", html)  # both: Answer

    def test_only_cases_whose_end_to_end_success_changed_are_listed_with_each_sides_earliest_failing_step(self):
        html = render_compare(before(), after(), "A", "B")
        self.assertEqual(html.count('class="changed"'), 1)
        self.assertIn('id="case-p1"', html)
        self.assertNotIn('id="case-x1"', html)
        self.assertIn("0/3", html)
        self.assertIn("2/3", html)
        self.assertIn("Search 3", html)
        self.assertIn("Path 1", html)

    def test_no_warning_when_case_file_model_and_thinking_match(self):
        self.assertNotIn('class="warning"', render_compare(before(), after(), "A", "B"))

    def test_a_warning_names_each_setting_that_differs(self):
        html = render_compare(before(), after(case_file="other.json", model="fake/other", thinking=True), "A", "B")
        self.assertIn('class="warning"', html)
        for detail in ("case file", "cases.json", "other.json", "model", "fake/other", "thinking"):
            self.assertIn(detail, html)

    def test_the_page_is_self_contained_and_escapes_text_from_the_runs(self):
        html = render_compare(before(), after(model="<b>m</b>"), "A", "<i>B</i>")
        self.assertNotIn("<script", html)
        self.assertNotIn("http", html)
        self.assertNotIn("<b>m</b>", html)
        self.assertNotIn("<i>B</i>", html)


class CompareCommandTest(unittest.TestCase):
    def test_writes_compare_html_from_two_run_folders_prints_its_path_and_warns_in_the_console(self):
        with tempfile.TemporaryDirectory() as tmp:
            folders = []
            for name, runs in (("a", before()), ("b", after(model="fake/other"))):
                folder = Path(tmp) / name
                folder.mkdir()
                for record in runs:
                    (folder / f"run_{record['run']}.json").write_text(json.dumps(record), encoding="utf-8")
                folders.append(str(folder))
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(folders), 0)
            page = Path(folders[1]) / "compare.html"
            self.assertTrue(page.exists())
            self.assertIn(str(page), out.getvalue())
            self.assertIn("Warning", out.getvalue())
            self.assertIn("fake/other", out.getvalue())
            self.assertIn('id="case-p1"', page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
