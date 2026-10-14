"""The evaluation command: run a case file through the answer function, store each run, write a report.

    python src/evaluate.py evaluation/sample_cases.json            # 3 runs, results under evaluation/runs/
    python src/evaluate.py <case file> --runs 3 --out evaluation/runs --label tutor_v3 --workers 4

Each run is stored as soon as it finishes, so an interrupted evaluation keeps the runs that completed.
"""
import argparse
import itertools
import json
import sys
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from cases import EvaluationCase, load_cases
from course_material import CourseMaterial, default_course_materials
from prompts import ROUTER_PROMPT_VERSION, TUTOR_PROMPT_VERSION
from scoring import CLASSES, END_TO_END, MACRO_RECALL, STEP_METRICS, STEPS, score_run, score_trace, summarise
from tutor import ROUTED_TUTOR, ChatModel, TutorResult, answer_question

DEFAULT_RUNS = 3
DEFAULT_WORKERS = 1
DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "evaluation" / "runs"

# Metrics that need the LLM judge (ticket #7). Shown as pending until the judge exists.
JUDGE_METRICS = ("Supported rate", "Responsive rate")


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


def run_evaluation(
    cases: list[EvaluationCase],
    model: ChatModel,
    runs: int = DEFAULT_RUNS,
    case_file: str = "",
    clock=lambda: datetime.now(timezone.utc),
    materials: dict[str, CourseMaterial] | None = None,
    on_run: Callable[[Run], None] = lambda run: None,
    workers: int = DEFAULT_WORKERS,
) -> list[Run]:
    """Answer every case once per run. `on_run` gets each run as soon as it finishes (e.g. to store it).

    With `workers` > 1 the cases of a run are answered in parallel threads; results stay in case order.
    """
    materials = default_course_materials() if materials is None else materials
    stored = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for number in range(1, runs + 1):
            timestamp = clock().isoformat(timespec="seconds")
            results = list(pool.map(lambda case: answer_question(case.question, model, materials), cases))
            run = Run(
                number,
                timestamp,
                case_file,
                model.name,
                getattr(model, "thinking", None),
                None,
                results,
                score_run(cases, results),
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
        "prompt_versions": {"router": ROUTER_PROMPT_VERSION, "tutor": TUTOR_PROMPT_VERSION},
        "models": {"app": run.app_model, "judge": run.judge_model},
        "thinking": run.app_thinking,
        "metrics": run.metrics,
        "outputs": [
            {
                "case_id": case.id,
                "type": case.type,
                "accepted_courses": case.accepted_courses,
                **_output(result),
                "steps": _steps(case, result),
            }
            for case, result in zip(cases, run.results, strict=True)
        ],
    }


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
    (run_dir / "report.md").write_text(render_report(runs, cases), encoding="utf-8")


def render_report(runs: list[Run], cases: list[EvaluationCase]) -> str:
    first = runs[0]
    type_counts = ", ".join(f"{n} {t}" for t, n in Counter(c.type for c in cases).items())
    run_headers = " | ".join(f"Run {r.number}" for r in runs)
    lines = [
        f"# Evaluation report, {first.timestamp}",
        "",
        f"- Case file: `{first.case_file}` ({len(cases)} cases: {type_counts})",
        f"- Runs: {len(runs)} (every case answered once per run)",
        f"- App model (Router and Course Tutor): `{first.app_model}`. Thinking: {_on_off(first.app_thinking)}",
        f"- Prompt versions: Router `{ROUTER_PROMPT_VERSION}`, Course Tutor `{TUTOR_PROMPT_VERSION}`",
        f"- Judge model: {f'`{first.judge_model}`' if first.judge_model else 'none yet (LLM judge comes in ticket #7)'}",
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
        "scope. Code checks only: claims are not checked until the LLM judge exists (ticket #7).",
        f"- {END_TO_END}: the Trace passes all three Steps.",
        "",
        "Per case: Traces passing each Step out of the runs, and the earliest failing Step with its reason.",
        "",
        f"| Case | Type | {' | '.join(STEPS)} | {END_TO_END} | Earliest failing Step |",
        "|---|---|---|---|---|---|---|",
        *(_step_row(case, [r.results[index] for r in runs]) for index, case in enumerate(cases)),
        "",
        "## Metrics",
        "",
        f"Mean and range (lowest to highest) across the {len(runs)} runs. "
        "n/a: no cases of that kind in the case file.",
        "",
        f"| Metric | Mean | Range | {run_headers} |",
        "|---|---|---|" + "---|" * len(runs),
    ]
    lines += [_metric_row(runs, name, bold=name == MACRO_RECALL) for name in first.metrics if name not in STEP_METRICS]
    for name in JUDGE_METRICS:
        lines.append(f"| {name} | pending | needs the LLM judge (ticket #7) |" + " |" * len(runs))
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


def main(argv: list[str] | None = None, model: ChatModel | None = None, clock=None) -> int:
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
    args = parser.parse_args(argv)

    cases = load_cases(args.case_file)
    if model is None:
        from llm import get_chat_model

        model = get_chat_model()
    clock = clock or (lambda: datetime.now(timezone.utc))
    run_dir = create_run_folder(args.out, clock(), args.label)

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
    )
    write_report(runs, cases, run_dir)
    print(f"Stored {len(runs)} runs of {len(cases)} cases in {run_dir}")
    print(f"Report: {run_dir / 'report.md'}")
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


def _step_row(case: EvaluationCase, results: list[TutorResult]) -> str:
    scores = [score_trace(case, r) for r in results]
    passed = [sum(getattr(s, step.lower()).passed for s in scores) for step in STEPS]
    successes = sum(s.success for s in scores)
    failures = Counter(f"{step}: {reason}" for step, reason in (s.earliest_failure for s in scores if not s.success))
    earliest = "; ".join(f"{failure} ({n}/{len(scores)})" for failure, n in failures.items()) or "-"
    counts = " | ".join(f"{n}/{len(scores)}" for n in (*passed, successes))
    return f"| {case.id} | {case.type} | {counts} | {earliest.replace('|', '/')} |"


def _steps(case: EvaluationCase, result: TutorResult) -> dict:
    score = score_trace(case, result)
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
