---
status: accepted
---

# Score every Trace by Search, Path and Answer Steps; report them as HTML

To compare the Routed Tutor and the Agentic Tutor on equal terms, every Trace of both gets three Step verdicts (Search,
Path, Answer), and End-to-end Success means passing all three. A single answer-level rate hides where failures start:
an answer step can look high while End-to-end Success is far lower. The evaluation stays our own Python harness
(`src/evaluate.py`, `src/scoring.py`), not an eval framework.

## Considered Options

- **Search passes if any Accepted Course was read.** Rejected: reading all four Course Materials would always pass.
  Search fails if any Course Material outside the Accepted Courses was chosen or read; the Trace still records recall
  and the extra Reads.
- **Wait for the judge before scoring the Answer Step.** Rejected: the Answer Step uses code checks now (expected
  Section cited, only valid Sections, exact Refusal or Out of scope Sentence) and adds Supported and Responsive when
  the judge exists. Until then the report says that claims are not checked.
- **promptfoo, Inspect AI or DeepEval.** Rejected with six days to the deadline: the harness already runs the same
  answer function as the screen, stores Runs and is unit-tested; a framework would mean rewriting cases and metrics
  into its format.
- **A chart library or a Streamlit page for the report.** Rejected: a dependency in the first case, a second screen in
  the second.

## Consequences

- For the Routed Tutor, the routed Course counts as the Course Material read; its Path Step passes when the Router
  reply is valid and no call failed.
- `run_N.json` stores each Trace: Course Materials read in order, tool arguments and the three Step verdicts.
- Each run folder gets a self-contained `report.html` (no JavaScript, no external files) next to `report.md`: pass
  rate per Step and End-to-end Success as mean and range over the three Runs, one example Trace per failure pattern
  (earliest failing Step plus reason), all Traces in a collapsible section, and the rates labelled as computed from the
  run files.
- `python src/compare.py <run folder A> <run folder B>` writes `compare.html`: both variants' Step rates side by side
  and the cases whose End-to-end Success changed. It reads stored Runs only.
- The failure taxonomy (`failures.md`) stays in the group's own words; the report only names the earliest failing
  Step.
- Step verdicts are pure functions in `src/scoring.py`, tested with fake Traces; the HTML comes from a pure render
  function, tested for its numbers and rows, not its layout.
