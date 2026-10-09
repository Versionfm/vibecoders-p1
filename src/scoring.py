"""Seam B: metrics as pure functions over evaluation cases and answer results (paired by position)."""
from dataclasses import dataclass

from cases import EvaluationCase
from tutor import OUT_OF_SCOPE, TutorResult

CLASSES = ("GAIF", "PEID", "AITB", "DTGS", OUT_OF_SCOPE)

MACRO_RECALL = "Recall (macro average)"


@dataclass(frozen=True)
class Summary:
    mean: float
    low: float
    high: float


def score_run(cases: list[EvaluationCase], results: list[TutorResult]) -> dict[str, float | None]:
    """Every metric of one run, by report name. None where a metric has no cases to score.

    End-to-end Success, Supported rate and Responsive rate need the LLM judge's verdicts; they join here in
    ticket #7 (the report lists them as pending until then).
    """
    per_class = recall_per_class(cases, results)
    return {
        "Routing accuracy": routing_accuracy(cases, results),
        **{f"Recall {c}": v for c, v in per_class.items()},
        MACRO_RECALL: macro_recall(per_class),
        "Citation correctness": citation_correctness_rate(cases, results),
        "Refusal correctness": refusal_correctness(cases, results),
        "Out of scope correctness": out_of_scope_correctness(cases, results),
    }


def summarise(values: list[float | None]) -> Summary | None:
    """Mean and range (lowest, highest) across runs, ignoring runs where the metric had no cases."""
    present = [v for v in values if v is not None]
    if not present:
        return None
    return Summary(sum(present) / len(present), min(present), max(present))


def routing_accuracy(cases: list[EvaluationCase], results: list[TutorResult]) -> float:
    hits = [_routed_correctly(c, r) for c, r in zip(cases, results, strict=True)]
    return sum(hits) / len(hits)


def recall_per_class(cases: list[EvaluationCase], results: list[TutorResult]) -> dict[str, float | None]:
    """Recall for each of the five classes; None for a class with no cases.

    A case belongs to one reference class: the routed Course when it is one of the Accepted Courses,
    otherwise its first Accepted Course. So an Overlap Case routed to either Accepted Course is a hit.
    """
    hits = {c: 0 for c in CLASSES}
    totals = {c: 0 for c in CLASSES}
    for case, result in zip(cases, results, strict=True):
        correct = _routed_correctly(case, result)
        reference = result.course if correct else case.accepted_courses[0]
        totals[reference] += 1
        hits[reference] += correct
    return {c: hits[c] / totals[c] if totals[c] else None for c in CLASSES}


def macro_recall(per_class: dict[str, float | None]) -> float | None:
    """Unweighted mean of the per-class recalls, over the classes that have cases."""
    values = [v for v in per_class.values() if v is not None]
    return sum(values) / len(values) if values else None


def citation_correctness_rate(cases: list[EvaluationCase], results: list[TutorResult]) -> float | None:
    """Share of answers given where an answer was expected that cite an expected Section and no invalid one."""
    scored = [
        bool(set(r.citations) & set(c.expected_sections)) and not r.invalid_citations
        for c, r in zip(cases, results, strict=True)
        if expects_answer(c) and gave_answer(r)
    ]
    return _rate(scored)


def refusal_correctness(cases: list[EvaluationCase], results: list[TutorResult]) -> float | None:
    """Share of Refusal-expected cases routed to an Accepted Course that gave the Refusal."""
    scored = [
        _routed_correctly(c, r) and r.is_refusal and r.error is None
        for c, r in zip(cases, results, strict=True)
        if c.expect_refusal
    ]
    return _rate(scored)


def out_of_scope_correctness(cases: list[EvaluationCase], results: list[TutorResult]) -> float | None:
    """Share of Out of scope-expected cases that the Router marked Out of scope."""
    scored = [r.course == OUT_OF_SCOPE for c, r in zip(cases, results, strict=True) if expects_out_of_scope(c)]
    return _rate(scored)


def expects_out_of_scope(case: EvaluationCase) -> bool:
    return case.accepted_courses == [OUT_OF_SCOPE]


def expects_answer(case: EvaluationCase) -> bool:
    return not case.expect_refusal and not expects_out_of_scope(case)


def gave_answer(result: TutorResult) -> bool:
    return result.error is None and result.course not in (None, OUT_OF_SCOPE) and not result.is_refusal


def _rate(scored: list[bool]) -> float | None:
    return sum(scored) / len(scored) if scored else None


def _routed_correctly(case: EvaluationCase, result: TutorResult) -> bool:
    return result.course in case.accepted_courses
