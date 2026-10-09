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
