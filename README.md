# Course Tutor

A single-screen tutor for four Courses (GAIF, PEID, AITB, DTGS). A Router picks the Course for your question, and the Course Tutor answers only from that Course's Course Material, citing the Section behind every claim (e.g. `[PEID-2.3]`). Vocabulary: [CONTEXT.md](CONTEXT.md).

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows; use .venv/bin/python elsewhere
```

## Add your API key locally

The key goes in a local `.env` file, which Git ignores.

1. Copy the example file: `cp .env.example .env`
2. Open `.env` and paste your NVIDIA API key after `LLM_API_KEY=`. The base URL (`https://integrate.api.nvidia.com/v1`) and app model are already the defaults.
3. Do not rename the file and do not put the key anywhere else (code, notes, chat, issues).
4. `git status` must **not** list `.env`.

Never commit `.env` or paste the key into any committed file.

Other settings in `.env` (all optional):

- `LLM_THINKING`: `on` or `off` (default `off`). Switches the app model's reasoning ("thinking") mode, sent as
  `chat_template_kwargs.enable_thinking`. Off is much faster on Nemotron (a Router call took about 2 s instead of
  about 22 s). Every answer and every stored evaluation run records the setting, so both can be compared.
- `LLM_BASE_URL`, `LLM_MODEL`: endpoint and app model (defaults above). `LLM_JUDGE_MODEL`: the LLM judge (later).

Each model call times out after 60 s and is retried at most once, so one call fails after about 2 minutes at worst
and the screen then asks you to try again.

## Run

```bash
streamlit run src/app.py
```

## Evaluate

One command runs a case file (JSON, in the Golden Set format) through the same answer function the screen uses, three times:

```bash
python src/evaluate.py evaluation/sample_cases.json
```

Options: `--runs 3` (default), `--out evaluation/runs` (default), `--label tutor_v3` (added to the run folder name),
`--workers 4` (cases answered in parallel within a run; default 1, keep it small because of the endpoint's rate limit).
It needs the API key in `.env`, like the app. Each run is stored as soon as it finishes, so stopping the command
keeps the runs already completed (the report is written at the end).

Each evaluation writes a folder `evaluation/runs/<date>_<time>[_<label>]/` with:

- `run_1.json`, `run_2.json`, `run_3.json`: timestamp, tutor (`routed`), case file, prompt versions, model names, the metrics of that run and every case's output (routed Course, evidence, answer, citations, Refusal, invalid citations, error), its Trace (`materials_read` in order, `tool_arguments`, `read_count`, `read_limit_hit`) and its `steps` (Search, Path and Answer verdicts with reasons, End-to-end Success, earliest failing Step);
- `report.md`: the Step matrix (pass rate per Step and End-to-end Success as mean and range across the runs; per case each Step as e.g. `3/3` with the earliest failing Step), each metric as mean and range, plus a per-case table, ready to paste into the report;
- `report.html`: the same Runs as one self-contained page (no JavaScript, no external files; opens offline and follows the browser's light or dark theme). It shows End-to-end Success as the headline (mean and range, with tutor, model, prompt versions and case file), a pass-rate bar per Step, the Answer Step rate ("the number you would have reported") next to End-to-end Success ("the number that matters"), how many failing Traces first fail at each Step, one example Trace per failure pattern (earliest failing Step plus reason) with a "what went wrong" note, and every Trace in a collapsible section. Its rates are computed from the stored `run_N.json` files by `src/html_report.py`, never typed in.

Every Trace is scored by three Steps, checked in this order (see [ADR 0002](docs/adr/0002-trace-steps-and-html-report.md)):

- **Search Step:** at least one Accepted Course and no other Course chosen or read; none for an Out of scope case. For the Routed Tutor the routed Course is the Course Material read. Recall and extra Reads are recorded.
- **Path Step:** fails on a failed model call or an invalid Router reply, a `read_file` argument that is not a Course, a Course Material read twice, the Read limit reached, or an in-scope answer or Refusal with no Read.
- **Answer Step:** cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope. Code checks only until the LLM judge adds Supported and Responsive.
- **End-to-end Success:** the Trace passes all three Steps. It is the headline number.

Metrics kept from before: routing accuracy (choice within Accepted Courses), recall per class over GAIF, PEID, AITB, DTGS and OUT_OF_SCOPE with its macro average (labelled "macro"), citation correctness, Refusal correctness and Out of scope correctness. The Supported and Responsive rates need the LLM judge and are shown as pending until it exists.

Case file fields: `id`, `type` (`in_material`, `near_miss`, `overlap`, `out_of_scope`, `refusal`), `question`, `accepted_courses` (`["OUT_OF_SCOPE"]` for Out of scope cases), `expected_sections`, `expect_refusal`, `key_facts`. `evaluation/sample_cases.json` is a small synthetic SAMPLE for trying the command; it is not the Golden Set.

Record every evaluated change, kept or abandoned, in [evaluation/ITERATION_LOG.md](evaluation/ITERATION_LOG.md).

## Test

```bash
python -m unittest discover -s tests -t .
```

The tests use a fake model: no API key and no network needed.
