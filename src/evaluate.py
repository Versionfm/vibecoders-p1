"""The evaluation command: run a case file through the answer function, store each run, write a report.

    python src/evaluate.py evaluation/sample_cases.json            # 3 runs, results under evaluation/runs/
    python src/evaluate.py <case file> --runs 3 --out evaluation/runs --label tutor_v3 --workers 4
    python src/evaluate.py <case file> --tutor agentic            # the Agentic Tutor instead of the Routed Tutor

Every evaluation is judged by the LLM judge set in .env (`LLM_JUDGE_MODEL`, see .env.example); the command refuses to
run without it. Each run is stored as soon as it finishes, so an interrupted evaluation keeps the runs that completed.
"""
import argparse
import itertools
import json
import sys
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from cases import EvaluationCase, load_cases
from course_material import CourseMaterial, default_course_materials
from html_report import load_runs, render_html_report
from judge import JUDGE_PROMPT_VERSIONS, Judgement, judge_answer
from prompts import AGENTIC_TUTOR_PROMPT_VERSION, ROUTER_PROMPT_VERSION, TUTOR_PROMPT_VERSION
from scoring import (
    CLASSES,
    END_TO_END,
    JUDGE_METRICS,
    JUDGE_UNDECIDED,
    MACRO_RECALL,
    STEP_METRICS,
    STEPS,
    needs_judge,
    score_run,
    score_trace,
    summarise,
)
from tutor import AGENTIC_TUTOR, ROUTED_TUTOR, TUTORS, ChatModel, TutorResult, answer_question

PROMPT_VERSIONS = {
    ROUTED_TUTOR: {"router": ROUTER_PROMPT_VERSION, "tutor": TUTOR_PROMPT_VERSION},
    AGENTIC_TUTOR: {"agentic_tutor": AGENTIC_TUTOR_PROMPT_VERSION},
}
APP_MODEL_ROLES = {ROUTED_TUTOR: "Router and Course Tutor", AGENTIC_TUTOR: "Agentic Tutor"}
DEFAULT_RUNS = 3
DEFAULT_WORKERS = 1
DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "evaluation" / "runs"


@dataclass
class Run:
    number: int
    timestamp: str
    case_file: str
    app_model: str
    app_thinking: bool | None
    judge_model: str | None
    results: list[TutorResult]
    metrics: dict[str, float | None]
    tutor: str = ROUTED_TUTOR
    judgements: list[Judgement | None] = field(default_factory=list)  # one per case; empty when no judge was set


def run_evaluation(
    cases: list[EvaluationCase],
    model: ChatModel,
    runs: int = DEFAULT_RUNS,
    case_file: str = "",
    clock=lambda: datetime.now(timezone.utc),
    materials: dict[str, CourseMaterial] | None = None,
    on_run: Callable[[Run], None] = lambda run: None,
    workers: int = DEFAULT_WORKERS,
    tutor: str = ROUTED_TUTOR,
    judge: ChatModel | None = None,
) -> list[Run]:
    """Answer every case once per run. `on_run` gets each run as soon as it finishes (e.g. to store it).

    With a `judge`, every answer given where an answer was expected is judged right after it is given (never a
    Refusal or Out of scope). With `workers` > 1 the cases of a run are answered in parallel threads; results stay
    in case order.
    """
    materials = default_course_materials() if materials is None else materials

    def answer(case: EvaluationCase) -> tuple[TutorResult, Judgement | None]:
        result = answer_question(case.question, model, materials, tutor)
        judged = judge is not None and needs_judge(case, result)
        return result, judge_answer(case, result, judge, materials) if judged else None

    stored = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for number in range(1, runs + 1):
            timestamp = clock().isoformat(timespec="seconds")
            answered = list(pool.map(answer, cases))
            results = [result for result, _ in answered]
            judgements = [judgement for _, judgement in answered] if judge is not None else []
            run = Run(
                number,
                timestamp,
                case_file,
                model.name,
                getattr(model, "thinking", None),
                judge.name if judge is not None else None,
                results,
                score_run(cases, results, judgements if judge is not None else None),
                tutor,
                judgements,
            )
            on_run(run)
            stored.append(run)
    return stored


