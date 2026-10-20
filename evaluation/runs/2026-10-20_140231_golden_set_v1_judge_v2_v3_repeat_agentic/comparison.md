# Repeat evaluation comparison

Unchanged merged Agentic Tutor v3, commit `585f47a`; source matches main merge `54e9daf`. App `deepseek-flash` thinking off; judge `openai/gpt-oss-20b` on NVIDIA, thinking `none`, unchanged calibrated prompts and scoring. 216 deterministic tests passed before calls. 3 Runs x 36 cases completed.

Previous recorded evaluation: `2026-10-20_130617_golden_set_v1_judge_v2_purpose_v3_agentic`. Comparison uses its original 84.3%, not the supplementary re-judged 91.7%.

| Metric | Previous mean (range) | This round mean (range) |
|---|---|---|
| Search Step | 97.2% (97.2% to 97.2%) | 97.2% (97.2% to 97.2%) |
| Path Step | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Answer Step | 84.3% (69.4% to 91.7%) | 86.1% (80.6% to 88.9%) |
| End-to-end Success | 84.3% (69.4% to 91.7%) | 86.1% (80.6% to 88.9%) |
| Routing accuracy | 97.2% (97.2% to 97.2%) | 97.2% (97.2% to 97.2%) |
| Recall GAIF | 83.3% (83.3% to 83.3%) | 83.3% (83.3% to 83.3%) |
| Recall PEID | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Recall AITB | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Recall DTGS | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Recall OUT_OF_SCOPE | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Recall (macro average) | 96.7% (96.7% to 96.7%) | 96.7% (96.7% to 96.7%) |
| Citation correctness | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Refusal correctness | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Out of scope correctness | 100.0% (100.0% to 100.0%) | 100.0% (100.0% to 100.0%) |
| Supported rate | 87.7% (74.1% to 96.3%) | 90.1% (88.9% to 92.6%) |
| Responsive rate | 95.1% (88.9% to 100.0%) | 95.1% (88.9% to 100.0%) |
| Judge undecided rate | 4.9% (0.0% to 13.0%) | 3.1% (0.0% to 7.4%) |

15/108 failing Traces in 9 cases; 0 tutor errors; 5 judge ERROR criteria across 5 Traces. No selective re-judging or resampling.

| Case failing in this round | Failures | Earliest failing Steps |
|---|---|---|
| GS-03 | 1/3 | Answer 1 |
| GS-05 | 3/3 | Search 3 |
| GS-10 | 2/3 | Answer 2 |
| GS-11 | 1/3 | Answer 1 |
| GS-15 | 1/3 | Answer 1 |
| GS-16 | 1/3 | Answer 1 |
| GS-21 | 2/3 | Answer 2 |
| GS-27 | 3/3 | Answer 3 |
| GS-28 | 1/3 | Answer 1 |

## Changed case outcomes

| Case | Previous passes | This round passes |
|---|---|---|
| GS-01 | 2/3 | 3/3 |
| GS-03 | 3/3 | 2/3 |
| GS-07 | 2/3 | 3/3 |
| GS-08 | 2/3 | 3/3 |
| GS-10 | 3/3 | 1/3 |
| GS-11 | 1/3 | 2/3 |
| GS-14 | 2/3 | 3/3 |
| GS-15 | 3/3 | 2/3 |
| GS-16 | 3/3 | 2/3 |
| GS-21 | 3/3 | 1/3 |
| GS-23 | 2/3 | 3/3 |
| GS-24 | 2/3 | 3/3 |
| GS-25 | 1/3 | 3/3 |
| GS-26 | 2/3 | 3/3 |
| GS-27 | 1/3 | 0/3 |

## Interpretation

93/108 Traces passed, versus 91/108 previously. The higher recorded result accompanies fewer judge timeouts
(8 -> 5); failures without a judge error changed from 9 to 10. No app or prompt change was measured, and the
previous judge-thinking setting is not recorded. These data do not establish an underlying quality improvement.

The main remaining issues are GS-05's Course choice, extra unsupported claims or citation placement in GS-21,
GS-27 and GS-11, and the GS-10 judge expectation mismatch. See the failure sheet for each actual verdict.

## Limits and evidence

- Both evaluations use the same recorded model names, app thinking, prompts and scoring; provider deployment and sampling may vary.
- Previous Run schema does not store judge thinking. This round explicitly uses none (no switch sent), as documented for the calibrated judge; local unset setting would default off.
- Previous recorded End-to-end Success is 84.3%; its supplementary re-judged 91.7% is not the comparison headline.
- Golden Set v1 has single questions, without conversation history; this round does not measure follow-up quality or learning.
- This is a repeat measurement, not an implementation change or proof of improved quality or learning.
- No new keep/abandon decision was requested: decision pending; the app selection remains unchanged.

[New report](report.md) · [All failures](failures.md) · [Compare](compare.html) · [Configuration](configuration.json) · [Preservation](preservation.json)
