# Loop instruction live probe — 20 October 2026

Tested the application's `answer_question(..., tutor="agentic", history=...)` with the configured DeepSeek `deepseek-flash` model, thinking off, temperature 0. No UI automation or judge was used. User explicitly authorized transmission of the pasted conversation and relevant Course Material to DeepSeek.

Two variants used the same seed: the first two completed exchanges in the supplied transcript (initial question reconstructed as “Talk to me about gradient descent”). Each then continued independently through “What is adaline”, “You can t answer the adaline question?”, and “Why are you looping”. Each successful result entered that variant's history, matching the app's behavior. One three-turn continuation per variant; this is a focused reproduction, not a repeated evaluation or Golden Set score.

The baseline used unchanged agentic_tutor_v3. The other variant appended this exact instruction to the system message on every model call, without editing the selected prompt:

> Answer the latest user message. Use earlier messages as context, without treating the original question as a permanent task. If the user reports repetition or challenges your answer, address that feedback directly and reconsider your interpretation.

## Observed result

The proposed instruction did not resolve the loop. In the added-instruction variant, all three turns produced an initial answer addressing Adaline or acknowledging repetition, but requested no Read. The app therefore appended its existing READ_FIRST recovery message as a new user message. That message begins “Reconsider the original student request”. The model then requested GAIF and returned the gradient-descent explanation, explicitly referring to the original gradient-descent request on the latter two turns.

The baseline reproduced the reset on the first and third follow-ups. Its middle follow-up requested a Read immediately and returned an Adaline explanation without triggering recovery. All six final results had no application error, read GAIF once, and had no invalid citations. Those checks do not establish answer responsiveness or factual support.

This directly identifies the recovery path as a failure mechanism in these recorded traces. It does not prove this is the only cause of looping. A next fix should explicitly bind recovery to the current question rather than using the ambiguous “original student request”, and preserve the fresh-material-read requirement. That fix has not been implemented or tested.

## Evidence and limits

`baseline.json` and `added_instruction.json` preserve seed history, final TutorResults, timing, every model request message and returned content/tool calls. The JSON result's prompt-version field remains agentic_tutor_v3; the top-level variant and instruction distinguish the experimental system append. No API keys are recorded.

The initial sandbox attempt failed to connect; those results were superseded by the successful authorized network run. No evaluated prompt, runtime source, Course Material, Golden Set, or labels were modified. No broader regression or UI tests were run.
