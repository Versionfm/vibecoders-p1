# Slide 3 · How we steered the coding assistant

## Facts

- **Tool:** Claude Code, not GitHub Copilot. The brief's files map to Claude Code's: `AGENTS.md` → [CLAUDE.md](../CLAUDE.md),
  `.github/skills/<name>/SKILL.md` → [.claude/skills/evaluate-course-tutor/SKILL.md](../.claude/skills/evaluate-course-tutor/SKILL.md),
  `.github/agents/<name>.agent.md` → [.claude/agents/evaluator.md](../.claude/agents/evaluator.md). Say this in the
  report ([PATHWAY_CHECKLIST](../docs/PATHWAY_CHECKLIST.md), M1).
- **The workflow:** a grilling session on the documentation → a written spec (GitHub issue #1) → tickets (#2–#8, then a
  second spec #10 for the Agentic Tutor with tickets #11–#17, and spec #20 with ticket #21 for the citation footer) →
  implementation ticket by ticket, each through the same answer function and tests
  ([WORKFLOW_ITERATIONS](../docs/WORKFLOW_ITERATIONS.md#iteration-1--requirements-to-a-working-prototype)).
- **The steering files and what each holds:**
  - [CLAUDE.md](../CLAUDE.md) (always on, 30 lines): the module layout and the project's rules: one screen only; never
    commit secrets; never edit an evaluated prompt, create the next version; never change the Golden Set or the human
    labels to move a score; log every evaluated change, including abandoned ones; Golden Set questions never in a
    prompt; Course Material frozen; tests through the seams, with fake models and no network.
  - [CONTEXT.md](../CONTEXT.md): the shared vocabulary (Course, Course Material, Section, Router, Course Tutor, Refusal,
    Golden Set, Trace, Step, ...), used in code, tests, prompts and commits.
  - The skill [evaluate-course-tutor](../.claude/skills/evaluate-course-tutor/SKILL.md): the evaluation procedure:
    pin the configuration, run the tests, run 3 Runs, read the failures, write the failure sheet, log the result,
    report back; and its boundaries (it measures and changes nothing it measures).
  - The sub-agent [evaluator](../.claude/agents/evaluator.md): runs that skill in its own context and may not change
    app code, prompts or labels.
  - Decision records in [docs/adr/](../docs/adr/), which later sessions read before changing the tutor.
- **Evidence 1, `CLAUDE.md` without and with it (2026-10-18):** two fresh sessions at the same commit (`e94f674`), same
  request ("add a second model call that rewrites the answer in simpler language"), plan mode. Session A had
  `CLAUDE.md` deleted; session B2 had it. Both plans followed the conventions visible in the code. **Only B2** applied
  the rules that exist only in `CLAUDE.md`: it ruled out a switch on the screen ("the one-screen rule forbids settings
  there") and planned to keep `CLAUDE.md`'s layout current. Our reading: by then most rules were built into the code, so
  `CLAUDE.md` adds the rules no file shows by example. One run per condition
  ([WORKFLOW_ITERATIONS, steering evidence](../docs/WORKFLOW_ITERATIONS.md#steering-evidence-2026-10-18)).
- **Evidence 2, the skill firing without being named:** "How are we doing on the Golden Set? Measure the Routed Tutor
  again." In session C the skill **did not** load: its description said what it does, not how people ask. We changed
  the description to name such requests ([commit 3f66605](https://github.com/Versionfm/vibecoders-p1/commit/3f66605)).
  In session D2, same request, the skill loaded as the first step and the session followed it.
- **The steering files changed with the project:** [commit 9f83b7a](https://github.com/Versionfm/vibecoders-p1/commit/9f83b7a)
  added the skill and the agent (2026-10-13); [commit b4f8482](https://github.com/Versionfm/vibecoders-p1/commit/b4f8482)
  taught both the Agentic Tutor (2026-10-14); `CLAUDE.md` gained the read-first rule when the code did (2026-10-19).
- **The rules held in practice:** every prompt change is a new version (`router_v2`, `tutor_v2`, `judge_supported_v2`);
  the Golden Set file has never changed since it was frozen; every evaluation, including abandoned ones, is in the
  [iteration log](../evaluation/ITERATION_LOG.md) (31 entries); a label correction proposed after seeing the judge was
  recorded and **abandoned**, the first labels stayed official ([06_abandoned.md](06_abandoned.md)).

**Screenshots to take (open item):** the final messages of sessions A and B2, and session D2's skill call.

## Slide

- Claude Code instead of Copilot: `CLAUDE.md` = `AGENTS.md`, `.claude/skills/` and `.claude/agents/` = `.github/…`
- `CLAUDE.md`: layout + rules (one screen · never edit an evaluated prompt · never move a label to move a score · log everything)
- Skill `evaluate-course-tutor` + sub-agent `evaluator`: one repeatable, logged evaluation procedure
- Evidence: without `CLAUDE.md` the plan broke the one-screen rule; with it, it did not
- Evidence: the skill did not fire until its description named how we ask for it

## Report paragraph (draft)

> We built the app with Claude Code rather than GitHub Copilot, so the steering files the brief names live where Claude
> Code reads them: the always-on rules file is `CLAUDE.md` (the brief's `AGENTS.md`), the skill is
> `.claude/skills/evaluate-course-tutor/SKILL.md` and the sub-agent is `.claude/agents/evaluator.md`. `CLAUDE.md`
> gives the module layout and the rules we wanted held in every session: one screen only, never edit an evaluated
> prompt, never change the Golden Set or the labels to move a score, and log every evaluated change. To see what it
> changed, we gave two fresh sessions at the same commit the same feature request, one without `CLAUDE.md` and one with
> it. Both followed the conventions already visible in the code, but only the session with `CLAUDE.md` ruled out a new
> setting on the screen and planned to keep the file current: by that stage the file mattered for the rules that no
> code shows by example. The evaluation skill first failed to fire on "How are we doing on the Golden Set?", because
> its description said what it does rather than how we ask; after we rewrote the description, the same request loaded
> the skill as the first step. Both checks are single runs.

## Sources

[CLAUDE.md](../CLAUDE.md) · [CONTEXT.md](../CONTEXT.md) · [.claude/](../.claude/) ·
[WORKFLOW_ITERATIONS.md](../docs/WORKFLOW_ITERATIONS.md) · [PATHWAY_CHECKLIST.md](../docs/PATHWAY_CHECKLIST.md)
