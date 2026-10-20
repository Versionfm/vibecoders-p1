# Slide 5 · Our number

## The number

**End-to-end Success 84.3% (69.4% to 91.7% across 3 Runs)**: the Agentic Tutor as the app runs it now
(`agentic_tutor_v3` with the purpose boundary and scope-aware recovery), on Golden Set v1, 36 cases × 3 Runs = 108
Traces, judged by the calibrated judge. Source:
[report.md](../evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/report.md) of run
`2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic` (commit `b40bb5d`).

**Read it with its caveat:** 8 judge calls timed out (7 in Run 1, 1 in Run 2), and a judge error fails the Answer
Step, so Run 1 scored 69.4% while Runs 2 and 3 scored 91.7% each. Judged again with the same judge, all 8 pass:
**91.7% (88.9% to 94.4%)**. That figure is supplementary; the stored Runs are unchanged
([rejudged_judge_errors.json](../evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/rejudged_judge_errors.json)).
Quote 84.3% as the recorded number and 91.7% only with "after re-judging the 8 timed-out judge calls".

## Facts

- **What End-to-end Success means:** a Trace passes all three Steps, checked in this order
  ([src/scoring.py](../src/scoring.py), [ADR 0002](../docs/adr/0002-trace-steps-and-html-report.md)):
  - **Search:** it read at least one Accepted Course and no other (none for an Out of scope case);
  - **Path:** no failed model call, no bad `read_file` argument, no Course read twice, within the Read limit, no
    in-scope answer without a Read;
  - **Answer:** it cites an expected Section and only valid Sections (or gives the expected Refusal or Out of scope),
    **and** the LLM judge finds the answer Supported and Responsive.
- **Why this metric:** a student is helped only when everything is right at once: the right material, a clean path, and
  an answer that is grounded and on point. An answer that is correct after reading a wrong extra Course still fails,
  because grounding is the product. It is one number, but each failure is filed under its earliest failing Step, so it
  stays diagnosable. The same strictness counts a judge timeout as a failure, which is why this run's caveat exists.
- **Code checks for everything with a right answer; the judge only for what code cannot check** (whether each claim is
  in its cited Section, and whether the answer addresses the question). Every case runs 3 times, because the model is
  sampled: we report mean and range, never one run.
- **Step rates, this run** (mean, range):

  | Step or metric | Mean | Range |
  | --- | --- | --- |
  | Search Step | 97.2% | 97.2% to 97.2% |
  | Path Step | 100.0% | 100.0% to 100.0% |
  | Answer Step | 84.3% | 69.4% to 91.7% |
  | **End-to-end Success** | **84.3%** | **69.4% to 91.7%** |
  | Supported rate (judge) | 87.7% | 74.1% to 96.3% |
  | Responsive rate (judge) | 95.1% | 88.9% to 100.0% |
  | Judge undecided rate (timeouts) | 4.9% | 0.0% to 13.0% |
  | Routing accuracy | 97.2% | 97.2% to 97.2% |
  | Citation, Refusal and Out of scope correctness | 100.0% | 100.0% to 100.0% |

- **Context, the same Golden Set, model and judge:**

  | Configuration | End-to-end Success, mean (range) | Search Step | Source |
  | --- | --- | --- | --- |
  | **Agentic Tutor v3, purpose boundary (the app now)** | **84.3% (69.4% to 91.7%)**; 91.7% (88.9% to 94.4%) with the 8 timed-out judge calls re-judged | 97.2% | [run 2026-10-20](../evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/report.md) |
  | Agentic Tutor v1, read-first guard | 85.2% (83.3% to 86.1%) | 91.7% | [run 2026-10-19](../evaluation/runs/2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic/report.md) |
  | Agentic Tutor v1 before the guard | 87.0% (83.3% to 88.9%) | 91.7% | [run 2026-10-18](../evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic/report.md) |
  | Routed Tutor (Router + Course Tutor) | 92.6% (88.9% to 94.4%) | 97.2% | [run 2026-10-18](../evaluation/runs/2026-10-18_040522_golden_set_v1_judge_v2_routed/report.md) |

  What changed with v3: the extra Course Reads that made the Agentic Tutor trail the Routed Tutor are gone (GS-02 and
  GS-15 failed 3/3 before, 0/3 now), so its Search Step now equals the Routed Tutor's 97.2%. Claims beyond the cited
  Section stayed at 6 Traces, on partly different cases; GS-05 still reads the wrong Course in every run. The Routed
  Tutor's 92.6% also counts one judge timeout as a failure and was not re-judged.
