# Course Tutor

A single-screen tutor for four Courses (GAIF, PEID, AITB, DTGS), answering from Course Material with Section citations (e.g. `[PEID-2.3]`). The chosen teaching experience is the Agentic Tutor chat: one model reads the Course Materials it needs through a `read_file(course)` tool and keeps conversation context for follow-up questions. The Routed Tutor remains available for comparison: a Router picks one Course, then the Course Tutor answers from its Course Material. We kept the chat for its conversational teaching format despite its lower measured single-question End-to-end Success; improved learning has not been measured. The current purpose-boundary candidate is awaiting real-model evaluation; earlier scores describe earlier versions. See [the decision and evidence](docs/adr/0003-keep-agentic-chat-for-teaching.md), [the iteration log](evaluation/ITERATION_LOG.md), [the Agentic Tutor design](docs/adr/0001-agentic-tutor-without-router.md) and [CONTEXT.md](CONTEXT.md) for vocabulary.

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows; use .venv/bin/python elsewhere
```

## Add your API key locally

The key goes in a local `.env` file, which Git ignores.

1. Copy the example file: `cp .env.example .env`
2. Open `.env` and paste your DeepSeek API key after `LLM_API_KEY=`. The example file already selects DeepSeek (`LLM_BASE_URL=https://api.deepseek.com`, `LLM_MODEL=deepseek-flash`); it also lists the NVIDIA and course endpoints, commented out.
3. Do not rename the file and do not put the key anywhere else (code, notes, chat, issues).
4. `git status` must **not** list `.env`.

Never commit `.env` or paste the key into any committed file.

To use the professor's course endpoint instead (the group key, shared inside the group only; it stops working on
21 October 2026 at 12:00 Lisbon time), put these lines in `.env` in place of the DeepSeek ones:

```
LLM_API_KEY=<the group key from the professor's e-mail>
LLM_BASE_URL=https://llm-proxy-obfzuamujq-ew.a.run.app/v1
LLM_MODEL=course-chat
LLM_THINKING=none
```

The Routed Tutor works there (2 to 6 s per question). Since the professor's proxy fix on 18 October 2026, native tool
calls work too, so the Agentic Tutor runs there as well. The first question after a quiet period can take 30 to 60 s
while the service wakes up. The evaluations in the iteration log were run on DeepSeek, not on this endpoint.

Other settings in `.env` (optional unless marked required):

- `LLM_THINKING`: `on`, `off` or `none` (default `off`). Switches the app model's reasoning ("thinking") mode, sent both as
  `chat_template_kwargs.enable_thinking` (Nemotron) and as DeepSeek's `thinking` type. Off is much faster (on Nemotron a
  Router call took about 2 s instead of about 22 s). `none` sends no switch, for endpoints that reject it. Every answer and every stored evaluation run records the setting, so both can be compared.
- `LLM_BASE_URL`, `LLM_MODEL`: endpoint and app model. Required, with no defaults in the code: switch provider by
  changing these two lines.
- `LLM_JUDGE_MODEL`: the LLM judge, required by the evaluation command (the screen does not use it):
  `openai/gpt-oss-20b` on NVIDIA, with your NVIDIA key in `LLM_JUDGE_API_KEY`. It must be another model family than
  the app model. `LLM_JUDGE_BASE_URL` and `LLM_JUDGE_API_KEY`
  default to the app's endpoint and key; set them when the judge sits on another provider. `LLM_JUDGE_THINKING`
  works like `LLM_THINKING`.
