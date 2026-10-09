# Course Tutor — instructions for the coding assistant

A single-screen Streamlit app: a Router picks the Course for a student question, then a Course Tutor answers from that Course's Course Material and cites Sections like `[PEID-2.3]`. The spec is GitHub issue #1.

Use the vocabulary in [CONTEXT.md](CONTEXT.md) (Course, Course Material, Section, Router, Course Tutor, Refusal, Golden Set, ...) in code, tests, prompts and commits. "Agent" never names a part of the app.

## Layout

- `src/llm.py` — the only place model access is configured, from environment variables `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_JUDGE_MODEL`.
- `src/course_material.py` — loads `data/courses/*.md` into Sections keyed by identifier.
- `src/tutor.py` — `answer_question(question, model)`: the one answer function (Seam A). The screen and the evaluation runner both call it.
- `src/cases.py` — loads case files in the Golden Set format. `src/scoring.py` — metrics as pure functions (Seam B).
- `src/evaluate.py` — the evaluation command: `python src/evaluate.py <case file>` runs each case 3 times, stores runs and `report.md` under `evaluation/runs/`. Log results in `evaluation/ITERATION_LOG.md`.
- `src/app.py` — the screen. `prompts/` — versioned prompt files. `tests/` — standard library `unittest`.
- Run tests: `python -m unittest discover -s tests -t .` (no API key, no network; use fake models).

## Rules

- One screen only: one text box, one button. No login, settings, history or second page.
- Never commit secrets, API keys or the `.env` file. `.env.example` holds names only, never real values.
- Never edit a prompt that has been evaluated. Create the next version (`tutor_v2.md`) and point the code at it.
- Never change the Golden Set or the human labels to move a score.
- Log every evaluated change in the iteration log, including abandoned ones, with its result and reason.
- No copyrighted text in the repository: no lecturer slides, no copied passages. Course Material is the group's own words.
- Golden Set questions never appear in any prompt, not even as examples.
- Course Material in `data/courses/` is frozen. Do not edit it.
- Tests check behaviour through the seams (answer function, scoring functions), not prompt wording or internal helpers.
