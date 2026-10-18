# Evaluation report, 2026-10-18T02:05:03+00:00

- Case file: `evaluation/golden_set.json` (36 cases: 16 in_material, 4 near_miss, 8 overlap, 4 out_of_scope, 4 refusal)
- Runs: 3 (every case answered once per run)
- App model (Router and Course Tutor): `deepseek-flash`. Thinking: off
- Prompt versions: router `router_v2`, tutor `tutor_v2`, judge_supported `judge_supported_v1`, judge_responsive `judge_responsive_v1`
- Judge model: `openai/gpt-oss-20b`. The Answer Step uses the judge.
- Tutor: `routed`

## Steps

Share of Traces passing each Step, as mean and range (lowest to highest) across the 3 runs.

| Step | Mean | Range | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|
| Search Step | 97.2% | 97.2% to 97.2% | 97.2% | 97.2% | 97.2% |
| Path Step | 100.0% | 100.0% to 100.0% | 100.0% | 100.0% | 100.0% |
| Answer Step | 90.7% | 88.9% to 91.7% | 91.7% | 88.9% | 91.7% |
| **End-to-end Success** | 90.7% | 88.9% to 91.7% | 91.7% | 88.9% | 91.7% |

- Search Step: at least one Accepted Course and no other Course chosen or read; none for an Out of scope case. For the Routed Tutor the routed Course is the Course Material read.
- Path Step: no failed model call or invalid Router reply, no `read_file` argument that is not a Course, no Course Material read twice, within the Read limit, and no in-scope answer or Refusal without a Read.
- Answer Step: cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope; an expected answer must also be judged Supported and Responsive by the LLM judge.
- End-to-end Success: the Trace passes all three Steps.

Per case: Traces passing each Step out of the runs, and the earliest failing Step with its reason.

