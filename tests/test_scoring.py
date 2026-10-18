"""Seam B: scoring is pure functions over cases and answer results. Expected values are worked out by hand."""
import unittest

from cases import EvaluationCase
from scoring import (
    citation_correctness_rate,
    macro_recall,
    out_of_scope_correctness,
    recall_per_class,
    refusal_correctness,
    routing_accuracy,
    score_run,
    summarise,
)
from tutor import TutorResult


def case(case_id, accepted, case_type="in_material", expected_sections=(), expect_refusal=False):
    return EvaluationCase(
        id=case_id,
        type=case_type,
        question=f"question {case_id}",
        accepted_courses=list(accepted),
        expected_sections=list(expected_sections),
        expect_refusal=expect_refusal,
        key_facts=[],
    )


def routed(course, **fields):
    return TutorResult(question="q", course=course, **fields)


class RoutingAccuracyTest(unittest.TestCase):
    def test_either_accepted_course_of_an_overlap_case_counts_as_correct(self):
        cases = [
            case("o1", ["PEID", "AITB"], "overlap"),
            case("o2", ["PEID", "AITB"], "overlap"),
            case("o3", ["DTGS", "AITB"], "overlap"),
            case("g1", ["GAIF"]),
        ]
        results = [routed("PEID"), routed("AITB"), routed("PEID"), routed("GAIF")]
        # o1 right (first Accepted Course), o2 right (second), o3 wrong, g1 right -> 3 of 4
        self.assertAlmostEqual(routing_accuracy(cases, results), 0.75)

    def test_a_router_error_counts_as_a_routing_failure(self):
        cases = [case("p1", ["PEID"]), case("x1", ["OUT_OF_SCOPE"], "out_of_scope")]
        results = [TutorResult(question="q", error="Router reply is not valid JSON"), routed("OUT_OF_SCOPE")]
        self.assertAlmostEqual(routing_accuracy(cases, results), 0.5)


class RecallPerClassTest(unittest.TestCase):
    def test_recall_per_class_over_the_five_classes_and_its_macro_average(self):
        cases = [
            case("g1", ["GAIF"]),
            case("g2", ["GAIF"]),
            case("p1", ["PEID"]),
            case("o1", ["PEID", "AITB"], "overlap"),
            case("o2", ["PEID", "AITB"], "overlap"),
            case("d1", ["DTGS"]),
            case("x1", ["OUT_OF_SCOPE"], "out_of_scope"),
            case("x2", ["OUT_OF_SCOPE"], "out_of_scope"),
        ]
        results = [
            routed("GAIF"),
            routed("PEID"),
            routed("PEID"),
            routed("AITB"),  # Overlap Case routed to an Accepted Course: a hit for AITB
            routed("DTGS"),  # Overlap Case routed elsewhere: a miss for its first Accepted Course, PEID
            routed("DTGS"),
            routed("OUT_OF_SCOPE"),
            TutorResult(question="q", error="Router reply is not valid JSON"),
        ]
        per_class = recall_per_class(cases, results)
        self.assertEqual(
            per_class,
            {"GAIF": 0.5, "PEID": 0.5, "AITB": 1.0, "DTGS": 1.0, "OUT_OF_SCOPE": 0.5},
        )
        self.assertAlmostEqual(macro_recall(per_class), 0.7)  # (0.5 + 0.5 + 1 + 1 + 0.5) / 5

    def test_a_class_with_no_cases_has_no_recall_and_is_left_out_of_the_macro_average(self):
        cases = [case("g1", ["GAIF"]), case("p1", ["PEID"])]
        results = [routed("GAIF"), routed("AITB")]
        per_class = recall_per_class(cases, results)
        self.assertEqual(per_class["GAIF"], 1.0)
        self.assertEqual(per_class["PEID"], 0.0)
        self.assertIsNone(per_class["DTGS"])
        self.assertAlmostEqual(macro_recall(per_class), 0.5)

