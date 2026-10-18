# Course Tutor — instructions for the coding assistant

A single-screen Streamlit app: a Router picks the Course for a student question, then a Course Tutor answers from that Course's Course Material and cites Sections like `[PEID-2.3]`. The spec is GitHub issue #1.

Use the vocabulary in [CONTEXT.md](CONTEXT.md) (Course, Course Material, Section, Router, Course Tutor, Refusal, Golden Set, ...) in code, tests, prompts and commits. "Agent" never names a part of the app.

## Layout

- `src/llm.py` — the only place model access is configured, from environment variables `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` (all three required, no defaults; providers listed in `.env.example`), `LLM_JUDGE_MODEL` (with optional `LLM_JUDGE_BASE_URL`, `LLM_JUDGE_API_KEY`, `LLM_JUDGE_THINKING`; `get_judge_model()` is None when unset). `chat(messages, temperature, tools=None)` offers tools and returns a `ModelReply` (text plus `ToolCall`s); `complete` returns text only.
- `src/course_material.py` — loads `data/courses/*.md` into Sections keyed by identifier.
- `src/tutor.py` — `answer_question(question, model, materials=None, tutor="routed"|"agentic")` (`materials`: Course Material by code, loaded from `data/courses/` when None): the one answer function (Seam A). The screen and the evaluation runner both call it. The Routed Tutor (default) is Router then Course Tutor (`router_v2`, `tutor_v2`). The Agentic Tutor (ADR 0001, prompt `agentic_tutor_v1`) is a plain Python loop, no framework: offer `read_file(course)` (enum of the four codes, returns that whole Course Material), feed each tool result back, stop at a reply with no tool calls or after four Reads (then one last call with tools off). A citation is valid only if its Course Material was read.
- `src/cases.py` — loads case files in the Golden Set format. `src/scoring.py` — metrics as pure functions (Seam B), including the Steps: `search_step`, `path_step`, `answer_step` and `score_trace` (End-to-end Success = passes Search, Path and Answer; the earliest failing Step is checked in that order, except that a failed model call or invalid Router reply is filed under Path). Steps read the Trace fields of the answer result: `tutor`, `materials_read`, `read_arguments`, `read_count`, `read_limit_hit`.
- `src/judge.py` — the LLM judge: `judge_answer(case, result, judge, materials)` makes one call per criterion (Supported, Responsive; prompts `judge_supported_v1`, `judge_responsive_v1`) and returns a `Judgement`; a failed call or unparseable reply is `ERROR`, never a pass. `scoring.answer_step` takes the `Judgement`; `needs_judge` says when the judge is called (an expected answer that was given, never a Refusal or Out of scope).
- `src/evaluate.py` — the evaluation command: `python src/evaluate.py <case file>` runs each case 3 times, stores runs, `report.md` and `report.html` under `evaluation/runs/`; `--tutor agentic` runs the Agentic Tutor; the judge runs whenever `LLM_JUDGE_MODEL` is set (`--no-judge` to skip it). Log results in `evaluation/ITERATION_LOG.md`.
- `src/calibration.py` — judge calibration (#8): `export` draws a fixed sample of judged answers and a held-out/tuning split into `evaluation/calibration/` (sheet without the judge's verdicts, one label file per labeller); `report` compares the agreed labels with the judge (`agreement`: accuracy, Cohen's kappa, TPR, TNR; pure). Never edit `items.json` or the labels to move a number.
- `src/html_report.py` — `render_html_report(runs, cases)`: `report.html` from the stored Runs (pure). `src/compare.py` — `python src/compare.py <run folder A> <run folder B>` writes `compare.html`.
- `src/app.py` — the screen; `src/screen.py` — its testable part (guarded answer call, `$` escaping, the `TUTOR` setting: `routed` by default or `agentic`), no Streamlit import. `prompts/` — versioned prompt files. `tests/` — standard library `unittest`.
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
