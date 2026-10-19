# Slide 5 · Our number

## The number

**End-to-end Success 85.2% (83.3% to 86.1% across 3 Runs)**: the Agentic Tutor as the app runs it now (with the
read-first guard), on Golden Set v1, 36 cases × 3 Runs = 108 Traces, judged by the calibrated judge.
Source: [report.md](../evaluation/runs/2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic/report.md) of run
`2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic` (commit `5ae0257`).

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
  stays diagnosable.
- **Code checks for everything with a right answer; the judge only for what code cannot check** (whether each claim is
  in its cited Section, and whether the answer addresses the question). Every case runs 3 times, because the model is
  sampled: we report mean and range, never one run.
- **Step rates, this run** (mean, range):

  | Step or metric | Mean | Range |
  | --- | --- | --- |
  | Search Step | 91.7% | 91.7% to 91.7% |
  | Path Step | 100.0% | 100.0% to 100.0% |
  | Answer Step | 90.7% | 88.9% to 91.7% |
  | **End-to-end Success** | **85.2%** | **83.3% to 86.1%** |
  | Supported rate (judge) | 92.6% | 88.9% to 96.3% |
  | Responsive rate (judge) | 98.8% | 96.3% to 100.0% |
  | Routing accuracy | 94.4% | 94.4% to 94.4% |
  | Citation, Refusal and Out of scope correctness | 100.0% | 100.0% to 100.0% |

- **Context, the same Golden Set, model and judge:**

  | Configuration | End-to-end Success, mean (range) | Source |
  | --- | --- | --- |
  | **Agentic Tutor, read-first guard (the app now)** | **85.2% (83.3% to 86.1%)** | [run 2026-10-19](../evaluation/runs/2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic/report.md) |
  | Agentic Tutor before the guard | 87.0% (83.3% to 88.9%) | [run 2026-10-18](../evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic/report.md) |
  | Routed Tutor (Router + Course Tutor) | 92.6% (88.9% to 94.4%) | [run 2026-10-18](../evaluation/runs/2026-10-18_040522_golden_set_v1_judge_v2_routed/report.md) |

  The guard changed nothing on single questions: no in-scope answer came without a Read in either Agentic run, so
  87.0% → 85.2% is run-to-run variation (the ranges overlap). The gap to the Routed Tutor is mostly the Search Step: 6
  of 16 failing Traces read an extra Course that is not Accepted, which a Router rules out by choosing one Course.
- **The judge is checked against our hand labels** (28 answers labelled by one labeller who did not see the judge's
  verdicts; 19 held out, 9 used to revise the prompt). PASS is the positive class. Held-out, `judge_supported_v2`
  ([calibration report](../evaluation/calibration/report_first_labels_judge_v2.md)):

  | Criterion | Accuracy | Cohen's kappa | TPR | TNR |
  | --- | --- | --- | --- | --- |
  | Supported | 84.2% | 0.56 | 86.7% | 75.0% (3 of 4 human FAILs caught) |
  | Responsive | 84.2% | 0.00 | 84.2% | not measurable (no human FAIL) |

  With `judge_supported_v1` Supported was 63.2% accurate (kappa 0.13); the revised prompt passes the 80% threshold.
- **What the number does not cover:**
  - **Conversation and learning:** every case is a single question with no chat history, so follow-ups, clarification
    and whether students learn are not measured. That is exactly what we chose the chat for (ADR 0003).
  - **Size:** 36 cases and 3 Runs; one case is about 2.8 points of one Run.
  - **The judge:** calibrated with one labeller on 28 answers from 15 questions; the held-out disagreements were seen
    when v2 was written; Responsive never met a human FAIL, so its ability to catch an off-point answer is untested.
  - **The model can drift:** the same prompts and model name gave different Agentic failures four days apart, so a run
    is a sample of the model on that day ([ITERATION_LOG, 2026-10-18](../evaluation/ITERATION_LOG.md)).
  - **Latency** is not recorded in the Traces.

## Slide

- **85.2%** End-to-end Success (83.3%–86.1%), 108 Traces: right Course read, clean path, cited answer judged Supported and Responsive
- Code checks everything with a right answer; an LLM judge only grounding and responsiveness
- Judge vs our labels (held-out): Supported 84.2% accuracy, κ 0.56, TPR 86.7%, TNR 75.0%
- Routed Tutor scores 92.6%; we kept the chat for teaching (gap = extra Course Reads)
- Not measured: conversation, learning, latency; 36 cases, one labeller

## Report paragraph (draft)

> The number we defend is End-to-end Success: the share of Traces that read the right Course and no other, follow a
> clean path, and give an answer that cites the expected Section and that the LLM judge finds both Supported (every
> claim is in its cited Section) and Responsive (it answers what was asked). For the app as it runs now, the Agentic
> Tutor, it is 85.2% over three Runs of the 36-case Golden Set (83.3% to 86.1%). We chose it because a student is
> only helped when all of this holds at once, and because each failure is filed under the earliest Step that broke,
> which keeps it diagnosable. Everything with a right answer is checked in code; the judge, `openai/gpt-oss-20b`, a
> different model family from the app's, is used only for grounding and responsiveness. We checked it against 28
> answers labelled by hand without seeing its verdicts: on the 19 held-out answers, after one prompt revision, it
> agreed with us 84.2% of the time on Supported (Cohen's kappa 0.56, TPR 86.7%, TNR 75.0%). The simpler Routed
> Tutor scores 92.6% under the same conditions; the gap is mostly extra Course Reads, and we accepted it for the
> chat's conversational teaching. The number does not measure conversation, follow-ups or learning: every Golden Set
> case is a single question. It rests on 36 cases, three Runs and one labeller.

## Sources

[run report (app now)](../evaluation/runs/2026-10-19_205545_golden_set_v1_judge_v2_read_first_agentic/report.md) ·
[ITERATION_LOG](../evaluation/ITERATION_LOG.md) · [calibration report](../evaluation/calibration/report_first_labels_judge_v2.md) ·
[src/scoring.py](../src/scoring.py) · [src/judge.py](../src/judge.py) ·
[ADR 0002](../docs/adr/0002-trace-steps-and-html-report.md) · [ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md)
