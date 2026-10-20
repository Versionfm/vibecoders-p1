# Slide 4 · Failure taxonomy and Golden Set

## Facts: the Golden Set (the dataset)

- **File:** [evaluation/golden_set.json](../evaluation/golden_set.json), version 1, **36 cases, frozen 2026-10-14**,
  unchanged since (`git log` shows one commit, `123d939`). A correction would be a new version, never an edit
  ([CLAUDE.md](../CLAUDE.md), Rules).
- **Each case holds:** the question, its type, the Accepted Courses, the expected Sections, whether a Refusal is
  expected, and key facts (used by the Responsive judge).
- **Five types:**

  | Type | Cases | What it tests |
  | --- | --- | --- |
  | `in_material` | 16 | A question one Course answers |
  | `overlap` | 8 | A question two Courses cover; either is accepted |
  | `near_miss` | 4 | Sounds like one Course, answered only by another (e.g. GS-05: a workplace study that sounds like DTGS but is only in GAIF) |
  | `out_of_scope` | 4 | A subject no Course teaches (e.g. the offside rule in football) |
  | `refusal` | 4 | In a Course's domain but must be refused: a new calculation exercise, Course logistics, or a topic the material does not cover |

- **How it was made:** the coding assistant drafted 36 candidates; the group decided every label. Reviewer 1, Gonçalo
  Augusto, reviewed all 36 against the Course Material; Rodrigo gave a second, non-blind review whose comments changed
  three cases (GS-01, GS-08, GS-15). Decisions, dates and reasons per case are in
  [golden_set_review.md](../evaluation/golden_set_review.md).
- **Guarded by tests:** [tests/test_golden_set.py](../tests/test_golden_set.py) checks the agreed composition, that
  every expected Section exists in its Accepted Course, and that **no Golden Set question appears in any prompt**.
- **Limitations to state:** the candidates were run as pilots before the freeze, so the group had seen how the app
  behaved on them ([ITERATION_LOG, 2026-10-14 pilots](../evaluation/ITERATION_LOG.md)); one full reviewer and a
  non-blind second review, so no agreement score for the Golden Set labels; 36 single questions, no conversation.

## Facts: the failure taxonomy

- **File:** [evaluation/FAILURE_TAXONOMY.md](../evaluation/FAILURE_TAXONOMY.md). Built from what we read: the **52
  failing Traces** of five Golden Set evaluations (3 Runs × 36 cases each) and the **28 answers labelled by hand** for the
  judge calibration. Each failure counted once.
- **The names were drafted by the coding assistant** from the labeller's reasons, for the group to confirm or rename.
  The brief wants them in our own words: **an open item**.
- **The eight categories:**

  | # | Category | Failing Traces (five evaluations) | Example |
  | --- | --- | --- | --- |
  | 1 | Wrong Course chosen | 15 | GS-05 in every evaluation: a GAIF question read or routed as AITB |
  | 2 | Reads a Course too many | 11 | GS-02, GS-13, GS-15: the Agentic Tutor reads the right Course, then another |
  | 3 | Refuses without reading | 6 | GS-33 (calculation exercise), GS-35 (licence logistics) |
  | 4 | Answers, then says it is not in the material | 6 + 1 labelled | GS-27: answers, then ends with the Refusal sentence |
  | 5 | Claim beyond the Section | 8 + 2 labelled | GS-24 "six elements", not in the cited Section |
  | 6 | Uncited summary sentence | 5 | A measurement failure: only `judge_supported_v1` failed these |
  | 7 | Related but no answer | labels only (1) | GS-02: accurate, on topic, does not answer |
  | 8 | Judge timeout | 1 | GS-10: a judge call timed out |

- **Style notes from the labeller** (not failures, nothing measures them): over-explains and names the Course;
  reports what "the material says" instead of answering; splits one answer in two.
- **In the app as it is now** (Agentic Tutor with the read-first guard, run
  [2026-10-19_205545](../evaluation/runs/2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic/failures.md)):
  16 failing Traces of 108, in 7 cases: **2 Reads a Course too many 6** (GS-02 3/3, GS-15 3/3); **1 Wrong Course
  chosen 3** (GS-05 3/3); **5 Claim beyond the Section 6** (GS-06 1, GS-24 2, GS-27 2, GS-28 1); **7 Related but no
  answer 1** (GS-27). This run is newer than the taxonomy file; its failures all fit the existing categories.
- **What it points at:** category 1 is one gap in the Courses' "Covers" descriptions (GAIF does not mention the topic
  of GAIF-1.7); category 2 is the Agentic Tutor's main cost (slide 5); categories 4, 5 and the style notes point at a
  next tutor prompt that answers directly; categories 6 and 8 are measurement, not tutor, failures.

## Slide

- **Golden Set v1:** 36 questions, frozen before any score: 16 in-material, 8 overlap, 4 near-miss, 4 out-of-scope,
  4 must-refuse
- Labels decided by the group (2 reviewers), drafted by the assistant, never edited after the freeze
- **Taxonomy** from 52 failing Traces + 28 hand-labelled answers: 8 categories
- Top three: wrong Course (15) · reads a Course too many (11) · claim beyond the Section (8)
- In the app now: 16 of 108 Traces fail: extra Course Read 6 · claim beyond the Section 6 · wrong Course 3 · no answer 1

## Report paragraph (draft)

> Our dataset is Golden Set v1: 36 questions with their labels, committed and frozen on 14 October before any score
> was computed on it. Sixteen are answered by one Course, eight by either of two Courses, four are near-misses that
> sound like one Course but are answered only by another, four are about subjects none of the Courses teaches, and four
> must be refused (a new calculation exercise, Course logistics, an uncovered topic). Each case lists the Accepted
> Courses, the expected Sections and key facts. The coding assistant drafted candidate questions; the group decided
> every label, with one reviewer going through all 36 against the Course Material and a second commenting on three.
> To name how the tutor fails, we read the 52 failing Traces of five evaluations and labelled 28 answers by hand. We
> grouped them into eight categories: the most frequent are choosing the wrong Course (15 Traces, one question in
> every run), reading a Course too many (11) and a claim that goes beyond the cited Section (8). Two categories turned
> out to be failures of the measurement rather than the tutor: a judge too strict about summary sentences, and a judge
> call that timed out.

## Sources

[golden_set.json](../evaluation/golden_set.json) · [golden_set_review.md](../evaluation/golden_set_review.md) ·
[FAILURE_TAXONOMY.md](../evaluation/FAILURE_TAXONOMY.md) · [CONTEXT.md](../CONTEXT.md) (case types) ·
[latest failure sheet](../evaluation/runs/2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic/failures.md)
