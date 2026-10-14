"""`report.html`: a pure render over stored Runs (the `run_N.json` records) and the cases they answered.

Self-contained in the style of the "twenty traces, scored" slide (ADR 0002): no JavaScript, no external files and no
chart library. Bars are HTML and CSS; light and dark themes follow the browser. `page`, `bar` and `pct` are the visual
language shared with `compare.html`.
"""
import json
from collections import Counter
from html import escape
from pathlib import Path

from cases import EvaluationCase
from scoring import END_TO_END, STEP_METRICS, STEPS, summarise

CSS = """
:root { color-scheme: light dark; --bg: #faf9f6; --fg: #1d1d1b; --muted: #6b6a66; --line: #e2e0da;
  --track: #ecebe6; --fill: #3d6fb6; --strong: #c2562d; --pass: #2f7d4f; --fail: #b3362f; --panel: #ffffff; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #161615; --fg: #ecebe6; --muted: #a09f99; --line: #34332f; --track: #2a2a27;
    --fill: #6e9be0; --strong: #ee8a5f; --pass: #6cc28f; --fail: #f07a72; --panel: #1f1f1d; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, sans-serif; }
main { max-width: 960px; margin: 0 auto; padding: 32px 16px 48px; }
h1 { font-size: 1.3rem; margin: 0 0 4px; } h2 { font-size: 1.05rem; margin: 32px 0 8px; }
.meta, small, footer { color: var(--muted); }
.headline { font-size: 3.2rem; font-weight: 700; line-height: 1.1; color: var(--strong); margin-top: 16px; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }
.bar-row { display: grid; grid-template-columns: 11rem 1fr 11rem; gap: 12px; align-items: center; margin: 8px 0; }
.track { position: relative; height: 18px; background: var(--track); border-radius: 4px; overflow: hidden; }
.fill { position: absolute; inset: 0 auto 0 0; background: var(--fill); }
.range { position: absolute; top: 0; bottom: 0; border-left: 2px solid var(--fg); border-right: 2px solid var(--fg);
  opacity: .45; }
.strong .fill { background: var(--strong); } .strong .label { font-weight: 700; }
.callout { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.callout .big { font-size: 2rem; font-weight: 700; }
.callout .matters .big { color: var(--strong); }
.starts td { font-size: 1.6rem; font-weight: 700; }
table { border-collapse: collapse; width: 100%; font-size: .88rem; }
th, td { text-align: left; vertical-align: top; padding: 6px 8px; border-bottom: 1px solid var(--line); }
.scroll { overflow-x: auto; }
.pass { color: var(--pass); } .fail { color: var(--fail); font-weight: 600; }
a { color: var(--fill); }
details summary { cursor: pointer; font-weight: 600; }
footer { margin-top: 32px; font-size: .85rem; }
@media (max-width: 640px) {
  .bar-row { grid-template-columns: 1fr; gap: 4px; } .callout { grid-template-columns: 1fr; }
}
"""


def load_runs(run_dir: Path) -> list[dict]:
    """The stored Runs of a run folder, in Run order."""
    records = [json.loads(p.read_text(encoding="utf-8")) for p in Path(run_dir).glob("run_*.json")]
    return sorted(records, key=lambda r: r["run"])


def page(title: str, body: str) -> str:
    """A whole self-contained HTML page with the shared stylesheet."""
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n"
    )


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def bar(label: str, values: list[float | None], strong: bool = False) -> str:
    """One pass-rate bar over the Runs: the mean filled, the range (lowest to highest) marked, both as text."""
    summary = summarise(values)
    if summary is None:
        track, text = "", "n/a"
    else:
        track = (
            f'<span class="fill" style="width:{summary.mean:.1%}"></span>'
            f'<span class="range" style="left:{summary.low:.1%};width:{summary.high - summary.low:.1%}"></span>'
        )
        text = f"{pct(summary.mean)} <small>{pct(summary.low)} to {pct(summary.high)}</small>"
    return (
        f'<div class="bar-row{" strong" if strong else ""}"><span class="label">{escape(label)}</span>'
        f'<span class="track">{track}</span><span class="value">{text}</span></div>'
    )


