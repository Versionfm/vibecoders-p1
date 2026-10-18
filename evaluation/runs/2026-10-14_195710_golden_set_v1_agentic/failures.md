# Failing cases: Agentic Tutor on Golden Set v1, deepseek-flash

Run folder: `evaluation/runs/2026-10-14_195710_golden_set_v1_agentic` (Agentic Tutor, prompt `agentic_tutor_v1`,
app model `deepseek-flash`, thinking off, no judge, `--workers 3`, commit `b6f0a43`). 3 of 3 Runs and 108 of 108
Traces finished; no Trace recorded an error and no Trace reached the Read limit. A case fails in a run when its
Trace fails End-to-end Success. The Answer Step is a code check only (no judge yet), so a case that passes here can
still have unsupported claims.

Observable facts only; the group names the failures. `evaluation/FAILURE_TAXONOMY.md` does not exist yet, so there is
no category column.

"Course" below is the `course` field stored in `run_N.json` (the Course the Agentic Tutor answered for). When it is
empty, `report.md` shows `error` in its Routed column, although the Trace's `error` field is empty.

| Case | Type | Question | Expected | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|---|---|
| GS-05 (failed 3/3) | near_miss | What did the Microsoft and Carnegie Mellon study of knowledge workers suggest about using AI? | Accepted Courses: GAIF. Expected Sections: GAIF-1.7. No Refusal. | Earliest failing Step: Search ("read AITB, not an Accepted Course"). Reads: `read_file("AITB")` only (1 Read). Course: AITB. Cited Sections: none. Answer: "This is not covered in the AITB material." (the Refusal). Error: none. | Same as Run 1: Search; read AITB only; no citations; the AITB Refusal; no error. | Same as Run 1: Search; read AITB only; no citations; the AITB Refusal; no error. |
| GS-13 (failed 3/3) | in_material | What happened with Klarna's AI customer service assistant after its launch? | Accepted Courses: DTGS. Expected Sections: DTGS-3.20. No Refusal. | Earliest failing Step: Search ("read AITB, not an Accepted Course"). Reads: DTGS then AITB (2 Reads; extra Read: AITB). Course: DTGS. Cited Sections: DTGS-3.20. Answer: "Klarna's customer-service deployment is covered in the DTGS material:" followed by a list citing DTGS-3.20. Path and Answer Steps passed. Error: none. | Search, same reason. Reads: DTGS then AITB (extra Read: AITB). Course: DTGS. Cited Sections: DTGS-3.20, DTGS-3.18. Answer: "The Klarna case is covered in the DTGS material:" followed by a list citing DTGS-3.20. Path and Answer Steps passed. Error: none. | Search, same reason. Reads: AITB only (1 Read; DTGS not read). Course: AITB. Cited Sections: none. Answer: "This is not covered in the AITB material." (the Refusal). Answer Step failed ("gave the Refusal where an answer was expected"). Error: none. |
| GS-15 (failed 3/3) | near_miss | For a company, how do retrieval and fine-tuning compare in cost, time to value and risk, and when does each one fit? | Accepted Courses: DTGS. Expected Sections: DTGS-3.7. No Refusal. | Earliest failing Step: Search ("read PEID, not an Accepted Course"). Reads: DTGS then PEID (2 Reads; extra Read: PEID). Course: DTGS. Cited Sections: DTGS-3.7, DTGS-3.10, DTGS-3.6, DTGS-3.8. Answer: "Comparing retrieval and fine-tuning as ways to put a model into a process is a make-or-buy decision, which is covered in DTGS." Path and Answer Steps passed. Error: none. | Search, same reason. Reads: DTGS then PEID (extra Read: PEID). Course: DTGS. Cited Sections: none. Answer: "This is not covered in the DTGS material." (the Refusal). Answer Step failed ("gave the Refusal where an answer was expected"). Error: none. | Same as Run 2: Search; read DTGS then PEID; no citations; the DTGS Refusal; no error. |
| GS-33 (failed 3/3) | refusal | Using Hebb's rule with bipolar inputs, compute the final weights and bias after training on the OR function. | Accepted Courses: GAIF. The Refusal (new exercise). | Earliest failing Step: Search ("no Course Material read"). Reads: none (0 Reads). Course: empty. Cited Sections: none. Answer: "This is a request to solve a new calculation exercise, so I must refuse." followed by "This is not covered in the GAIF material." Not counted as the Refusal (`is_refusal` false: the Refusal sentence is preceded by another sentence). Path Step failed ("answered without reading any Course Material"); Answer Step failed ("expected the Refusal"). Error: none. | Same as Run 1: Search; no Read; same two sentences; Path and Answer failed; no error. | Same as Run 1, first sentence "This is a new calculation exercise, so I must refuse."; no Read; Path and Answer failed; no error. |
| GS-35 (failed 3/3) | refusal | How do I assign Microsoft 365 Copilot licences to my team in the admin centre? | Accepted Courses: AITB. The Refusal (product how-to outside the Course Material). | Earliest failing Step: Search ("no Course Material read"). Reads: none (0 Reads). Course: OUT_OF_SCOPE. Cited Sections: none. Answer: "This question is outside the four Courses." (the Out of scope sentence). Path Step passed; Answer Step failed ("expected the Refusal"). Error: none. | Same as Run 1: Search; no Read; the Out of scope sentence; no error. | Same as Run 1: Search; no Read; the Out of scope sentence; no error. |

Notes (facts, not failures in this run):

- Read behaviour over all 108 Traces: 85 Traces made 1 Read, 5 made 2 Reads (GS-13 runs 1 and 2, GS-15 runs 1 to
  3), 18 made no Read (GS-29 to GS-32, GS-33 and GS-35, 3 runs each). No Course Material was read twice in a Trace
  and no Trace reached the Read limit. Reads of a Course that is not an Accepted Course: 9 Traces (GS-05 x3, GS-13
  x3, GS-15 x3).
- Compared with the Agentic Tutor pilot on the candidates (`2026-10-14_120227_pilot_deepseek_agentic`), on cases
  whose question and labels are unchanged: GS-05 and GS-35 failed 3/3 in both; GS-13 failed 1/3 in the pilot (an
  extra Read of AITB) and 3/3 here; GS-33 failed 2/3 in the pilot (it read GAIF and gave the exact Refusal in
  pilot run 2) and 3/3 here.
- GS-15 is a new question in Golden Set v1; the pilot's different GS-15 question also failed 3/3 (read PEID only).
  GS-36 is a new question (Lewin's change model) and passed 3/3 here with a DTGS Read and the DTGS Refusal; the
  pilot's GS-36 question gave the Out of scope sentence 3/3.
- The Routed Tutor on the same file (`2026-10-14_193513_golden_set_v1_routed`) passed GS-13, GS-15, GS-33 and GS-35
  3/3 and failed GS-05 3/3 in the same way (AITB, then the AITB Refusal). See `compare.html` in this folder.