- `TUTOR`: `routed` (the code's fallback when unset) or `agentic`. Use `agentic` for the chosen teaching experience
  and demo: a conversation with the Course Materials read alongside each answer. The choice prioritises conversation
  despite the lower single-question score; see [ADR 0003](docs/adr/0003-keep-agentic-chat-for-teaching.md).

Each model call times out after 60 s and is retried at most once, so one call fails after about 2 minutes at worst
and the screen then asks you to try again.

## Run

```bash
TUTOR=agentic streamlit run src/app.py
```

Alternatively, set `TUTOR=agentic` in `.env` and run `streamlit run src/app.py`. For the Routed Tutor comparison,
set `TUTOR=routed`. The chat keeps prior questions and answers in the browser
session and sends them with each follow-up. Each answer reads its own Course Material; prior
answers are conversation context, not source material. **New conversation** clears the history.

Both tutor screens consolidate standalone Section markers under **Cited Sections** instead of repeating them
beside each claim. Invalid citations still appear in the footer and warning. Only the displayed answer is cleaned:
follow-up context, evaluation, saved Traces and reports retain the original cited answer, so the Golden Set and
judge criteria are unchanged. No new model evaluation was run for this presentation change.

Wording for the group's project report:

> The screen consolidates references under Cited Sections; evaluation and saved Traces retain the original answer
> with citations beside its claims. This presentation change does not establish improved readability or learning.

## How the Agentic Tutor works

Student message → LLM requests Course Material → Python reads it → LLM answers.

The repeatable tool loop lives in `src/agentic.py`. `src/tutor.py` prepares the shared result and checks citations;
`src/app.py` keeps the chat history. See [the short workflow guide](docs/AGENTIC_TUTOR_WORKFLOW.md) for the main path,
Read limits and evaluation details.

The Agentic Tutor's prompt `agentic_tutor_v3` treats identity requests, requests about this app's internals, greetings
without a Course question and unrelated requests as Out of scope. Both screens show:

> This tutor answers questions about GAIF, PEID, AITB and DTGS. Please ask a question about one of these Courses.

The model still returns the exact internal Out of scope Sentence, without a Read. A noncanonical reply without
a Read gets one recovery attempt: either return that sentence or read the relevant Course Material and answer.
Another unsupported reply produces the existing retry notice and stays out of successful conversation history.
Course questions about models or tools, mixed greeting/Course questions and contextual follow-ups keep the grounded
answer path; a missing Read alone is never interpreted as Out of scope.

The deterministic tests use fake models and the separate
[purpose-boundary cases](evaluation/purpose_boundary_cases.json). They verify outcome handling, not live-model
classification. The live model was checked separately (#25): a probe of the 12 purpose-boundary cases, 3 times each,
passed 36 of 36 ([evaluation/probes/purpose_boundary_probe.json](evaluation/probes/purpose_boundary_probe.json)).
On unchanged Golden Set v1, v3 scored 84.3% End-to-end Success (69.4% to 91.7%) over three Runs; 8 judge calls
timed out in Runs 1 and 2 and count as failures, and judged again they all pass (91.7%, supplementary). The earlier
85.2% was measured with `agentic_tutor_v1` and is not a measurement of v3. Golden Set v1 contains single questions
and does not measure contextual follow-ups. Details: [the iteration log](evaluation/ITERATION_LOG.md).

## Evaluate

One command runs a case file (JSON, in the Golden Set format) through the same answer function the screen uses, three times:

```bash
python src/evaluate.py evaluation/sample_cases.json
```

Options: `--runs 3` (default), `--out evaluation/runs` (default), `--label tutor_v3` (added to the run folder name),
`--workers 4` (cases answered in parallel within a run; default 1, keep it small because of the endpoint's rate limit),
`--tutor agentic` (run the Agentic Tutor instead of the Routed Tutor; the tutor is added to the run folder name and
stored in every run).
It needs the API key in `.env`, like the app. Each run is stored as soon as it finishes, so stopping the command
keeps the runs already completed (the report is written at the end).

Each evaluation writes a folder `evaluation/runs/<date>_<time>[_<label>]/` with:

- `run_1.json`, `run_2.json`, `run_3.json`: timestamp, tutor (`routed` or `agentic`), case file, prompt versions (`router` and `tutor`, or `agentic_tutor`), model names, the metrics of that run and every case's output (routed Course, evidence, answer, citations, Refusal, invalid citations, error), its Trace (`materials_read` in order, `read_arguments`, `read_count`, `read_limit_hit`) and its `steps` (Search, Path and Answer verdicts with reasons, End-to-end Success, earliest failing Step);
- `report.md`: the Step matrix (pass rate per Step and End-to-end Success as mean and range across the runs; per case each Step as e.g. `3/3` with the earliest failing Step), each metric as mean and range, plus a per-case table, ready to paste into the report;
- `report.html`: the same Runs as one self-contained page (no JavaScript, no external files; opens offline and follows the browser's light or dark theme). It shows End-to-end Success as the headline (mean and range, with tutor, model, prompt versions and case file), a pass-rate bar per Step, the Answer Step rate ("the number you would have reported") next to End-to-end Success ("the number that matters"), how many failing Traces first fail at each Step, one example Trace per failure pattern (earliest failing Step plus reason) with a "what went wrong" note, and every Trace in a collapsible section. Its rates are computed from the stored `run_N.json` files by `src/html_report.py`, never typed in.

To compare two evaluations (for example a baseline and a change, kept or abandoned), point the compare command at their
run folders:

```bash
python src/compare.py evaluation/runs/<run folder A> evaluation/runs/<run folder B>
```

It reads only the stored `run_N.json` files (no model calls, no API key) and writes `compare.html` into run folder B,
printing its path. The page, in the same style as `report.html`, shows both evaluations' pass rate per Step and
End-to-end Success side by side (mean and range over the Runs), and the cases whose End-to-end Success changed, with
each side's success count (e.g. `0/3` to `2/3`) and earliest failing Step. When the two run folders used different
case files, models or thinking settings, it warns on the page and in the console, so two changes are never compared
as one.

Every Trace is scored by three Steps, checked in this order (see [ADR 0002](docs/adr/0002-trace-steps-and-html-report.md)):

- **Search Step:** at least one Accepted Course and no other Course chosen or read; none for an Out of scope case. For the Routed Tutor the routed Course is the Course Material read. Recall and extra Reads are recorded.
- **Path Step:** fails on a failed model call or an invalid Router reply, a `read_file` argument that is not a Course, a Course Material read twice, the Read limit reached, or an in-scope answer or Refusal with no Read.
- **Answer Step:** cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope. With a judge model set, an expected answer must also be judged **Supported** (every claim is in the Section it cites) and **Responsive** (it addresses what was asked); without one it is code checks only, and the report says so.
- **End-to-end Success:** the Trace passes all three Steps. It is the headline number.

Metrics kept from before: routing accuracy (choice within Accepted Courses), recall per class over GAIF, PEID, AITB, DTGS and OUT_OF_SCOPE with its macro average (labelled "macro"), citation correctness, Refusal correctness and Out of scope correctness. With the judge: Supported rate, Responsive rate and the Judge undecided rate (UNKNOWN verdicts and judge errors, which count as a fail).

The LLM judge ([src/judge.py](src/judge.py)) makes one call per criterion at temperature 0, with its own versioned prompt (`prompts/judge_supported_v2.md`, `prompts/judge_responsive_v1.md`; `judge_supported_v1` is kept, and switching back is one line in `src/prompts.py`). Each reply is JSON with the evidence before the verdict (`PASS`, `FAIL` or `UNKNOWN`); an unparseable reply or a failed call is a judge error, never a pass. The judge is called only for an answer given where an answer was expected, never for a Refusal or Out of scope. The evaluation command refuses to run without it; runs stored before the judge existed show the judge rates as "not measured".

### Judge calibration

The judge is checked against our own labels (#8):

```bash
python src/calibration.py export <run folder> <run folder>   # once: sample, split and labels.md
python src/calibration.py report                             # after labelling: evaluation/calibration/report.md
```

`export` writes `evaluation/calibration/items.json` (the sample and its held-out/tuning split, fixed before labelling) and `labels.md`, one file to read and fill in: for each answer, the question, key facts, answer and cited Section text, then four lines to complete (`Supported:`, `Supported reason:`, `Responsive:`, `Responsive reason:`; PASS or FAIL, or P or F, and one sentence for every FAIL). The judge's verdicts are not in it. One labeller (Gonçalo Augusto) labels. `report` gives, per criterion and per set, the judge's accuracy, Cohen's kappa, TPR and TNR (PASS is the positive class), the items where the judge and the labels differ, and the FAIL reasons for the failure taxonomy. Below 80% accuracy on the held-out set, the judge prompt gets a new version, revised on the tuning set only.

Case file fields: `id`, `type` (`in_material`, `near_miss`, `overlap`, `out_of_scope`, `refusal`), `question`, `accepted_courses` (`["OUT_OF_SCOPE"]` for Out of scope cases), `expected_sections`, `expect_refusal`, `key_facts`. `evaluation/sample_cases.json` is a small synthetic SAMPLE for trying the command; it is not the Golden Set.

Record every evaluated change, kept or abandoned, in [evaluation/ITERATION_LOG.md](evaluation/ITERATION_LOG.md).

## Test

```bash
python -m unittest discover -s tests -t .
```

The tests use a fake model: no API key and no network needed.
