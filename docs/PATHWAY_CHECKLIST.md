# Pathway checklist: status

The professor's "Capstone Project — Pathway Checklist" (Prompt Engineering and Interaction Design), restated in our
own words, with the status of each item for the Course Tutor and a link to the evidence. Update the status and the
evidence when an item moves; the checklist is the professor's, the statuses are ours.

The checklist was written for GitHub Copilot (`AGENTS.md`, `.github/skills/`, `.github/agents/`). We build with
Claude Code, so the same steering files live where Claude Code reads them: `CLAUDE.md`, `.claude/skills/`,
`.claude/agents/`. The report must say so.

**Deadline:** report, deck and public repository by 20 October 2026, 18:00; no commits after it.

**Status:** Done · Partial · Missing · Outside the repo (cannot be checked from the files).

Last checked: 2026-10-18, branch `golden-set` (judge baselines and the #17 decision).

Tutor choice updated on 2026-10-19: [ADR 0003](adr/0003-keep-agentic-chat-for-teaching.md) selects the Agentic Tutor
chat for teaching, superseding the earlier decision to abandon it. Other checklist statuses retain their previous
check date.

## M1 · Foundations

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| Team: roles split (app; data, demo inputs and Golden Set; steering files and report log) | Outside the repo | Not written down anywhere. State the roles in the report. Golden Set reviewers: Gonçalo Augusto and Rodrigo ([golden_set.json](../evaluation/golden_set.json), `agreed_by`). |
| App: one-sentence problem statement; the product disappears without the LLM call; demo fits in 90 s | Done | [README.md](../README.md), first paragraph. Without the model there is no routing and no cited answer. |
| App: repo from project-starter, group key in `.env`, the app answers | Done | `streamlit run src/app.py` ([README.md](../README.md#run)); key in `.env`, names only in [.env.example](../.env.example). Report which key and provider (DeepSeek) were used. |
| Copilot: always-on rules file at the repo root | Done (as `CLAUDE.md`) | [CLAUDE.md](../CLAUDE.md), with the vocabulary in [CONTEXT.md](../CONTEXT.md). Not named `AGENTS.md`; explain in the report. |
| Copilot: before/after evidence for the rules file (same request without and with it) | Done (screenshots to take) | [WORKFLOW_ITERATIONS.md](WORKFLOW_ITERATIONS.md#steering-evidence-2026-10-18): the same request in fresh sessions at the same commit, without and with `CLAUDE.md`. Small difference: only the session with it applied the one-screen rule and kept `CLAUDE.md` current; the other conventions were already in the code. Screenshots: the final messages of sessions A and B2. |

## M2 · Running skeleton

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| App: input → LLM call → output, end to end on one screen | Done | [src/app.py](../src/app.py), [src/screen.py](../src/screen.py); the chosen Agentic Tutor has chat input, conversation history and New conversation on one screen. |
| App: the working prompt in its own versioned file, with label definitions and boundaries, 2–3 examples, fixed JSON output and an "unknown" exit | Partial | [prompts/](../prompts/): `router_v1` → `router_v2`, `tutor_v1` → `tutor_v2`, `agentic_tutor_v1`. The Router has label definitions with boundaries, JSON output and `OUT_OF_SCOPE` as the exit; the Course Tutor has the Refusal. **No worked examples** in any prompt (examples must not be Golden Set questions). |
| [Optional] App: data in an internal database or RAG | Done (files, not a database) | Course Material in [data/courses/](../data/courses/), loaded by Section ([src/course_material.py](../src/course_material.py)); the Agentic Tutor reads it with `read_file(course)` ([ADR 0001](adr/0001-agentic-tutor-without-router.md)). |
| App: evaluation traces with input, output, prompt version and latency | Partial | Every Trace is stored in `evaluation/runs/<folder>/run_N.json` with output, prompt versions, model, Reads and Steps ([ADR 0002](adr/0002-trace-steps-and-html-report.md)). **Latency is not recorded.** |
| Copilot: at least one skill for a repeated procedure, which fires without being named | Done (screenshot to take) | [.claude/skills/evaluate-course-tutor/SKILL.md](../.claude/skills/evaluate-course-tutor/SKILL.md). It did not fire on "How are we doing on the Golden Set? Measure the Routed Tutor again."; after its description named such requests (`3f66605`) it did, in a fresh session ([WORKFLOW_ITERATIONS.md](WORKFLOW_ITERATIONS.md#steering-evidence-2026-10-18)). Screenshot: session D2's skill call. |
| [Optional] Copilot: a sub-agent or an MCP server | Done | [.claude/agents/evaluator.md](../.claude/agents/evaluator.md) (measures and logs; leaves code, prompts and labels unchanged). |

## M3 · Evaluation

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| App: 20+ realistic outputs read; failure taxonomy named in our own words | Done (names to confirm) | [FAILURE_TAXONOMY.md](../evaluation/FAILURE_TAXONOMY.md): 8 categories from 52 failing Traces and 28 hand-labelled answers, with counts per evaluation and example cases, plus the labeller's style notes. The names were drafted from the labeller's reasons: the group confirms or renames them. |
| App: Golden Set of 20+ cases, labelled before seeing a score | Done | [evaluation/golden_set.json](../evaluation/golden_set.json): 36 cases, version 1, frozen 2026-10-14; review in [golden_set_review.md](../evaluation/golden_set_review.md); checks in [tests/test_golden_set.py](../tests/test_golden_set.py). Limitation to report: the pilots on the candidates were seen before the freeze ([ITERATION_LOG](../evaluation/ITERATION_LOG.md)). |
| App: deterministic checks in code for everything with a right answer | Done | [src/scoring.py](../src/scoring.py): routing accuracy, recall per Course and macro, citation correctness, Refusal and Out of scope correctness, Search/Path/Answer Steps and End-to-end Success; tested in [tests/test_scoring.py](../tests/test_scoring.py) and [tests/test_steps.py](../tests/test_steps.py). |
| App: LLM-as-a-judge for what code cannot check (one criterion per call, evidence before PASS/FAIL, an "unknown" exit) | Done | [src/judge.py](../src/judge.py), prompts `judge_supported_v1` and `judge_responsive_v1`: one call per criterion, JSON with the evidence before PASS/FAIL/UNKNOWN; a failed call or unparseable reply is a judge error and never a pass. Judge `openai/gpt-oss-20b` on NVIDIA, chosen by [a probe](../evaluation/probes/judge_probe.py) (iteration log, 2026-10-17). |
| App: judge checked against our hand labels (about 20, TPR and TNR with PASS as positive) | Done | Ticket #8: 28 answers labelled by one labeller without the judge ([labels.md](../evaluation/calibration/labels.md)); held-out (19): `judge_supported_v2` 84.2% accuracy, kappa 0.56, TPR 86.7%, TNR 75.0%; Responsive 84.2% ([report](../evaluation/calibration/report_first_labels_judge_v2.md)). Limits: one labeller, 15 questions, no human Responsive FAIL on held-out. |

## M4 · Iterate and measure

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| App: one number we can defend (the metric, why, what it does not cover) | Partial | Selected Agentic Tutor: 87.0% End-to-end Success (83.3% to 88.9%) over 3 Runs ([report](../evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic/report.md)); Routed Tutor comparison: 92.6%. [ADR 0003](adr/0003-keep-agentic-chat-for-teaching.md) explains the teaching rationale and the unmeasured conversational benefit. Still to include this distinction in the report. |
| App: one change tried, measured, and kept or abandoned with a reason | Done | [ITERATION_LOG.md](../evaluation/ITERATION_LOG.md): Lightning → Super (Lightning abandoned: no citations), the professor's endpoint (not adopted), Nemotron → DeepSeek (kept). The Agentic Tutor was initially abandoned under #17, then selected for conversation on 2026-10-19 ([ADR 0003](adr/0003-keep-agentic-chat-for-teaching.md)); do not present the earlier abandonment as the current decision. |
| Copilot: evidence for every steering file, at least two in the report | Partial | Commits that show the files changing: `9f83b7a` (evaluator skill and agent), `b4f8482` (both learn the Agentic Tutor). Still to collect: what changed *because of* `CLAUDE.md` and the skill (screenshots or before/after outputs). Context in [WORKFLOW_ITERATIONS.md](WORKFLOW_ITERATIONS.md). |

## M5 · Submit

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| Deck: at most 6 slides, in order: idea · prompt · how we steered the coding assistant · failure taxonomy and Golden Set · our number · what we abandoned | Missing | Not started. |
| Report: at most 5 pages, no appendices: screenshots, actual prompts, dataset, evaluation method and result, what did not work, repo link | Missing | Notes to draw on: [WORKFLOW_ITERATIONS.md](WORKFLOW_ITERATIONS.md), [ITERATION_LOG.md](../evaluation/ITERATION_LOG.md), the run reports. |
| Repo: public at submission, link in the report, no commits after the deadline; secrets scan green; `.env` never in history | Partial | [secrets-scan.yml](../.github/workflows/secrets-scan.yml) exists; `.env` is not in the history of any branch (checked 2026-10-17). **The repository is private**, and `main` has only the first two commits: the work on `golden-set`, `course-tutor` and `agent-tutor` must be merged into `main` before it is made public. |
| Demo: rehearsed with a timer (8 min: about 4 slides, 4 live, plus 2 for questions) and a backup recording | Outside the repo | Rehearsal and recording not verified. Demo with `TUTOR=agentic` ([ADR 0003](adr/0003-keep-agentic-chat-for-teaching.md)); configure it explicitly because the code still falls back to `routed` when unset. |

## Open work, in order

1. Confirm or rename the categories in `evaluation/FAILURE_TAXONOMY.md`.
2. Screenshots of the steering evidence (sessions A, B2 and D2).
3. Merge into `main`, make the repo public, check the secrets scan.
4. Report, deck, rehearsal and backup recording.

Done since 2026-10-17: the LLM judge (#7) and its baselines; Routed vs Agentic Tutor decided (#17); judge calibration (#8), with `judge_supported_v2` and the baseline judged again (92.6%).

Smaller gaps: no worked examples in the prompts (a candidate change to measure: a new prompt version, never an edit
of an evaluated one); latency not stored in the Traces.
