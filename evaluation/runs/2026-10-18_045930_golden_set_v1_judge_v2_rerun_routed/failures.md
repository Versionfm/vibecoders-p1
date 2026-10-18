# Failing cases: Routed Tutor on Golden Set v1, deepseek-flash, judge_supported_v2 (re-run)

Run folder: `evaluation/runs/2026-10-18_045930_golden_set_v1_judge_v2_rerun_routed` (Routed Tutor, Router `router_v2`,
Course Tutor `tutor_v2`, app model `deepseek-flash`, thinking off, judge `openai/gpt-oss-20b` with
`judge_supported_v2` and `judge_responsive_v1`, `--workers 2`, commit `3f66605`). This is the same configuration as
`2026-10-18_040522_golden_set_v1_judge_v2_routed`, run again: nothing under `src/`, `prompts/`, `data/` or the Golden Set changed in between.
3 of 3 Runs and 108 of 108 Traces finished. No Trace recorded an error, and no judge call failed. A case fails in a run when its Trace
fails End-to-end Success.

Observable facts only; the group names the failures. The Category column takes the nearest category from
`evaluation/FAILURE_TAXONOMY.md`. The judge's evidence for each failed verdict is in the Trace's `judge` field in
`run_N.json`.

| Case | Type | Question | Expected | Category | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|---|---|
| GS-05 (failed 3/3) | near_miss | What did the Microsoft and Carnegie Mellon study of knowledge workers suggest about using AI? | Accepted Courses: GAIF. Expected Sections: GAIF-1.7. No Refusal. | 1 Wrong Course chosen | Earliest failing Step: Search ("read AITB, not an Accepted Course"). Routed and read: AITB. Cited Sections: none. Answer: "This is not covered in the AITB material." (the Refusal). Also failed: Answer (gave the Refusal where an answer was expected). Error: none. | Same as Run 1: routed to AITB, the AITB Refusal, no citation. | Same as Run 1: routed to AITB, the AITB Refusal, no citation. |
| GS-24 (failed 1/3) | overlap | Why ask an AI for a table or a fixed schema instead of free text, and what can structure not guarantee? | Accepted Courses: PEID, AITB. Expected Sections: PEID-2.7, AITB-2.6, AITB-2.4. No Refusal. | 5 Claim beyond the Section (the sentence is also uncited, as in 6) | Passed. Routed and read: AITB. Cited Sections: AITB-2.4, AITB-2.6. | Earliest failing Step: Answer ("judged not Supported: The claim "Structure does not guarantee accuracy or grounding" is not fully supported: the cited sections state that a table can still contain errors and must be compared with the source, but they do not mention grounding."). Routed and read: AITB. Cited Sections: AITB-2.4, AITB-2.6. Answer begins: "Structured outputs such as tables reduce editing, ease comparison and expose missing elements" and ends with the uncited sentence "Structure does not guarantee accuracy or grounding." Judge: Supported FAIL, Responsive PASS. Error: none. | Passed. Routed and read: AITB. Cited Sections: AITB-2.4, AITB-2.6. |
| GS-27 (failed 3/3) | overlap | What is shadow AI, and why should a company worry about it? | Accepted Courses: AITB, DTGS. Expected Sections: AITB-1.1, DTGS-3.7. No Refusal. | 4 Answers, then says it is not in the material | Earliest failing Step: Answer ("judged not Responsive: … the answer merely states that the material does not define shadow AI or explain the concern, providing no definition or rationale."). Routed and read: DTGS. Cited Sections: DTGS-3.7. Answer begins: "Shadow AI is mentioned only as a risk of the off-the-shelf tool rung (licensed assistant or copilot)…" and ends with "This is not covered in the DTGS material." Judge: Supported PASS, Responsive FAIL. Error: none. | Earliest failing Step: Answer (judged not Responsive, same reason). Routed and read: DTGS. Cited Sections: DTGS-3.7. Answer begins: "Shadow AI is mentioned only as a risk of the off-the-shelf tool rung:" and ends with the DTGS Refusal sentence. Judge: Supported PASS, Responsive FAIL. Error: none. | Earliest failing Step: Answer (judged not Responsive, same reason). Routed and read: DTGS. Cited Sections: DTGS-3.7. Answer begins: "Shadow AI is mentioned only as a risk of the off-the-shelf tool rung of the make-or-buy ladder:" and ends with the DTGS Refusal sentence. Judge: Supported PASS, Responsive FAIL. Error: none. |

Compared with the first run of this configuration: GS-05 and GS-27 fail 3/3 in both. GS-06 (1/3, a claim beyond
PEID-3.13) and GS-10 (1/3, judge timeout) passed 3/3 this time. GS-24 is new at 1/3: the same kind of failure the calibration noted
for `judge_supported_v2` on the tuning items ("adds a word such as grounding").
