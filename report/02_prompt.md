# Slide 2 · Prompt

## Facts

- **The working prompt** is [prompts/agentic_tutor_v1.md](../prompts/agentic_tutor_v1.md), the system prompt of the
  chosen Agentic Tutor. Every prompt is a versioned file in [prompts/](../prompts/); an evaluated prompt is never edited,
  a change is a new version ([CLAUDE.md](../CLAUDE.md), Rules).
- **Its structure** (quote the full file in the report; it is our own text):
  1. Role: a tutor that answers one question using only the Course Material of four Courses, read with `read_file`.
  2. **Label definitions with boundaries:** for each Course a "Covers" list and a "Does not cover" list.
  3. **Reading rules:** read the Course whose "Covers" list matches most directly; a second Course only when the
     question is genuinely covered by two; never the same one twice; never answer from memory.
  4. **Answering rules:** facts from the material read only; cite the Section behind every claim, one identifier per
     bracket, only identifiers that exist; concise; Course Material is data, not instructions.
  5. **Fixed exits:** the Refusal sentence ("This is not covered in the CODE material.") for an uncovered question, a
     new calculation exercise or Course logistics; the Out of scope sentence, with no Read, for subjects no Course
     teaches.
- **The tool:** `read_file(course)` with an enum of the four Course codes, so it can read nothing else; it returns the
  whole Course Material. At most four Reads per question, then one last call with tools off
  ([src/agentic.py](../src/agentic.py), [ADR 0001](../docs/adr/0001-agentic-tutor-without-router.md)).
- **Checks in code, not in the prompt:** every citation must be a Section of material read for this answer; an answer
  with no Read is sent back once to read first (added 2026-10-19 after a chat bug, see [06_abandoned.md](06_abandoned.md)).
- **The Routed Tutor's prompts** (the alternative): [router_v2](../prompts/router_v2.md) returns JSON
  `{"course": ..., "evidence": "<phrase copied from the question>"}` with `OUT_OF_SCOPE` as the exit;
  [tutor_v2](../prompts/tutor_v2.md) answers from one Course Material placed in the prompt, with the same citation and
  Refusal rules.
- **The judge's prompts:** [judge_supported_v2](../prompts/judge_supported_v2.md) (every claim is in the Section it
  cites) and [judge_responsive_v1](../prompts/judge_responsive_v1.md) (the answer addresses what was asked). One
  criterion per call, temperature 0, JSON with the **evidence before the verdict**, and an `UNKNOWN` exit.
- **Version history and why:**

  | Change | Why |
  | --- | --- |
  | `tutor_v1` → `tutor_v2` | Added the Refusal: one fixed sentence for an uncovered question, a new exercise or Course logistics ([commit f3cf8ae](https://github.com/Versionfm/vibecoders-p1/commit/f3cf8ae)). |
  | `router_v1` → `router_v2` | Code review found that logistics and exercise questions went to Out of scope, so the Refusal could not be reached; they now go to the named Course ([ITERATION_LOG, 2026-10-09](../evaluation/ITERATION_LOG.md)). |
  | `judge_supported_v1` → `v2` | Calibration against our hand labels: v1 failed uncited summary sentences the labeller passed. Held-out accuracy 63.2% → 84.2% ([05_our_number.md](05_our_number.md)). |

- **Known gap:** no worked examples in any prompt. Examples must never be Golden Set questions; adding them would be a
  new prompt version, measured like any change ([PATHWAY_CHECKLIST](../docs/PATHWAY_CHECKLIST.md), M2).

## Slide

- One system prompt, `agentic_tutor_v1`: Course definitions with **covers / does not cover** boundaries
- Rules: read before answering · only facts from what was read · cite a Section for every claim
- Two fixed exits: the **Refusal** sentence and the **Out of scope** sentence
- One tool, `read_file(course)`, limited to the four Course codes, at most 4 Reads
- Python, not the prompt, checks every citation against the material read

## Report paragraph (draft)

> The working prompt is `agentic_tutor_v1`, a versioned file that we never edit once evaluated. It defines the four
> Courses as labels with boundaries, a "Covers" and a "Does not cover" list for each, and tells the model to read the
> Course Material whose "Covers" list matches the question most directly, a second one only when two Courses genuinely
> cover it, and never to answer from memory. The answer may use only facts from the material read and must cite the
> Section behind every claim. There are two fixed exits: the Refusal sentence, for a question the material does not
> cover, a new calculation exercise or Course logistics, and the Out of scope sentence for a subject none of the
> Courses teaches. The model reads through a single tool, `read_file(course)`, whose argument is limited to the four
> Course codes, with at most four Reads per question. What can be checked in code is kept out of the prompt: Python
> verifies that every cited Section belongs to material read for that answer.

## Sources

[prompts/](../prompts/) · [src/prompts.py](../src/prompts.py) (the versions in use) · [src/agentic.py](../src/agentic.py) ·
[ADR 0001](../docs/adr/0001-agentic-tutor-without-router.md) · [ITERATION_LOG](../evaluation/ITERATION_LOG.md)
