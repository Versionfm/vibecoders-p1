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

Options: `--runs 3` (default), `--out evaluation/runs` (default), `--label tutor_v3` (added to the run folder name).
It needs the API key in `.env`, like the app.

Each evaluation writes a folder `evaluation/runs/<date>_<time>[_<label>]/` with:

- `run_1.json`, `run_2.json`, `run_3.json`: timestamp, case file, prompt versions, model names, the metrics of that run and every case's output (routed Course, evidence, answer, citations, Refusal, invalid citations, error);
- `report.md`: each metric as mean and range across the runs, plus a per-case table, ready to paste into the report.

Metrics: routing accuracy (choice within Accepted Courses), recall per class over GAIF, PEID, AITB, DTGS and OUT_OF_SCOPE with its macro average (labelled "macro"), citation correctness, Refusal correctness and Out of scope correctness. End-to-end Success and the Supported and Responsive rates need the LLM judge and are shown as pending until it exists.

Case file fields: `id`, `type` (`in_material`, `near_miss`, `overlap`, `out_of_scope`, `refusal`), `question`, `accepted_courses` (`["OUT_OF_SCOPE"]` for Out of scope cases), `expected_sections`, `expect_refusal`, `key_facts`. `evaluation/sample_cases.json` is a small synthetic SAMPLE for trying the command; it is not the Golden Set.

Record every evaluated change, kept or abandoned, in [evaluation/ITERATION_LOG.md](evaluation/ITERATION_LOG.md).

## Test

```bash
python -m unittest discover -s tests -t .
```

The tests use a fake model: no API key and no network needed.
