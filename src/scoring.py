"""Seam B: metrics as pure functions over evaluation cases and answer results (paired by position)."""
from dataclasses import dataclass

from cases import EvaluationCase
from course_material import COURSES
from tutor import OUT_OF_SCOPE, TutorResult

CLASSES = (*COURSES, OUT_OF_SCOPE)

MACRO_RECALL = "Recall (macro average)"
STEPS = ("Search", "Path", "Answer")
END_TO_END = "End-to-end Success"
STEP_METRICS = (*(f"{step} Step" for step in STEPS), END_TO_END)


@dataclass(frozen=True)
class Summary:
    mean: float
    low: float
    high: float


@dataclass(frozen=True)
class StepVerdict:
    passed: bool
    reason: str = ""  # why it failed; empty when it passed


@dataclass(frozen=True)
class SearchVerdict(StepVerdict):
    recall: float | None = None  # share of Accepted Courses read; None for an Out of scope case
    extra_reads: tuple[str, ...] = ()  # Courses read that are not Accepted Courses, in order


def search_step(case: EvaluationCase, result: TutorResult) -> SearchVerdict:
    """At least one Accepted Course and no other Course chosen or read; nothing at all for an Out of scope case."""
    read = list(dict.fromkeys(result.materials_read))
    extra = tuple(c for c in read if c not in case.accepted_courses)
    if expects_out_of_scope(case):
        reason = f"read {', '.join(extra)} for an Out of scope case" if extra else ""
        return SearchVerdict(not extra, reason, None, extra)
    recall = len(set(read) & set(case.accepted_courses)) / len(case.accepted_courses)
    if extra:
        reason = f"read {', '.join(extra)}, not an Accepted Course"
    elif not read:
        reason = "no Course Material read" + (f" ({result.error})" if result.error else "")
    else:
        reason = ""
    return SearchVerdict(not reason, reason, recall, extra)


def path_step(case: EvaluationCase, result: TutorResult) -> StepVerdict:
    """Got to its answer properly. The first broken rule is the reason.

    Fails on a failed model call or an invalid Router reply, a `read_file` argument that is not a Course, a Course
    Material read twice, the Read limit reached, or an in-scope answer or Refusal given without any Read.
    """
    invalid = [a for a in result.read_arguments if a not in COURSES]
    repeated = sorted({c for c in result.materials_read if result.materials_read.count(c) > 1})
    if result.error:
        return StepVerdict(False, result.error)
    if invalid:
        return StepVerdict(False, f"read_file asked for something that is not a Course: {', '.join(invalid)}")
    if repeated:
        return StepVerdict(False, f"read {', '.join(repeated)} more than once")
    if result.read_limit_hit:
        return StepVerdict(False, "Read limit reached")
    answered = result.answer.strip() and result.course != OUT_OF_SCOPE
    if answered and not result.materials_read and not expects_out_of_scope(case):
        return StepVerdict(False, "answered without reading any Course Material")
    return StepVerdict(True)


def answer_step(case: EvaluationCase, result: TutorResult) -> StepVerdict:
    """Cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope.

    Code checks only: once the LLM judge exists (#7) the answer must also be Supported and Responsive.
    """
    if result.error:
        return StepVerdict(False, "no answer")
    if expects_out_of_scope(case):
        return StepVerdict(True) if gave_out_of_scope(result) else StepVerdict(False, "expected Out of scope")
    if case.expect_refusal:
        return StepVerdict(True) if result.is_refusal else StepVerdict(False, "expected the Refusal")
    if gave_out_of_scope(result):
        return StepVerdict(False, "gave Out of scope where an answer was expected")
    if result.is_refusal:
        return StepVerdict(False, "gave the Refusal where an answer was expected")
    if result.invalid_citations:
        return StepVerdict(False, f"cites invalid Sections: {', '.join(result.invalid_citations)}")
    if not set(result.citations) & set(case.expected_sections):
        return StepVerdict(False, f"cites no expected Section ({', '.join(case.expected_sections)})")
    return StepVerdict(True)


@dataclass(frozen=True)
class TraceScore:
    search: SearchVerdict
    path: StepVerdict
    answer: StepVerdict
    errored: bool = False  # a failed model call or invalid Router reply, filed under the Path Step

    @property
    def success(self) -> bool:
        """End-to-end Success: the Trace passes the Search, Path and Answer Steps."""
        return self.earliest_failure is None

    @property
    def earliest_failure(self) -> tuple[str, str] | None:
        """(Step, reason) of the first failing Step in the order Search, Path, Answer; None when all pass.

        A Trace with an error fails at the Path Step, even when nothing was read (which also fails Search)."""
        if self.errored:
            return "Path", self.path.reason
        for step, verdict in zip(STEPS, (self.search, self.path, self.answer)):
            if not verdict.passed:
                return step, verdict.reason
        return None


def score_trace(case: EvaluationCase, result: TutorResult) -> TraceScore:
    return TraceScore(
        search_step(case, result), path_step(case, result), answer_step(case, result), result.error is not None
    )


def gave_out_of_scope(result: TutorResult) -> bool:
    """Out of scope with no Course Material read. Out of scope after a Read is a failed answer, not Out of scope."""
    return result.error is None and result.course == OUT_OF_SCOPE and not result.materials_read


def score_run(cases: list[EvaluationCase], results: list[TutorResult]) -> dict[str, float | None]:
    """Every metric of one run, by report name. None where a metric has no cases to score.

    Supported rate and Responsive rate need the LLM judge's verdicts; they join here in ticket #7 (the report
    lists them as pending until then).
    """
    per_class = recall_per_class(cases, results)
    traces = [score_trace(c, r) for c, r in zip(cases, results, strict=True)]
    return {
        **{f"{step} Step": _rate([getattr(t, step.lower()).passed for t in traces]) for step in STEPS},
        END_TO_END: _rate([t.success for t in traces]),
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