def run_record(run: Run, cases: list[EvaluationCase]) -> dict:
    return {
        "run": run.number,
        "timestamp": run.timestamp,
        "tutor": run.tutor,
        "case_file": run.case_file,
        "prompt_versions": _prompt_versions(run),
        "models": {"app": run.app_model, "judge": run.judge_model},
        "thinking": run.app_thinking,
        "metrics": run.metrics,
        "outputs": [
            {
                "case_id": case.id,
                "type": case.type,
                "accepted_courses": case.accepted_courses,
                **_output(result),
                "judge": judgement and asdict(judgement),
                "steps": _steps(case, result, judgement),
            }
            for case, result, judgement in zip(cases, run.results, _judgements(run), strict=True)
        ],
    }


def _prompt_versions(run: Run) -> dict[str, str]:
    return {**PROMPT_VERSIONS[run.tutor], **(JUDGE_PROMPT_VERSIONS if run.judge_model else {})}


def _judgements(run: Run) -> list[Judgement | None]:
    return run.judgements or [None] * len(run.results)


def create_run_folder(out_dir: Path, started: datetime, label: str = "") -> Path:
    """A new folder `<date>_<time>[_<label>]`; a numeric suffix is added when that name is taken."""
    name = started.strftime("%Y-%m-%d_%H%M%S") + (f"_{label}" if label else "")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for attempt in itertools.count(1):
        run_dir = Path(out_dir) / (name if attempt == 1 else f"{name}_{attempt}")
        try:
            run_dir.mkdir()
            return run_dir
        except FileExistsError:
            continue


def write_run(run: Run, cases: list[EvaluationCase], run_dir: Path) -> None:
    record = json.dumps(run_record(run, cases), indent=2, ensure_ascii=False)
    (run_dir / f"run_{run.number}.json").write_text(record + "\n", encoding="utf-8")


def write_report(runs: list[Run], cases: list[EvaluationCase], run_dir: Path) -> None:
    stored = load_runs(run_dir)
    (run_dir / "report.md").write_text(render_report(runs, cases, stored), encoding="utf-8")
    (run_dir / "report.html").write_text(render_html_report(stored, cases), encoding="utf-8")


