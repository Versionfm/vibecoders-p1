# Failure taxonomy

How the Course Tutor fails, in our own words, built from what we read: the 52 failing Traces of the five Golden Set
v1 evaluations (3 Runs each, 36 cases) and the 28 answers labelled by hand for the judge calibration. Each failure is
counted once, in the category of its earliest failing Step or of the labeller's reason. The category names were
drafted by the coding assistant from the labeller's reasons and the failure sheets, for the group to confirm or
rename.

Sources:

| Short name | Evaluation | Failing Traces |
|---|---|---|
| R-code | Routed Tutor, code checks only, 2026-10-14 ([failures](runs/2026-10-14_193513_golden_set_v1_routed/failures.md)) | 3 of 108 |
| A-code | Agentic Tutor, code checks only, 2026-10-14 ([failures](runs/2026-10-14_195710_golden_set_v1_agentic/failures.md)) | 15 of 108 |
| R-j1 | Routed Tutor, judge `judge_supported_v1`, 2026-10-18 ([failures](runs/2026-10-18_020503_golden_set_v1_judge_routed/failures.md)) | 10 of 108 |
| A-j1 | Agentic Tutor, judge `judge_supported_v1`, 2026-10-18 ([failures](runs/2026-10-18_022123_golden_set_v1_judge_agentic/failures.md)) | 16 of 108 |
| **R-j2** | **Routed Tutor, judge `judge_supported_v2` (the app as kept), 2026-10-18** ([failures](runs/2026-10-18_040522_golden_set_v1_judge_v2_routed/failures.md)) | **8 of 108** |
| Labels | 28 answers labelled by hand ([labels](calibration/labels.md)) | 6 labelled FAIL |

## Categories

| # | Category | What happens | Failing Traces (all five) | In the app as kept (R-j2) | Examples |
|---|---|---|---|---|---|
| 1 | **Wrong Course chosen** | The question is routed to (Routed Tutor) or read from (Agentic Tutor) a Course that does not cover it, so the answer is that Course's Refusal. The Router's description of GAIF does not mention the topic of GAIF-1.7 (the ethics and cost of convenience), so "knowledge workers… using AI" reads as AITB. | 15 (R-code 3, A-code 3, R-j1 3, A-j1 3, R-j2 3) | 3 | GS-05 in every evaluation |
| 2 | **Reads a Course too many** | The Agentic Tutor reads the right Course and then another one that is not an Accepted Course, sometimes after a correct answer was already possible. | 11 (A-code 6, A-j1 5) | 0 (Agentic Tutor abandoned) | GS-02, GS-13, GS-15 |
| 3 | **Refuses without reading** | The Agentic Tutor refuses, or calls the question Out of scope, without reading any Course Material, where the Refusal after a Read was expected. | 6 (A-code 6) | 0 | GS-33 (a calculation exercise), GS-35 (licence logistics) |
| 4 | **Answers, then says it is not in the material** | The answer gives what the Section says and then ends with the Refusal sentence or a claim that the material does not cover the question. The labeller: "it answers and at the end it says that it couldn't be found in the material". | 6 (R-j1 3, R-j2 3) + 1 labelled | 3 | GS-27 (labels L06) |
| 5 | **Claim beyond the Section** | One claim adds something the cited Section does not say, or cites a Section that does not hold it: a cause, a number, a framing or the wrong neighbouring Section. | 8 (R-j1 1, A-j1 6, R-j2 1) + labels L18, L20 | 1 | GS-06 ("the prefix is no longer byte-identical"), GS-24 ("six elements"), GS-27 Agentic ("frames this as a governance problem"), GS-28 (Klarna cited to DTGS-3.21, stated in DTGS-3.20) |
| 6 | **Uncited summary sentence** | A lead-in or summary sentence without its own citation ("Short answer: not reliably…"). Failed by `judge_supported_v1` only; the calibration found this too strict, and `judge_supported_v2` passes it when its content is in the cited Sections. A measurement failure, not a tutor failure. | 5 (R-j1 3, A-j1 2) | 0 | GS-24 (Routed), GS-25, GS-26 |
| 7 | **Related but no answer** | The content is accurate and on topic but does not answer what was asked. The labeller: "the content is accurate and related but there's no answer". Not caught by the judge. | labels only (1) | not measured | GS-02 (labels L25) |
| 8 | **Judge timeout** | The judge's call timed out, which fails the Answer Step although the answer was not checked. A measurement failure. | 1 (R-j2 1) | 1 | GS-10 |

Total failing Traces: 52 (categories 1, 2, 3, 4, 5, 6 and 8). In the app as kept (R-j2) the 8 failing Traces split
into wrong Course (3), answers then says it is not in the material (3), claim beyond the Section (1) and judge
timeout (1).

## Style notes (not failures: neither the code checks nor the judge measure them)

From the labeller's reasons on the 28 labelled answers:

- **Over-explains and names the Course**: "overexplains and shouldn't mention the course name" (GS-27, labels L01,
  L07).
- **Reports the material instead of answering**: "it should build an answer, not saying the material says x y z"
  (GS-28, labels L18).
- **Splits one answer in two**: "should write a full answer and not split into two answers" (GS-24, labels L20).

## What this points at

- Category 1 is one case, the same in every evaluation: a gap in the Router's Course Description, the candidate
  change `router_v3` (not made).
- Categories 2 and 3 are why the Agentic Tutor was abandoned (#17).
- Categories 4 and 5 and the style notes are about the Course Tutor's answers: a candidate `tutor_v3` that answers
  directly, never ends an answer with the Refusal sentence, and does not name the Course (not made).
- Categories 6 and 8 are about the measurement, not the tutor.
