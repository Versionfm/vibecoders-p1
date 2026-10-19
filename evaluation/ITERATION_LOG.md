# Iteration log

Every evaluated change goes here, including changes that were abandoned. Newest entry at the bottom. Never edit an
old entry to change its result; add a new entry instead.

## Format

Copy this block for each entry:

```markdown
## <YYYY-MM-DD> <short name of the change>

- **Change:** what changed, in one or two sentences (e.g. "tutor_v2 -> tutor_v3: stricter citation rule").
- **Configuration:** Router prompt, Course Tutor prompt, app model, judge model, case file.
- **Run folder:** `evaluation/runs/<folder>` (the stored runs and report.md this result comes from).
- **Result:** the metrics that moved, as mean (range) across the 3 runs, before -> after.
- **Decision:** kept | abandoned | pending.
- **Reason:** why it was kept or abandoned, in one or two sentences.
```

## 2026-10-09 Evaluation runner and first metrics (ticket #6)

- **Change:** added the evaluation command (`python src/evaluate.py <case file>`): it runs every case three times
  through the same answer function the screen uses, stores each run, and reports routing accuracy, recall per class
  and its macro average, citation correctness, Refusal correctness and Out of scope correctness as mean and range.
- **Configuration:** Router `router_v1`, Course Tutor `tutor_v2`, app model `nvidia/nemotron-3.5-lightning-30b-a3b`,
  no judge yet (ticket #7), case file `evaluation/sample_cases.json` (6 synthetic SAMPLE cases, not the Golden Set).
- **Run folder:** none committed. The command was checked end to end with a fake model only (no network, no key).
- **Result:** no score yet. The sample file only proves the command works; its numbers mean nothing.
- **Decision:** kept.
- **Reason:** the runner is needed before any prompt or model change can be measured. The first real entry will be
  the baseline on the Golden Set once it is frozen.

## 2026-10-09 router_v2: Course logistics and exercises go to the named Course (review fix)

- **Change:** router_v1 -> router_v2: a question about a named Course's logistics (exams, grading, deadlines,
  schedule, attendance) or asking to solve an exercise on a Course topic is routed to that Course; OUT_OF_SCOPE only
  for subjects none of the four Courses teaches. Under router_v1 such questions went to OUT_OF_SCOPE, so the
  tutor_v2 Refusal for logistics and new exercises could not be reached.
- **Configuration:** Router `router_v2`, Course Tutor `tutor_v2`, app model `nvidia/nemotron-3.5-lightning-30b-a3b`,
  no judge yet, case file: none yet.
- **Run folder:** none. Not evaluated yet.
- **Result:** not evaluated yet. Compare with router_v1 on the Golden Set (Out of scope correctness, Refusal
  correctness, routing accuracy) once it is frozen.
- **Decision:** pending.
- **Reason:** found in code review, not by a score. Made the default because the Refusal path was unreachable.

## 2026-10-09 App model thinking off by default (LLM_THINKING)

- **Change:** new setting `LLM_THINKING` (on/off, default off), sent to the app model as
  `chat_template_kwargs.enable_thinking`. Each answer and each stored run records the setting.
- **Configuration:** Router `router_v2`, Course Tutor `tutor_v2`, app model `nvidia/nemotron-3.5-lightning-30b-a3b`,
  no judge yet, case file: none yet.
- **Run folder:** none. Latency was measured on single Router calls on the NVIDIA endpoint, not with the evaluation
  command.
- **Result:** latency only: one Router call took 21.9 s and 813 tokens with thinking on, 2.1 s and 16 tokens with
  thinking off. Answer quality is not compared yet.
- **Decision:** pending (off is the default for latency).
- **Reason:** thinking on made the screen slow and long evaluations prone to timeouts. Run the Golden Set with
  `LLM_THINKING=off` and `LLM_THINKING=on` and compare routing, citation and Refusal metrics before deciding.

## 2026-10-09 App model: nemotron-3.5-lightning -> nemotron-3-super-120b-a12b (model probe)

- **Change:** default app model (Router and Course Tutor) changed from `nvidia/nemotron-3.5-lightning-30b-a3b` to
  `nvidia/nemotron-3-super-120b-a12b`, thinking off.
- **Configuration:** Router `router_v1`, Course Tutor `tutor_v2`, thinking off, no judge. Probe script
  `evaluation/probes/app_model_probe.py`: 6 Router questions (one per class plus a GAIF/PEID near-miss) and 4 Course
  Tutor questions (two answers, one exercise Refusal, one off-topic Refusal). Throwaway questions, not the Golden Set.
- **Run folder:** `evaluation/probes/app_model_probe_parallel.json` (8 models at once) and
  `evaluation/probes/app_model_probe_sequential.json` (4 models one at a time).
- **Result:** Super: routing 6/6 and valid JSON 6/6 in both probes; both answers cited the right Section
  (PEID-3.2, DTGS-3.15); both Refusals exact; about 1 s per call. Lightning: both answers had **no citation at all**
  in both probes, and one Router reply was not valid JSON (5/6). GLM-5.3: same quality as Super but 9-23 s per call.
  Nemotron Ultra: 503 overloaded on half the calls. gpt-oss-20b, gemma-4-31b-it, glm-5.3-flash,
  deepseek-v4.1-flash and kimi-k3 timed out (60-150 s) at probe time; mistral-large-2-instruct and kimi-k2.6 return
  404 (listed but not deployed).
- **Decision:** kept.
- **Reason:** an answer without citations fails End-to-end Success by definition, and Super is as fast as Lightning
  with thinking off. Tiny probe, not a score: confirm on the Golden Set baseline. Note for ticket #7: `z-ai/glm-5.3`
  answered reliably and is not a Nemotron model, so it is a judge candidate.

## 2026-10-14 Agentic Tutor model: native tool calling on nemotron-3-super-120b-a12b (tool-calling probe, ticket #11)

- **Change:** none to the app. Checked, before the Agentic Tutor depends on it, whether the endpoint returns real
  `tool_calls` for the `read_file(course)` tool (ADR 0001).
- **Configuration:** probe script `evaluation/probes/tool_call_probe.py`: one throwaway question (not the Golden Set)
  with the `read_file` tool, temperature 0; `nvidia/nemotron-3-super-120b-a12b` with thinking off and
  `openai/gpt-oss-120b` with low reasoning effort.
- **Run folder:** `evaluation/probes/tool_call_probe.json`.
- **Result:** Super: tool calls filled in (`finish_reason` `tool_calls`), one call `read_file({"course":"PEID"})`,
  the right Course for the question, in 0.8 s. gpt-oss-120b: HTTP 410, the model reached its end of life on the
  NVIDIA endpoint on 2026-09-03 and is no longer available.
- **Decision:** kept: the Agentic Tutor uses native tool calling on `nvidia/nemotron-3-super-120b-a12b`, thinking off.
- **Reason:** Super returns real tool calls although NVIDIA's request schema omits `tools`, and it is already the
  Routed Tutor's model, so the comparison in #17 changes only the tutor. One question, not a score: the Path Step on
  the Golden Set is the real check.

## 2026-10-14 Pilot: Routed Tutor on the Golden Set candidates, Nemotron Super (invalid: rate limited)

- **Change:** none. First run on `evaluation/golden_set_candidates.json`, the drafted candidates for #5, before the
  group has agreed the labels. A pilot to see how the app behaves, not the Golden Set baseline.
- **Configuration:** Routed Tutor, Router `router_v2`, Course Tutor `tutor_v2`, app model
  `nvidia/nemotron-3-super-120b-a12b`, thinking off, no judge, `--workers 3`, commit `9ddb4a1`.
