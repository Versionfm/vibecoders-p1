# Judge calibration report

- Sample: 28 judged answers from `2026-10-18_020503_golden_set_v1_judge_routed`, `2026-10-18_022123_golden_set_v1_judge_agentic` (seed 8): 11 the judge failed on at least one criterion and 17 it passed on both, so both labels occur. The sample is enriched with the judge's FAILs: the numbers describe this sample, not every answer.
- Split, fixed before labelling: 19 held-out, 9 tuning (used only to revise the judge prompt).
- Labeller: Gonçalo Augusto, alone, without seeing the judge's verdicts. With one labeller there is no agreement between labellers to report.
- Labels: `labels_corrected.md`. Judge: `openai/gpt-oss-20b` with judge_supported_v2, judge_responsive_v1, judged again (`verdicts_judge_supported_v2_judge_responsive_v1.json`).
- PASS is the positive class. TPR: human PASSes the judge passed. TNR: human FAILs the judge caught.

## Judge against the labels: held-out (19 items)

| Criterion | Accuracy | Cohen's kappa | TPR | TNR (human FAILs caught) | Human FAILs | Accuracy >= 80% |
|---|---|---|---|---|---|---|
| Supported | 68.4% | -0.10 | 72.2% | 0.0% | 1 | no |
| Responsive | 84.2% | 0.00 | 84.2% | n/a | 0 | yes |

## Judge against the labels: tuning (9 items)

| Criterion | Accuracy | Cohen's kappa | TPR | TNR (human FAILs caught) | Human FAILs | Accuracy >= 80% |
|---|---|---|---|---|---|---|
| Supported | 66.7% | 0.00 | 66.7% | n/a | 0 | no |
| Responsive | 88.9% | 0.00 | 100.0% | 0.0% | 1 | yes |

## Items where the judge and the labels differ

| Item | Set | Case | Criterion | Label | Judge | Label reason |
|---|---|---|---|---|---|---|
| L02 | tuning | GS-24 | supported | PASS | FAIL | - |
| L06 | held-out | GS-27 | supported | FAIL | PASS | IT answers and at the end it says that it couldn't be found in the material |
| L06 | held-out | GS-27 | responsive | PASS | FAIL | P |
| L07 | held-out | GS-27 | supported | PASS | FAIL | - |
| L10 | held-out | GS-10 | supported | PASS | ERROR | - |
| L11 | held-out | GS-27 | responsive | PASS | FAIL | - |
| L13 | tuning | GS-27 | supported | PASS | FAIL | - |
| L16 | held-out | GS-27 | responsive | PASS | FAIL | - |
| L18 | held-out | GS-28 | supported | PASS | FAIL | - |
| L20 | held-out | GS-24 | supported | PASS | FAIL | - |
| L24 | held-out | GS-24 | supported | PASS | FAIL | - |
| L25 | tuning | GS-02 | responsive | FAIL | PASS | It doesn't actually answer; the content is accurate and related but there's no answer. |
| L26 | tuning | GS-24 | supported | PASS | FAIL | - |

## FAIL reasons (input for the failure taxonomy)

| Item | Case | Criterion | Reason |
|---|---|---|---|
| L06 | GS-27 | supported | IT answers and at the end it says that it couldn't be found in the material |
| L25 | GS-02 | responsive | It doesn't actually answer; the content is accurate and related but there's no answer. |