def render_report(runs: list[Run], cases: list[EvaluationCase], stored: list[dict]) -> str:
    """`stored`: the same Runs as stored by `write_run`, whose Step verdicts are read rather than scored again."""
    first = runs[0]
    type_counts = ", ".join(f"{n} {t}" for t, n in Counter(c.type for c in cases).items())
    run_headers = " | ".join(f"Run {r.number}" for r in runs)
    lines = [
        f"# Evaluation report, {first.timestamp}",
        "",
        f"- Case file: `{first.case_file}` ({len(cases)} cases: {type_counts})",
        f"- Runs: {len(runs)} (every case answered once per run)",
        f"- App model ({APP_MODEL_ROLES[first.tutor]}): `{first.app_model}`. Thinking: {_on_off(first.app_thinking)}",
        "- Prompt versions: " + ", ".join(f"{k} `{v}`" for k, v in _prompt_versions(first).items()),
        f"- Judge model: {f'`{first.judge_model}`' if first.judge_model else 'none (LLM_JUDGE_MODEL not set)'}. "
        + ("The Answer Step uses the judge." if first.judge_model else "The Answer Step is code checks only."),
        f"- Tutor: `{first.tutor}`",
        "",
        "## Steps",
        "",
        f"Share of Traces passing each Step, as mean and range (lowest to highest) across the {len(runs)} runs.",
        "",
        f"| Step | Mean | Range | {run_headers} |",
        "|---|---|---|" + "---|" * len(runs),
        *(_metric_row(runs, name, bold=name == END_TO_END) for name in STEP_METRICS),
        "",
        "- Search Step: at least one Accepted Course and no other Course chosen or read; none for an Out of scope "
        "case. For the Routed Tutor the routed Course is the Course Material read.",
        "- Path Step: no failed model call or invalid Router reply, no `read_file` argument that is not a Course, "
        "no Course Material read twice, within the Read limit, and no in-scope answer or Refusal without a Read.",
        "- Answer Step: cites an expected Section and only valid Sections, or gives the expected Refusal or Out of "
        "scope; "
        + (
            "an expected answer must also be judged Supported and Responsive by the LLM judge."
            if first.judge_model
            else "code checks only: no judge model was set, so claims are not checked."
        ),
        f"- {END_TO_END}: the Trace passes all three Steps.",
        "",
        "Per case: Traces passing each Step out of the runs, and the earliest failing Step with its reason.",
        "",
        f"| Case | Type | {' | '.join(STEPS)} | {END_TO_END} | Earliest failing Step |",
        "|---|---|---|---|---|---|---|",
        *(_step_row(case, [r["outputs"][index]["steps"] for r in stored]) for index, case in enumerate(cases)),
        "",
        "## Metrics",
        "",
        f"Mean and range (lowest to highest) across the {len(runs)} runs. "
        "n/a: no cases of that kind in the case file.",
        "",
        f"| Metric | Mean | Range | {run_headers} |",
        "|---|---|---|" + "---|" * len(runs),
    ]
    shown = [name for name in first.metrics if name not in STEP_METRICS and name not in JUDGE_METRICS]
    lines += [_metric_row(runs, name, bold=name == MACRO_RECALL) for name in shown]
    for name in JUDGE_METRICS:
        if name in first.metrics:
            lines.append(_metric_row(runs, name))
        else:
            lines.append(f"| {name} | not measured | no judge model set |" + " |" * len(runs))
    lines += [
        "",
        "Definitions:",
        "",
        "- Routing accuracy: the Router's choice is one of the case's Accepted Courses.",
        f"- Recall per class over the five classes ({', '.join(CLASSES)}). A case counts for the routed Course "
        "when that is an Accepted Course, otherwise for its first Accepted Course, so an Overlap Case routed to "
        f"either Accepted Course is a hit. {MACRO_RECALL}: the unweighted mean over classes that have cases.",
        "- Citation correctness: of the answers given where an answer was expected, the share that cite at "
        "least one expected Section and no non-existent Section.",
        "- Refusal correctness: of the Refusal-expected cases, the share routed to an Accepted Course that gave "
        "the exact Refusal sentence.",
        "- Out of scope correctness: of the Out of scope-expected cases, the share the Router marked Out of scope.",
        "- Supported rate and Responsive rate: of the answers the judge was called for (an answer given where an "
        "answer was expected), the share judged Supported (every claim is in the Section it cites) and Responsive "
        f"(it addresses what was asked). {JUDGE_UNDECIDED}: the share of the judge's verdicts that were UNKNOWN or "
        "a judge error; both count as a fail.",
        "",
        "## Per case",
        "",
        "Routed Course and cited Sections in each run, separated by ` / `.",
        "",
        "| Case | Type | Accepted Courses | Routed | Cited Sections | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for index, case in enumerate(cases):
        results = [r.results[index] for r in runs]
        routed = " / ".join(r.course or "error" for r in results)
        cited = " / ".join(", ".join(r.citations) or "-" for r in results)
        lines.append(
            f"| {case.id} | {case.type} | {', '.join(case.accepted_courses)} | {routed} | {cited} | "
            f"{_notes(results)} |"
        )
    return "\n".join(lines) + "\n"


def main(
    argv: list[str] | None = None, model: ChatModel | None = None, clock=None, judge: ChatModel | None = None
) -> int:
    """`model` and `judge` stand in for the models from .env (tests); with `model` given, the judge comes only from
    `judge`."""
    parser = argparse.ArgumentParser(description="Run a case file through the Course Tutor and report metrics.")
    parser.add_argument("case_file", type=Path, help="JSON case file in the Golden Set format")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS, help="times each case is run (default 3)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR, help="folder for stored runs")
    parser.add_argument("--label", default="", help="short name added to the run folder, e.g. tutor_v3")
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"cases answered in parallel within a run (default {DEFAULT_WORKERS}; mind the endpoint's rate limit)",
    )
    parser.add_argument(
        "--tutor",
        choices=TUTORS,
        help=f"which tutor answers (default {ROUTED_TUTOR}); when given, it is added to the run folder name",
    )
    args = parser.parse_args(argv)

    cases = load_cases(args.case_file)
    if model is None:
        from llm import get_chat_model, get_judge_model

        model = get_chat_model()
        judge = judge or get_judge_model()
        if judge is None:
            raise SystemExit("LLM_JUDGE_MODEL is not set: the evaluation needs the LLM judge. Check your .env file.")
    print(f"Judge: {judge.name if judge else 'none, code checks only'}")
    clock = clock or (lambda: datetime.now(timezone.utc))
    run_dir = create_run_folder(args.out, clock(), "_".join(p for p in (args.label, args.tutor) if p))

    def store(run: Run) -> None:
        write_run(run, cases, run_dir)
        print(f"Run {run.number} of {args.runs} stored in {run_dir / f'run_{run.number}.json'}")

    runs = run_evaluation(
        cases,
        model,
        runs=args.runs,
        case_file=_display_path(args.case_file),
        clock=clock,
        on_run=store,
        workers=args.workers,
        tutor=args.tutor or ROUTED_TUTOR,
        judge=judge,
    )
    write_report(runs, cases, run_dir)
    print(f"Stored {len(runs)} runs of {len(cases)} cases in {run_dir}")
    print(f"Report: {run_dir / 'report.md'}")
    print(f"HTML report: {run_dir / 'report.html'}")
    return 0


