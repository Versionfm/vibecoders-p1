# Judge calibration report

- Sample: 28 judged answers from `2026-10-18_020503_golden_set_v1_judge_routed`, `2026-10-18_022123_golden_set_v1_judge_agentic` (seed 8): 13 the judge failed on at least one criterion and 15 it passed on both, so both labels occur. The sample is enriched with the judge's FAILs: the numbers describe this sample, not every answer.
- Split, fixed before labelling: 19 held-out, 9 tuning (used only to revise the judge prompt).
- Labeller: Gonçalo Augusto, alone, without seeing the judge's verdicts. With one labeller there is no agreement between labellers to report.
- Labels: `labels_corrected.md`. Judge: the verdicts stored in the runs.
- PASS is the positive class. TPR: human PASSes the judge passed. TNR: human FAILs the judge caught.

## Judge against the labels: held-out (19 items)

| Criterion | Accuracy | Cohen's kappa | TPR | TNR (human FAILs caught) | Human FAILs | Accuracy >= 80% |
|---|---|---|---|---|---|---|
| Supported | 57.9% | -0.10 | 61.1% | 0.0% | 1 | no |
| Responsive | 84.2% | 0.00 | 84.2% | n/a | 0 | yes |

## Judge against the labels: tuning (9 items)

| Criterion | Accuracy | Cohen's kappa | TPR | TNR (human FAILs caught) | Human FAILs | Accuracy >= 80% |
|---|---|---|---|---|---|---|
| Supported | 55.6% | 0.00 | 55.6% | n/a | 0 | no |
| Responsive | 88.9% | 0.00 | 100.0% | 0.0% | 1 | yes |

## Items where the judge and the labels differ

| Item | Set | Case | Criterion | Label | Judge | Label reason |
|---|---|---|---|---|---|---|
| L01 | tuning | GS-27 | supported | PASS | FAIL | - |
| L02 | tuning | GS-24 | supported | PASS | FAIL | - |
| L05 | held-out | GS-26 | supported | PASS | FAIL | - |
| L06 | held-out | GS-27 | supported | FAIL | PASS | IT answers and at the end it says that it couldn't be found in the material |
| L06 | held-out | GS-27 | responsive | PASS | FAIL | P |
| L07 | held-out | GS-27 | supported | PASS | FAIL | - |
| L11 | held-out | GS-27 | responsive | PASS | FAIL | - |
| L13 | tuning | GS-27 | supported | PASS | FAIL | - |
| L15 | held-out | GS-25 | supported | PASS | FAIL | - |
| L16 | held-out | GS-27 | supported | PASS | FAIL | - |
| L16 | held-out | GS-27 | responsive | PASS | FAIL | - |
| L20 | held-out | GS-24 | supported | PASS | FAIL | - |
| L22 | held-out | GS-26 | supported | PASS | FAIL | - |
| L24 | held-out | GS-24 | supported | PASS | FAIL | - |
| L25 | tuning | GS-02 | responsive | FAIL | PASS | It doesn't actually answer; the content is accurate and related but there's no answer. |
| L26 | tuning | GS-24 | supported | PASS | FAIL | - |

## FAIL reasons (input for the failure taxonomy)

| Item | Case | Criterion | Reason |
|---|---|---|---|
| L06 | GS-27 | supported | IT answers and at the end it says that it couldn't be found in the material |
| L25 | GS-02 | responsive | It doesn't actually answer; the content is accurate and related but there's no answer. |
