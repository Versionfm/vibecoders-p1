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
