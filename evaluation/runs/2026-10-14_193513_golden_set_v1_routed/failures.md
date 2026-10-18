# Failing cases: Routed Tutor on Golden Set v1, deepseek-flash

Run folder: `evaluation/runs/2026-10-14_193513_golden_set_v1_routed` (Routed Tutor, Router `router_v2`, Course Tutor
`tutor_v2`, app model `deepseek-flash`, thinking off, no judge, commit `123d939`). A case fails in a run when its
Trace fails End-to-end Success. The Answer Step is a code check only (no judge yet), so a case that passes here can
still have unsupported claims.

Observable facts only; the group names the failures. `evaluation/FAILURE_TAXONOMY.md` does not exist yet, so there is
no category column.

| Case | Type | Question | Expected | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|---|
| GS-05 (failed 3/3) | near_miss | What did the Microsoft and Carnegie Mellon study of knowledge workers suggest about using AI? | Accepted Courses: GAIF. Expected Sections: GAIF-1.7. No Refusal. | Earliest failing Step: Search ("read AITB, not an Accepted Course"). Router chose AITB, evidence "knowledge workers suggest about using AI". Course Material read: AITB. Cited Sections: none. Answer: "This is not covered in the AITB material." (the Refusal). Error: none. | Same as Run 1: Search; routed AITB; read AITB; no citations; "This is not covered in the AITB material."; no error. | Same as Run 1: Search; routed AITB; read AITB; no citations; "This is not covered in the AITB material."; no error. |

Notes (facts, not failures in this run):

- GS-05 failed the same way in 3/3 runs of the candidates pilot (`2026-10-14_120039_pilot_deepseek_routed`); its
  question and labels are the same in both case files.
- GS-27 (overlap, AITB or DTGS; question and labels unchanged from the candidates) passed 3/3 here, citing DTGS-3.7.
  In the pilot, with the same prompts, model and temperature 0, it gave the DTGS Refusal in 2/3 runs.
