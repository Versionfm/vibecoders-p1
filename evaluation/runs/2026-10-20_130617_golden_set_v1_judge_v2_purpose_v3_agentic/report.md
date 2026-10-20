# Evaluation report, 2026-10-20T13:06:17+00:00

- Case file: `evaluation/golden_set.json` (36 cases: 16 in_material, 4 near_miss, 8 overlap, 4 out_of_scope, 4 refusal)
- Runs: 3 (every case answered once per run)
- App model (Agentic Tutor): `deepseek-flash`. Thinking: off
- Prompt versions: agentic_tutor `agentic_tutor_v3`, judge_supported `judge_supported_v2`, judge_responsive `judge_responsive_v1`
- Judge model: `openai/gpt-oss-20b`. The Answer Step uses the judge.
- Tutor: `agentic`

## Steps

Share of Traces passing each Step, as mean and range (lowest to highest) across the 3 runs.

| Step | Mean | Range | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|
| Search Step | 97.2% | 97.2% to 97.2% | 97.2% | 97.2% | 97.2% |
| Path Step | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Answer Step | 84.3% | 69.4% to 91.7% | 69.4% | 91.7% | 91.7% |
| **End-to-end Success** | 84.3% | 69.4% to 91.7% | 69.4% | 91.7% | 91.7% |

- Search Step: at least one Accepted Course and no other Course chosen or read; none for an Out of scope case. For the Routed Tutor the routed Course is the Course Material read.
- Path Step: no failed model call or invalid Router reply, no `read_file` argument that is not a Course, no Course Material read twice, within the Read limit, and no in-scope answer or Refusal without a Read.
- Answer Step: cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope; an expected answer must also be judged Supported and Responsive by the LLM judge.
- End-to-end Success: the Trace passes all three Steps.

Per case: Traces passing each Step out of the runs, and the earliest failing Step with its reason.

| Case | Type | Search | Path | Answer | End-to-end Success | Earliest failing Step |
|---|---|---|---|---|---|---|
| GS-01 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Responsive: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-02 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-03 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-04 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-05 | near_miss | 0/3 | 3/3 | 0/3 | 0/3 | Search: read AITB, not an Accepted Course (3/3) |
| GS-06 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-07 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-08 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Responsive: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-09 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-10 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-11 | in_material | 3/3 | 3/3 | 1/3 | 1/3 | Answer: judged not Supported: The claim that the course material notes that these reasons should be matched to appropriate responses is not stated in [DTGS-1.5], which only lists the approaches but does not say they are matched to the reasons. (1/3); Answer: judge error on Responsive: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-12 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-13 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-14 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Responsive: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-15 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-16 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-17 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-18 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-19 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-20 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-21 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-22 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-23 | overlap | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judged not Supported: The claim that a comparison is only meaningful with settings fixed is not stated in PEID-1.3, which only says sampling settings change spread but does not assert that comparisons require them fixed. (1/3) |
| GS-24 | overlap | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judged not Supported: The claim that "Format is one of the six elements of a request" is not stated in any cited section; AITB-2.4 discusses format but does not list it as one of six request elements. (1/3) |
| GS-25 | overlap | 3/3 | 3/3 | 1/3 | 1/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3); Answer: judged not Supported: The claim that "the model predicts the next token rather than retrieving facts" is not fully supported: PEID‑1.9 states the model predicts next tokens but does not explicitly say it does not retrieve facts, so the comparison is not present in the cited section. (1/3) |
| GS-26 | overlap | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-27 | overlap | 3/3 | 3/3 | 1/3 | 1/3 | Answer: judged not Supported: The claim that the material frames shadow AI as a control and risk problem rather than a cost problem is not supported by DTGS-3.7, which states that choosing a model involves cost, control, and risk but does not say it is framed as control and risk rather than cost. (1/3); Answer: judged not Supported: The claim that "when staff use generic tools directly, the organisation has little visibility or control over what is done with its data" is unsupported – DTGS‑3.7 mentions low control but does not state that staff use generic tools directly or that this lack of visibility is a consequence. (1/3) |
| GS-28 | overlap | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-29 | out_of_scope | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-30 | out_of_scope | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-31 | out_of_scope | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-32 | out_of_scope | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-33 | refusal | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-34 | refusal | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-35 | refusal | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-36 | refusal | 3/3 | 3/3 | 3/3 | 3/3 | - |

## Metrics

Mean and range (lowest to highest) across the 3 runs. n/a: no cases of that kind in the case file.

