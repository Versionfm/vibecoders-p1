---
status: accepted
date: 2026-10-19
---

# Keep the Agentic Tutor chat for teaching

We choose the Agentic Tutor chat as the project's teaching experience and presentation demo, despite its lower
End-to-end Success on the current Golden Set. The purpose is to help students learn through a conversation:
follow-up questions, clarification and explanations that build on previous exchanges matter to that purpose.
This is a product decision based on the group's teaching goal, not a claim that the chat won the evaluation or
has been shown to improve learning.

This decision supersedes the tutor-selection rule in [ADR 0001](0001-agentic-tutor-without-router.md) and the
18 October iteration-log decisions to abandon the Agentic Tutor. Those entries remain as the historical record;
the measurements and scoring rules are unchanged.

## What the evaluation showed

The latest recorded comparison used Golden Set v1: 36 cases, three Runs per tutor, and 108 Traces per tutor.
Both used `deepseek-flash` with thinking off and the same judge, `openai/gpt-oss-20b`, with
`judge_supported_v2` and `judge_responsive_v1`.

| Metric | Routed Tutor | Agentic Tutor chat |
| --- | --- | --- |
| End-to-end Success, mean (range across Runs) | 92.6% (88.9% to 94.4%) | 87.0% (83.3% to 88.9%) |
| Search Step, mean | 97.2% | 91.7% |
| Path Step, mean | 100.0% | 100.0% |
| Answer Step, mean | 92.6% | 92.6% |

Sources: [Routed Tutor report](../../evaluation/runs/2026-10-18_040522_golden_set_v1_judge_v2_routed/report.md)
and [Agentic Tutor report](../../evaluation/runs/2026-10-18_113506_golden_set_v1_judge_v2_agentic/report.md).

The Agentic Tutor trails by 5.6 percentage points on End-to-end Success. The gap is mostly in Search: an extra
Read of a Course outside the Accepted Courses fails that Step even when the eventual answer passes. Six of its
14 failing Traces had this extra-Read pattern. We accept this measured weakness; we do not remove the rule or
relabel cases to favour the selected tutor. Equal mean Answer Step rates do not establish equal answer quality.

## Why keep the conversation

The current Routed Tutor screen handles isolated questions. The Agentic Tutor chat keeps completed exchanges
and sends them with a follow-up, allowing a student to refer to an earlier explanation instead of starting again.
For example, after an explanation the student can ask for clarification or a simpler explanation in the same
conversation. Each new answer still reads its own Course Material; earlier answers provide context, not evidence.
The implementation is described in [the workflow guide](../AGENTIC_TUTOR_WORKFLOW.md).

We consider this continuity a better fit for teaching than a sequence of independent questions. Its educational
benefit is our design rationale and remains a hypothesis to evaluate. The existing Golden Set supplies no chat
history and therefore does not measure follow-up interpretation, sustained explanations or learning outcomes.

Conversation and Course selection are separate choices: a chat interface could also be built around the Routed
Tutor. That alternative has not been implemented or compared here. We are selecting the existing Agentic Tutor
chat, not concluding that an agentic approach is inherently necessary for conversation.

## Consequences and next checks

- Use `TUTOR=agentic` for the chosen teaching experience and demo. The code's fallback when no tutor is configured
  remains `routed`; this decision record does not change runtime configuration.
- Keep the Routed Tutor available for comparison. Retain the earlier reports, failed outputs and iteration entries.
- Present 87.0% as the selected tutor's measured End-to-end Success, alongside the Routed Tutor's 92.6%, and explain
  that these are single-question results. Neither number is a measure of teaching effectiveness.
- Evaluate separate, human-reviewed multi-turn cases: references to earlier turns, clarification of a misunderstanding,
  simpler explanations and changes of Course. Check both conversational usefulness and support from Course Material.
  Keep Golden Set v1 intact so single-question regressions remain visible.
- Before claiming improved learning, measure whether students understand the material better after using the tutor.
  Multi-turn quality and learning outcomes are both unmeasured at this decision point. The current comparison also
  has only 36 cases, an imperfect judge calibrated with one labeller, and different code commits for the two tutors.

## Presentation wording

> We kept the Agentic Tutor chat because our purpose is to teach through conversation. It scored 87.0% on our
> single-question evaluation, compared with 92.6% for the Routed Tutor. We accepted that tradeoff to support
> follow-up questions and clarification. The current evaluation does not establish whether conversation improves
> learning; that is the next question to test.
