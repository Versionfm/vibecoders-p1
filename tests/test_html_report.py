"""The HTML report, rendered from stored Runs of hand-built Traces: its numbers and rows, not its layout."""
import unittest

from evaluate import Run, run_record
from html_report import render_html_report
from scoring import score_run
from tests.test_scoring import case
from tutor import TutorResult

CASES = [case("p1", ["PEID"], expected_sections=["PEID-2.3"]), case("x1", ["OUT_OF_SCOPE"], "out_of_scope")]


def answered(read=("PEID",), **fields):
    return TutorResult(
        question="question p1", course="PEID", answer="A [PEID-2.3].", citations=["PEID-2.3"],
        materials_read=list(read), read_count=len(read), **fields,
    )


OUT_OF_SCOPE = TutorResult(question="question x1", course="OUT_OF_SCOPE")


def stored_runs():
    """Run 1 succeeds on both cases; p1 fails Search in Run 2 and Path in Run 3, its answer always passes."""
    per_run = [
        [answered(), OUT_OF_SCOPE],
        [answered(read=["PEID", "AITB"]), OUT_OF_SCOPE],
        [answered(read_limit_hit=True), OUT_OF_SCOPE],
    ]
    return [
        run_record(Run(n, "2026-10-09T14:30:00+00:00", "cases.json", "fake/app-model", False, None, results,
                       score_run(CASES, results)), CASES)
        for n, results in enumerate(per_run, start=1)
    ]


class HtmlReportTest(unittest.TestCase):
    def setUp(self):
        self.html = render_html_report(stored_runs(), CASES)

    def test_the_headline_is_end_to_end_success_as_mean_and_range_with_tutor_model_and_case_file(self):
        self.assertIn("66.7%", self.html)
        self.assertIn("50.0% to 100.0%", self.html)
        for detail in ("routed", "fake/app-model", "cases.json"):
            self.assertIn(detail, self.html)

    def test_each_step_rate_is_shown_and_the_answer_step_is_contrasted_with_end_to_end_success(self):
        self.assertIn("83.3%", self.html)  # Search and Path
        self.assertIn("100.0%", self.html)  # Answer
        self.assertIn("the number you would have reported", self.html)
        self.assertIn("the number that matters", self.html)

    def test_one_example_row_per_failure_pattern_and_the_count_of_traces_first_failing_at_each_step(self):
        self.assertEqual(self.html.count('class="pattern"'), 2)
        self.assertIn("read AITB, not an Accepted Course", self.html)
        self.assertIn("Read limit reached", self.html)
        self.assertIn('data-step="Search">1<', self.html)
        self.assertIn('data-step="Path">1<', self.html)
        self.assertIn('data-step="Answer">0<', self.html)

    def test_every_trace_is_listed(self):
        for run in (1, 2, 3):
            for case_id in ("p1", "x1"):
                self.assertIn(f'id="trace-{run}-{case_id}"', self.html)

    def test_the_page_is_self_contained_and_says_the_rates_come_from_the_stored_runs(self):
        self.assertNotIn("<script", self.html)
        self.assertNotIn("http", self.html)
        self.assertIn("computed from the stored Runs", self.html)

    def test_text_from_the_runs_is_escaped(self):
        runs = stored_runs()
        runs[0]["outputs"][0]["answer"] = "<b>bold</b>"
        self.assertNotIn("<b>bold</b>", render_html_report(runs, CASES))


if __name__ == "__main__":
    unittest.main()