| Metric | Mean | Range | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|
| Routing accuracy | 97.2% | 97.2% to 97.2% | 97.2% | 97.2% | 97.2% |
| Recall GAIF | 83.3% | 83.3% to 83.3% | 83.3% | 83.3% | 83.3% |
| Recall PEID | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Recall AITB | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Recall DTGS | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Recall OUT_OF_SCOPE | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| **Recall (macro average)** | 96.7% | 96.7% to 96.7% | 96.7% | 96.7% | 96.7% |
| Citation correctness | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Refusal correctness | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Out of scope correctness | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Supported rate | 87.7% | 74.1% to 96.3% | 74.1% | 96.3% | 92.6% |
| Responsive rate | 95.1% | 88.9% to 100.0% | 88.9% | 96.3% | 100.0% |
| Judge undecided rate | 4.9% | 0.0% to 13.0% | 13.0% | 1.9% | 0.0% |

Definitions:

- Routing accuracy: the Router's choice is one of the case's Accepted Courses.
- Recall per class over the five classes (GAIF, PEID, AITB, DTGS, OUT_OF_SCOPE). A case counts for the routed Course when that is an Accepted Course, otherwise for its first Accepted Course, so an Overlap Case routed to either Accepted Course is a hit. Recall (macro average): the unweighted mean over classes that have cases.
- Citation correctness: of the answers given where an answer was expected, the share that cite at least one expected Section and no non-existent Section.
- Refusal correctness: of the Refusal-expected cases, the share routed to an Accepted Course that gave the exact Refusal sentence.
- Out of scope correctness: of the Out of scope-expected cases, the share the Router marked Out of scope.
- Supported rate and Responsive rate: of the answers the judge was called for (an answer given where an answer was expected), the share judged Supported (every claim is in the Section it cites) and Responsive (it addresses what was asked). Judge undecided rate: the share of the judge's verdicts that were UNKNOWN or a judge error; both count as a fail.

## Per case

Routed Course and cited Sections in each run, separated by ` / `.

