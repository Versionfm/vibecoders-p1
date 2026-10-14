# Evaluation report, 2026-10-14T11:30:09+00:00

- Case file: `evaluation/golden_set_candidates.json` (36 cases: 16 in_material, 4 near_miss, 8 overlap, 4 out_of_scope, 4 refusal)
- Runs: 3 (every case answered once per run)
- App model (Router and Course Tutor): `nvidia/nemotron-3-super-120b-a12b`. Thinking: off
- Prompt versions: router `router_v2`, tutor `tutor_v2`
- Judge model: none yet (LLM judge comes in ticket #7)
- Tutor: `routed`

## Steps

Share of Traces passing each Step, as mean and range (lowest to highest) across the 3 runs.

| Step | Mean | Range | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|
| Search Step | 28.7% | 11.1% to 63.9% | 63.9% | 11.1% | 11.1% |
| Path Step | 20.4% | 0.0% to 61.1% | 61.1% | 0.0% | 0.0% |
| Answer Step | 17.6% | 0.0% to 52.8% | 52.8% | 0.0% | 0.0% |
| **End-to-end Success** | 17.6% | 0.0% to 52.8% | 52.8% | 0.0% | 0.0% |

- Search Step: at least one Accepted Course and no other Course chosen or read; none for an Out of scope case. For the Routed Tutor the routed Course is the Course Material read.
- Path Step: no failed model call or invalid Router reply, no `read_file` argument that is not a Course, no Course Material read twice, within the Read limit, and no in-scope answer or Refusal without a Read.
- Answer Step: cites an expected Section and only valid Sections, or gives the expected Refusal or Out of scope. Code checks only: claims are not checked until the LLM judge exists (ticket #7).
- End-to-end Success: the Trace passes all three Steps.

Per case: Traces passing each Step out of the runs, and the earliest failing Step with its reason.

| Case | Type | Search | Path | Answer | End-to-end Success | Earliest failing Step |
|---|---|---|---|---|---|---|
| GS-01 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-02 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-03 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-04 | near_miss | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-05 | near_miss | 0/3 | 1/3 | 0/3 | 0/3 | Search: read DTGS, not an Accepted Course (1/3); Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-06 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-07 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-08 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-09 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-10 | near_miss | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-11 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-12 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-13 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-14 | in_material | 0/3 | 1/3 | 0/3 | 0/3 | Search: no Course Material read (1/3); Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-15 | near_miss | 0/3 | 1/3 | 0/3 | 0/3 | Search: read PEID, not an Accepted Course (1/3); Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-16 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-17 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-18 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-19 | in_material | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-20 | in_material | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-21 | overlap | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-22 | overlap | 1/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-23 | overlap | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-24 | overlap | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-25 | overlap | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-26 | overlap | 1/3 | 0/3 | 0/3 | 0/3 | Path: Course Tutor model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (1/3); Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-27 | overlap | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-28 | overlap | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-29 | out_of_scope | 3/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-30 | out_of_scope | 3/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-31 | out_of_scope | 3/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-32 | out_of_scope | 3/3 | 1/3 | 1/3 | 1/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (2/3) |
| GS-33 | refusal | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-34 | refusal | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-35 | refusal | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |
| GS-36 | refusal | 0/3 | 0/3 | 0/3 | 0/3 | Path: Router model call failed: RateLimitError: Error code: 429 - {'status': 429, 'title': 'Too Many Requests'} (3/3) |

## Metrics

Mean and range (lowest to highest) across the 3 runs. n/a: no cases of that kind in the case file.

| Metric | Mean | Range | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|
| Routing accuracy | 18.5% | 0.0% to 55.6% | 55.6% | 0.0% | 0.0% |
| Recall GAIF | 22.2% | 0.0% to 66.7% | 66.7% | 0.0% | 0.0% |
| Recall PEID | 22.2% | 0.0% to 66.7% | 66.7% | 0.0% | 0.0% |
| Recall AITB | 16.7% | 0.0% to 50.0% | 50.0% | 0.0% | 0.0% |
| Recall DTGS | 16.7% | 0.0% to 50.0% | 50.0% | 0.0% | 0.0% |
| Recall OUT_OF_SCOPE | 8.3% | 0.0% to 25.0% | 25.0% | 0.0% | 0.0% |
| **Recall (macro average)** | 17.2% | 0.0% to 51.7% | 51.7% | 0.0% | 0.0% |
| Citation correctness | 94.7% | 94.7% to 94.7% | 94.7% | n/a | n/a |
| Refusal correctness | 0.0% | 0.0% to 0.0% | 0.0% | 0.0% | 0.0% |
| Out of scope correctness | 8.3% | 0.0% to 25.0% | 25.0% | 0.0% | 0.0% |
| Supported rate | pending | needs the LLM judge (ticket #7) | | | |
| Responsive rate | pending | needs the LLM judge (ticket #7) | | | |

Definitions:

- Routing accuracy: the Router's choice is one of the case's Accepted Courses.
- Recall per class over the five classes (GAIF, PEID, AITB, DTGS, OUT_OF_SCOPE). A case counts for the routed Course when that is an Accepted Course, otherwise for its first Accepted Course, so an Overlap Case routed to either Accepted Course is a hit. Recall (macro average): the unweighted mean over classes that have cases.
- Citation correctness: of the answers given where an answer was expected, the share that cite at least one expected Section and no non-existent Section.
- Refusal correctness: of the Refusal-expected cases, the share routed to an Accepted Course that gave the exact Refusal sentence.
- Out of scope correctness: of the Out of scope-expected cases, the share the Router marked Out of scope.

## Per case

Routed Course and cited Sections in each run, separated by ` / `.

| Case | Type | Accepted Courses | Routed | Cited Sections | Notes |
|---|---|---|---|---|---|
| GS-01 | in_material | GAIF | GAIF / error / error | GAIF-1.3 / - / - | error in 2/3 |
| GS-02 | in_material | GAIF | GAIF / error / error | GAIF-2.5 / - / - | error in 2/3 |
| GS-03 | in_material | GAIF | GAIF / error / error | GAIF-1.6 / - / - | error in 2/3 |
| GS-04 | near_miss | GAIF | GAIF / error / error | GAIF-2.14 / - / - | error in 2/3 |
| GS-05 | near_miss | GAIF | DTGS / error / error | - / - / - | Refusal in 1/3; error in 2/3 |
| GS-06 | in_material | PEID | PEID / error / error | PEID-3.13 / - / - | error in 2/3 |
| GS-07 | in_material | PEID | PEID / error / error | PEID-5.6 / - / - | error in 2/3 |
| GS-08 | in_material | PEID | PEID / error / error | PEID-4.1 / - / - | error in 2/3 |
| GS-09 | in_material | PEID | PEID / error / error | PEID-5.12 / - / - | error in 2/3 |
| GS-10 | near_miss | PEID | PEID / error / error | PEID-1.4 / - / - | error in 2/3 |
| GS-11 | in_material | DTGS | DTGS / error / error | DTGS-1.4 / - / - | error in 2/3 |
| GS-12 | in_material | DTGS | DTGS / error / error | DTGS-3.9 / - / - | error in 2/3 |
| GS-13 | in_material | DTGS | DTGS / error / error | DTGS-3.20 / - / - | error in 2/3 |
| GS-14 | in_material | DTGS | OUT_OF_SCOPE / error / error | - / - / - | error in 2/3 |
| GS-15 | near_miss | DTGS | PEID / error / error | PEID-3.7, PEID-3.1 / - / - | error in 2/3 |
| GS-16 | in_material | AITB | AITB / error / error | AITB-3.5 / - / - | error in 2/3 |
| GS-17 | in_material | AITB | AITB / error / error | AITB-1.4 / - / - | error in 2/3 |
| GS-18 | in_material | AITB | AITB / error / error | AITB-1.6 / - / - | error in 2/3 |
| GS-19 | in_material | AITB | AITB / error / error | AITB-3.9 / - / - | error in 2/3 |
| GS-20 | in_material | AITB | error / error / error | - / - / - | error in 3/3 |
| GS-21 | overlap | PEID, AITB | PEID / error / error | PEID-3.10 / - / - | error in 2/3 |
| GS-22 | overlap | PEID, AITB | PEID / error / error | PEID-2.6 / - / - | error in 2/3 |
| GS-23 | overlap | PEID, AITB | error / error / error | - / - / - | error in 3/3 |
| GS-24 | overlap | PEID, AITB | error / error / error | - / - / - | error in 3/3 |
| GS-25 | overlap | PEID, AITB | error / error / error | - / - / - | error in 3/3 |
| GS-26 | overlap | PEID, AITB | PEID / error / error | - / - / - | error in 3/3 |
| GS-27 | overlap | AITB, DTGS | error / error / error | - / - / - | error in 3/3 |
| GS-28 | overlap | AITB, DTGS | error / error / error | - / - / - | error in 3/3 |
| GS-29 | out_of_scope | OUT_OF_SCOPE | error / error / error | - / - / - | error in 3/3 |
| GS-30 | out_of_scope | OUT_OF_SCOPE | error / error / error | - / - / - | error in 3/3 |
| GS-31 | out_of_scope | OUT_OF_SCOPE | error / error / error | - / - / - | error in 3/3 |
| GS-32 | out_of_scope | OUT_OF_SCOPE | OUT_OF_SCOPE / error / error | - / - / - | error in 2/3 |
| GS-33 | refusal | GAIF | error / error / error | - / - / - | error in 3/3 |
| GS-34 | refusal | PEID | error / error / error | - / - / - | error in 3/3 |
| GS-35 | refusal | AITB | error / error / error | - / - / - | error in 3/3 |
| GS-36 | refusal | DTGS | error / error / error | - / - / - | error in 3/3 |
