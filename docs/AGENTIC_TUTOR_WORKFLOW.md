# Agentic Tutor workflow

The Agentic Tutor has one model, one repeatable `read_file(course)` tool and a plain Python loop.

## The usual path

```mermaid
sequenceDiagram
    participant Student
    participant App
    participant LLM
    Student->>App: Question or follow-up
    App->>LLM: Prompt + previous turns + question + tool definition
    LLM-->>App: read_file("PEID")
    App->>LLM: Requested Course Material
    LLM-->>App: Answer with Section citations
    App-->>Student: Answer
```

A typical question takes two LLM calls and one Read. The LLM chooses the Course; Python validates the request and
returns the whole Course Material. If the model needs another Course, the same loop runs again. A reply without
tool calls ends the loop.

## Where to read the code

| Responsibility | Location |
| --- | --- |
| Keep and display the conversation | `src/app.py` |
| Run the model/Read loop | `run_agentic()` in `src/agentic.py` |
| Validate a Course code and return its material | `_read()` in `src/agentic.py` |
| Build the shared result and check the answer | `_answer_agentic()` in `src/tutor.py` |
| Send the actual provider request | `OpenAIChatModel.chat()` in `src/llm.py` |

`answer_question(..., tutor="agentic", history=...)` remains the entry point used by the screen and evaluator.
The dedicated module returns an `AgenticRun`: final text, Read records, limit status and any model-call error.
It does not decide whether citations, Refusals or evaluation Steps pass.

## Chat context

Previous user messages and assistant answers are sent between the system prompt and the latest question. Previous
Course Material and tool calls are not retained across questions. Each answer reads its own material; previous
answers provide conversational context, not evidence for new claims. **New conversation** clears the chat.

## Limits and errors

- The tool accepts only `GAIF`, `PEID`, `AITB` and `DTGS`. Invalid arguments return `Unknown Course.` and count as Reads.
- At most four Reads are executed per question. After the fourth, one final LLM call has tools disabled.
- Several tool calls in one reply are supported. Calls beyond the limit receive `Read limit reached.` without reading.
- Each tool result carries the ID of its matching assistant tool call, as required by the provider protocol.
- A failed model call returns an error with the Read records collected so far; the screen offers a retry.
- The model may answer Out of scope without a Read. An in-scope answer or Refusal without a Read fails evaluation.

## Evaluation is separate

`tutor.py` maps the execution records into the existing `TutorResult`, identifies the exact Refusal or Out of scope
sentence and checks citations against Sections of material read during this answer. `scoring.py` then grades Search,
Path and Answer. Repeated Reads and reaching the Read limit remain Path Step failures.

The evaluator supplies no chat history. Existing single-message scores do not measure follow-up answer quality.
The refactor changes code organization, keeping the prompt, model settings, tool behaviour and result fields intact.
