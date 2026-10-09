# Project workflow iterations

This is a working record for the final report. Workflow iterations describe complete cycles of project work;
the smaller prompt, model and evaluation changes inside each cycle remain in
[`evaluation/ITERATION_LOG.md`](../evaluation/ITERATION_LOG.md).

## Iteration 1 — requirements to a working prototype

- **Checkpoint date:** 2026-10-09.
- **Implementation checkpoint:** `90d4122de9df419c670dcc3fd1ad1badfaffc0ce`.
- **Workflow reported by the group:** grilling session using documentation → specification → tickets → implementation of the specification.
- **Purpose:** turn the Course Tutor idea into an explicit scope and an executable first version that can support subsequent evaluation and improvement.
- **Report status:** checked against `Session 5 - Project Brief.pdf` on 2026-10-09 (slides 8, 10–13). The final report text remains provisional; original session, specification and ticket evidence still needs collecting.

### What the Project Brief requires

The brief allows us to describe this checkpoint as our first workflow iteration, but does not prescribe that
label or a number of workflow cycles. Its iteration criterion is concrete: at least one thing tried, measured
and abandoned, with the reason (10% of the mark). The workflow sequence alone does not demonstrate that criterion.

| Requirement | Evidence or remaining work at this checkpoint |
| --- | --- |
| Iteration evidence: tried, measured and abandoned, with a reason | The Lightning-to-Super comparison is a candidate: preserve failing outputs, probe configuration, measured results and the reason for abandoning Lightning. Identify it as a small probe, not a full performance estimate. |
| Prompt and context quality (30%): show at least two steering artifacts and what changed because of them | The brief names root `AGENTS.md`, `.github/skills/<name>/SKILL.md`, `.github/agents/<name>.agent.md`, and optional `.vscode/mcp.json`. Collect the actual files used and their effects. `CONTEXT.md` and `CLAUDE.md` document useful context, but alone do not demonstrate the two named artifact types. |
| Building tool | The brief specifies GitHub Copilot and starting from `project-starter`. Record the tools and starting repository actually used; the workflow account alone does not verify these requirements. |
| Failure taxonomy | Read at least 20 of our own outputs and name what went wrong in the group's own words. This must inform the next cycle, not be inferred solely from code tests. |
| Golden Set | At least 20 cases, inputs and agreed labels committed as a file before seeing a score. Our plan specifies 36; the six synthetic sample cases do not fulfill this requirement. |
| Defensible metric | Name the metric, explain why it was chosen and what it does not cover. End-to-end Success is planned; judge-based verdicts and a full baseline are pending. If using a judge, retain evidence of its calibration. |
| Report | Maximum five pages including screenshots, no appendices: process, actual prompts, dataset, evaluation method/results and failed attempts. Include the public repository link. |
| Submission | Report, maximum six-slide deck and public code repository by 20 October at 18:00; no commits after the deadline. |
| Presentation | Eight minutes plus two for questions/changeover; six slides cover idea, working prompt, Copilot steering, failure taxonomy/Golden Set, metric, and abandoned attempt/next steps, followed by the live demo. Have a recording as backup. |

These requirements make the next cycle evaluation-driven: inspect outputs to form the failure taxonomy,
agree and freeze Golden Set labels before scoring, establish the baseline, then measure a targeted change.
Retain the first cycle's unsuccessful attempts as evidence rather than presenting only the final successful configuration.

### Process and evidence

| Stage | What to explain in the report | Evidence available or still to collect |
| --- | --- | --- |
| Grilling with documentation | Questions raised, alternatives considered, group decisions and their reasons | Group's account of the session; collect selected conversation excerpts and the documentation consulted |
| Specification | How decisions became concrete requirements and acceptance criteria | `CLAUDE.md` identifies GitHub issue #1 as the spec; collect the issue text/link and show its connection to the decisions |
| Tickets | How the specification was divided into implementable work | Commit history references tickets #3, #4 and #6; collect ticket links and acceptance criteria |
| Implementation and review | What was built, what review exposed and how the group responded | Source, versioned prompts, tests, commit history and `evaluation/ITERATION_LOG.md` |
| Observation and reflection | What evidence supports the outcome and what remains uncertain | Stored model probes and their logged interpretation; full Golden Set evaluation remains pending |

The grilling session, specification and ticket contents have not been independently reviewed for this checkpoint.
Their order is recorded from the group's description; local commit references alone do not establish their full content.

### Resulting prototype

The repository contains a single-screen Streamlit Course Tutor covering GAIF, PEID, AITB and DTGS. A Router
selects a Course or Out of scope; the Course Tutor answers using that Course's Course Material, cites Sections
and supports Refusal. The implementation also handles invalid citations and model errors.

At this checkpoint the defaults are Router `router_v2`, Course Tutor `tutor_v2`,
`nvidia/nemotron-3-super-120b-a12b`, and thinking off. The evaluation runner stores repeated runs and reports
routing, citation, Refusal and Out of scope metrics. The repository contains six synthetic sample cases,
not the planned 36-question Golden Set.

The app was launched locally and its server health endpoint returned `ok`. This establishes server availability;
it does not establish successful live question answering. No local `.env` file was present at launch.

### Changes already made within this iteration

- Review found that logistics and exercise questions could bypass the intended Refusal path. `router_v2` routes them to the relevant Course; its comparative evaluation is pending.
- A latency probe motivated thinking off by default. The log reports one Router call at 21.9 seconds with thinking on and 2.1 seconds with thinking off; quality equivalence has not been established.
- Small model probes motivated replacing Lightning with Super. The log records missing citations from Lightning and successful routing, citations and Refusals from Super on the probe questions. These probes support a model-selection decision, not a Golden Set performance claim.
- Citation parsing, Router JSON handling, error presentation and evaluation run storage were refined through implementation and review.

See the evaluation log and stored probe files for configurations, results and limitations.

### Reflection and next cycle

The first cycle produced an executable prototype, explicit terminology, versioned prompts and evaluation
infrastructure. It also exposed concrete routing, citation and latency problems that informed changes.
End-to-end quality is not yet established: the Golden Set baseline is pending, the judge is not implemented,
and Supported and Responsive verdicts are not yet available.

The next cycle should freeze the Golden Set and agreed labels, establish a repeatable baseline, identify
failure patterns, make a targeted change and compare results under documented configurations. Record the
decision to keep or abandon that change and its reason. Keep this implementation checkpoint identifiable;
later improvements should be described as later work rather than retroactively attributed to Iteration 1.

### Provisional report paragraph

> In our first workflow iteration, we moved from a documentation-supported grilling session to a specification,
> implementation tickets and a working Course Tutor prototype. The resulting system routes questions among four
> Courses, answers from the selected Course Material with Section citations, and handles Refusal and Out of scope
> questions. Review and small model probes exposed routing, citation and latency issues and informed revisions.
> This iteration established the implementation and evaluation infrastructure. A full Golden Set baseline and
> judge-based assessment were still pending, so we treated the prototype as the starting point for the next
> evaluation-driven cycle.