def _output(result: TutorResult) -> dict:
    fields = asdict(result)
    for key in ("question", "router_prompt_version", "tutor_prompt_version", "model", "thinking", "tutor"):
        fields.pop(key)
    return fields


def _metric_row(runs: list[Run], name: str, bold: bool = False) -> str:
    values = [r.metrics[name] for r in runs]
    summary = summarise(values)
    mean, spread = (_pct(summary.mean), f"{_pct(summary.low)} to {_pct(summary.high)}") if summary else ("n/a", "n/a")
    label = f"**{name}**" if bold else name
    return f"| {label} | {mean} | {spread} | " + " | ".join(_pct(v) for v in values) + " |"


def _step_row(case: EvaluationCase, scores: list[dict]) -> str:
    """One case's stored Step verdicts (the "steps" of each Run's output) as a report row."""
    passed = [sum(s[step.lower()]["passed"] for s in scores) for step in STEPS]
    successes = sum(s["end_to_end_success"] for s in scores)
    failures = Counter(
        f"{f['step']}: {f['reason']}" for f in (s["earliest_failing_step"] for s in scores) if f is not None
    )
    earliest = "; ".join(f"{failure} ({n}/{len(scores)})" for failure, n in failures.items()) or "-"
    counts = " | ".join(f"{n}/{len(scores)}" for n in (*passed, successes))
    return f"| {case.id} | {case.type} | {counts} | {earliest.replace('|', '/')} |"


def _steps(case: EvaluationCase, result: TutorResult, judgement: Judgement | None = None) -> dict:
    score = score_trace(case, result, judgement)
    failure = score.earliest_failure
    return {
        **{step.lower(): asdict(getattr(score, step.lower())) for step in STEPS},
        "end_to_end_success": score.success,
        "earliest_failing_step": failure and {"step": failure[0], "reason": failure[1]},
    }


def _notes(results: list[TutorResult]) -> str:
    notes = []
    refusals = sum(r.is_refusal for r in results)
    errors = sum(r.error is not None for r in results)
    invalid = sorted({c for r in results for c in r.invalid_citations})
    if refusals:
        notes.append(f"Refusal in {refusals}/{len(results)}")
    if errors:
        notes.append(f"error in {errors}/{len(results)}")
    if invalid:
        notes.append(f"invalid citations: {', '.join(invalid)}")
    return "; ".join(notes) or "-"


def _on_off(thinking: bool | None) -> str:
    return "not set" if thinking is None else ("on" if thinking else "off")


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _display_path(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path.cwd()).as_posix()
    except ValueError:
        return Path(path).as_posix()


if __name__ == "__main__":
    sys.exit(main())
