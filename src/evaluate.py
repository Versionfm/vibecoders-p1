"""The evaluation command: run a case file through the answer function, store each run, write a report.

    python src/evaluate.py evaluation/sample_cases.json            # 3 runs, results under evaluation/runs/
    python src/evaluate.py <case file> --runs 3 --out evaluation/runs --label tutor_v3
"""
import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from cases import EvaluationCase, load_cases
from course_material import CourseMaterial, load_all_course_materials
from prompts import ROUTER_PROMPT_VERSION, TUTOR_PROMPT_VERSION
from scoring import CLASSES, MACRO_RECALL, score_run, summarise
from tutor import ChatModel, TutorResult, answer_question

DEFAULT_RUNS = 3
DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "evaluation" / "runs"

# Metrics that need the LLM judge (ticket #7). Shown as pending until the judge exists.
JUDGE_METRICS = ("End-to-end Success", "Supported rate", "Responsive rate")


@dataclass
class Run:
    number: int
    timestamp: str
    case_file: str
    app_model: str
    judge_model: str | None
    results: list[TutorResult]
    metrics: dict[str, float | None]


def run_evaluation(
    cases: list[EvaluationCase],
    model: ChatModel,
    runs: int = DEFAULT_RUNS,
    case_file: str = "",
    clock=lambda: datetime.now(timezone.utc),
    materials: dict[str, CourseMaterial] | None = None,
) -> list[Run]:
    materials = materials or load_all_course_materials()
    stored = []
    for number in range(1, runs + 1):
        timestamp = clock().isoformat(timespec="seconds")
        results = [answer_question(case.question, model, materials) for case in cases]
        stored.append(
            Run(number, timestamp, case_file, model.name, None, results, score_run(cases, results))
        )
    return stored


def run_record(run: Run, cases: list[EvaluationCase]) -> dict:
    return {
        "run": run.number,
        "timestamp": run.timestamp,
        "case_file": run.case_file,
        "prompt_versions": {"router": ROUTER_PROMPT_VERSION, "tutor": TUTOR_PROMPT_VERSION},
        "models": {"app": run.app_model, "judge": run.judge_model},
        "metrics": run.metrics,
        "outputs": [
            {"case_id": case.id, "type": case.type, "accepted_courses": case.accepted_courses, **_output(result)}
            for case, result in zip(cases, run.results, strict=True)
        ],
    }


def write_evaluation(runs: list[Run], cases: list[EvaluationCase], out_dir: Path, label: str = "") -> Path:
    stamp = datetime.fromisoformat(runs[0].timestamp).strftime("%Y-%m-%d_%H%M%S")
    run_dir = Path(out_dir) / (f"{stamp}_{label}" if label else stamp)
    run_dir.mkdir(parents=True, exist_ok=False)
    for run in runs:
        record = json.dumps(run_record(run, cases), indent=2, ensure_ascii=False)
        (run_dir / f"run_{run.number}.json").write_text(record + "\n", encoding="utf-8")
    (run_dir / "report.md").write_text(render_report(runs, cases), encoding="utf-8")
    return run_dir


def render_report(runs: list[Run], cases: list[EvaluationCase]) -> str:
    first = runs[0]
    type_counts = ", ".join(f"{n} {t}" for t, n in Counter(c.type for c in cases).items())
    run_headers = " | ".join(f"Run {r.number}" for r in runs)
    lines = [
        f"# Evaluation report, {first.timestamp}",
        "",
        f"- Case file: `{first.case_file}` ({len(cases)} cases: {type_counts})",
        f"- Runs: {len(runs)} (every case answered once per run)",
        f"- App model (Router and Course Tutor): `{first.app_model}`",
        f"- Prompt versions: Router `{ROUTER_PROMPT_VERSION}`, Course Tutor `{TUTOR_PROMPT_VERSION}`",
        f"- Judge model: {f'`{first.judge_model}`' if first.judge_model else 'none yet (LLM judge comes in ticket #7)'}",
        "",
        "## Metrics",
        "",
        f"Mean and range (lowest to highest) across the {len(runs)} runs. "
        "n/a: no cases of that kind in the case file.",
        "",
        f"| Metric | Mean | Range | {run_headers} |",
        "|---|---|---|" + "---|" * len(runs),
    ]
    for name in first.metrics:
        values = [r.metrics[name] for r in runs]
        summary = summarise(values)
        mean, spread = (
            (_pct(summary.mean), f"{_pct(summary.low)} to {_pct(summary.high)}") if summary else ("n/a", "n/a")
        )
        label = f"**{name}**" if name == MACRO_RECALL else name
        lines.append(f"| {label} | {mean} | {spread} | " + " | ".join(_pct(v) for v in values) + " |")
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
    args = parser.parse_args(argv)

    cases = load_cases(args.case_file)
    if model is None:
        from llm import get_chat_model

        model = get_chat_model()
    runs = run_evaluation(
        cases,
        model,
        runs=args.runs,
        case_file=_display_path(args.case_file),
        clock=clock or (lambda: datetime.now(timezone.utc)),
    )
    run_dir = write_evaluation(runs, cases, args.out, args.label)
    print(f"Stored {len(runs)} runs of {len(cases)} cases in {run_dir}")
    print(f"Report: {run_dir / 'report.md'}")
    return 0


def _output(result: TutorResult) -> dict:
    fields = asdict(result)
    for key in ("question", "router_prompt_version", "tutor_prompt_version", "model"):
        fields.pop(key)
    return fields


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


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _display_path(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path.cwd()).as_posix()
    except ValueError:
        return Path(path).as_posix()


if __name__ == "__main__":
    sys.exit(main())
