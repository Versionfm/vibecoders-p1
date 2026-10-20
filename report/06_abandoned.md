# Slide 6 · What we abandoned (and what we kept)

Every evaluated change is in [evaluation/ITERATION_LOG.md](../evaluation/ITERATION_LOG.md) (28 entries), including the
abandoned ones, with its configuration, run folder, result and reason. The brief asks for at least one change tried,
measured and abandoned with its reason.

## Facts: abandoned, with the reason

| Date | Tried | Measured | Why abandoned |
| --- | --- | --- | --- |
| 2026-10-09 | App model `nemotron-3.5-lightning` | Model probe of 10 questions: **both answers had no citation at all**, in both probes; one Router reply was not valid JSON (5/6) | An answer without a citation fails End-to-end Success by definition; `nemotron-3-super` was as fast and cited correctly |
| 2026-10-14 | Golden Set candidates on the NVIDIA endpoint | Run 1 hit HTTP 429 after about 50 calls in 18 s; about 22 of 108 Traces answered | The endpoint's rate limit is below what an evaluation needs. Led to the move to DeepSeek (kept) |
| 2026-10-14 | The professor's endpoint (`course-chat`) | Plain answers worked; native tool calls returned 404; the thinking switch returned 400; the model behind it was not disclosed | The Agentic Tutor would need a rewrite, the endpoint is shared by the class, and we could not name the model in the report |
| 2026-10-18 | `course-chat` again, after the professor fixed the proxy | Tool calls and the Agentic Tutor worked on four throwaway questions | Not adopted: both tutors were already measured on `deepseek-flash`, with no time to measure again under 30 requests per minute before the deadline. Not a quality comparison |
| 2026-10-18 | **The Agentic Tutor as the app's tutor (#17)** | End-to-end Success 85.2% vs 90.7% (judge v1), then 87.0% vs 92.6% (calibrated judge), against the Routed Tutor | Abandoned twice on the measurement: the gap is extra Course Reads. **Then selected on 2026-10-19 for teaching** ([ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md)): see below |
| 2026-10-18 | **Correcting our own labels** after seeing the judge (moving five Supported FAILs to the criterion their written reason described) | With corrected labels, held-out Supported agreement fell (57.9% with v1, 68.4% with v2, against 84.2% with the first labels and v2) | The judge's evidence showed three of the first FAILs were right. Changing labels after seeing the judge would move the score toward the judge. The first, blind labels stay official |

Sources: the [iteration log](../evaluation/ITERATION_LOG.md) entries of those dates; probe files in
[evaluation/probes/](../evaluation/probes/).

## Facts: kept, and why it matters to the story

- **`judge_supported_v1` → `v2`:** v1 failed uncited summary sentences that our labeller passed; v2 (revised on the 9
  tuning answers only) raised held-out Supported accuracy from 63.2% to 84.2% (kappa 0.13 → 0.56). Kept.
- **Nemotron Super → `deepseek-flash`:** concurrency limit instead of a per-minute cap, native tool calls, a named
  model; cheap. Kept for both tutors, so the comparison changes only the tutor. The judge then had to come from
  another family: `openai/gpt-oss-20b`, chosen by a probe with deliberately wrong answers (it caught 4/4 swapped
  Sections and 4/4 wrong questions).
- **Choosing the Agentic Tutor chat despite the lower score (ADR 0003):** a product decision for teaching through
  conversation, stated as such: "It scored 87.0% on our single-question evaluation, compared with 92.6% for the Routed
  Tutor. We accepted that tradeoff to support follow-up questions and clarification." The earlier "abandoned" entries
  stay as the record. Present it as it actually happened: measured, abandoned, then chosen for a reason the
  measurement does not cover.
- **The read-first guard (2026-10-19), found in the chat:** a follow-up was sometimes answered from the conversation
  alone, with no Read, so every citation was correctly flagged invalid. The loop now sends such an answer back once to
  read first. Measured on the Golden Set: 87.0% → 85.2%, inside the variation, and the guard never fired on single
  questions. Kept, because the Golden Set cannot see the follow-up case it fixes.
- **Citations only in the footer (2026-10-19):** presentation only. The screen hides the inline markers; evaluation,
  saved Traces and follow-up context keep the original cited answer. An offline check over all 216 saved Traces showed
  answers, judge inputs, Steps and reports unchanged, so no new evaluation was needed. Not a claim of better readability.

## Next steps (not made)

- A multi-turn evaluation set (follow-ups, clarification, a change of Course), human-reviewed, beside Golden Set v1.
- `router_v3` / a "Covers" fix for the GAIF gap behind GS-05 (category 1).
- A tutor prompt that answers directly, never ends with the Refusal sentence and does not name the Course (categories
  4, 5 and the style notes).
- Worked examples in the prompt (never Golden Set questions), measured as a new version.
- Record latency in the Traces; a second labeller for the judge.
- Observed on 2026-10-19 while taking the screenshots: asked "Can you explain that more simply?", the chat repeated its
  first answer almost word for word. The prompt asks for facts from the material only, so a simpler explanation is not
  encouraged. One observation, not measured: a reason for the multi-turn evaluation above.

## Slide

- **Abandoned:** Nemotron Lightning: answers with **no citations** → switched model
- **Abandoned:** the professor's endpoint: no native tool calls, undisclosed model
- **Abandoned:** correcting our labels after seeing the judge: it moved the score toward the judge
- **Measured, abandoned, then chosen:** the Agentic chat, 87.0% vs 92.6%, kept for teaching (ADR 0003)
- **Next:** multi-turn evaluation · fix the GAIF "Covers" gap · a tutor prompt that answers directly

## Report paragraph (draft)

> Not everything we tried stayed. The first app model, Nemotron Lightning, returned answers without a single citation
> in our model probe, which fails our metric by definition, so we moved to Nemotron Super and later to DeepSeek when the
> NVIDIA endpoint's rate limit made a full evaluation impossible. We probed the professor's course endpoint twice and
> did not adopt it: at first it had no native tool calls, and the model behind it was not disclosed. In calibrating the
> judge, we tried correcting our own labels after seeing its verdicts; agreement fell, and the judge's evidence showed
> three of our first FAILs had been right, so we abandoned the corrections and kept the blind labels. The largest
> decision went both ways: measured against the Routed Tutor, the Agentic Tutor lost twice (87.0% against 92.6% with
> the calibrated judge), and we recorded it as abandoned. We then chose it anyway for the app, because our purpose is
> teaching through conversation and the Routed screen takes only isolated questions. We report that tradeoff rather
> than hide it. Using the chat revealed a gap the Golden Set could not: follow-ups answered from the conversation
> alone, without reading any Course Material. We fixed it in code and measured that single questions did not change.

## Sources

[ITERATION_LOG.md](../evaluation/ITERATION_LOG.md) · [ADR 0003](../docs/adr/0003-keep-agentic-chat-for-teaching.md) ·
[evaluation/probes/](../evaluation/probes/) · [calibration/](../evaluation/calibration/) ·
[FAILURE_TAXONOMY.md](../evaluation/FAILURE_TAXONOMY.md)
