# Label corrections: from `labels.md` to `labels_corrected.md`

`labels.md` holds the labeller's first labels (Gonçalo Augusto, 2026-10-18) and stays unchanged. After the first
calibration report, the labeller noticed that several Supported FAILs gave reasons about how the answer is written or
whether it answers, not about a claim missing from its cited Section, and asked the coding assistant to move each of
the six FAIL labels to the criterion its own reason describes, using the definitions at the top of `labels.md`:

- **Supported**: a claim in the answer is not in the Section it cites, goes beyond it or contradicts it.
- **Responsive**: the answer does not address what the question asked.
- **Neither** (a style note): a preference about how the answer is written. Labelled PASS on both criteria; the
  reason is kept below for the failure taxonomy.

This was done after the judge's verdicts had been seen in the first report, so both versions are reported and the
corrected one is marked as such. No PASS label was changed, and no FAIL label was removed without being moved or
recorded here.

| Item | Case | Labeller's reason | First labels (Supported / Responsive) | Corrected | Why |
|---|---|---|---|---|---|
| L01 | GS-27 | Overexplains and shouldn't mention the course name. | FAIL / PASS | PASS / PASS, style note | About how the answer is written, not a claim missing from a Section. |
| L06 | GS-27 | It answers and at the end it says that it couldn't be found in the material. | FAIL / PASS | unchanged | The closing claim that the material does not cover it contradicts the cited Section: Supported. |
| L07 | GS-27 | Overexplains and shouldn't mention the course name. | FAIL / PASS | PASS / PASS, style note | As L01. |
| L18 | GS-28 | It should build an answer, not saying the material says x y z. | FAIL / PASS | PASS / PASS, style note | About framing ("the material says"), not a missing claim. |
| L20 | GS-24 | Should write a full answer and not split into two answers. | FAIL / PASS | PASS / PASS, style note | About structure; both parts of the question are answered. |
| L25 | GS-02 | It doesn't actually answer; the content is accurate and related but there's no answer. | FAIL / PASS | PASS / FAIL | "Accurate content but no answer" is the definition of not Responsive. |

## Style notes (input for the failure taxonomy, not for the judge)

- Over-explaining and naming the Course in the answer (L01, L07, both GS-27).
- Reporting what "the material says" instead of answering directly (L18, GS-28).
- Splitting one answer into two separate answers (L20, GS-24).

## Outcome: the corrections were abandoned (2026-10-18)

Re-judged with `judge_supported_v2`, three of the four answers moved to PASS here were judged not Supported for a
concrete claim: L07 (a claim about how the material "frames" shadow AI that DTGS-3.2 does not make), L18 (Klarna
claims cited to DTGS-3.21 but stated only in DTGS-3.20) and L20 ("format is one of the six elements of a request",
not in the cited AITB-2.4). The labeller's first FAIL labels on those answers were right; the reasons written next
to them described something else. The official labels for the calibration are therefore the first labels in
`labels.md`, labelled without seeing the judge, unchanged. `labels_corrected.md` and its reports are kept as the
record of this attempt.