- **The purpose boundary, checked with the live model** (not part of the Golden Set): 12 cases, 3 times each, through
  the app's answer function: **36 of 36 passed**. "Who are you?", greetings and unrelated requests gave Out of scope
  with no Read; Course questions about models and tools, a greeting plus a Course question, and a follow-up ("Can you
  explain that more simply?") read the right Course and gave cited answers
  ([probe](../evaluation/probes/purpose_boundary_probe.json)).
- **The judge is checked against our hand labels** (28 answers labelled by one labeller who did not see the judge's
  verdicts; 19 held out, 9 used to revise the prompt). PASS is the positive class. Held-out, `judge_supported_v2`
  ([calibration report](../evaluation/calibration/report_first_labels_judge_v2.md)):

  | Criterion | Accuracy | Cohen's kappa | TPR | TNR |
  | --- | --- | --- | --- | --- |
  | Supported | 84.2% | 0.56 | 86.7% | 75.0% (3 of 4 human FAILs caught) |
  | Responsive | 84.2% | 0.00 | 84.2% | not measurable (no human FAIL) |

  With `judge_supported_v1` Supported was 63.2% accurate (kappa 0.13); the revised prompt passes the 80% threshold.
  The judge model, prompts and criteria did not change for v3, so no new calibration was needed.
- **What the number does not cover:**
  - **Conversation and learning:** every Golden Set case is a single question with no chat history, so follow-ups,
    clarification and whether students learn are not measured; the follow-up probe is one case, three times. That is
    what we chose the chat for (ADR 0003).
  - **Size:** 36 cases and 3 Runs; one case is about 2.8 points of one Run.
  - **The judge:** calibrated with one labeller on 28 answers from 15 questions; the held-out disagreements were seen
    when v2 was written; Responsive never met a human FAIL; and its endpoint can time out, as in Run 1.
  - **The model can drift:** the same prompts and model name gave different Agentic failures four days apart, so a run
    is a sample of the model on that day ([ITERATION_LOG, 2026-10-18](../evaluation/ITERATION_LOG.md)).
  - **Latency** is not recorded in the Traces.

## Slide

- **84.3%** End-to-end Success (69.4%–91.7%), 108 Traces; Run 1 lost 7 Traces to judge timeouts. Re-judged: **91.7%**
- Search Step 97.2%: the extra Course Reads are gone; re-judged, it is within one case per Run of the Routed Tutor (92.6%)
- Code checks everything with a right answer; an LLM judge only grounding and responsiveness
- Judge vs our labels (held-out): Supported 84.2% accuracy, κ 0.56, TPR 86.7%, TNR 75.0%
- Not measured: conversation, learning, latency; 36 cases, one labeller

## Report paragraph (draft)

> The number we defend is End-to-end Success: the share of Traces that read the right Course and no other, follow a
> clean path, and give an answer that cites the expected Section and that the LLM judge finds both Supported (every
> claim is in its cited Section) and Responsive (it answers what was asked). For the app as it runs now, the Agentic
> Tutor with prompt `agentic_tutor_v3`, it is 84.3% over three Runs of the 36-case Golden Set, with a wide range
> (69.4% to 91.7%) that has a single cause: in the first Run seven calls to the judge timed out, and our metric counts
> a judge error as a failure. The other two Runs scored 91.7% each, and judging the eight timed-out answers again gave
> 91.7% overall. We chose this metric because a student is only helped when all of this holds at once, and because
> each failure is filed under the earliest Step that broke, which keeps it diagnosable; the timeouts show both its
> strictness and that the judge is part of what we measure. Everything with a right answer is checked in code; the
> judge, `openai/gpt-oss-20b`, a different model family from the app's, is used only for grounding and
> responsiveness. On 19 held-out answers we labelled by hand, it agreed with us 84.2% of the time on Supported
> (Cohen's kappa 0.56, TPR 86.7%, TNR 75.0%). The number does not measure conversation, follow-ups or learning: every
> Golden Set case is a single question. It rests on 36 cases, three Runs and one labeller.

## Sources

[run report (app now)](../evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/report.md) ·
[failures](../evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/failures.md) ·
[compare.html](../evaluation/runs/2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic/compare.html) ·
[ITERATION_LOG](../evaluation/ITERATION_LOG.md) · [calibration report](../evaluation/calibration/report_first_labels_judge_v2.md) ·
[purpose-boundary probe](../evaluation/probes/purpose_boundary_probe.json) ·
[src/scoring.py](../src/scoring.py) · [src/judge.py](../src/judge.py) ·
[ADR 0002](../docs/adr/0002-trace-steps-and-html-report.md) · [ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md)
