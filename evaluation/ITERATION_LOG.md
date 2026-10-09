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