| Case | Type | Accepted Courses | Routed | Cited Sections | Notes |
|---|---|---|---|---|---|
| GS-01 | in_material | GAIF | GAIF / GAIF / GAIF | GAIF-1.3 / GAIF-1.3 / GAIF-1.3 | - |
| GS-02 | near_miss | GAIF | GAIF / GAIF / GAIF | GAIF-2.10 / GAIF-2.10 / GAIF-2.10 | - |
| GS-03 | in_material | GAIF | GAIF / GAIF / GAIF | GAIF-1.6 / GAIF-1.6 / GAIF-1.6 | - |
| GS-04 | in_material | GAIF | GAIF / GAIF / GAIF | GAIF-2.14 / GAIF-2.14 / GAIF-2.14 | - |
| GS-05 | near_miss | GAIF | AITB / AITB / AITB | - / - / - | Refusal in 3/3 |
| GS-06 | in_material | PEID | PEID / PEID / PEID | PEID-3.13 / PEID-3.13 / PEID-3.13 | - |
| GS-07 | in_material | PEID | PEID / PEID / PEID | PEID-5.6, PEID-5.8 / PEID-5.6, PEID-5.8 / PEID-5.6, PEID-5.8 | - |
| GS-08 | in_material | PEID | PEID / PEID / PEID | PEID-4.1, PEID-4.2 / PEID-4.1, PEID-4.2 / PEID-4.1, PEID-4.2 | - |
| GS-09 | in_material | PEID | PEID / PEID / PEID | PEID-5.12 / PEID-5.12 / PEID-5.12 | - |
| GS-10 | near_miss | PEID | PEID / PEID / PEID | PEID-1.4, PEID-1.8, PEID-3.3 / PEID-1.4, PEID-1.8 / PEID-1.4, PEID-1.8, PEID-3.3 | - |
| GS-11 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-1.4, DTGS-1.5 / DTGS-1.4 / DTGS-1.4, DTGS-1.6 | - |
| GS-12 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-3.9 / DTGS-3.9, DTGS-3.22 / DTGS-3.9 | - |
| GS-13 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-3.20 / DTGS-3.20 / DTGS-3.20, DTGS-3.18 | - |
| GS-14 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-1.7 / DTGS-1.7 / DTGS-1.7 | - |
| GS-15 | near_miss | DTGS | DTGS / DTGS / DTGS | DTGS-3.7, DTGS-3.10 / DTGS-3.7, DTGS-3.10, DTGS-3.6 / DTGS-3.7, DTGS-3.10, DTGS-3.6 | - |
| GS-16 | in_material | AITB | AITB / AITB / AITB | AITB-3.5 / AITB-3.5 / AITB-3.5 | - |
| GS-17 | in_material | AITB | AITB / AITB / AITB | AITB-1.4, AITB-1.2 / AITB-1.4, AITB-1.2 / AITB-1.4, AITB-1.2 | - |
| GS-18 | in_material | AITB | AITB / AITB / AITB | AITB-1.6, AITB-4.10 / AITB-1.6, AITB-4.10 / AITB-1.6, AITB-4.10 | - |
| GS-19 | in_material | AITB | AITB / AITB / AITB | AITB-3.9, AITB-3.3 / AITB-3.9, AITB-3.3 / AITB-3.9, AITB-3.3 | - |
| GS-20 | in_material | AITB | AITB / AITB / AITB | AITB-4.10, AITB-1.6 / AITB-4.10, AITB-1.6 / AITB-4.10, AITB-1.6 | - |
| GS-21 | overlap | PEID, AITB | PEID / AITB / AITB | PEID-3.10, PEID-2.2, PEID-2.15 / AITB-2.8, AITB-2.5, AITB-1.6 / AITB-2.8 | - |
| GS-22 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-2.6, PEID-2.11 / PEID-2.6, PEID-2.11 / PEID-2.6, PEID-2.11 | - |
| GS-23 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-2.10, PEID-2.14, PEID-5.1, PEID-1.3, PEID-5.10, PEID-5.11, PEID-5.3, PEID-5.4 / PEID-2.10, PEID-2.14, PEID-5.1, PEID-1.3, PEID-5.10, PEID-2.15, PEID-5.11, PEID-5.13 / PEID-2.10, PEID-2.14, PEID-5.1, PEID-2.15, PEID-1.3, PEID-5.10, PEID-5.11, PEID-2.11 | - |
| GS-24 | overlap | PEID, AITB | AITB / AITB / AITB | AITB-2.4, AITB-2.6, AITB-2.9 / AITB-2.4, AITB-2.6, AITB-2.9, AITB-2.5 / AITB-2.4, AITB-2.6, AITB-2.9 | - |
| GS-25 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-1.9, PEID-1.8, PEID-3.1, PEID-2.4, PEID-3.10, PEID-3.12, PEID-2.7, PEID-2.15, PEID-3.8, PEID-3.9, PEID-4.10, PEID-5.13 / PEID-1.9, PEID-1.8, PEID-3.1, PEID-2.4, PEID-2.7, PEID-2.15, PEID-3.12, PEID-3.10, PEID-3.8, PEID-2.6 / PEID-1.9, PEID-1.8, PEID-3.1, PEID-2.4, PEID-2.7, PEID-3.12, PEID-2.5, PEID-3.8, PEID-3.9, PEID-5.11, PEID-2.15 | - |
| GS-26 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-4.10, PEID-4.2, PEID-2.11, PEID-5.13 / PEID-4.10, PEID-2.11, PEID-5.13 / PEID-4.10, PEID-5.13, PEID-4.2, PEID-2.11 | - |
| GS-27 | overlap | AITB, DTGS | DTGS / DTGS / DTGS | DTGS-3.7, DTGS-3.2, DTGS-3.8 / DTGS-3.7, DTGS-3.2, DTGS-3.3, DTGS-3.8, DTGS-3.6 / DTGS-3.7, DTGS-3.2, DTGS-3.8 | - |
| GS-28 | overlap | AITB, DTGS | DTGS / DTGS / DTGS | DTGS-3.21, DTGS-3.11, DTGS-3.20, DTGS-3.9, DTGS-3.2, DTGS-3.19 / DTGS-3.21, DTGS-3.11, DTGS-3.20, DTGS-3.2, DTGS-3.9, DTGS-3.19 / DTGS-3.11, DTGS-3.20, DTGS-3.21, DTGS-3.2, DTGS-3.9, DTGS-3.19 | - |
| GS-29 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-30 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-31 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-32 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-33 | refusal | GAIF | GAIF / GAIF / GAIF | - / - / - | Refusal in 3/3 |
| GS-34 | refusal | PEID | PEID / PEID / PEID | - / - / - | Refusal in 3/3 |
| GS-35 | refusal | AITB | AITB / AITB / AITB | - / - / - | Refusal in 3/3 |
| GS-36 | refusal | DTGS | DTGS / DTGS / DTGS | - / - / - | Refusal in 3/3 |
