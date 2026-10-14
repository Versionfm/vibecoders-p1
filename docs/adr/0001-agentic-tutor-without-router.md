---
status: accepted
---

# Agentic Tutor: no Router, whole-file Reads, a plain Python loop

We are building the Agentic Tutor as a variant next to the Routed Tutor, not as a replacement, and measuring both on the
same Golden Set; the loser is logged as abandoned in the iteration log. The Agentic Tutor has no Router: one model,
given the four Course Descriptions, asks for Course Material through a single `read_file(course)` tool whose only
accepted arguments are `GAIF`, `PEID`, `AITB` and `DTGS`, each returning that whole Course Material. The loop is
plain Python inside `answer_question(question, model, tutor="agentic")`, with no agent framework.

## Considered Options

- **Replace the Routed Tutor outright.** Rejected: there is no Golden Set score showing the Routed Tutor fails, and a
  measured comparison is iteration evidence whichever variant wins.
- **Keep the Router and only change how context arrives.** Rejected: with whole-file Reads it reproduces today's
  context through an extra round trip, so the comparison would measure almost nothing. Choosing the Course Material is
  the part worth testing.
- **`read_file(path)` or Section-level tools.** A free path could reach `.env` (the API key); Section-level tools
  (`list_sections`, `read_section`) are a later, separate experiment.
- **LangGraph, LangChain or an agent SDK.** Rejected: one tool, a capped number of Reads and one straight path leave
  nothing for a graph, checkpoints or hand-offs to manage. The framework would add a model wrapper that the test
  fakes cannot stand in for, and the Trace would have to be rebuilt from callbacks. In the plain loop the Trace is a
  list the code appends to, and every group member can explain it.
- **A total time limit per question.** Rejected: if the endpoint is too slow, the group switches `LLM_BASE_URL` and
  `LLM_MODEL` to a paid API (e.g. DeepSeek) instead.

## Consequences

- At most 4 Reads per question; after the fourth, one last call with tools switched off forces an answer, and the
  Trace fails the Path Step.
- A `read_file` argument that is not a Course returns "Unknown Course." to the model; it is a Path Step failure, not
  a crash. Every tool call in a reply is handled and counted.
- Out of scope is the Out of scope Sentence given with no Read; the Refusal is the existing sentence naming the Course
  read. Both are matched exactly by code, so the existing Refusal and Out of scope metrics still work.
- A cited Section is valid only if its Course Material was read in that answer.
- Native tool calling is used only after `evaluation/probes/tool_call_probe.py` shows `tool_calls` come back filled
  in on the chosen model (NVIDIA's docs advertise it for Nemotron Super but its request schema omits `tools`). If the
  Agentic Tutor needs another model (e.g. `openai/gpt-oss-120b` or DeepSeek), the Routed Tutor is measured on that
  model too, so only one thing changes between the two.
- A `.env` setting chooses the tutor on the screen; the default stays the Routed Tutor until the Agentic Tutor wins.
  The screen shows the Course Materials read where the Router's evidence used to be.
- The prompt lives in a new versioned file, `prompts/agentic_tutor_v1.md`, with no Golden Set questions in it.
