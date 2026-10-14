# Golden Set candidates: review sheet

Draft from the coding assistant (2026-10-14) for issue #5. The cases are in `golden_set_candidates.json`. The group
decides the labels: edit or replace any case, fill in **Agreed by**, then freeze the agreed file before any score is
computed on it. Do not run an evaluation on this draft.

Already checked by script: 36 cases; 5 in-material per Course (4 of them Near-miss); 6 PEID/AITB and 2 AITB/DTGS
Overlap Cases; 4 Out of scope; 4 Refusal; every expected Section exists; Section prefixes match the Accepted
Courses; no question appears in `prompts/`, `evaluation/probes/` or `sample_cases.json`.

Still to check by people: key facts are really in the expected Sections; labels; wording.

| Id | Type | Accepted | Expected Sections | Why this case / doubt for reviewers | Agreed by |
|---|---|---|---|---|---|
| GS-01 | in_material | GAIF | GAIF-1.3 | Philosophy side of GAIF. | |
| GS-02 | in_material | GAIF | GAIF-2.5 | GAIF-2.9 and 2.15 also mention XOR; 2.5 holds the AND/OR weights. | |
| GS-03 | in_material | GAIF | GAIF-1.6 | Short Section; tests exact definition. | |
| GS-04 | near_miss GAIF/PEID | GAIF | GAIF-2.14 | Sounds like deep learning / LLM training (PEID), but only GAIF covers it. | |
| GS-05 | near_miss GAIF/DTGS | GAIF | GAIF-1.7 | Sounds like a DTGS business survey (McKinsey, Gartner), but it is in GAIF. | |
| GS-06 | in_material | PEID | PEID-3.13 | | |
| GS-07 | in_material | PEID | PEID-5.6 | | |
| GS-08 | in_material | PEID | PEID-4.1, PEID-4.2 | | |
| GS-09 | in_material | PEID | PEID-5.12 | | |
| GS-10 | near_miss GAIF/PEID | PEID | PEID-1.4 | Sounds like neural networks (GAIF), but GAIF excludes transformers. | |
| GS-11 | in_material | DTGS | DTGS-1.4 | | |
| GS-12 | in_material | DTGS | DTGS-3.9 | | |
| GS-13 | in_material | DTGS | DTGS-3.20 | | |
| GS-14 | in_material | DTGS | DTGS-1.7 | | |
| GS-15 | near_miss DTGS/PEID | DTGS | DTGS-3.7 | Sounds like PEID (RAG, PEID-3.7), but only DTGS compares retrieval with fine-tuning. **Doubt:** could be argued as Overlap; decide. | |
| GS-16 | in_material | AITB | AITB-3.5 | | |
| GS-17 | in_material | AITB | AITB-1.4 | | |
| GS-18 | in_material | AITB | AITB-1.6 | | |
| GS-19 | in_material | AITB | AITB-3.9 | | |
| GS-20 | in_material | AITB | AITB-4.10 | | |
| GS-21 | overlap | PEID, AITB | PEID-3.10, AITB-2.8 | Prompt injection is in both. | |
| GS-22 | overlap | PEID, AITB | PEID-2.6, AITB-2.3 | Role prompting is in both. | |
| GS-23 | overlap | PEID, AITB | PEID-2.14, PEID-2.10, AITB-2.10 | | |
| GS-24 | overlap | PEID, AITB | PEID-2.7, AITB-2.6, AITB-2.4 | | |
| GS-25 | overlap | PEID, AITB | PEID-2.15, PEID-3.12, PEID-2.4, AITB-2.9 | Close in theme to the sample case on hallucination, but a different question (how to prevent, not why). | |
| GS-26 | overlap | PEID, AITB | PEID-4.10, AITB-2.5, AITB-4.6 | | |
| GS-27 | overlap | AITB, DTGS | AITB-1.1, DTGS-3.7 | **Doubt:** DTGS-3.7 only names shadow AI as a risk of rung 1; AITB-1.1 defines it. Is DTGS coverage enough for an Overlap? | |
| GS-28 | overlap | AITB, DTGS | AITB-4.5, DTGS-3.21, DTGS-3.20 | | |
| GS-29 | out_of_scope | | | | |
| GS-30 | out_of_scope | | | Technical but not taught by any Course. | |
| GS-31 | out_of_scope | | | | |
| GS-32 | out_of_scope | | | **Doubt:** an "AI for job interview" angle would touch AITB; as written it is general advice. | |
| GS-33 | refusal (exercise) | GAIF | | New calculation; GAIF-2.8 has the method, so the Refusal is for solving it. | |
| GS-34 | refusal (logistics) | PEID | | Course logistics are excluded from all Course Material. | |
| GS-35 | refusal | AITB | | Tool administration is in AITB's domain but not in its Course Material. **Doubt:** some may label it Out of scope. | |
| GS-36 | refusal | DTGS | | Classic strategy framework in DTGS's domain, not in its Course Material. **Doubt:** same as GS-35. | |

Reviewers: ______ , ______ , ______  Date agreed: ______

Notes on disagreements (PEID-5.10 asks for them):
