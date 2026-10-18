# Golden Set v1: review sheet

The frozen Golden Set is [`golden_set.json`](golden_set.json) (version 1, frozen on 2026-10-14). It was built from the
candidates in [`golden_set_candidates.json`](golden_set_candidates.json), drafted by the coding assistant; the draft
review notes are in [`golden_set_candidates_review.md`](golden_set_candidates_review.md). Never edit the frozen file: a
correction is a new version with an entry in [`ITERATION_LOG.md`](ITERATION_LOG.md).

## Reviewers and process

- **Reviewer 1: Gonçalo Augusto.** Reviewed all 36 cases on 2026-10-14 against the Course Material (question, type,
  Accepted Courses, expected Sections, key facts), on a review page that showed each case beside the text of its
  expected Sections and a search over all four Course Materials. Decisions were made from the Course Material, not
  from the pilot runs.
- **Second review: Rodrigo (not blind).** Read reviewer 1's decisions and commented on three cases; each comment led
  to an edit (GS-01, GS-08, GS-15). This was not an independent labelling, so no agreement score (Cohen's kappa) is
  reported for the Golden Set labels.
- **Coding assistant.** Drafted the 36 candidates and three replacement questions (GS-02, GS-15, GS-36), ran the
  automatic checks and explained the definitions when a decision was discussed. It did not decide labels.

## Cases

| Id | Type | Accepted Courses | Expected Sections | Decision | Agreed by | Date | Note |
|---|---|---|---|---|---|---|---|
| GS-01 | in_material | GAIF | GAIF-1.3 | Edited | Gonçalo Augusto; Rodrigo (comment) | 2026-10-14 | Removed the key fact describing the set-up (person with the rule book): the question asks what the experiment is meant to show, not how it works. |
| GS-02 | near_miss | GAIF | GAIF-2.10 | Replaced | Gonçalo Augusto | 2026-10-14 | McCulloch-Pitts question replaced by a new GAIF/PEID Near-miss Case (sounds like PEID model training; only GAIF-2.10 covers learning rate and gradient descent), to restore the fourth Near-miss Case after GS-04 became in_material. Question drafted by the assistant, accepted by the reviewer. |
| GS-03 | in_material | GAIF | GAIF-1.6 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-04 | in_material | GAIF | GAIF-2.14 | Edited | Gonçalo Augusto | 2026-10-14 | Near-miss Case changed to in_material by the reviewer: question and key facts are right and only GAIF-2.14 answers it. |
| GS-05 | near_miss | GAIF | GAIF-1.7 | Approved after discussion | Gonçalo Augusto | 2026-10-14 | Near-miss GAIF/DTGS: sounds like a DTGS workplace study, but the Microsoft and Carnegie Mellon study is only in GAIF-1.7. First changed to in_material, restored after re-reading the Near-miss definition. |
| GS-06 | in_material | PEID | PEID-3.13 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-07 | in_material | PEID | PEID-5.6 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-08 | in_material | PEID | PEID-4.1 | Edited | Gonçalo Augusto; Rodrigo (comment) | 2026-10-14 | Reworded to a more natural question and to "LLM workflow" (in AITB, workflow means a work process). PEID-4.2 removed: it only touches the topic; the full answer is in PEID-4.1. |
| GS-09 | in_material | PEID | PEID-5.12 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-10 | near_miss | PEID | PEID-1.4 | Approved after discussion | Gonçalo Augusto | 2026-10-14 | Near-miss GAIF/PEID: sounds like neural networks (GAIF), but GAIF excludes transformers and only PEID-1.4 answers. First changed to in_material, restored after re-reading the Near-miss definition. |
| GS-11 | in_material | DTGS | DTGS-1.4 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-12 | in_material | DTGS | DTGS-3.9 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-13 | in_material | DTGS | DTGS-3.20 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-14 | in_material | DTGS | DTGS-1.7 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-15 | near_miss | DTGS | DTGS-3.7 | Edited | Gonçalo Augusto; Rodrigo (comment) | 2026-10-14 | Near-miss DTGS/PEID. The old question (when to use retrieval instead of fine-tuning) was answered better by PEID-3.7 than by DTGS, so it was not a Near-miss Case. The new question asks about cost, time to value and risk, which only DTGS-3.7 covers. Generic "lowest rung" key fact removed. Question drafted by the assistant, accepted by the reviewer. |
| GS-16 | in_material | AITB | AITB-3.5 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-17 | in_material | AITB | AITB-1.4 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-18 | in_material | AITB | AITB-1.6 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-19 | in_material | AITB | AITB-3.9 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-20 | in_material | AITB | AITB-4.10 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-21 | overlap | PEID, AITB | PEID-3.10, AITB-2.8 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-22 | overlap | PEID, AITB | PEID-2.6, AITB-2.3 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-23 | overlap | PEID, AITB | PEID-2.14, PEID-2.10, AITB-2.10 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-24 | overlap | PEID, AITB | PEID-2.7, AITB-2.6, AITB-2.4 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-25 | overlap | PEID, AITB | PEID-2.15, PEID-3.12, PEID-2.4, AITB-2.9 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-26 | overlap | PEID, AITB | PEID-4.10, AITB-2.5, AITB-4.6 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-27 | overlap | AITB, DTGS | AITB-1.1, DTGS-3.7 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-28 | overlap | AITB, DTGS | AITB-4.5, DTGS-3.21, DTGS-3.20 | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-29 | out_of_scope | OUT_OF_SCOPE | - | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-30 | out_of_scope | OUT_OF_SCOPE | - | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-31 | out_of_scope | OUT_OF_SCOPE | - | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-32 | out_of_scope | OUT_OF_SCOPE | - | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-33 | refusal | GAIF | - | Approved after discussion | Gonçalo Augusto | 2026-10-14 | Refusal (new exercise). GAIF-2.8 explains Hebb's rule, but the case asks for a new calculation, which the tutor must refuse. The reviewer first added GAIF-2.8 as an expected Section; removed, since a Refusal cites nothing. |
| GS-34 | refusal | PEID | - | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-35 | refusal | AITB | - | Approved | Gonçalo Augusto | 2026-10-14 |  |
| GS-36 | refusal | DTGS | - | Replaced | Gonçalo Augusto | 2026-10-14 | Porter's five forces removed: in no Course Material and general competitive strategy, closer to Out of scope than to a DTGS Refusal. Replaced by Lewin's change model: change management is in DTGS's description (Kotter, ADKAR), but Lewin is not in the material. Question drafted by the assistant, accepted by the reviewer. |

Near-miss pairs (the Course each case only sounds like): GS-02 GAIF (sounds like PEID), GS-05 GAIF (sounds like
DTGS), GS-10 PEID (sounds like GAIF), GS-15 DTGS (sounds like PEID). Refusal cases: GS-33 a new exercise, GS-34 Course
logistics, GS-35 and GS-36 a subject in the Course's domain that its Course Material does not cover.

## Changes from the candidates

Six cases differ from the candidates; three more were changed during the review and restored after discussion.

| Case | What changed | Why | Raised by |
|---|---|---|---|
| GS-01 | One key fact removed | The question asks what the experiment shows, not how it works | Rodrigo |
| GS-02 | New question (learning rate, GAIF/PEID Near-miss Case) | Restore the fourth Near-miss Case after GS-04 | Reviewer 1 |
| GS-04 | Near-miss Case to in_material | Reviewer 1's decision | Reviewer 1 |
| GS-08 | Reworded; PEID-4.2 removed | Unnatural wording, ambiguous "workflow"; PEID-4.2 only touches the topic | Rodrigo |
| GS-15 | New question (cost, time to value and risk); one key fact removed | PEID-3.7 answered the old question better than DTGS | Rodrigo |
| GS-36 | New question (Lewin's change model) | Porter's five forces judged Out of scope; the Refusal case needed replacing | Reviewer 1 |
| GS-05, GS-10 | Changed to in_material, then restored | "Only one Course answers" is what makes a Near-miss Case | Discussion |
| GS-33 | GAIF-2.8 added, then removed | A Refusal has no expected Sections | Discussion |

## Notes on disagreements

- **Near-miss definition (GS-04, GS-05, GS-10).** Reviewer 1 first read "only one Section answers" as a reason for
  in_material. After re-reading the definition in [`CONTEXT.md`](../CONTEXT.md), GS-05 and GS-10 went back to
  near_miss; GS-04 stayed in_material by the reviewer's decision, and GS-02 became the fourth Near-miss Case.
- **Refusal or Out of scope (GS-36).** Porter's five forces is general competitive strategy and is in no Course
  Material; the reviewer judged it Out of scope. To keep four Refusal cases, the slot went to a question clearly in
  DTGS's domain (change management) that its Course Material does not cover.
- **Near-miss or Overlap (GS-15).** Rather than turn the case into a DTGS/PEID Overlap Case (a pair the spec does not
  list), the question was rewritten so that only DTGS answers it.

## Limitations

- The questions are synthetic: drafted by the coding assistant, reviewed and partly rewritten by the group, not
  collected from students (no real personal data, as the brief requires).
- Pilot runs on the candidates (2026-10-14, see `ITERATION_LOG.md`) were seen before the freeze. Labels were decided
  from the Course Material; four questions changed afterwards (GS-02, GS-08, GS-15, GS-36), so pilot numbers are not
  comparable with runs on this file.
- One full review plus a non-blind second review; no independent double labelling.

## Automatic checks

`tests/test_golden_set.py` (standard library, no API key) checks the counts per type, five in-material cases per
Course, unique ids, valid Courses, that every expected Section exists and belongs to an Accepted Course, the Overlap
pairs, that Refusal and Out of scope cases have no expected Sections or key facts, and that no question appears in a
prompt.