def render_html_report(runs: list[dict], cases: list[EvaluationCase]) -> str:
    first = runs[0]
    questions = {c.id: c.question for c in cases}
    rates = {name: [r["metrics"][name] for r in runs] for name in STEP_METRICS}
    end_to_end, answer = summarise(rates[END_TO_END]), summarise(rates["Answer Step"])
    traces = [(r["run"], o) for r in runs for o in r["outputs"]]
    failing = [(run, o) for run, o in traces if o["steps"]["earliest_failing_step"]]
    starts = Counter(o["steps"]["earliest_failing_step"]["step"] for _, o in failing)
    patterns: dict[tuple[str, str], list] = {}
    for run, o in failing:
        f = o["steps"]["earliest_failing_step"]
        patterns.setdefault((f["step"], f["reason"]), []).append((run, o))
    prompts = ", ".join(f"{name} {version}" for name, version in first["prompt_versions"].items())

    body = f"""
<h1>{len(traces)} Traces, scored</h1>
<p class="meta">Tutor <b>{escape(first["tutor"])}</b> · model <b>{escape(str(first["models"]["app"]))}</b> ·
prompts {escape(prompts)} · case file <b>{escape(first["case_file"])}</b> · {len(runs)} Runs of {len(cases)} cases</p>
<div class="headline">{pct(end_to_end and end_to_end.mean)}</div>
<p>{END_TO_END}, mean over {len(runs)} Runs (range {_range(end_to_end)}): the Trace passes the Search, Path and Answer
Steps.</p>

<h2>Pass rate per Step</h2>
<div class="panel">
{"".join(bar(name, rates[name], strong=name == END_TO_END) for name in STEP_METRICS)}
<small>Bar: mean over the Runs. Marks: lowest to highest Run. Answer Step uses code checks only; claims are not
checked until the LLM judge exists.</small>
</div>

<div class="callout" style="margin-top:16px">
<div class="panel"><div class="big">{pct(answer and answer.mean)}</div>Answer Step:
the number you would have reported</div>
<div class="panel matters"><div class="big">{pct(end_to_end and end_to_end.mean)}</div>{END_TO_END}:
the number that matters</div>
</div>

<h2>Where to start</h2>
<p>Failing Traces by the earliest Step they fail ({len(failing)} of {len(traces)} Traces fail).</p>
<table class="panel starts"><tr>{"".join(f"<th>{s} Step</th>" for s in STEPS)}</tr>
<tr>{"".join(f'<td data-step="{s}">{starts[s]}</td>' for s in STEPS)}</tr></table>

<h2>One example per failure pattern</h2>
{_patterns_table(patterns) if patterns else "<p>No failing Traces.</p>"}

<h2>All Traces</h2>
<details><summary>Show all {len(traces)} Traces</summary>
<div class="scroll"><table>
<tr><th>Run</th><th>Case</th><th>Question</th><th>Accepted</th><th>Read</th><th>Cited</th>
{"".join(f"<th>{s}</th>" for s in STEPS)}<th>{END_TO_END}</th><th>Earliest failing Step</th><th>Answer text</th></tr>
{"".join(_trace_row(run, o, questions.get(o["case_id"], "")) for run, o in traces)}
</table></div>
</details>

<footer>Every rate on this page is computed from the stored Runs (<code>run_N.json</code>) by
<code>src/html_report.py</code>, not typed in. First Run started {escape(first["timestamp"])}.</footer>
"""
    return page(f"Evaluation report {first['timestamp']}", body)


def _patterns_table(patterns: dict[tuple[str, str], list]) -> str:
    rows = []
    for (step, reason), examples in patterns.items():
        run, o = examples[0]
        steps = o["steps"]
        rows.append(
            f'<tr class="pattern"><td>{step}</td><td>{escape(reason)}</td><td>{len(examples)}</td>'
            f'<td><a href="#{_trace_id(run, o)}">{escape(o["case_id"])}</a> <small>Run {run}</small></td>'
            f'<td>{pct(steps["search"]["recall"])}</td>{_verdict(steps["path"]["passed"])}'
            f'{_verdict(steps["answer"]["passed"])}{_verdict(steps["end_to_end_success"])}'
            f"<td>{escape(_what_went_wrong(o))}</td></tr>"
        )
    return (
        '<div class="scroll"><table><tr><th>Earliest failing Step</th><th>Reason</th><th>Traces</th><th>Example</th>'
        f"<th>Search recall</th><th>Path</th><th>Answer</th><th>{END_TO_END}</th><th>What went wrong</th></tr>"
        + "".join(rows)
        + "</table></div>"
    )


def _what_went_wrong(o: dict) -> str:
    steps = o["steps"]
    first = steps["earliest_failing_step"]
    later = [s for s in STEPS if s != first["step"] and not steps[s.lower()]["passed"]]
    note = (
        f"Failed first at the {first['step']} Step: {first['reason']}. "
        f"Accepted {', '.join(o['accepted_courses'])}; read {', '.join(o['materials_read']) or 'nothing'}; "
        f"cited {', '.join(o['citations']) or 'no Section'}."
    )
    return note + (f" Also failed: {', '.join(later)}." if later else "")


def _trace_row(run: int, o: dict, question: str) -> str:
    steps = o["steps"]
    failure = steps["earliest_failing_step"]
    earliest = f"{failure['step']}: {failure['reason']}" if failure else "-"
    return (
        f'<tr id="{_trace_id(run, o)}"><td>{run}</td><td>{escape(o["case_id"])}<br><small>{escape(o["type"])}</small>'
        f"</td><td>{escape(question)}</td><td>{escape(', '.join(o['accepted_courses']))}</td>"
        f"<td>{escape(', '.join(o['materials_read']) or '-')}</td><td>{escape(', '.join(o['citations']) or '-')}</td>"
        + "".join(_verdict(steps[s.lower()]["passed"]) for s in STEPS)
        + _verdict(steps["end_to_end_success"])
        + f"<td>{escape(earliest)}</td>"
        f"<td>{escape(o['error'] or o['answer'])}</td></tr>"
    )


def _trace_id(run: int, o: dict) -> str:
    return escape(f"trace-{run}-{o['case_id']}")


def _verdict(passed: bool) -> str:
    return '<td class="pass">pass</td>' if passed else '<td class="fail">fail</td>'


def _range(summary) -> str:
    return "n/a" if summary is None else f"{pct(summary.low)} to {pct(summary.high)}"
