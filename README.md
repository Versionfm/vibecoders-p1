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

## Run

```bash
streamlit run src/app.py
```

## Test

```bash
python -m unittest discover -s tests -t .
```

The tests use a fake model: no API key and no network needed.