class CitationCorrectnessTest(unittest.TestCase):
    def test_counts_answers_that_cite_an_expected_section_and_no_invalid_one(self):
        cases = [
            case("a1", ["PEID"], expected_sections=["PEID-2.3"]),
            case("a2", ["PEID"], expected_sections=["PEID-2.3"]),
            case("a3", ["GAIF"], expected_sections=["GAIF-2.9"]),
            case("a4", ["DTGS"], expected_sections=["DTGS-1.1"]),
            case("r1", ["PEID"], "refusal", expect_refusal=True),
        ]
        results = [
            routed("PEID", answer="...", citations=["PEID-2.3", "PEID-2.5"]),
            routed("PEID", answer="...", citations=["PEID-2.3", "PEID-9.9"], invalid_citations=["PEID-9.9"]),
            routed("GAIF", answer="...", citations=["GAIF-2.8"]),
            routed("DTGS", answer="This is not covered in the DTGS material.", is_refusal=True),
            routed("PEID", answer="...", citations=["PEID-2.3"]),
        ]
        # Only answers given where an answer was expected count: a1 (right), a2 (invalid), a3 (no expected) -> 1 of 3
        self.assertAlmostEqual(citation_correctness_rate(cases, results), 1 / 3)

    def test_no_answers_to_score_gives_no_rate(self):
        cases = [case("r1", ["PEID"], "refusal", expect_refusal=True)]
        results = [routed("PEID", answer="This is not covered in the PEID material.", is_refusal=True)]
        self.assertIsNone(citation_correctness_rate(cases, results))


class RefusalAndOutOfScopeCorrectnessTest(unittest.TestCase):
    def setUp(self):
        self.cases = [
            case("r1", ["PEID"], "refusal", expect_refusal=True),
            case("r2", ["AITB"], "refusal", expect_refusal=True),
            case("r3", ["DTGS"], "refusal", expect_refusal=True),
            case("r4", ["GAIF"], "refusal", expect_refusal=True),
            case("x1", ["OUT_OF_SCOPE"], "out_of_scope"),
            case("x2", ["OUT_OF_SCOPE"], "out_of_scope"),
            case("a1", ["PEID"], expected_sections=["PEID-2.3"]),
        ]
        self.results = [
            routed("PEID", answer="This is not covered in the PEID material.", is_refusal=True),
            routed("AITB", answer="An invented answer.", citations=[]),
            routed("PEID", answer="This is not covered in the PEID material.", is_refusal=True),  # wrong Course
            routed("GAIF", answer="This is not covered in the GAIF material.", is_refusal=True),
            routed("OUT_OF_SCOPE"),
            routed("GAIF", answer="...", citations=["GAIF-1.1"]),
            routed("PEID", answer="This is not covered in the PEID material.", is_refusal=True),
        ]

    def test_refusal_correctness_needs_an_accepted_course_and_the_refusal(self):
        # r1 right, r2 answered, r3 refused in the wrong Course, r4 right -> 2 of 4
        self.assertAlmostEqual(refusal_correctness(self.cases, self.results), 0.5)

    def test_out_of_scope_correctness(self):
        # x1 right, x2 routed to GAIF -> 1 of 2
        self.assertAlmostEqual(out_of_scope_correctness(self.cases, self.results), 0.5)

class AcrossRunsTest(unittest.TestCase):
    def test_mean_and_range_across_three_runs(self):
        summary = summarise([0.5, 1.0, 0.75])
        self.assertAlmostEqual(summary.mean, 0.75)
        self.assertEqual((summary.low, summary.high), (0.5, 1.0))

    def test_runs_without_a_value_are_left_out_and_no_values_give_no_summary(self):
        self.assertAlmostEqual(summarise([None, 0.4, 0.6]).mean, 0.5)
        self.assertIsNone(summarise([None, None, None]))

    def test_one_run_is_scored_with_every_metric_and_the_macro_average_is_labelled_macro(self):
        cases = [case("g1", ["GAIF"], expected_sections=["GAIF-2.9"]), case("x1", ["OUT_OF_SCOPE"], "out_of_scope")]
        results = [routed("GAIF", answer="...", citations=["GAIF-2.9"]), routed("PEID", answer="...")]
        scores = score_run(cases, results)
        self.assertAlmostEqual(scores["Routing accuracy"], 0.5)
        self.assertAlmostEqual(scores["Recall GAIF"], 1.0)
        self.assertAlmostEqual(scores["Recall OUT_OF_SCOPE"], 0.0)
        self.assertIsNone(scores["Recall PEID"])
        self.assertAlmostEqual(scores["Recall (macro average)"], 0.5)
        self.assertAlmostEqual(scores["Citation correctness"], 1.0)
        self.assertIsNone(scores["Refusal correctness"])
        self.assertAlmostEqual(scores["Out of scope correctness"], 0.0)


if __name__ == "__main__":
    unittest.main()
