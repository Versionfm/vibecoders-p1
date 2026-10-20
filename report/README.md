# Material for the report and the deck

Facts, numbers and draft text for the final report and the six-slide deck, gathered from the repository in one place.
Every fact links to its source in the repo; the slide bullets and report paragraphs are drafts for the group to edit.
When a number here and its source disagree, the source wins.

## Deadline and limits

- **Due 20 October 2026, 18:00:** report, deck and public repository. No commits after the deadline.
- **Deck:** at most 6 slides, in this order: idea · prompt · how we steered the coding assistant · failure taxonomy
  and Golden Set · our number · what we abandoned. Presentation: 8 minutes (about 4 on slides, 4 live demo) plus 2 for
  questions; keep a backup recording of the demo.
- **Report:** at most 5 pages including screenshots, no appendices. It must show: screenshots, the actual prompts, the
  dataset, the evaluation method and result, what did not work, and the repo link.

Source: [docs/PATHWAY_CHECKLIST.md](../docs/PATHWAY_CHECKLIST.md) (the professor's checklist in our words) and
[docs/WORKFLOW_ITERATIONS.md](../docs/WORKFLOW_ITERATIONS.md#what-the-project-brief-requires).

## Map: slide → file → report section

| Slide | File | Report section it feeds |
| --- | --- | --- |
| 1 Idea | [01_idea.md](01_idea.md) | Problem, the app, screenshots |
| 2 Prompt | [02_prompt.md](02_prompt.md) | The actual prompts |
| 3 Steering the coding assistant | [03_steering.md](03_steering.md) | How we built it (process, steering files and their effect) |
| 4 Failure taxonomy and Golden Set | [04_failures_and_golden_set.md](04_failures_and_golden_set.md) | Dataset; failure taxonomy |
| 5 Our number | [05_our_number.md](05_our_number.md) | Evaluation method and result |
| 6 What we abandoned | [06_abandoned.md](06_abandoned.md) | What did not work; next steps |

Screenshots of the app (real answers from `deepseek-flash`; the answer screens taken 2026-10-19 with `agentic_tutor_v1`, the Out of scope screen 2026-10-20 with `agentic_tutor_v3`; the answer path did not change between them):

| File | Shows |
| --- | --- |
| [agentic_chat_1_answer.jpg](screenshots/agentic_chat_1_answer.jpg) | Agentic Tutor chat: "What does temperature do when a model samples its next token?" → "Course Materials read: PEID", the answer, Cited Sections: PEID-1.3; the follow-up question below |
| [agentic_chat_2_follow_up.png](screenshots/agentic_chat_2_follow_up.png) | The follow-up "And top-p, which you mentioned, how is it different?" answered from a new Read of PEID |
| [agentic_out_of_scope.png](screenshots/agentic_out_of_scope.png) | "Who are you?" on the Agentic chat (2026-10-20, `agentic_tutor_v3`): Course: Out of scope and the purpose notice, no Answer, no Read |
| [routed_screen.png](screenshots/routed_screen.png) | Routed Tutor screen, same question: the Router's Course and evidence phrase, the answer, Cited Sections |

## Facts only the report needs

- **Repo:** https://github.com/Versionfm/vibecoders-p1 (still **private** on 2026-10-19: make it public before
  submitting).
- **App model:** `deepseek-flash` (DeepSeek-V4.1-Flash) on the DeepSeek API, thinking off, temperature 0. The group's
  own DeepSeek key, in a local `.env` only ([README](../README.md#add-your-api-key-locally)). The professor's endpoint
  (`course-chat`) was probed twice and not adopted ([06_abandoned.md](06_abandoned.md)).
- **Judge model:** `openai/gpt-oss-20b` on the NVIDIA endpoint, a different model family from the app model
  ([ITERATION_LOG, 2026-10-17](../evaluation/ITERATION_LOG.md)).
- **Coding assistant:** Claude Code, not GitHub Copilot. The brief's `AGENTS.md`, `.github/skills/` and `.github/agents/`
  are, for us, [CLAUDE.md](../CLAUDE.md), [.claude/skills/](../.claude/skills/) and [.claude/agents/](../.claude/agents/).
  The report must say so ([PATHWAY_CHECKLIST](../docs/PATHWAY_CHECKLIST.md)).
- **Stack:** Python, Streamlit (one screen), the OpenAI-compatible client, standard-library `unittest` (209 tests, no
  network). No agent framework: the Agentic Tutor is a plain Python loop ([ADR 0001](../docs/adr/0001-agentic-tutor-without-router.md)).
- **Committers:** Francisco Malhado and Gonçalo Augusto (`git log`). Golden Set reviewers: Gonçalo Augusto and Rodrigo.

## Open items for the group

- [ ] **Team roles** (app; data, demo inputs and Golden Set; steering files and report log): not written anywhere in the
      repo. Write them in the report.
- [ ] **Screenshots of the steering evidence**: the final messages of sessions A and B2 and the skill call of session D2
      ([03_steering.md](03_steering.md)).
- [ ] **Confirm or rename the failure categories** in [FAILURE_TAXONOMY.md](../evaluation/FAILURE_TAXONOMY.md): the
      names were drafted by the coding assistant; the brief wants them in our own words.
- [ ] **Make the repo public** and check that the secrets scan is green (`.env` is not in the history).
- [ ] **Rehearse with a timer** and record a backup of the demo. Run the demo with `TUTOR=agentic` in `.env` (the
      code falls back to `routed` when unset).
- [ ] **Pick the screenshots** for the report from [screenshots/](screenshots/) (four app captures).