- **Run folder:** `evaluation/runs/2026-10-14_113009_pilot_candidates_routed`.
- **Result:** not a measurement. Run 1 sent about 50 calls in 18 s and then got HTTP 429 (Too Many Requests); Runs 2
  and 3 failed almost entirely on 429 in 7 s each. About 22 of 108 Traces got an answer. End-to-end Success 17.6%
  (0.0% to 52.8%) reflects the rate limit, not the tutor. Among the answered Traces of Run 1: GS-05 was routed to
  DTGS and GS-15 to PEID (both Near-miss Cases), GS-14 (ADKAR) to OUT_OF_SCOPE.
- **Decision:** abandoned.
- **Reason:** the NVIDIA endpoint's rate limit (about 40 calls per minute, not confirmed) is below what a run needs,
  and the client retries only once. Superseded by the move to DeepSeek below.

## 2026-10-14 Professor's endpoint (`course-chat`) probed and not adopted

- **Change:** none to the app. Probed the course endpoint the professor provided (a LiteLLM proxy in front of Azure
  OpenAI) with its only model, `course-chat`.
- **Configuration:** throwaway calls from the command line and the app's own answer function, temperature 0.
- **Run folder:** none (single calls).
- **Result:** plain answers work in 2 to 6 s, and the Routed Tutor answered four test questions correctly (PEID-1.3,
  Out of scope, the GAIF Refusal, GAIF-2.5) when no thinking switch was sent. `chat_template_kwargs` returns HTTP 400,
  so every app call fails with `LLM_THINKING` set. Native tool calls (`tools`) return 404 ("Azure OpenAI Responses
  API is not enabled in this region"); only the legacy `functions` format works. One failed call put the deployment
  in a 5 s cooldown (HTTP 429 for every call). The model behind `course-chat` is not disclosed.
- **Decision:** abandoned.
- **Reason:** the Agentic Tutor would need a rewrite to the legacy `functions` format, the endpoint is probably
  shared with the whole class, and an undisclosed model cannot be named in the report.

## 2026-10-14 App model: nemotron-3-super-120b-a12b -> deepseek-flash (DeepSeek API); thinking switch fixed

- **Change:** default endpoint `https://api.deepseek.com` and app model `deepseek-flash` (DeepSeek-V4.1-Flash) for
  both tutors, as ADR 0001 foresaw. `LLM_THINKING` is now also sent as DeepSeek's `thinking` type: DeepSeek ignores
  `chat_template_kwargs`, so `LLM_THINKING=off` had left thinking on while runs recorded it as off.
- **Configuration:** Router `router_v2`, Course Tutor `tutor_v2`, Agentic Tutor `agentic_tutor_v1`, thinking off,
  no judge.
- **Run folder:** none yet; single calls through the app's answer function and the screen.
- **Result:** native tool calls work (`read_file({"course": "PEID"})` for a top-p question, 1.1 s). Both tutors
  answered four test questions correctly (PEID-1.3; Out of scope, with no Read for the Agentic Tutor; the GAIF
  Refusal; PEID-2.6 and PEID-2.11 for a PEID/AITB Overlap question) in 1 to 4 s. With both switches sent, a reply had
  no reasoning and 36 output tokens instead of 163.
- **Decision:** kept.
- **Reason:** DeepSeek lists a concurrency limit rather than a per-minute cap, runs the Agentic Tutor unchanged and
  names its model; the cost is small (about $0.30 per million input tokens on a cache miss, $1.20 per million output
  tokens at peak). Both tutors are measured on it, so the comparison changes only the tutor. The judge (#7) must now
  come from a family other than DeepSeek.

## 2026-10-14 Pilot: Routed Tutor on the Golden Set candidates, deepseek-flash

- **Change:** none; pilot of the Routed Tutor on the new app model. Labels of `evaluation/golden_set_candidates.json`
  are not yet agreed by the group, so this is not the Golden Set baseline.
- **Configuration:** Routed Tutor, Router `router_v2`, Course Tutor `tutor_v2`, app model `deepseek-flash`, thinking
  off, no judge (Answer Step uses code checks only), `--workers 3`, commit `c92da4e`.
- **Run folder:** `evaluation/runs/2026-10-14_120039_pilot_deepseek_routed` (with `failures.md`).
- **Result:** End-to-end Success 89.8% (88.9% to 91.7%); Search Step 91.7% (91.7% to 91.7%); Path Step 100.0%;
  Answer Step 89.8% (88.9% to 91.7%). Routing accuracy 91.7%, Refusal correctness 75.0%, Out of scope correctness
  100.0%, citation correctness 96.2%. Failing cases: GS-05 3/3 (routed AITB), GS-15 3/3 (routed PEID), GS-36 3/3
  (Out of scope), GS-27 2/3 (DTGS Refusal).
- **Decision:** pending.
- **Reason:** first usable numbers for the Routed Tutor; three of the four failing cases have labels the group still
  has to decide. Repeat on the frozen Golden Set as the baseline for #17.

## 2026-10-14 Pilot: Agentic Tutor on the Golden Set candidates, deepseek-flash

- **Change:** Routed Tutor -> Agentic Tutor (`agentic_tutor_v1`), same case file, model and thinking setting as the
  entry above.
- **Configuration:** Agentic Tutor `agentic_tutor_v1`, app model `deepseek-flash`, thinking off, no judge,
  `--workers 3`, commit `c92da4e`.
- **Run folder:** `evaluation/runs/2026-10-14_120227_pilot_deepseek_agentic` (with `failures.md` and `compare.html`
  against the Routed Tutor pilot).
- **Result:** End-to-end Success 89.8% -> 86.1% (86.1% to 86.1%); Search Step 91.7% -> 86.1%; Path Step 100.0% ->
  98.1% (97.2% to 100.0%); Answer Step 89.8% -> 87.0% (86.1% to 88.9%). Refusal correctness 75.0% -> 33.3%; Out of
  scope correctness 100.0% in both. Failing cases: GS-05 3/3 (read AITB), GS-15 3/3 (read PEID), GS-35 3/3 and
  GS-36 3/3 (Out of scope Sentence), GS-33 2/3 (refused the exercise in its own words without a Read), GS-13 1/3
  (an extra Read of AITB). No Trace reached the Read limit; no model call failed.
- **Decision:** pending.
- **Reason:** 1.3 cases fewer per Run on average, mostly Refusal cases answered as Out of scope (GS-35, GS-36, two
  labels the group still has to decide) and one exercise refused without reading. On the candidates the Routed
  Tutor stays ahead; decide on the frozen Golden Set (#17).

## 2026-10-14 Agentic Tutor: single-message screen -> built-in chat

- **Change:** replaced the Agentic Tutor's question box and Ask button with Streamlit's built-in chat input and
  message bubbles. The screen keeps questions and answers in session state and sends completed exchanges with each
  follow-up; **New conversation** clears the history. The title now identifies the Agentic Tutor. The Routed Tutor
  keeps its single-message screen.
- **Configuration:** `TUTOR=agentic`, Agentic Tutor `agentic_tutor_v1`; no prompt, app model, thinking or judge setting
  changed. Prior questions and answers provide conversational context; each answer still reads its own Course
  Material and has its own four-Read limit. Single-message evaluation calls continue with empty history. Branch
  `agent-tutor-chat`, implementation commit `2a0cb5d`; no case file run for this change.
- **Run folder:** none. Checked with `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests` and the local
  app's health endpoint, not with a Golden Set run or a live multi-turn LLM evaluation.
- **Result:** all 147 deterministic tests passed. A two-turn test through the actual Streamlit screen with a fake
  model confirmed that both exchanges remain visible, the follow-up request contains the previous question and
  answer, and New conversation clears the chat. The first running-app attempt failed with
  `ask() got an unexpected keyword argument 'history'`: Streamlit loaded the updated screen while retaining the old
  imported helper. Restarting the server cleared the stale import; the chat regression test passed again and the
  health endpoint returned `ok`. Live multi-turn answer quality and End-to-end Success were not measured.
- **Decision:** kept for the conversation interface; live multi-turn quality evaluation pending.
- **Reason:** selecting the Agentic Tutor had changed the answer path but still allowed only isolated questions.
  The built-in chat makes follow-up questions possible and supplies the context needed to interpret them. Existing
  single-message pilot scores do not establish conversation quality.

## 2026-10-14 Agentic Tutor: isolate the tool loop from answer checks

- **Change:** moved the Agentic Tutor loop, tool definition and Course Material reader into `src/agentic.py`.
  `run_agentic()` returns final text and execution records; `src/tutor.py` converts them into the shared Trace and
  checks citations and fixed sentences. The model interface now lives with the model adapter in `src/llm.py`.
  Added a short workflow guide showing the usual path before limits and evaluation details.
- **Configuration:** branch `agent-tutor-chat`, Agentic Tutor `agentic_tutor_v1`; no prompt, model, thinking,
  chat-history policy, four-Read limit or evaluation result fields changed. No new agent framework.
- **Run folder:** none. Deterministic tests only; no new Golden Set run or live multi-turn quality evaluation.
- **Result:** all 149 tests passed with `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -t .`.
  Existing tests cover the shared answer entry point, failure records, invalid and repeated Reads, multiple calls,
  Read-limit handling and the chat screen. Two additional regressions verify matching tool-call/result IDs and that
  a follow-up leaves supplied history untouched and validates citations only against material read in that turn.
  These checks establish behaviour preservation for the tested cases, not an improvement in answer quality.
- **Decision:** kept.
- **Reason:** the previous implementation mixed the conversation loop and answer analysis in one function.
  A dedicated module makes the workflow easier to follow while preserving the evaluator and screen entry point.

## 2026-10-14 Pilot: Routed Tutor after built-in chat and loop refactor, deepseek-flash

- **Change:** re-evaluated Routed Tutor after the built-in chat and loop separation at commit `8f939a5`. Comparison is against the prior same-tutor pilot at `c92da4e`; prompts, candidate labels, app model and thinking are unchanged. Single-message calls use empty history.
- **Configuration:** `routed`; prompts `router=router_v2`, `tutor=tutor_v2`; app model `deepseek-flash`; thinking off; no judge; case file `evaluation/golden_set_candidates.json` (36 candidates, not the frozen Golden Set); three Runs; `--workers 3`; branch `agent-tutor-chat`, commit `8f939a5`. All 149 deterministic tests passed. An initial probe failed because the configured hostname was `api.deepseek.comz`; the main session corrected the extra trailing z. The next timed Agentic Tutor request succeeded in 2.505 s, read PEID and cited PEID-1.3. Probe evidence is kept in the folders named in `evaluator_metadata.json`.
- **Run folder:** `evaluation/runs/2026-10-14_173156_pilot_chat_refactor_deepseek_routed`; includes three stored Runs, Markdown/HTML reports, `failures.md` and pinned evaluator metadata. Previous same-tutor pilot: `evaluation/runs/2026-10-14_120039_pilot_deepseek_routed`.
- **Result:** mean (range) across three Runs, previous same-tutor pilot -> current pilot:

| Metric | Before | After |
|---|---|---|
| Search Step | 91.7% (91.7%–91.7%) | 91.7% (91.7%–91.7%) |
| Path Step | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Answer Step | 89.8% (88.9%–91.7%) | 91.7% (91.7%–91.7%) |
| End-to-end Success | 89.8% (88.9%–91.7%) | 91.7% (91.7%–91.7%) |
| Routing accuracy | 91.7% (91.7%–91.7%) | 91.7% (91.7%–91.7%) |
| Recall GAIF | 83.3% (83.3%–83.3%) | 83.3% (83.3%–83.3%) |
| Recall PEID | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Recall AITB | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Recall DTGS | 75.0% (75.0%–75.0%) | 75.0% (75.0%–75.0%) |
| Recall OUT_OF_SCOPE | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Recall (macro average) | 91.7% (91.7%–91.7%) | 91.7% (91.7%–91.7%) |
| Citation correctness | 96.2% (96.2%–96.3%) | 96.3% (96.3%–96.3%) |
| Refusal correctness | 75.0% (75.0%–75.0%) | 75.0% (75.0%–75.0%) |
| Out of scope correctness | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Supported rate | pending | pending |
| Responsive rate | pending | pending |

- **Failing cases:** 4 -> 3 unique cases; 11/108 -> 9/108 failed Traces. Current: GS-05 3/3 (Search 3); GS-15 3/3 (Search 3); GS-36 3/3 (Search 3). Model-call errors 0/108; Read limit reached 0/108. Every failing case is documented across all Runs in `failures.md`.
- **Decision:** pending.
- **Reason:** this pilot checks single-message behaviour after the refactor on unchanged candidate labels. Retain the preserved failure evidence for deciding whether to keep the tutor; group review of the labels and a frozen Golden Set comparison are still required. The Answer Step and End-to-end Success use code checks only; Supported and Responsive rates need the LLM judge. This does not evaluate multi-turn chat history quality.

## 2026-10-14 Pilot: Agentic Tutor after built-in chat and loop refactor, deepseek-flash

- **Change:** re-evaluated Agentic Tutor after the built-in chat and loop separation at commit `8f939a5`. Comparison is against the prior same-tutor pilot at `c92da4e`; prompts, candidate labels, app model and thinking are unchanged. Single-message calls use empty history.
- **Configuration:** `agentic`; prompts `agentic_tutor=agentic_tutor_v1`; app model `deepseek-flash`; thinking off; no judge; case file `evaluation/golden_set_candidates.json` (36 candidates, not the frozen Golden Set); three Runs; `--workers 3`; branch `agent-tutor-chat`, commit `8f939a5`. All 149 deterministic tests passed. An initial probe failed because the configured hostname was `api.deepseek.comz`; the main session corrected the extra trailing z. The next timed Agentic Tutor request succeeded in 2.505 s, read PEID and cited PEID-1.3. Probe evidence is kept in the folders named in `evaluator_metadata.json`.
- **Run folder:** `evaluation/runs/2026-10-14_173330_pilot_chat_refactor_deepseek_agentic`; includes three stored Runs, Markdown/HTML reports, `failures.md` and pinned evaluator metadata. Previous same-tutor pilot: `evaluation/runs/2026-10-14_120227_pilot_deepseek_agentic`.
- **Result:** mean (range) across three Runs, previous same-tutor pilot -> current pilot:

| Metric | Before | After |
|---|---|---|
| Search Step | 86.1% (86.1%–86.1%) | 86.1% (83.3%–88.9%) |
| Path Step | 98.1% (97.2%–100.0%) | 98.1% (97.2%–100.0%) |
| Answer Step | 87.0% (86.1%–88.9%) | 87.0% (86.1%–88.9%) |
| End-to-end Success | 86.1% (86.1%–86.1%) | 86.1% (83.3%–88.9%) |
| Routing accuracy | 87.0% (86.1%–88.9%) | 87.0% (86.1%–88.9%) |
| Recall GAIF | 72.2% (66.7%–83.3%) | 72.2% (66.7%–83.3%) |
| Recall PEID | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Recall AITB | 85.7% (85.7%–85.7%) | 85.7% (85.7%–85.7%) |
| Recall DTGS | 75.0% (75.0%–75.0%) | 75.0% (75.0%–75.0%) |
| Recall OUT_OF_SCOPE | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Recall (macro average) | 86.6% (85.5%–88.8%) | 86.6% (85.5%–88.8%) |
| Citation correctness | 96.3% (96.3%–96.3%) | 96.3% (96.3%–96.3%) |
| Refusal correctness | 33.3% (25.0%–50.0%) | 33.3% (25.0%–50.0%) |
| Out of scope correctness | 100.0% (100.0%–100.0%) | 100.0% (100.0%–100.0%) |
| Supported rate | pending | pending |
| Responsive rate | pending | pending |

- **Failing cases:** 6 -> 6 unique cases; 15/108 -> 15/108 failed Traces. Current: GS-05 3/3 (Search 3); GS-13 1/3 (Search 1); GS-15 3/3 (Search 3); GS-33 2/3 (Search 2); GS-35 3/3 (Search 3); GS-36 3/3 (Search 3). Model-call errors 0/108; Read limit reached 0/108. Every failing case is documented across all Runs in `failures.md`.
- **Decision:** pending.
- **Reason:** this pilot checks single-message behaviour after the refactor on unchanged candidate labels. Retain the preserved failure evidence for deciding whether to keep the tutor; group review of the labels and a frozen Golden Set comparison are still required. The Answer Step and End-to-end Success use code checks only; Supported and Responsive rates need the LLM judge. This does not evaluate multi-turn chat history quality.
- **Cross-tutor comparison:** `evaluation/runs/2026-10-14_173330_pilot_chat_refactor_deepseek_agentic/compare.html` compares the current Routed Tutor and Agentic Tutor runs on the same candidates, configured LLM and thinking setting. Routed -> Agentic: End-to-end Success 91.7% (91.7%–91.7%) -> 86.1% (83.3%–88.9%); Search Step 91.7% -> 86.1%; Path Step 100.0% -> 98.1%; Answer Step 91.7% -> 87.0%; Refusal correctness 75.0% -> 33.3%. These pilot results do not establish a causal change in quality from the refactor.

## 2026-10-14 Golden Set v1 frozen (#5)

- **Change:** the 36 candidates in `evaluation/golden_set_candidates.json` were reviewed against the Course Material
  and frozen as `evaluation/golden_set.json` (version 1). Six cases differ from the candidates: GS-01 (one key fact
  removed), GS-02 (new GAIF/PEID Near-miss question), GS-04 (near_miss to in_material), GS-08 (reworded, PEID-4.2
  removed), GS-15 (new DTGS question on cost, time to value and risk), GS-36 (Lewin's change model replaces Porter's
  five forces). Reasons per case: `evaluation/golden_set_review.md`.
- **Configuration:** reviewer 1 Gonçalo Augusto (all 36 cases); second review by Rodrigo, not blind (comments on
  GS-01, GS-08, GS-15). Automatic checks: `tests/test_golden_set.py`.
- **Run folder:** none. No score has been computed on `evaluation/golden_set.json`.
- **Result:** no score. The pilot runs above used the candidates, where four questions differ (GS-02, GS-08, GS-15,
  GS-36), so their numbers are not comparable with runs on the frozen file.
- **Decision:** kept.
- **Reason:** the Golden Set had to be agreed and frozen before the baseline (#7). Labels were decided from the
  Course Material, not from the pilot outputs; the pilots having been seen before the freeze is reported as a
  limitation.

## 2026-10-14 Baseline: Routed Tutor on Golden Set v1, deepseek-flash (code checks only)

- **Change:** none to the app; first run of the Routed Tutor on the frozen `evaluation/golden_set.json` (version 1).
  Compared with the pilot on the candidates (`2026-10-14_120039_pilot_deepseek_routed`), which used a different case
  file: four questions changed (GS-02, GS-08, GS-15, GS-36) and labels changed on GS-01 and GS-04, so the overall
  before -> after is not like for like.
- **Configuration:** Routed Tutor, Router `router_v2`, Course Tutor `tutor_v2`, app model `deepseek-flash`, thinking
  off, no judge (Answer Step and End-to-end Success are code checks only), `--workers 3`, commit `123d939`, case file
  `evaluation/golden_set.json`. 3 of 3 Runs and 108 of 108 Traces finished, no model call failed.
- **Run folder:** `evaluation/runs/2026-10-14_193513_golden_set_v1_routed` (with `failures.md`).
- **Result:** pilot on candidates -> Golden Set v1, mean (range): End-to-end Success 89.8% (88.9% to 91.7%) -> 97.2%
  (97.2% to 97.2%); Search Step 91.7% -> 97.2%; Path Step 100.0% -> 100.0%; Answer Step 89.8% (88.9% to 91.7%) ->
  97.2%; Routing accuracy 91.7% -> 97.2%; Recall (macro average) 91.7% -> 96.7%; Recall DTGS 75.0% -> 100.0%; Recall
  GAIF 83.3% -> 83.3%; Citation correctness 96.2% (96.2% to 96.3%) -> 100.0%; Refusal correctness 75.0% -> 100.0%; Out
  of scope correctness 100.0% -> 100.0%. Ranges in the new run are 0 for every Step and metric. Supported rate and
  Responsive rate: pending (#7). On the 30 cases whose question and labels are unchanged, End-to-end Success 94.4%
  (93.3% to 96.7%) -> 96.7% (96.7% to 96.7%), the only change being GS-27 1/3 -> 3/3. The six changed cases (GS-01,
  GS-02, GS-04, GS-08, GS-15, GS-36) all passed 3/3. Failing cases: GS-05 3/3 (Search: routed AITB, then the AITB
  Refusal), as in the pilot.
- **Decision:** pending.
- **Reason:** code-check baseline only: the Routed Tutor baseline for #7 and #17 needs the judge's Supported and
  Responsive rates. Most of the gain over the pilot comes from the changed case file (GS-15, GS-36) and from GS-27
  passing 3/3 under the same configuration that gave the Refusal in 2/3 pilot runs, which shows run-to-run variation
  at temperature 0.

## 2026-10-14 Agentic Tutor on Golden Set v1, deepseek-flash (code checks only)

- **Change:** none to the app; first run of the Agentic Tutor on the frozen `evaluation/golden_set.json` (version 1).
  Compared with the Agentic Tutor pilot on the candidates (`2026-10-14_120227_pilot_deepseek_agentic`), which used a
  different case file: four questions changed (GS-02, GS-08, GS-15, GS-36) and labels changed on GS-01 and GS-04, so
  the overall before -> after is not like for like; the like-for-like comparison is on the 30 unchanged cases.
- **Configuration:** Agentic Tutor `agentic_tutor_v1`, app model `deepseek-flash`, thinking off, no judge (Answer
  Step and End-to-end Success are code checks only), `--workers 3`, commit `b6f0a43` (Agentic Tutor code as on
  `agent-tutor` at `b4f8482`), case file `evaluation/golden_set.json`. 3 of 3 Runs and 108 of 108 Traces finished;
  no Trace recorded an error.
- **Run folder:** `evaluation/runs/2026-10-14_195710_golden_set_v1_agentic` (with `failures.md` and `compare.html`
  against the Routed Tutor on Golden Set v1, `2026-10-14_193513_golden_set_v1_routed`).
- **Result:** pilot on candidates -> Golden Set v1, mean (range): End-to-end Success 86.1% (86.1% to 86.1%) -> 86.1%
  (86.1% to 86.1%); Search Step 86.1% -> 86.1%; Path Step 98.1% (97.2% to 100.0%) -> 97.2% (97.2% to 97.2%); Answer
  Step 87.0% (86.1% to 88.9%) -> 88.9% (86.1% to 91.7%); Routing accuracy 87.0% (86.1% to 88.9%) -> 90.7% (88.9% to
  91.7%); Recall (macro average) 86.6% (85.5% to 88.8%) -> 89.6% (88.0% to 90.5%); Recall GAIF 72.2% (66.7% to
  83.3%) -> 66.7%; Recall PEID 100.0% -> 100.0%; Recall AITB 85.7% -> 85.7%; Recall DTGS 75.0% -> 95.8% (87.5% to
  100.0%); Recall OUT_OF_SCOPE 100.0% -> 100.0%; Citation correctness 96.3% -> 100.0%; Refusal correctness 33.3%
  (25.0% to 50.0%) -> 50.0% (50.0% to 50.0%); Out of scope correctness 100.0% -> 100.0%. Supported rate and Responsive
  rate: pending (#7). On the 30 unchanged cases, End-to-end Success 90.0% (90.0% to 90.0%) -> 86.7% (86.7% to
  86.7%) (GS-13 2/3 -> 0/3, GS-33 1/3 -> 0/3; GS-05 and GS-35 0/3 in both). Six changed cases: GS-01, GS-02, GS-04,
  GS-08 3/3 in both; GS-36 0/3 -> 3/3 (new question, DTGS Refusal); GS-15 0/3 -> 0/3 (new question, still an extra
  Read of PEID). Failing cases: GS-05 3/3 (Search: read AITB only, AITB Refusal), GS-13 3/3 (Search: extra Read of
  AITB in runs 1-2 with a correct DTGS-3.20 answer; AITB only and the AITB Refusal in run 3), GS-15 3/3 (Search:
  extra Read of PEID after DTGS; answer citing DTGS-3.7 in run 1, DTGS Refusal in runs 2-3), GS-33 3/3 (Search: no
  Read, refused in its own words before the Refusal sentence), GS-35 3/3 (Search: no Read, Out of scope sentence).
  No Trace reached the Read limit and no Course Material was read twice. Routed Tutor -> Agentic Tutor on the same
  file: End-to-end Success 97.2% -> 86.1%; Search 97.2% -> 86.1%; Path 100.0% -> 97.2%; Answer 97.2% -> 88.9% (86.1%
  to 91.7%); Refusal correctness 100.0% -> 50.0%; cases passing 3/3 for the Routed Tutor and 0/3 for the Agentic
  Tutor: GS-13, GS-15, GS-33, GS-35; none the other way.
- **Decision:** pending.
- **Reason:** for keeping the Agentic Tutor: GS-36 now passes and Citation correctness is 100.0% on the answers it
  gave. For abandoning it: on the frozen file it trails the Routed Tutor by four cases per Run (15 failing Traces
  vs 3), all failing at the Search Step (extra Reads of a non-Accepted Course, or no Read before a Refusal), and on
  the 30 unchanged cases it lost one case per Run against its own pilot. Evidence toward #17; no decision until the
  judge's Supported and Responsive rates exist.

## 2026-10-17 LLM judge (Supported, Responsive) and the choice of judge model

- **Change:** the LLM judge (#7). One call per criterion at temperature 0, prompts `judge_supported_v1` and
  `judge_responsive_v1`, JSON reply with the evidence before the verdict (PASS, FAIL or UNKNOWN); a failed call or
  an unparseable reply is a judge error and fails the Answer Step. The judge is called only for an answer given
  where an answer was expected. With a judge model set, the Answer Step needs both verdicts PASS. The judge may sit on
  another endpoint than the app model (`LLM_JUDGE_BASE_URL`, `LLM_JUDGE_API_KEY`).
- **Configuration:** probe `evaluation/probes/judge_probe.py` on the first Run of
  `2026-10-14_193513_golden_set_v1_routed` (answers by `deepseek-flash`): 8 answers as given, 4 with every cited
  Section swapped for a Section of another Course (should be judged not Supported), 4 answers paired with the question
  of a case from another Course (should be judged not Responsive); 16 items, 32 calls per model, 3 at a time, 120 s
  timeout, no retry. Candidates exclude the app model's family (DeepSeek) and Nemotron. Results in
  `evaluation/probes/judge_probe.json`.
- **Run folder:** none (probe only); the baseline with the judge is the next entry.
- **Result:** `openai/gpt-oss-20b` (NVIDIA, no thinking switch sent): 0 judge errors in 32 calls, median 3.7 s
  (slowest 9.8 s), originals 8/8 Supported and 8/8 Responsive, swapped Sections caught 4/4, wrong questions caught
  4/4. `course-chat` (the professor's endpoint, `azure/gpt-5.4-nano`): median 1.6 s, originals 8/8 and 8/8, swapped
  Sections 4/4, wrong questions 3/4, the fourth a judge error: 2 calls hit HTTP 429 (the proxy allows 30 requests per
  minute per key). `z-ai/glm-5.3`: 24 of 32 calls timed out at 120 s. `google/gemma-4-31b-it`: 30 of 32 timed out.
  `mistralai/mistral-large`: 404 on every call.
- **Decision:** kept, with `openai/gpt-oss-20b` as the judge model.
- **Reason:** the only candidate with no judge error, fast enough for three Runs, from a family other than the app
  model's, and on an endpoint that keeps working after the course key stops on 2026-10-21. The probe only shows that
  the judge works and catches gross errors; whether its verdicts agree with ours is ticket #8 (hand labels, TPR and
  TNR). `course-chat` is the fallback, within its rate limit and before its key stops.

## 2026-10-18 Professor's endpoint re-tested after the proxy fix; app model stays deepseek-flash

- **Change:** none to the app. The professor changed the course proxy (LiteLLM) to assume `reasoning_effort = none`
  when the parameter is missing; before, it treated such requests as thinking-mode requests and sent them to the
  Responses API, which is not enabled in the region (the 404 on `tools` in the 2026-10-14 entry). Re-tested
  `course-chat` (`/model/info` reports `azure/gpt-5.4-nano`).
- **Configuration:** single calls on 2026-10-18 through the app's own code: `read_file` offered as a native tool with
  and without `reasoning_effort="none"`, then the Agentic Tutor (`agentic_tutor_v1`) on four throwaway questions
  (not Golden Set cases), `LLM_THINKING=none`.
- **Run folder:** none (single calls).
- **Result:** native tool calls work with and without `reasoning_effort` (1.5 s; 59 s for the first call after a quiet
  period). The Agentic Tutor gave the expected behaviour on all four questions: a PEID answer citing PEID-1.3, Out of
  scope with no Read, the GAIF Refusal for an exam-date question, and an AITB answer citing AITB-2.7, AITB-3.5,
  AITB-3.8 and AITB-3.9 (1.5 to 5.6 s). The Router gave the same Course as `deepseek-flash` on six Golden Set
  questions, including the wrong AITB for GS-05.
- **Decision:** app model stays `deepseek-flash`; `course-chat` not adopted.
- **Reason:** both tutors were already measured on `deepseek-flash`, and the deadline (2026-10-20) leaves no room to
  measure both again under the proxy's limit of 30 requests per minute; the course key also stops on 2026-10-21. This
  is not a quality comparison: the two models were never run on the Golden Set under the same conditions, so nothing
  here says that one is better.

## 2026-10-18 Routed Tutor on Golden Set v1 with the LLM judge (baseline)

- **Change:** none to the app; the first evaluation with the LLM judge (#7). The Answer Step now also needs every
  expected answer to be judged Supported and Responsive. Compared with the Routed Tutor run on 2026-10-14
  (`2026-10-14_193513_golden_set_v1_routed`, code checks only), so the before -> after below is not like for like:
  it adds the judge, it does not change the app.
- **Configuration:** Routed Tutor, Router `router_v2`, Course Tutor `tutor_v2`, app model `deepseek-flash`, thinking
  off, judge `openai/gpt-oss-20b` (NVIDIA, no thinking switch) with `judge_supported_v1` and `judge_responsive_v1`,
  `--workers 2`, commit `683608f`, case file `evaluation/golden_set.json` (version 1). 3 of 3 Runs and 108 of 108
  Traces finished; no Trace recorded an error; 81 answers judged, no verdict UNKNOWN or a judge error.
- **Run folder:** `evaluation/runs/2026-10-18_020503_golden_set_v1_judge_routed` (with `failures.md`).
- **Result:** code checks only -> with the judge, mean (range): End-to-end Success 97.2% (97.2% to 97.2%) -> 90.7%
  (88.9% to 91.7%); Search Step 97.2% -> 97.2%; Path Step 100.0% -> 100.0%; Answer Step 97.2% -> 90.7% (88.9% to
  91.7%). New: Supported rate 93.8% (92.6% to 96.3%), Responsive rate 96.3% (96.3% to 96.3%), Judge undecided rate
  0.0%. Unchanged: Routing accuracy 97.2%, Recall (macro average) 96.7%, Citation correctness 100.0%, Refusal
  correctness 100.0%, Out of scope correctness 100.0%. Failing cases: GS-05 3/3 (Search: routed to AITB, the AITB
  Refusal; as on 2026-10-14), GS-27 3/3 (Answer: judged not Responsive in runs 1-2, not Supported in run 3; the
  answer cites DTGS-3.7 and then ends with the DTGS Refusal sentence), GS-24 2/3 (Answer: judged not Supported, the
  claim that structure does not guarantee accuracy), GS-06 1/3 and GS-25 1/3 (Answer: judged not Supported). Every
  case that fails only through the judge passed the code checks on 2026-10-14.
- **Decision:** kept as the baseline with the judge.
- **Reason:** the number to defend is now 90.7% End-to-end Success, which checks claims as well as citations. The
  drop from 97.2% comes only from the judge: the code-check Steps and diagnostics did not move. The judge is not yet
  checked against our hand labels (#8): some verdicts may be too strict (GS-06: a timestamp "changes the prefix" was
  judged not stated by a Section that says a timestamp disables caching), so the 90.7% is provisional until #8.

## 2026-10-18 Agentic Tutor on Golden Set v1 with the LLM judge

- **Change:** none to the app; the Agentic Tutor evaluated with the LLM judge, the same day, model, judge and commit
  as the Routed Tutor baseline above, so Routed -> Agentic below changes only the tutor. Also compared with the
  Agentic Tutor run on 2026-10-14 (`2026-10-14_195710_golden_set_v1_agentic`, code checks only).
- **Configuration:** Agentic Tutor `agentic_tutor_v1`, app model `deepseek-flash`, thinking off, judge
  `openai/gpt-oss-20b` with `judge_supported_v1` and `judge_responsive_v1`, `--workers 2`, commit `683608f`, case
  file `evaluation/golden_set.json`. 3 of 3 Runs and 108 of 108 Traces finished; no Trace recorded an error or reached
  the Read limit; 81 answers judged, no verdict UNKNOWN or a judge error.
- **Run folder:** `evaluation/runs/2026-10-18_022123_golden_set_v1_judge_agentic` (with `failures.md` and
  `compare.html` against the Routed Tutor baseline above).
- **Result:** Routed Tutor -> Agentic Tutor, both with the judge, mean (range): End-to-end Success 90.7% (88.9% to
  91.7%) -> 85.2% (83.3% to 86.1%); Search Step 97.2% -> 92.6% (91.7% to 94.4%); Path Step 100.0% -> 100.0%; Answer
  Step 90.7% (88.9% to 91.7%) -> 89.8% (88.9% to 91.7%); Supported rate 93.8% -> 90.1% (88.9% to 92.6%); Responsive
  rate 96.3% -> 100.0%; Routing accuracy 97.2% -> 95.4% (94.4% to 97.2%); Recall GAIF 83.3% -> 72.2% (66.7% to
  83.3%); Refusal correctness 100.0% -> 100.0%. Cases that differ: GS-02 3/3 -> 0/3 (Search: reads GAIF then PEID,
  with a correct answer citing GAIF-2.10), GS-15 3/3 -> 1/3 (Search: extra Read of PEID), GS-26 3/3 -> 1/3 (Answer:
  judged not Supported, an uncited "Short answer" sentence), GS-25 2/3 -> 3/3. Both fail GS-05 3/3, GS-27 3/3, GS-24
  2/3 and GS-06 1/3. Against the Agentic Tutor on 2026-10-14 (code checks only, same code apart from the judge):
  End-to-end Success 86.1% -> 85.2%, Search Step 86.1% -> 92.6%, Path Step 97.2% -> 100.0%, Refusal correctness
  50.0% -> 100.0%; GS-13, GS-33 and GS-35 went from 0/3 to 3/3, and GS-02 from 3/3 to 0/3, with the same prompts,
  model name and temperature 0.
- **Decision:** abandoned (#17): the Routed Tutor stays the app's tutor and the screen default (`TUTOR=routed`); the
  Agentic Tutor stays in the code as the measured alternative.
- **Reason:** measured the same day with the same model and judge, the Routed Tutor leads by about two cases per Run
  (90.7% vs 85.2% End-to-end Success), and it led on 2026-10-14 too (97.2% vs 86.1%, code checks only). The Agentic
  Tutor's extra losses are mostly extra Reads of a Course that is not Accepted (Search Step), which the Router rules
  out by choosing exactly one Course. In its favour: Responsive rate 100.0% and GS-25 3/3. The four-day shift in which
  Agentic Traces fail, with nothing changed on our side, shows that a run on one day is a sample of a model that can
  change behind the same name; this comparison is like for like because both tutors ran the same day.

## 2026-10-18 Judge calibration, first result (judge_supported_v1, judge_responsive_v1)

- **Change:** none to the app or the judge; the first check of the judge against our own labels (#8).
- **Configuration:** `python src/calibration.py export` on the two 2026-10-18 judge runs (seed 8): 28 distinct
  answers, 13 the judge failed on a criterion and 15 it passed on both; 19 held-out and 9 tuning, split committed
  before labelling (`316950c`). One labeller (Gonçalo Augusto), alone, without the judge's verdicts, in
  `evaluation/calibration/labels.md`. Judge `openai/gpt-oss-20b`, verdicts as stored in the runs.
- **Run folder:** `evaluation/calibration` (`items.json`, `labels.md`, `report.md`).
- **Result:** held-out (19): Supported accuracy 63.2%, Cohen's kappa 0.13, TPR 66.7%, TNR 50.0% (2 of 4 human FAILs
  caught); Responsive accuracy 84.2%, kappa 0.00, TPR 84.2%, no human FAIL (TNR not measurable). Tuning (9):
  Supported 55.6% (kappa 0.05), Responsive 100.0%. The 28 answers cover only 15 Golden Set questions: GS-27 6 times,
  GS-24 4, GS-25 3, because the judge's FAILs cluster on a few questions and the sample was drawn per distinct answer.
  Two patterns in the 14 disagreements: (1) 6 of the 8 answers the judge failed on Supported and the labeller passed
  were failed for an uncited summary or lead-in sentence ("Short answer: not reliably...", "To stop the model
  inventing facts...:") or a sentence about what the material does not say; (2) the labeller's Supported FAILs give
  reasons about how the answer is written or whether it answers ("overexplains and shouldn't mention the course
  name", "it doesn't actually answer"), not about a claim missing from its Section, and no answer was labelled not
  Responsive.
- **Decision:** pending.
- **Reason:** Supported is below the 80% threshold, so the protocol calls for a new judge prompt version revised on
  the tuning set. Before that, the labels and the judge must apply the same definition: pattern (1) points at a
  judge rubric that is stricter than the labeller about summary sentences; pattern (2) at labels that put answer
  quality and style under Supported. The sample's repetition of a few questions is a limitation to report.

## 2026-10-18 Judge calibration: judge_supported_v1 -> judge_supported_v2

- **Change:** new judge prompt `judge_supported_v2` (the Responsive prompt stays `judge_responsive_v1`), revised from
  the disagreements in the 9 tuning items of the first calibration result above: a lead-in, summary or concluding
  sentence is supported when its content is in the Sections the answer cites, even without its own citation; a
  sentence about the Course Material itself fails only when the cited Sections contradict it; style and
  responsiveness are explicitly outside Supported. Also tried and abandoned: moving five of the labeller's six
  Supported FAILs to the criterion their written reason described (`labels_corrected.md`,
  `label_corrections.md`), done by the coding assistant at the labeller's request after the judge's verdicts had
  been seen.
- **Configuration:** the same 28 answers, split and judge model (`openai/gpt-oss-20b`) as the first result; the 28
  answers judged again on both criteria (`python src/calibration.py rejudge`,
  `evaluation/calibration/verdicts_judge_supported_v2_judge_responsive_v1.json`). One Supported call timed out
  (L10, a judge error, counted as FAIL).
- **Run folder:** `evaluation/calibration` (`report_first_labels_judge_v2.md`, `report_corrected_judge_v1.md`,
  `report_corrected_judge_v2.md`).
- **Result:** held-out (19), first labels: Supported accuracy 63.2% -> 84.2%, Cohen's kappa 0.13 -> 0.56, TPR 66.7% ->
  86.7%, TNR 50.0% -> 75.0% (3 of 4 human FAILs caught); Responsive 84.2% -> 84.2% (same prompt; still no human
  FAIL, so TNR is not measurable). Tuning (9), first labels: Supported 55.6% -> 44.4%. With the corrected labels,
  held-out Supported was 57.9% with v1 and 68.4% with v2. With v2 the judge failed L07, L18 and L20 for concrete
  claims (a claim about how the material "frames" shadow AI that DTGS-3.2 does not make; Klarna claims cited to
  DTGS-3.21 but stated in DTGS-3.20; "six elements" not in the cited AITB-2.4): three of the four answers the
  correction had moved from FAIL to PASS.
- **Decision:** `judge_supported_v2` kept (the code points at it); the label corrections abandoned. The official
  labels are the first labels, unchanged.
- **Reason:** with the labels as first given, blind to the judge, v2 passes the 80% threshold on the held-out set
  for both criteria, and its Supported FAILs name checkable claims. The corrections lowered agreement and v2's
  evidence showed that the labeller's first FAILs on L07, L18 and L20 were right, so they are kept only as a record.
  Limits to report: one labeller; 28 answers from 15 questions (GS-27 6 times); the held-out disagreements were
  visible in the first report when v2 was written, so the held-out set is not fully unseen; v2 did not improve the
  tuning items (44.4%), where it still fails sentences that add a word such as "grounding" to what the Section
  says; Responsive has no human FAIL on held-out, so the judge's ability to catch an unresponsive answer is
  untested. The Golden Set baselines above were judged with v1 and must be judged again with v2.

## 2026-10-18 Routed Tutor on Golden Set v1 with the calibrated judge (judge_supported_v2)

- **Change:** none to the app; the Routed Tutor baseline judged again with `judge_supported_v2`, the version kept
  after calibration. Compared with the baseline judged by `judge_supported_v1`
  (`2026-10-18_020503_golden_set_v1_judge_routed`): same app, model and case file, so the before -> after changes
  only the judge's Supported prompt (and the app's answers, which are generated again).
- **Configuration:** Routed Tutor, Router `router_v2`, Course Tutor `tutor_v2`, app model `deepseek-flash`, thinking
  off, judge `openai/gpt-oss-20b` with `judge_supported_v2` and `judge_responsive_v1`, `--workers 2`, commit
  `dcee50a`, case file `evaluation/golden_set.json`. 3 of 3 Runs and 108 of 108 Traces finished; no Trace recorded
  an error; 81 answers judged; one judge call timed out (GS-10, Run 1), a judge error counted as a fail.
- **Run folder:** `evaluation/runs/2026-10-18_040522_golden_set_v1_judge_v2_routed` (with `failures.md` and
  `compare.html` against the v1-judge baseline).
- **Result:** judge v1 -> judge v2, mean (range): End-to-end Success 90.7% (88.9% to 91.7%) -> 92.6% (88.9% to
  94.4%); Answer Step 90.7% (88.9% to 91.7%) -> 92.6% (88.9% to 94.4%); Supported rate 93.8% (92.6% to 96.3%) ->
  97.5% (92.6% to 100.0%); Responsive rate 96.3% -> 96.3%; Judge undecided rate 0.0% -> 0.6% (0.0% to 1.9%). Search
  Step 97.2%, Path Step 100.0%, Routing accuracy 97.2%, Citation correctness 100.0% and Refusal correctness 100.0%
  unchanged. Failing cases: GS-05 3/3 (Search: routed to AITB, the AITB Refusal), GS-27 3/3 (Answer: judged not
  Responsive, the answer says the material does not cover what is asked), GS-06 1/3 (Answer: judged not Supported,
  "the prefix is no longer byte-identical" is not in PEID-3.13), GS-10 1/3 (Answer: judge error, timeout). GS-24 and
  GS-25, failed by the v1 judge for uncited summary sentences, now pass 3/3.
- **Decision:** kept as the baseline: the number to defend is 92.6% End-to-end Success, Routed Tutor, calibrated
  judge.
- **Reason:** the judge behind it now agrees with our labels on 84.2% of held-out answers on both criteria, and the
  drop from 97.2% (code checks only) is explained case by case: GS-05 is a routing failure, GS-27 a partial answer
  that ends with the Refusal sentence, GS-06 one extra claim. GS-10 failed on a judge timeout, not on the answer, so
  1 of the 3 failing Traces in Run 1 says nothing about the tutor. The judge's ability to catch an unresponsive answer
  is untested (no human Responsive FAIL in the held-out set).

## 2026-10-18 Agentic Tutor (chat version) on Golden Set v1 with the calibrated judge (judge_supported_v2)

- **Change:** none to the prompts or model; the Agentic Tutor of branch `agent-tutor-chat` (the chat screen with
  conversation history and the tool loop separated from the answer checks, `src/agentic.py`), measured for the first
  time on the frozen Golden Set with the calibrated judge. Routed -> Agentic below is compared with the Routed Tutor
  baseline judged by `judge_supported_v2` (`2026-10-18_040522_golden_set_v1_judge_v2_routed`): same case file, app
  model, thinking setting, judge model and judge prompts, so the change is the tutor (and the code of this branch,
  commit `3b7125c` against `dcee50a`). Same-tutor previous entry: the Agentic Tutor judged by `judge_supported_v1`
  (`2026-10-18_022123_golden_set_v1_judge_agentic`, commit `683608f`, before the chat refactor was merged).
- **Configuration:** Agentic Tutor `agentic_tutor_v1`, app model `deepseek-flash`, thinking off, judge
  `openai/gpt-oss-20b` on NVIDIA with `judge_supported_v2` and `judge_responsive_v1`, judge thinking `none` (the
  judge model and judge thinking were passed as environment variables because `.env` still held an empty
  `LLM_JUDGE_MODEL=` line; same values as `.env.example`), `--workers 2`, commit `3b7125c`, case file
  `evaluation/golden_set.json`. 3 of 3 Runs and 108 of 108 Traces finished; no Trace recorded an error or reached the
  Read limit; 81 answers judged, no verdict UNKNOWN or a judge error. 188 tests passed before the run.
- **Run folder:** `evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic` (with `failures.md` and
  `compare.html` against the Routed Tutor baseline with the calibrated judge).
- **Result:** Routed Tutor -> Agentic Tutor, both with `judge_supported_v2`, mean (range): End-to-end Success 92.6%
  (88.9% to 94.4%) -> 87.0% (83.3% to 88.9%); Search Step 97.2% -> 91.7% (88.9% to 94.4%); Path Step 100.0% ->
  100.0%; Answer Step 92.6% (88.9% to 94.4%) -> 92.6% (91.7% to 94.4%); Supported rate 97.5% (92.6% to 100.0%) ->
  93.8% (92.6% to 96.3%); Responsive rate 96.3% -> 100.0%; Judge undecided rate 0.6% (0.0% to 1.9%) -> 0.0%; Routing
  accuracy 97.2% -> 94.4%; Recall GAIF 83.3% -> 66.7%; Recall (macro average) 96.7% -> 93.3%; Citation correctness,
  Refusal correctness and Out of scope correctness 100.0% -> 100.0%. Failing cases (14 Traces): GS-02 3/3 (Search:
  reads PEID, then GAIF, with an answer citing GAIF-2.10 that the judge passes), GS-05 3/3 (Search: reads AITB only,
  the AITB Refusal), GS-13 2/3 (Search: extra Read of AITB), GS-27 2/3 (Answer: judged not Supported, sentences about
  how "the material" frames or defines shadow AI), GS-06 1/3, GS-24 1/3 ("six elements"), GS-28 1/3 (Answer: judged
  not Supported, one claim beyond the cited Section), GS-15 1/3 (Search: extra Read of PEID). Against the Routed
  Tutor, the cases that differ: GS-02 3/3 -> 0/3, GS-13 3/3 -> 1/3, GS-15, GS-24 and GS-28 3/3 -> 2/3, GS-27 0/3 ->
  1/3, GS-10 2/3 -> 3/3 (the Routed Tutor's judge timeout). Same tutor, judge v1 -> judge v2: End-to-end Success
  85.2% (83.3% to 86.1%) -> 87.0%; Search Step 92.6% (91.7% to 94.4%) -> 91.7%; Answer Step 89.8% (88.9% to 91.7%)
  -> 92.6%; Supported rate 90.1% (88.9% to 92.6%) -> 93.8%; Routing accuracy 95.4% (94.4% to 97.2%) -> 94.4%; GS-26
  1/3 -> 3/3, GS-27 0/3 -> 1/3, GS-24 1/3 -> 2/3, GS-15 1/3 -> 2/3, GS-13 3/3 -> 1/3.
- **Decision:** abandoned again (#17 stands): the Routed Tutor stays the app's tutor and the screen default
  (`TUTOR=routed`); the Agentic Tutor, chat version included, stays in the code as the measured alternative.
- **Reason:** for keeping the Routed Tutor as the app's tutor (the #17 decision): with the calibrated judge, the same
  day, model and judge, it still leads by about two cases per Run (92.6% vs 87.0% End-to-end Success; the ranges
  touch only at 88.9%), and the gap is almost all in the Search Step: 6 of the Agentic Tutor's 14 failing Traces are
  an extra Read of a Course that is not Accepted (taxonomy category 2), which the Router rules out by choosing one
  Course. For the Agentic Tutor: its Answer Step equals the Routed Tutor's (92.6%), its Responsive rate is 100.0%
  (the Routed Tutor fails GS-27 3/3 on Responsive), and the judge v1 -> v2 change moved it by about as much as the
  Routed Tutor (+1.8 and +1.9 points). Not covered: the difference between commits `dcee50a` and `3b7125c` and the
  conversation history of the chat screen (each Golden Set case is a single question); one labeller behind the judge
  calibration; 36 cases and three Runs.

## 2026-10-19 Keep the Agentic Tutor chat for teaching

- **Change:** product decision, not a new implementation or evaluation. The group chooses the existing Agentic
  Tutor chat for the teaching experience and demo because it enables follow-up questions and clarification in
  context. This supersedes the 18 October decisions to abandon it under #17; those entries remain historical.
- **Configuration:** unchanged from the latest recorded comparison: app model `deepseek-flash`, thinking off,
  Golden Set v1 (36 cases), judge `openai/gpt-oss-20b`, `judge_supported_v2` and `judge_responsive_v1`.
- **Run folders:** existing evidence only: `evaluation/runs/2026-10-18_040522_golden_set_v1_judge_v2_routed` and
  `evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic`. No new Runs performed for this decision.
- **Result:** unchanged: Routed Tutor -> Agentic Tutor, End-to-end Success 92.6% (88.9% to 94.4%) -> 87.0%
  (83.3% to 88.9%); Search Step 97.2% -> 91.7%; Path Step 100.0% -> 100.0%; Answer Step 92.6% -> 92.6%.
- **Decision:** kept for teaching and presentation, despite the lower measured single-question result. Use
  `TUTOR=agentic` explicitly; the code fallback remains `routed`. The Routed Tutor remains available for comparison.
- **Reason:** conversation is a better fit for the group's teaching purpose: students can clarify an explanation
  and build on earlier exchanges. This is a design rationale, not demonstrated improvement in learning. The current
  evaluator supplies no conversation history; multi-turn quality and learning outcomes remain unmeasured. The
  next evaluation should cover them without changing Golden Set v1 or its scoring rules. See
  [ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md) for the tradeoff, limitations and presentation wording.

## 2026-10-19 Consolidate displayed citations under Cited Sections

- **Change:** presentation only (#21, spec #20). Both tutor screens hide standalone inline Section markers in a
  display copy and retain the existing Cited Sections footer and invalid-citation warnings. Ordinary brackets and
  Markdown links stay intact. Original answers and citation metadata remain in conversation history, follow-up
  requests, evaluation, saved Traces and reports.
- **Configuration:** no changes to tutor selection, prompts, model settings, the Golden Set, Course Material,
  judge calibration, scoring, human labels, stored Runs or report renderers. No new model evaluation was run.
- **Checks completed:** 201 deterministic tests pass (188 existing plus 13 new), including both real Streamlit
  screens with fake models, follow-up and rerender behavior, raw conversation context, invalid references,
  Refusal, Out of scope, retry, citation formatting, links, emphasis, lists and dollar amounts. `git diff --check` passes.
- **Acceptance still pending:** the implemented helper's offline preservation check over all 216 saved Traces
  and local visual inspection of the screens. These checks must finish before marking the ticket complete.
- **Result:** no new tutor score or measured improvement in readability or learning. Existing single-question
  End-to-end Success figures (87.0% Agentic Tutor, 92.6% Routed Tutor) describe the original underlying tutors,
  not this display. A new Golden Set run or judge calibration is unnecessary if the pending check confirms raw
  answers, judge inputs and scoring remain unchanged; crossing that boundary requires reassessing evaluation.
- **Project report wording:** “The screen consolidates references under Cited Sections; evaluation and saved
  Traces retain the original answer with citations beside its claims. This presentation change does not establish
  improved readability or learning.” No project report is present in the repository; the group can use this wording.