| Case | Type | Search | Path | Answer | End-to-end Success | Earliest failing Step |
|---|---|---|---|---|---|---|
| GS-01 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-02 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-03 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-04 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-05 | near_miss | 0/3 | 3/3 | 0/3 | 0/3 | Search: read AITB, not an Accepted Course (3/3) |
| GS-06 | in_material | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judged not Supported: The claim that a timestamp changes the prefix on every call is unsupported because the cited section only states that a timestamp at the top of a system prompt silently disables caching, not that it changes the prefix. (1/3) |
| GS-07 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-08 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-09 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-10 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-11 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-12 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-13 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-14 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-15 | near_miss | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-16 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-17 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-18 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-19 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-20 | in_material | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-21 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-22 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-23 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-24 | overlap | 3/3 | 3/3 | 1/3 | 1/3 | Answer: judged not Supported: The claim "Structure does not guarantee accuracy or grounding" is unsupported because no cited section states it. (1/3); Answer: judged not Supported: The claim that "Structure therefore does not guarantee accuracy or grounding" is not fully supported by the cited section AITB-2.6, which only states that a table can still contain errors and that fields should be compared with the source; it does not mention "grounding". (1/3) |
| GS-25 | overlap | 3/3 | 3/3 | 2/3 | 2/3 | Answer: judged not Supported: The claim "To stop the model inventing facts, supply the missing information and give it a permitted way out:" is not supported by any cited section. (1/3) |
| GS-26 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
| GS-27 | overlap | 3/3 | 3/3 | 0/3 | 0/3 | Answer: judged not Responsive: The answer does not provide a definition of shadow AI nor explain why a company should worry about it; it merely states that the material does not cover the topic, which does not address the question asked. (1/3); Answer: judged not Responsive: The answer does not provide a definition of shadow AI or explain why a company should worry about it; it merely states that the material does not cover the topic, which does not address the question asked. (1/3); Answer: judged not Supported: The claim that the Course Material does not define shadow AI further or explain why a company should worry about it is unsupported, as no section is cited to support this absence of content. (1/3) |
| GS-28 | overlap | 3/3 | 3/3 | 3/3 | 3/3 | - |
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
| Supported rate | 93.8% | 92.6% to 96.3% | 96.3% | 92.6% | 92.6% |
| Responsive rate | 96.3% | 96.3% to 96.3% | 96.3% | 96.3% | 96.3% |
| Judge undecided rate | 0.0% | 0.0% to 0.0% | 0.0% | 0.0% | 0.0% |

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
| GS-07 | in_material | PEID | PEID / PEID / PEID | PEID-5.6 / PEID-5.6 / PEID-5.6, PEID-5.8 | - |
| GS-08 | in_material | PEID | PEID / PEID / PEID | PEID-4.1, PEID-4.2 / PEID-4.1, PEID-4.2 / PEID-4.1, PEID-4.2 | - |
| GS-09 | in_material | PEID | PEID / PEID / PEID | PEID-5.12 / PEID-5.12 / PEID-5.12 | - |
| GS-10 | near_miss | PEID | PEID / PEID / PEID | PEID-1.4 / PEID-1.4 / PEID-1.4 | - |
| GS-11 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-1.4 / DTGS-1.4 / DTGS-1.4 | - |
| GS-12 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-3.9 / DTGS-3.9 / DTGS-3.9 | - |
| GS-13 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-3.20 / DTGS-3.20 / DTGS-3.20 | - |
| GS-14 | in_material | DTGS | DTGS / DTGS / DTGS | DTGS-1.7 / DTGS-1.7 / DTGS-1.7 | - |
| GS-15 | near_miss | DTGS | DTGS / DTGS / DTGS | DTGS-3.7 / DTGS-3.7 / DTGS-3.7 | - |
| GS-16 | in_material | AITB | AITB / AITB / AITB | AITB-3.5 / AITB-3.5 / AITB-3.5 | - |
| GS-17 | in_material | AITB | AITB / AITB / AITB | AITB-1.4 / AITB-1.4 / AITB-1.4 | - |
| GS-18 | in_material | AITB | AITB / AITB / AITB | AITB-1.6 / AITB-1.6 / AITB-1.6 | - |
| GS-19 | in_material | AITB | AITB / AITB / AITB | AITB-3.9 / AITB-3.9 / AITB-3.9 | - |
| GS-20 | in_material | AITB | AITB / AITB / AITB | AITB-4.10 / AITB-4.10 / AITB-4.10 | - |
| GS-21 | overlap | PEID, AITB | PEID / PEID / AITB | PEID-3.10, PEID-2.2 / PEID-3.10, PEID-3.12 / AITB-2.8 | - |
| GS-22 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-2.6 / PEID-2.6, PEID-2.11 / PEID-2.6, PEID-2.11 | - |
| GS-23 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-2.14, PEID-5.1, PEID-5.10, PEID-2.15, PEID-2.13 / PEID-2.10, PEID-2.14, PEID-5.1, PEID-5.10 / PEID-2.10, PEID-2.14, PEID-5.1, PEID-5.10, PEID-2.15 | - |
| GS-24 | overlap | PEID, AITB | AITB / AITB / AITB | AITB-2.4, AITB-2.6, AITB-2.7 / AITB-2.4, AITB-2.6 / AITB-2.4, AITB-2.6 | - |
| GS-25 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-1.9, PEID-3.1, PEID-2.4, PEID-2.7, PEID-3.12, PEID-2.15 / PEID-1.9, PEID-3.1, PEID-2.4, PEID-2.7, PEID-3.12 / PEID-1.9, PEID-3.1, PEID-2.4, PEID-2.7, PEID-3.12, PEID-3.10 | - |
| GS-26 | overlap | PEID, AITB | PEID / PEID / PEID | PEID-4.10, PEID-5.13 / PEID-4.10, PEID-5.13 / PEID-4.10, PEID-5.13 | - |
| GS-27 | overlap | AITB, DTGS | DTGS / DTGS / DTGS | DTGS-3.7 / DTGS-3.7 / DTGS-3.7 | - |
| GS-28 | overlap | AITB, DTGS | DTGS / DTGS / DTGS | DTGS-3.21, DTGS-3.20, DTGS-3.9, DTGS-3.10, DTGS-3.11 / DTGS-3.21, DTGS-3.20, DTGS-3.9, DTGS-3.11, DTGS-3.10 / DTGS-3.21, DTGS-3.20, DTGS-3.11, DTGS-3.9, DTGS-3.10 | - |
| GS-29 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-30 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-31 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-32 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / OUT_OF_SCOPE / OUT_OF_SCOPE | - / - / - | - |
| GS-33 | refusal | GAIF | GAIF / GAIF / GAIF | - / - / - | Refusal in 3/3 |
| GS-34 | refusal | PEID | PEID / PEID / PEID | - / - / - | Refusal in 3/3 |
| GS-35 | refusal | AITB | AITB / AITB / AITB | - / - / - | Refusal in 3/3 |
| GS-36 | refusal | DTGS | DTGS / DTGS / DTGS | - / - / - | Refusal in 3/3 |
