# Failing cases: Routed Tutor pilot on the Golden Set candidates (deepseek-flash)

Pilot on `evaluation/golden_set_candidates.json` (labels not yet agreed by the group). Observable facts only; the
group names the failures in its own words. 4 of 36 cases fail in at least one Run.

| Case | Type | Question | Expected | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|---|
| GS-05 | near_miss | What did the Microsoft and Carnegie Mellon study of knowledge workers suggest about using AI? | GAIF; cite GAIF-1.7 | routed AITB; Refusal "This is not covered in the AITB material." | same as Run 1 | same as Run 1 |
| GS-15 | near_miss | When should a company ground a model in its own documents with retrieval instead of fine-tuning it? | DTGS; cite DTGS-3.7 | routed PEID; cited PEID-3.7, PEID-3.1; "Grounding with retrieval is the right choice when the model needs facts it cannot know: ..." | routed PEID; cited PEID-3.7, PEID-1.6, PEID-3.1; same opening | routed PEID; cited PEID-3.7, PEID-3.1; same opening |
| GS-27 | overlap | What is shadow AI, and why should a company worry about it? | AITB or DTGS; cite AITB-1.1 or DTGS-3.7 | routed DTGS; cited DTGS-3.7; "Shadow AI is mentioned as a risk of the off-the-shelf tool rung of the make-or-buy ladder: ..." (passed) | routed DTGS; Refusal "This is not covered in the DTGS material." | same as Run 2 |
| GS-36 | refusal | What are Porter's five forces? | DTGS; the DTGS Refusal | routed OUT_OF_SCOPE; no answer | same as Run 1 | same as Run 1 |

Notes for the group:

- GS-15, GS-27 and GS-36 are cases whose labels the review sheet already marks as doubtful.
- No model call failed in any Run (Path Step 100%).
