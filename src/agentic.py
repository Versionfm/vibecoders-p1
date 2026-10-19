"""One Agentic Tutor: call the model, execute Reads, repeat until it answers.

This module owns the tool protocol and Read limit. Citation checks and evaluation verdicts live in tutor.py.
"""
import json
from dataclasses import dataclass, field

from course_material import COURSES, CourseMaterial
from llm import ChatModel, ModelReply, ToolCall
from prompts import AGENTIC_TUTOR_PROMPT_VERSION, load_prompt

TEMPERATURE = 0.0
UNKNOWN_COURSE = "Unknown Course."
READ_LIMIT_REACHED = "Read limit reached."
OUT_OF_SCOPE_SENTENCE = "This question is outside the four Courses."  # the Agentic Tutor's, given with no Read
# Sent once when the model answers with no Read (e.g. a follow-up answered from the conversation alone).
READ_FIRST = (
    "Read the Course Material with read_file before answering. Earlier answers in this conversation are not "
    "Course Material."
)
READ_LIMIT = 4  # Reads per question, valid or not, before the Agentic Tutor is forced to answer (ADR 0001)
# The Agentic Tutor's one tool. Its only accepted arguments are the four Course codes, so it can read nothing else.
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Return the whole Course Material of one Course.",
        "parameters": {
            "type": "object",
            "properties": {"course": {"type": "string", "enum": list(COURSES)}},
            "required": ["course"],
        },
    },
}


@dataclass
class AgenticRun:
    """The final text and facts recorded during execution, before answer checks."""
    answer: str = ""
    read_arguments: list[str] = field(default_factory=list)
    materials_read: list[str] = field(default_factory=list)
    read_limit_hit: bool = False
    error: Exception | None = None


def run_agentic(
    question: str, model: ChatModel, materials: dict[str, CourseMaterial], history: list[dict] | None = None,
) -> AgenticRun:
    """Run one question. Keep partial Read records if a model call fails; leave the supplied history untouched."""
    messages = [
        {"role": "system", "content": load_prompt(AGENTIC_TUTOR_PROMPT_VERSION)},
        *[dict(turn) for turn in (history or [])],
        {"role": "user", "content": question},
    ]
    run = AgenticRun()
    sent_back = False
    while True:
        run.read_limit_hit = len(run.read_arguments) >= READ_LIMIT
        tools = None if run.read_limit_hit else [READ_FILE_TOOL]
        try:
            reply = model.chat(messages, TEMPERATURE, tools=tools)
        except Exception as error:
            run.error = error
            return run
        if not reply.tool_calls and not run.read_arguments and not sent_back \
                and reply.content.strip() != OUT_OF_SCOPE_SENTENCE:
            sent_back = True
            messages += [{"role": "assistant", "content": reply.content}, {"role": "user", "content": READ_FIRST}]
            continue
        if run.read_limit_hit or not reply.tool_calls:
            run.answer = reply.content
            return run
        messages.append(_assistant_message(reply))
        for call in reply.tool_calls:
            messages.append({"role": "tool", "tool_call_id": call.id, "content": _read(call, materials, run)})


def _read(call: ToolCall, materials: dict[str, CourseMaterial], run: AgenticRun) -> str:
    """Handle one `read_file` call and record it in the Trace. Returns the tool result for the model.

    Past the Read limit a call is answered but not read or recorded, so the conversation stays valid."""
    if len(run.read_arguments) >= READ_LIMIT:
        return READ_LIMIT_REACHED
    try:
        course = json.loads(call.arguments).get("course")
    except (TypeError, json.JSONDecodeError, AttributeError):
        course = None
    run.read_arguments.append(course if isinstance(course, str) else str(call.arguments))
    if not isinstance(course, str) or course not in materials:
        return UNKNOWN_COURSE
    run.materials_read.append(course)
    return materials[course].text.strip()


def _assistant_message(reply: ModelReply) -> dict:
    """The model's tool-calling reply, in the OpenAI chat format, so the next call sees what it asked for."""
    calls = [
        {"id": c.id, "type": "function", "function": {"name": c.name, "arguments": c.arguments}}
        for c in reply.tool_calls
    ]
    return {"role": "assistant", "content": reply.content, "tool_calls": calls}
