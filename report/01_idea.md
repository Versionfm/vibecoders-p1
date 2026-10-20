# Slide 1 · Idea

## Facts

- **Problem:** a student of our degree has questions about four Courses and needs answers that come from that Course's
  material, with a pointer to where it says so, not from the model's general knowledge.
  ([README](../README.md), first paragraph.)
- **The product:** a one-screen tutor for four Courses. Every answer comes only from the group's own Course Material
  and cites the Section behind each claim, e.g. `[PEID-2.3]`. A question the material does not cover gets a fixed
  **Refusal** ("This is not covered in the PEID material."); a subject none of the Courses teaches gets **Out of
  scope**.
- **The four Courses:** GAIF (Generative AI Foundations), PEID (Prompt Engineering and Interaction Design), AITB
  (AI Tools for Business Professionals), DTGS (Digital Transformation and Generative AI Strategy).
- **Course Material:** written by the group in its own words, about 22,500 words in 167 numbered Sections (GAIF 22,
  PEID 63, AITB 41, DTGS 41), frozen in [data/courses/](../data/courses/).
- **Without the LLM call there is no product:** no Course is chosen, no answer is written, no Section is cited.
- **The chosen tutor, the Agentic Tutor chat:** one model reads the Course Material it needs with a `read_file(course)`
  tool, answers with citations, and keeps the conversation so a student can ask a follow-up
  ([ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md), [workflow](../docs/AGENTIC_TUTOR_WORKFLOW.md)).
  The **Routed Tutor** (a Router picks one Course, then the Course Tutor answers) stays in the code as the measured
  alternative.
- **One question, step by step:** student message → the model calls `read_file("PEID")` → Python returns the whole
  PEID Course Material → the model answers with Section citations → Python checks every cited Section was in material
  read for this answer → the screen shows the answer with a **Cited Sections** footer (and a warning for any invalid
  citation).
- **Citations on screen (2026-10-19):** the screen hides the inline markers and lists the Sections once under Cited
  Sections. Evaluation, saved Traces and follow-up context keep the original answer with citations beside its claims
  ([ITERATION_LOG](../evaluation/ITERATION_LOG.md), "Consolidate displayed citations").
- **Why the chat, honestly:** we chose it for teaching through conversation, although it scores lower than the Routed
  Tutor on single questions; better learning has not been measured ([ADR 0003, Presentation wording](../docs/adr/0003-keep-agentic-chat-for-teaching.md#presentation-wording)).

## Slide

- A tutor for our four Courses that answers **only from our Course Material** and cites the Section behind each claim
- Says "not covered" instead of guessing; says "out of scope" for subjects we do not teach
- A chat: the tutor reads the Course it needs, answers, and takes follow-up questions
- Screenshots: [first answer](screenshots/agentic_chat_1_answer.jpg) and [a follow-up](screenshots/agentic_chat_2_follow_up.png)

## Report paragraph (draft)

> Course Tutor is a one-screen chat for the four Courses of our degree (GAIF, PEID, AITB and DTGS). It answers a
> student's question only from Course Material the group wrote in its own words, about 22,500 words in 167 numbered
> Sections, and cites the Section behind every claim, for example [PEID-2.3]. When the material does not cover a
> question it gives a fixed Refusal, and for a subject none of the Courses teaches it says the question is out of
> scope. The model reads the Course Material it needs through a `read_file(course)` tool; Python checks that every
> cited Section belongs to material read for that answer and lists the Sections under the answer. Without the model
> call there is no product: nothing chooses the Course, writes the answer or finds the Sections. We kept the chat
> because our purpose is teaching through conversation, even though a simpler Routed Tutor scores higher on single
> questions (slide 5).

## 90-second demo script

1. `TUTOR=agentic` in `.env`, `streamlit run src/app.py`.
2. Ask an in-material question, e.g. "What is a golden set?" → "Course Materials read: PEID", a cited answer, the
   Cited Sections footer.
3. Follow up: "Where does it fail and what does it protect against?" → the tutor reads PEID again for the follow-up.
4. Ask something no Course teaches, e.g. "How do I bake bread?" → Out of scope, no Read.
5. Ask "When is the DTGS exam?" → the Refusal after reading DTGS.

Use demo questions that are **not** Golden Set questions, so the demo is not mistaken for the evaluation.

## Sources

[README.md](../README.md) · [ADR 0001](../docs/adr/0001-agentic-tutor-without-router.md) ·
[ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md) · [AGENTIC_TUTOR_WORKFLOW.md](../docs/AGENTIC_TUTOR_WORKFLOW.md) ·
[CONTEXT.md](../CONTEXT.md) · [data/courses/](../data/courses/)
