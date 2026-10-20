# Evaluation report, 2026-10-20T14:02:31+00:00

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
| Answer Step | 86.1% | 80.6% to 88.9% | 80.6% | 88.9% | 88.9% |
| **End-to-end Success** | 86.1% | 80.6% to 88.9% | 80.6% | 88.9% | 88.9% |

- Search Step: at least one Accepted Course and no other Course chosen or read; none for an Out of scope case. For the Routed Tutor the routed Course is the Course Material read.
- Path Step: no failed model call or invalid Router reply, no `read_file` argument that is not a Course, no Course Material read twice, within the Read limit, and no in-scope answer or Refusal without a Read.
- Answer Step: cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope; an expected answer must also be judged Supported and Responsive by the LLM judge.
- End-to-end Success: the Trace passes all three Steps.

Per case: Traces passing each Step out of the runs, and the earliest failing Step with its reason.

| Case | Type | Search | Path | Answer | End-to-end Success | Earliest failing Step |
|---|---|---|---|---|---|---|
| GS-01 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-02 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-03 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-04 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-05 | near_miss | 0/3 | 3/3 | 0/3 | 0/3 | Search: read AITB, not an Accepted Course (3/3) |
| GS-06 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-07 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-08 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-09 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-10 | near_miss | 3/3 | 3/3 | 1/3 | 1/3 | Answer: judged not Responsive: The question asks how attention decides which earlier words matter for the next token, i.e., the mechanism of computing attention weights. The answer only states that attention re‑weights all previous tokens and that the weighting is learned, without explaining the query‑key‑value dot‑product, softmax, or how the model learns to assign higher weights to relevant words. Thus it does not fully address the question. (1/3); Answer: judged not Responsive: The question asks how attention decides which earlier words matter for the next token, i.e., the mechanism of weighting (query‑key‑value, dot‑product, softmax). The answer only states that attention re‑weights all previous tokens and that this weighting is learned, but it does not explain the actual decision process or the key components of attention. Therefore it does not fully address the question asked. (1/3) |
| GS-11 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judged not Supported: The claim that Kotter and Schlesinger recommend choosing among the six approaches (education and communication, participation and involvement, facilitation and support, negotiation and agreement, manipulation and co-optation, coercion) is not stated in the cited section [DTGS-1.6], which only says to choose the methods for managing resistance accordingly without listing those six approaches. (1/3) |
| GS-12 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-13 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-14 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-15 | near_miss | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Responsive: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-16 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3) |
| GS-17 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-18 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-19 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-20 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-21 | overlap | 3/3 | 3/3 | 1/3 | 1/3 | Answer: judged not Supported: The claim that ‘keep the source pack explicit and approved’ is unsupported because AITB‑1.3 does not mention it. (1/3); Answer: judged not Supported: The claim that "keep source packs explicit and approved" is unsupported because AITB-1.3 does not contain that phrase. (1/3) |
| GS-22 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-23 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-24 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-25 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-26 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-27 | overlap | 3/3 | 3/3 | 0/3 | 0/3 | Answer: judge error on Supported: judge model call failed: APITimeoutError: Request timed out. (1/3); Answer: judged not Supported: The claim that the material frames shadow AI as a control and risk problem rather than a technology one is not stated in any of the cited sections (DTGS‑3.7, DTGS‑3.2, DTGS‑3.3, DTGS‑3.8). (1/3); Answer: judged not Supported: The claim that "the material frames it as a control and risk problem rather than a technology problem" is not stated in any of the cited sections (DTGS‑3.7, 3.2, 3.3, 3.6, 3.8). (1/3) |
| GS-28 | overlap | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judge error on Responsive: judge model call failed: APITimeoutError: Request timed out. (1/3) |
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
| Supported rate | 90.1% | 88.9% to 92.6% | 88.9% | 88.9% | 92.6% |
| Responsive rate | 95.1% | 88.9% to 100.0% | 88.9% | 100.0% | 96.3% |
| Judge undecided rate | 3.1% | 0.0% to 7.4% | 7.4% | 1.9% | 0.0% |

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
| GS-10 | near_miss | PEID | PEID / PEID / PEID | PEID-1.4, PEID-1.8 / PEID-1.4, PEID-1.8 / PEID-1.4, PEID-1.8, PEID-3.3 | - |
| GS-11 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-1.4, DTGS-1.6 / DTGS-1.4, DTGS-1.6 / DTGS-1.4, DTGS-1.6 | - |
| GS-12 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-3.9 / DTGS-3.9, DTGS-3.22 / DTGS-3.9 | - |
| GS-13 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-3.20, DTGS-3.18 / DTGS-3.20 / DTGS-3.20 | - |
| GS-14 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-1.7 / DTGS-1.7 / DTGS-1.7 | - |
| GS-15 | near_miss | DTGS | DTGS / DTGS / DTGS | DTGS-3.7, DTGS-3.10, DTGS-3.6 / DTGS-3.7, DTGS-3.10, DTGS-3.6 / DTGS-3.7, DTGS-3.6 | - |
| GS-16 | in_material | AITB | AITB / AITB / AITB | AITB-3.5 / AITB-3.5 / AITB-3.5 | - |
| GS-17 | in_material | AITB | AITB / AITB / AITB | AITB-1.4, AITB-1.2 / AITB-1.4, AITB-1.2 / AITB-1.4, AITB-1.2 | - |
| GS-18 | in_material | AITB | AITB / AITB / AITB | AITB-1.6, AITB-4.10 / AITB-1.6, AITB-4.10 / AITB-1.6, AITB-4.10 | - |
| GS-19 | in_material | AITB | AITB / AITB / AITB | AITB-3.9, AITB-3.8 / AITB-3.9, AITB-3.3 / AITB-3.9, AITB-3.8, AITB-3.3 | - |
| GS-20 | in_material | AITB | AITB / AITB / AITB | AITB-4.10, AITB-1.6 / AITB-4.10, AITB-1.6 / AITB-4.10, AITB-1.6 | - |
| GS-21 | overlap | PEID, AITB | AITB / AITB / AITB | AITB-2.8, AITB-1.3, AITB-2.7 / AITB-2.8, AITB-1.3, AITB-2.7 / AITB-2.8 | - |
| GS-22 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-2.6, PEID-2.11 / PEID-2.6, PEID-2.11 / PEID-2.6, PEID-2.11 | - |
| GS-23 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-2.10, PEID-2.14, PEID-5.1, PEID-5.10, PEID-2.15, PEID-5.11, PEID-2.13 / PEID-2.10, PEID-2.14, PEID-5.1, PEID-5.10, PEID-5.11, PEID-1.3 / PEID-2.10, PEID-2.14, PEID-5.1, PEID-1.3, PEID-5.10, PEID-5.11 | - |
| GS-24 | overlap | PEID, AITB | AITB / AITB / AITB | AITB-2.4, AITB-2.6, AITB-3.7, AITB-3.9, AITB-2.9, AITB-3.10 / AITB-2.4, AITB-2.6, AITB-3.7, AITB-3.10, AITB-2.2, AITB-2.9, AITB-2.5 / AITB-2.4, AITB-2.6, AITB-3.10, AITB-1.3, AITB-2.9, AITB-3.8 | - |
| GS-25 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-1.9, PEID-1.8, PEID-3.1, PEID-3.12, PEID-2.7, PEID-2.4, PEID-3.7, PEID-3.8, PEID-5.11, PEID-2.15 / PEID-3.1, PEID-1.8, PEID-1.9, PEID-2.4, PEID-2.7, PEID-3.12, PEID-2.5, PEID-3.8, PEID-3.9, PEID-5.11, PEID-2.15 / PEID-1.9, PEID-1.8, PEID-3.1, PEID-2.15, PEID-2.7, PEID-2.4, PEID-3.12, PEID-3.7, PEID-3.8, PEID-3.9, PEID-3.6, PEID-5.11 | - |
| GS-26 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-4.10, PEID-5.13, PEID-4.2, PEID-2.11 / PEID-4.10, PEID-5.13, PEID-4.2, PEID-2.11 / PEID-4.10, PEID-5.13, PEID-2.11, PEID-4.2 | - |
| GS-27 | overlap | AITB, DTGS | DTGS / DTGS / DTGS | DTGS-3.7, DTGS-3.2, DTGS-3.3, DTGS-3.8 / DTGS-3.7, DTGS-3.2, DTGS-3.3, DTGS-3.8 / DTGS-3.7, DTGS-3.2, DTGS-3.3, DTGS-3.8, DTGS-3.6 | - |
| GS-28 | overlap | AITB, DTGS | DTGS / DTGS / DTGS | DTGS-3.11, DTGS-3.20, DTGS-3.21, DTGS-3.2, DTGS-3.9, DTGS-3.10, DTGS-3.19 / DTGS-3.21, DTGS-3.11, DTGS-3.20, DTGS-3.2, DTGS-3.10, DTGS-3.19 / DTGS-3.11, DTGS-3.20, DTGS-3.21, DTGS-3.2, DTGS-3.9, DTGS-3.19 | - |
| GS-29 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-30 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-31 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-32 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-33 | refusal | GAIF | GAIF / GAIF / GAIF | - / - / - | Refusal in 3/3 |
| GS-34 | refusal | PEID | PEID / PEID / PEID | - / - / - | Refusal in 3/3 |
| GS-35 | refusal | AITB | AITB / AITB / AITB | - / - / - | Refusal in 3/3 |
| GS-36 | refusal | DTGS | DTGS / DTGS / DTGS | - / - / - | Refusal in 3/3 |
