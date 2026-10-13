---
name: evaluate-course-tutor
description: Run the Course Tutor evaluation on a case file and record the result in the iteration log. Use to set a baseline on the Golden Set, to measure a prompt, model or setting change against the previous run, or to collect failing outputs for the failure taxonomy.
---

# Evaluate the Course Tutor

One evaluation is one configuration, three runs and one iteration log entry. The run folder and the log entry are
the evidence for the report, so a run that went badly is kept and logged like any other. Vocabulary (Golden Set,
Accepted Courses, Refusal, ...) is in [CONTEXT.md](../../../CONTEXT.md); each metric is defined at the end of the
`report.md` the run writes.

## Steps

### 1. Pin the configuration

Write down, before running anything:

- **Case file**: the frozen Golden Set file, or `evaluation/sample_cases.json` for a smoke check only. Sample scores
  mean nothing: a smoke check is reported as "the command works" and never logged as a result.
- **Prompt versions**: Router and Course Tutor, from `src/prompts.py`.
- **App model and thinking**: `LLM_MODEL` and `LLM_THINKING` from `.env`, defaults in `src/llm.py`. Read only these
  two names; the API key stays in `.env`.
- **Commit**: `git rev-parse --short HEAD`. If `git status` shows changes under `src/` or `prompts/`, ask the user to
  commit them first: an uncommitted configuration cannot be traced later.
- **The change being measured**, in one sentence, and the **previous entry** in
  [evaluation/ITERATION_LOG.md](../../../evaluation/ITERATION_LOG.md) on the same case file that it is compared
  against (none for a baseline).

Then run the tests with the project's virtual environment (README, Setup): `python -m unittest discover -s tests -t .`

Done when every item above has a value and the tests pass.

### 2. Run

```bash
python src/evaluate.py <case file> --label <short-change-name>
```

Use labels like `baseline` or `router_v2`. Keep `--workers` between 1 and 4: the endpoint is rate limited.

Done when the run folder printed at the end holds `run_1.json`, `run_2.json`, `run_3.json` and `report.md`. If the
command stops early, the runs already stored remain: record how many finished and carry on with those.

### 3. Read the results

- From `report.md`: the mean and range of every metric, set against the previous entry as before → after.
- End-to-end Success, Supported rate and Responsive rate stay `pending` until the LLM judge exists. Report them as
  pending.
- A case **fails** in a run when it is routed outside its Accepted Courses, cites no expected Section or an invalid
  one where an answer was expected, misses an expected Refusal, refuses where an answer was expected, or errors.
  For every case that fails in at least one run, open its output in each `run_N.json`: routed Course, cited
  Sections, answer text, Refusal, error.

Done when every metric is listed as before → after (or as baseline) and every failing case is named with its count,
for example "GS-14 failed in 2/3 runs".

### 4. Write the failure sheet

Write `failures.md` in the run folder, one row per failing case: case id, type, question, what was expected
(Accepted Courses, expected Sections or Refusal) and what happened in each run (routed Course, cited Sections, the
first sentence of the answer, error).

Describe what happened in observable facts; the group names the failures. The failure taxonomy has to be in the
group's own words (Project Brief, evaluation requirement). When `evaluation/FAILURE_TAXONOMY.md` exists, add a
column with the matching category from it, and mark a case that fits none as `unnamed`.

Done when every failing case from step 3 has a row.

### 5. Log the result

Append an entry to the end of [evaluation/ITERATION_LOG.md](../../../evaluation/ITERATION_LOG.md) in the format at
the top of that file. Configuration comes from step 1, including the commit; Run folder is the folder from step 2;
Result lists the metrics that moved as mean (range), before → after. Decision is the one the user gave, otherwise
`pending`, with the evidence for keeping and for abandoning in Reason. A correction to an earlier entry is a new
entry.

Done when the entry is appended and names the run folder.

### 6. Report back

Reply with the configuration, the metrics as before → after, the number of failing cases, the run folder and the log
entry, and one sentence on what the numbers do not cover (pending judge metrics, number of cases, three runs).

## Boundaries

An evaluation measures and leaves what it measures unchanged:

- Golden Set files and their labels are frozen. A label changed to move a score invalidates the evaluation.
- `prompts/`, `src/` and `data/courses/` stay as they are. A fix spotted while reading failures goes into the report
  back as a suggested next change.
- Run folders are kept, including bad and interrupted ones: they are the iteration evidence.
