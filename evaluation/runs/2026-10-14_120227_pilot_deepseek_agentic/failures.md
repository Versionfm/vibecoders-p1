# Failing cases: Agentic Tutor pilot on the Golden Set candidates (deepseek-flash)

Pilot on `evaluation/golden_set_candidates.json` (labels not yet agreed by the group). Observable facts only; the
group names the failures in its own words. 6 of 36 cases fail in at least one Run.

| Case | Type | Question | Expected | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|---|
| GS-05 | near_miss | What did the Microsoft and Carnegie Mellon study of knowledge workers suggest about using AI? | GAIF; cite GAIF-1.7 | read AITB; Refusal "This is not covered in the AITB material." | same as Run 1 | same as Run 1 |
| GS-13 | in_material | What happened with Klarna's AI customer service assistant after its launch? | DTGS; cite DTGS-3.20 | read DTGS; cited DTGS-3.20 (passed) | read DTGS, then AITB; cited DTGS-3.20, DTGS-3.18 | read DTGS; cited DTGS-3.20 (passed) |
| GS-15 | near_miss | When should a company ground a model in its own documents with retrieval instead of fine-tuning it? | DTGS; cite DTGS-3.7 | read PEID; cited PEID-3.7, PEID-3.1, PEID-1.9; "The question is about when to use retrieval (RAG) versus fine-tuning ..." | read PEID; cited PEID-3.7, PEID-3.1, PEID-1.9, PEID-3.8, PEID-3.10 | same as Run 2 |
| GS-33 | refusal (exercise) | Using Hebb's rule with bipolar inputs, compute the final weights and bias after training on the OR function. | GAIF; the GAIF Refusal | nothing read; "This is a request to solve a new calculation exercise, so I must refuse." (not the exact Refusal) | read GAIF; Refusal "This is not covered in the GAIF material." (passed) | nothing read; "This is a new calculation exercise, so I must refuse." |
| GS-35 | refusal | How do I assign Microsoft 365 Copilot licences to my team in the admin centre? | AITB; the AITB Refusal | nothing read; Out of scope Sentence | same as Run 1 | same as Run 1 |
| GS-36 | refusal | What are Porter's five forces? | DTGS; the DTGS Refusal | nothing read; Out of scope Sentence | same as Run 1 | same as Run 1 |

Notes for the group:

- GS-15, GS-35 and GS-36 are cases whose labels the review sheet already marks as doubtful. The Routed Tutor also
  sent GS-36 to Out of scope; it routed GS-35 to AITB and gave the Refusal.
- GS-33 in Runs 1 and 3 is the only Path Step failure (an in-scope Refusal with no Read); its earliest failing Step
  is Search because nothing was read.
- GS-13 Run 2 is the only Trace that read a second Course Material; the extra Read of AITB fails the Search Step
  although the answer cites only DTGS.
- No model call failed and no Trace reached the Read limit.
