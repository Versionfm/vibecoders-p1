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

## M1 · Foundations

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| Team: roles split (app; data, demo inputs and Golden Set; steering files and report log) | Outside the repo | Not written down anywhere. State the roles in the report. Golden Set reviewers: Gonçalo Augusto and Rodrigo ([golden_set.json](../evaluation/golden_set.json), `agreed_by`). |
| App: one-sentence problem statement; the product disappears without the LLM call; demo fits in 90 s | Done | [README.md](../README.md), first paragraph. Without the model there is no routing and no cited answer. |
| App: repo from project-starter, group key in `.env`, the app answers | Done | `streamlit run src/app.py` ([README.md](../README.md#run)); key in `.env`, names only in [.env.example](../.env.example). Report which key and provider (DeepSeek) were used. |
| Copilot: always-on rules file at the repo root | Done (as `CLAUDE.md`) | [CLAUDE.md](../CLAUDE.md), with the vocabulary in [CONTEXT.md](../CONTEXT.md). Not named `AGENTS.md`; explain in the report. |
| Copilot: before/after evidence for the rules file (same request without and with it) | Missing | Run one request twice, without and with `CLAUDE.md`, and screenshot the difference (e.g. a second model client vs reuse of `chat()` in `src/llm.py`). |

## M2 · Running skeleton

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| App: input → LLM call → output, end to end on one screen | Done | [src/app.py](../src/app.py), [src/screen.py](../src/screen.py); one text box, one button. |
| App: the working prompt in its own versioned file, with label definitions and boundaries, 2–3 examples, fixed JSON output and an "unknown" exit | Partial | [prompts/](../prompts/): `router_v1` → `router_v2`, `tutor_v1` → `tutor_v2`, `agentic_tutor_v1`. The Router has label definitions with boundaries, JSON output and `OUT_OF_SCOPE` as the exit; the Course Tutor has the Refusal. **No worked examples** in any prompt (examples must not be Golden Set questions). |
| [Optional] App: data in an internal database or RAG | Done (files, not a database) | Course Material in [data/courses/](../data/courses/), loaded by Section ([src/course_material.py](../src/course_material.py)); the Agentic Tutor reads it with `read_file(course)` ([ADR 0001](adr/0001-agentic-tutor-without-router.md)). |
| App: evaluation traces with input, output, prompt version and latency | Partial | Every Trace is stored in `evaluation/runs/<folder>/run_N.json` with output, prompt versions, model, Reads and Steps ([ADR 0002](adr/0002-trace-steps-and-html-report.md)). **Latency is not recorded.** |
| Copilot: at least one skill for a repeated procedure, which fires without being named | Partial | [.claude/skills/evaluate-course-tutor/SKILL.md](../.claude/skills/evaluate-course-tutor/SKILL.md). Still to collect: a screenshot of it firing on a request that does not name it (e.g. "how are we doing on the Golden Set?"). |
| [Optional] Copilot: a sub-agent or an MCP server | Done | [.claude/agents/evaluator.md](../.claude/agents/evaluator.md) (measures and logs; leaves code, prompts and labels unchanged). |

## M3 · Evaluation

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| App: 20+ realistic outputs read; failure taxonomy named in our own words | Partial | Observed facts per failing case, with the judge: [routed failures.md](../evaluation/runs/2026-10-18_020503_golden_set_v1_judge_routed/failures.md), [agentic failures.md](../evaluation/runs/2026-10-18_022123_golden_set_v1_judge_agentic/failures.md); code checks only: [routed](../evaluation/runs/2026-10-14_193513_golden_set_v1_routed/failures.md), [agentic](../evaluation/runs/2026-10-14_195710_golden_set_v1_agentic/failures.md). **`evaluation/FAILURE_TAXONOMY.md` does not exist**: the group still has to name the categories and count them (e.g. "extra Read of a non-Accepted Course", "refuses in its own words without reading", "Out of scope instead of the Refusal"). |
| App: Golden Set of 20+ cases, labelled before seeing a score | Done | [evaluation/golden_set.json](../evaluation/golden_set.json): 36 cases, version 1, frozen 2026-10-14; review in [golden_set_review.md](../evaluation/golden_set_review.md); checks in [tests/test_golden_set.py](../tests/test_golden_set.py). Limitation to report: the pilots on the candidates were seen before the freeze ([ITERATION_LOG](../evaluation/ITERATION_LOG.md)). |
| App: deterministic checks in code for everything with a right answer | Done | [src/scoring.py](../src/scoring.py): routing accuracy, recall per Course and macro, citation correctness, Refusal and Out of scope correctness, Search/Path/Answer Steps and End-to-end Success; tested in [tests/test_scoring.py](../tests/test_scoring.py) and [tests/test_steps.py](../tests/test_steps.py). |
| App: LLM-as-a-judge for what code cannot check (one criterion per call, evidence before PASS/FAIL, an "unknown" exit) | Done | [src/judge.py](../src/judge.py), prompts `judge_supported_v1` and `judge_responsive_v1`: one call per criterion, JSON with the evidence before PASS/FAIL/UNKNOWN; a failed call or unparseable reply is a judge error and never a pass. Judge `openai/gpt-oss-20b` on NVIDIA, chosen by [a probe](../evaluation/probes/judge_probe.py) (iteration log, 2026-10-17). |
| App: judge checked against our hand labels (about 20, TPR and TNR with PASS as positive) | Missing | Ticket #8. Hand-label about 20 answers from the 2026-10-18 runs (judge verdicts hidden), then report TPR and TNR. Until then the judge's verdicts are provisional. |

## M4 · Iterate and measure

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| App: one number we can defend (the metric, why, what it does not cover) | Partial | End-to-end Success on Golden Set v1 with the judge: Routed Tutor 90.7% (88.9% to 91.7%) over 3 Runs ([report](../evaluation/runs/2026-10-18_020503_golden_set_v1_judge_routed/report.md)); 97.2% with code checks only. Still to write: the "why this one / what it misses" sentence, after the judge's calibration (#8). |
| App: one change tried, measured, and kept or abandoned with a reason | Done | [ITERATION_LOG.md](../evaluation/ITERATION_LOG.md): Lightning → Super (Lightning abandoned: no citations), the professor's `course-chat` endpoint (abandoned), Nemotron → DeepSeek (kept), the professor's endpoint re-tested after his proxy fix (not adopted), and the Agentic Tutor (abandoned, #17): 85.2% vs 90.7% End-to-end Success with the judge, same day ([compare.html](../evaluation/runs/2026-10-18_022123_golden_set_v1_judge_agentic/compare.html)). |
| Copilot: evidence for every steering file, at least two in the report | Partial | Commits that show the files changing: `9f83b7a` (evaluator skill and agent), `b4f8482` (both learn the Agentic Tutor). Still to collect: what changed *because of* `CLAUDE.md` and the skill (screenshots or before/after outputs). Context in [WORKFLOW_ITERATIONS.md](WORKFLOW_ITERATIONS.md). |

## M5 · Submit

| Item | Status | Evidence or what is left |
| --- | --- | --- |
| Deck: at most 6 slides, in order: idea · prompt · how we steered the coding assistant · failure taxonomy and Golden Set · our number · what we abandoned | Missing | Not started. |
| Report: at most 5 pages, no appendices: screenshots, actual prompts, dataset, evaluation method and result, what did not work, repo link | Missing | Notes to draw on: [WORKFLOW_ITERATIONS.md](WORKFLOW_ITERATIONS.md), [ITERATION_LOG.md](../evaluation/ITERATION_LOG.md), the run reports. |
| Repo: public at submission, link in the report, no commits after the deadline; secrets scan green; `.env` never in history | Partial | [secrets-scan.yml](../.github/workflows/secrets-scan.yml) exists; `.env` is not in the history of any branch (checked 2026-10-17). **The repository is private**, and `main` has only the first two commits: the work on `golden-set`, `course-tutor` and `agent-tutor` must be merged into `main` before it is made public. |
| Demo: rehearsed with a timer (8 min: about 4 slides, 4 live, plus 2 for questions) and a backup recording | Outside the repo | Not done. Demo with `TUTOR=routed` (#17 decided for the Routed Tutor). |

## Open work, in order

1. Judge calibration on our hand labels: TPR and TNR (#8).
2. `evaluation/FAILURE_TAXONOMY.md` in the group's words, from the `failures.md` files.
3. Steering evidence: before/after for `CLAUDE.md`, the skill firing unnamed.
4. Merge into `main`, make the repo public, check the secrets scan.
5. Report, deck, rehearsal and backup recording.

Done since 2026-10-17: the LLM judge (#7) and its baselines; Routed vs Agentic Tutor decided (#17).

Smaller gaps: no worked examples in the prompts (a candidate change to measure: a new prompt version, never an edit
of an evaluated one); latency not stored in the Traces.
