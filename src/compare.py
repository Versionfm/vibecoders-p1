"""The compare command: two run folders' stored Runs side by side, as `compare.html` in the second folder.

    python src/compare.py evaluation/runs/<run folder A> evaluation/runs/<run folder B>

Reads the stored `run_N.json` files only; makes no model calls. Warns on the page and in the console when the two
evaluations used different case files, models or thinking settings, so two changes are never compared as one.
"""
import argparse
from collections import Counter
from html import escape
from pathlib import Path

from html_report import bar, load_runs, page
from scoring import END_TO_END, STEP_METRICS


def differences(runs_a: list[dict], runs_b: list[dict]) -> list[str]:
    """One sentence per setting that differs between the two evaluations (first Run of each)."""
    a, b = runs_a[0], runs_b[0]
    settings = {
        "case file": lambda r: r["case_file"],
        "app model": lambda r: r["models"]["app"],
        "judge model": lambda r: r["models"]["judge"],
        "thinking": lambda r: {None: "not set", True: "on", False: "off"}[r["thinking"]],
    }
    return [
        f"different {name}: {value(a)} in A, {value(b)} in B."
        for name, value in settings.items()
        if value(a) != value(b)
    ]


def render_compare(runs_a: list[dict], runs_b: list[dict], name_a: str, name_b: str) -> str:
    warnings = differences(runs_a, runs_b)
    changed = _changed_cases(runs_a, runs_b)
    body = f"""
<h1>Compare two evaluations</h1>
<p class="meta">A <b>{escape(name_a)}</b> ({len(runs_a)} Runs) · B <b>{escape(name_b)}</b> ({len(runs_b)} Runs)</p>
{"".join(f'<p class="warning"><b class="fail">Warning:</b> {escape(w)}</p>' for w in warnings)}

<h2>Pass rate per Step</h2>
{"".join(_metric_panel(name, runs_a, runs_b) for name in STEP_METRICS)}
<small>Bar: mean over the Runs. Marks: lowest to highest Run.</small>

<h2>Cases whose {END_TO_END} changed</h2>
{_changed_table(changed, name_a, name_b) if changed else f"<p>No case changed its {END_TO_END}.</p>"}

<footer>Every rate on this page is computed from the stored Runs (<code>run_N.json</code>) of both run folders by
<code>src/compare.py</code>, not typed in.</footer>
"""
    return page(f"Compare {name_a} and {name_b}", body)


def _metric_panel(name: str, runs_a: list[dict], runs_b: list[dict]) -> str:
    """Bars are labelled with A or B and the tutor only: the run folder names are too long for the label column."""
    strong = name == END_TO_END
    return (
        f'<div class="panel" style="margin-bottom:8px"><b>{name}</b>'
        + bar(f"A {runs_a[0]['tutor']}", [r["metrics"][name] for r in runs_a], strong)
        + bar(f"B {runs_b[0]['tutor']}", [r["metrics"][name] for r in runs_b], strong)
        + "</div>"
    )


def _per_case(runs: list[dict]) -> dict[str, list[str | None]]:
    """Per case, per Run: the earliest failing Step, or None when the Trace succeeded end to end."""
    cases: dict[str, list[str | None]] = {}
    for run in runs:
        for o in run["outputs"]:
            failure = o["steps"]["earliest_failing_step"]
            cases.setdefault(o["case_id"], []).append(failure and failure["step"])
    return cases


def _changed_cases(runs_a: list[dict], runs_b: list[dict]) -> list[tuple[str, list, list]]:
    a, b = _per_case(runs_a), _per_case(runs_b)
    return [(case, a[case], b[case]) for case in a if case in b and _rate(a[case]) != _rate(b[case])]


def _rate(steps: list[str | None]) -> float:
    return steps.count(None) / len(steps)


def _cell(steps: list[str | None]) -> str:
    return f"{steps.count(None)}/{len(steps)}"


def _changed_table(changed: list, name_a: str, name_b: str) -> str:
    rows = "".join(
        f'<tr class="changed" id="case-{escape(case_id)}"><td>{escape(case_id)}</td>'
        f"<td>{_cell(a)}</td><td>{_failures(a)}</td><td>{_cell(b)}</td><td>{_failures(b)}</td></tr>"
        for case_id, a, b in changed
    )
    return (
        f'<div class="scroll"><table><tr><th>Case</th><th>A {END_TO_END}</th><th>A earliest failing Step</th>'
        f"<th>B {END_TO_END}</th><th>B earliest failing Step</th></tr>{rows}</table></div>"
        f"<small>A is {escape(name_a)}, B is {escape(name_b)}. Earliest failing Step: the Step and the number of Runs "
        "in which the case failed there first.</small>"
    )


def _failures(steps: list[str | None]) -> str:
    return ", ".join(f"{step} {count}" for step, count in Counter(filter(None, steps)).items()) or "-"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare the stored Runs of two run folders as compare.html.")
    parser.add_argument("run_folder_a", type=Path, help="run folder of the first evaluation (e.g. the baseline)")
    parser.add_argument("run_folder_b", type=Path, help="run folder of the second evaluation; compare.html goes here")
    args = parser.parse_args(argv)

    runs_a, runs_b = load_runs(args.run_folder_a), load_runs(args.run_folder_b)
    for folder, runs in ((args.run_folder_a, runs_a), (args.run_folder_b, runs_b)):
        if not runs:
            parser.error(f"no stored Runs (run_N.json) in {folder}")
    for warning in differences(runs_a, runs_b):
        print(f"Warning: {warning}")
    out = args.run_folder_b / "compare.html"
    out.write_text(
        render_compare(runs_a, runs_b, args.run_folder_a.resolve().name, args.run_folder_b.resolve().name),
        encoding="utf-8",
    )
    print(f"Compare page: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
