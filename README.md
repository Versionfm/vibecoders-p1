# Course Tutor

A one-screen Streamlit tutor that answers students' questions using only the group's Course Material and cites
the Sections behind its claims, such as `[PEID-2.3]`.

| Course | Name |
| --- | --- |
| GAIF | Generative AI Foundations |
| PEID | Prompt Engineering and Interaction Design |
| AITB | AI Tools for Business Professionals |
| DTGS | Digital Transformation and Generative AI Strategy |

The chosen teaching experience is the **Agentic Tutor chat**: one model reads the Course Materials it needs through
`read_file(course)` and uses conversation context for follow-up questions. The **Routed Tutor** remains available
for comparison: a Router picks one Course, then the Course Tutor answers from its Course Material.

We chose the chat to support conversation and clarification, despite its lower single-question End-to-end Success
in the original comparison. Improved learning has not been measured. The current prompt, `agentic_tutor_v3`, was
evaluated and kept on 20 October 2026; see [evaluation results and limits](#evaluation-results-and-limits) for the
version-specific evidence and [ADR 0003](docs/adr/0003-keep-agentic-chat-for-teaching.md) for the teaching decision.

## Project materials

- [Actual working prompt: `agentic_tutor_v3`](prompts/agentic_tutor_v3.md)
- [Course Material](data/courses/) and [shared vocabulary](CONTEXT.md)
- [Golden Set v1](evaluation/golden_set.json), [failure taxonomy](evaluation/FAILURE_TAXONOMY.md) and
  [iteration log](evaluation/ITERATION_LOG.md)
- [Report source material and app screenshots](report/README.md)
- [Editable presentation](https://docs.google.com/presentation/d/19HXoCDeYyv_cvhhZVjpvb6L0LsbZk2xzInvGO-6YdTk/edit)

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows; use .venv/bin/python elsewhere
```

Activate the virtual environment before using the commands below:

```bash
source .venv/bin/activate              # Linux / macOS
```

```powershell
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
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
TUTOR=agentic python -m streamlit run src/app.py
```

On Windows PowerShell:

```powershell
$env:TUTOR = "agentic"
python -m streamlit run src/app.py
```

Alternatively, set `TUTOR=agentic` in `.env` and run `python -m streamlit run src/app.py`. For the Routed Tutor comparison,
set `TUTOR=routed`. The chat keeps prior questions and answers in the browser
session and sends them with each follow-up. Each answer reads its own Course Material; prior
answers are conversation context, not source material. **New conversation** clears the history.

Both tutor screens consolidate standalone Section markers under **Cited Sections** instead of repeating them
beside each claim. Invalid citations still appear in the footer and warning. Only the displayed answer is cleaned:
follow-up context, evaluation, saved Traces and reports retain the original cited answer, so the Golden Set and
judge criteria are unchanged. The display formatting has not been evaluated for readability or learning.

## Working prompt

The [full system prompt](prompts/agentic_tutor_v3.md) is the actual text loaded by
[src/agentic.py](src/agentic.py), with its version selected in [src/prompts.py](src/prompts.py). It is separate
from the instructions used to steer Claude Code during development.

Its structure is:

1. **Role:** a university tutor that answers using only the four Courses' Course Material.
2. **Course boundaries:** a Covers and Does not cover description for each Course.
3. **Purpose and scope:** decide scope from the request's meaning and conversation context before any Read.
4. **Reading:** read the relevant Course Material; read a second Course only for genuine overlap.
5. **Answering and Refusal:** use only facts from the material, cite every claim, keep the answer concise, and use
   the fixed Refusal for uncovered questions, new calculation exercises or Course logistics.

Two verbatim instructions from the prompt:

> Earlier answers help interpret a follow-up; they are not Course Material or evidence for the new answer.

> Use only facts stated in the Course Material you read. Do not add anything from general knowledge.

Evaluated prompt files are kept unchanged; a revision gets a new version. The Routed Tutor uses
[router_v2](prompts/router_v2.md) and [tutor_v2](prompts/tutor_v2.md).

## How we steered Claude Code

| Artifact | Purpose |
| --- | --- |
| [CLAUDE.md](CLAUDE.md) | Gives Claude Code the project context, conventions and rules to follow. |
| [Evaluation skill](.claude/skills/evaluate-course-tutor/SKILL.md) | Defines a repeatable evaluation procedure: three Runs, failure analysis and logged results. |
| [Evaluator agent](.claude/agents/evaluator.md) | Runs the evaluation skill and reports results, with instructions to leave code, prompts and labels unchanged. |

The evaluator is a development sub-agent. The student-facing Agentic Tutor answers Course questions; the LLM judge
checks Supported and Responsive during evaluation. The evaluator follows the skill, writes run evidence and
iteration-log entries, and returns suggested fixes to the main coding session. See
[the workflow record](docs/WORKFLOW_ITERATIONS.md#steering-evidence-2026-10-18) for the documented steering checks
and their limitations.

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
classification. A separate live probe of 12 purpose-boundary cases, repeated three times each, passed **36 of 36**
([probe evidence](evaluation/probes/purpose_boundary_probe.json)). It includes one contextual follow-up case,
repeated three times; it is not a general multi-turn evaluation.

## Evaluation results and limits

Golden Set v1 has **36 human-reviewed cases**: 16 in material, 4 near-miss, 8 overlap, 4 Out of scope and 4 Refusal.
Each evaluation below has three Runs, giving 108 Traces. End-to-end Success requires Search, Path and Answer all
to pass, including the judge's Supported and Responsive verdicts for an expected answer.

| Configuration and measurement | End-to-end Success, mean (range) | Evidence |
| --- | --- | --- |
| Agentic Tutor v3, latest local repeat, 20 October 2026 | **86.1% (80.6% to 88.9%)** | [Report](evaluation/runs/2026-10-20_140231_golden_set_v1_judge_v2_v3_repeat_agentic/report.md), [comparison and limits](evaluation/runs/2026-10-20_140231_golden_set_v1_judge_v2_v3_repeat_agentic/comparison.md) |
| Agentic Tutor v3, initial evaluation, 20 October 2026 | 84.3% (69.4% to 91.7%) | [Report](evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/report.md) |
| Agentic Tutor v1, original teaching-decision comparison, 18 October 2026 | 87.0% (83.3% to 88.9%) | [Report](evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic/report.md) |
| Routed Tutor, original teaching-decision comparison, 18 October 2026 | 92.6% (88.9% to 94.4%) | [Report](evaluation/runs/2026-10-18_040522_golden_set_v1_judge_v2_routed/report.md) |

The latest repeat used the unchanged v3 implementation at `585f47a`, app model `deepseek-flash` with thinking off,
and judge `openai/gpt-oss-20b` with `judge_supported_v2` and `judge_responsive_v1`. Five judge timeouts remain scored
as failures. Search passed 97.2% and Path 100.0%. The previous v3 run had eight judge timeouts; re-judging those
answers gives a **supplementary 91.7%**, not a replacement for its recorded 84.3%. No selective re-judging was used
in the latest repeat. The previous run did not record judge thinking, so its exact flag cannot be verified;
the repeat explicitly used `none`. The change from 84.3% to 86.1% does not establish an implementation improvement.

The original 87.0% versus 92.6% comparison explains the teaching decision; those are historical measurements of
the then-current versions. The current prompt is v3. Golden Set v1 contains isolated questions with no conversation
history, so these results do **not** measure follow-up quality or student learning. The judge was calibrated with
one human labeller and can disagree or time out. Full configurations, failures and decisions are in the
[iteration log](evaluation/ITERATION_LOG.md).

## Evaluate

Configure the app model and `LLM_JUDGE_MODEL` (and the judge's endpoint and key when separate) in `.env` first.
One command runs the Golden Set through the same answer function the screen uses, three times:

```bash
python src/evaluate.py evaluation/golden_set.json --tutor agentic --label agentic_v3 --workers 4
```

For a smoke check only, use `evaluation/sample_cases.json` in place of the Golden Set; sample scores are not
Golden Set results. The evaluation command defaults to the Routed Tutor, so pass `--tutor agentic` explicitly even
when the screen uses `TUTOR=agentic`.

Options: `--runs 3` (default), `--out evaluation/runs` (default), `--label agentic_v3` (added to the run folder name),
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
