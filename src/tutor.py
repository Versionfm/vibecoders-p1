"""Seam A: answer one question, with the chat model injected.

Routed Tutor: a Router call, then one Course Tutor call. Agentic Tutor: one model Reads Course Material through the
`read_file` tool in a plain loop (ADR 0001), then answers.
"""
import json
import re
from dataclasses import dataclass, field
from typing import Protocol

from course_material import COURSES, CourseMaterial, default_course_materials
from llm import ModelReply, ToolCall
from prompts import AGENTIC_TUTOR_PROMPT_VERSION, ROUTER_PROMPT_VERSION, TUTOR_PROMPT_VERSION, fill, load_prompt

OUT_OF_SCOPE = "OUT_OF_SCOPE"
OUT_OF_SCOPE_SENTENCE = "This question is outside the four Courses."  # the Agentic Tutor's, given with no Read
# A bracket holds one Section identifier or several separated by "," or ";". Any ID-shaped token in a bracket
# (upper-case code, hyphen, numbers) counts as a citation, so malformed or unknown ones can be reported as invalid.
BRACKET = re.compile(r"\[([^\[\]\n]{1,200})\]")
CITATION_LIKE = re.compile(r"[A-Z]{2,}-\d+(?:\.\d+)*")
ROUTER_TEMPERATURE = 0.0
TUTOR_TEMPERATURE = 0.0
ROUTED_TUTOR = "routed"
AGENTIC_TUTOR = "agentic"
TUTORS = (ROUTED_TUTOR, AGENTIC_TUTOR)
UNKNOWN_COURSE = "Unknown Course."
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


class ChatModel(Protocol):
    name: str
    thinking: bool | None  # the model's reasoning mode switch; None when not set

    def complete(self, messages: list[dict], temperature: float = 0.0) -> str: ...

    def chat(self, messages: list[dict], temperature: float = 0.0, tools: list[dict] | None = None) -> ModelReply: ...


@dataclass
class TutorResult:
    question: str
    course: str | None = None
    evidence: str = ""
    answer: str = ""
    citations: list[str] = field(default_factory=list)
    is_refusal: bool = False
    invalid_citations: list[str] = field(default_factory=list)
    error: str | None = None
    router_prompt_version: str | None = ROUTER_PROMPT_VERSION  # None for the Agentic Tutor, which has no Router
    tutor_prompt_version: str = TUTOR_PROMPT_VERSION
    model: str = ""
    thinking: bool | None = None
    # The Trace, filled the same way by every tutor. For the Routed Tutor the routed Course is the one Course
    # Material read; it makes no tool calls and has no Read limit.
    tutor: str = ROUTED_TUTOR
    materials_read: list[str] = field(default_factory=list)  # Courses whose Course Material was chosen or read, in order
    tool_arguments: list[str] = field(default_factory=list)  # every `read_file` argument as given, valid or not
    read_count: int = 0
    read_limit_hit: bool = False


def answer_question(
    question: str,
    model: ChatModel,
    materials: dict[str, CourseMaterial] | None = None,
    tutor: str = ROUTED_TUTOR,
) -> TutorResult:
    """Answer with the Routed Tutor (default) or the Agentic Tutor (`tutor="agentic"`). Both fill the same Trace."""
    if tutor not in TUTORS:
        raise ValueError(f"Unknown tutor {tutor!r}; choose one of {', '.join(TUTORS)}")
    materials = default_course_materials() if materials is None else materials
    result = TutorResult(question=question, model=model.name, thinking=getattr(model, "thinking", None))
    if tutor == AGENTIC_TUTOR:
        return _answer_agentic(question, model, materials, result)

    try:
        reply = model.complete(_messages(load_prompt(ROUTER_PROMPT_VERSION), question), ROUTER_TEMPERATURE)
    except Exception as error:
        result.error = _model_failure("Router", error)
        return result
    try:
        result.course, result.evidence = parse_router_reply(reply, set(materials))
    except RouterReplyError as error:
        result.error = str(error)
        return result
    if result.course == OUT_OF_SCOPE:
        return result

    material = materials[result.course]
    result.materials_read, result.read_count = [material.code], 1
    system = fill(
        load_prompt(TUTOR_PROMPT_VERSION),
        COURSE_CODE=material.code,
        COURSE_NAME=material.name,
        COURSE_MATERIAL=material.text.strip(),
    )
    try:
        result.answer = model.complete(_messages(system, question), TUTOR_TEMPERATURE)
    except Exception as error:
        result.error = _model_failure("Course Tutor", error)
        return result
    result.citations = extract_citations(result.answer)
    result.invalid_citations = [c for c in result.citations if c not in material.sections]
    result.is_refusal = is_refusal(result.answer, material.code)
    return result


def _answer_agentic(
    question: str, model: ChatModel, materials: dict[str, CourseMaterial], result: TutorResult
) -> TutorResult:
    """The Agentic Tutor loop: offer `read_file`, feed each Read back, stop at the first reply with no tool calls
    or at the Read limit. Never raises on a bad Trace: a failed model call becomes `error`."""
    result.tutor = AGENTIC_TUTOR
    result.router_prompt_version, result.tutor_prompt_version = None, AGENTIC_TUTOR_PROMPT_VERSION
    messages = _messages(load_prompt(AGENTIC_TUTOR_PROMPT_VERSION), question)
    while True:
        # At the Read limit, one last call with tools switched off forces an answer; its tool calls are not followed.
        result.read_limit_hit = result.read_count >= READ_LIMIT
        try:
            reply = model.chat(messages, TUTOR_TEMPERATURE, tools=None if result.read_limit_hit else [READ_FILE_TOOL])
        except Exception as error:
            result.error = _model_failure("Agentic Tutor", error)
            return result
        if result.read_limit_hit or not reply.tool_calls:
            break
        messages.append(_assistant_message(reply))
        for call in reply.tool_calls:
            messages.append({"role": "tool", "tool_call_id": call.id, "content": _read(call, materials, result)})

    result.answer = reply.content
    if result.materials_read:
        result.course = result.materials_read[0]
        result.is_refusal = any(is_refusal(result.answer, code) for code in result.materials_read)
    elif result.answer.strip() == OUT_OF_SCOPE_SENTENCE:  # after a Read it is a failed answer, not Out of scope
        result.course = OUT_OF_SCOPE
    result.citations = extract_citations(result.answer)
    read_sections = {s for code in result.materials_read for s in materials[code].sections}
    result.invalid_citations = [c for c in result.citations if c not in read_sections]
    return result


def _read(call: ToolCall, materials: dict[str, CourseMaterial], result: TutorResult) -> str:
    """Handle one `read_file` call and record it in the Trace. Returns the tool result for the model."""
    try:
        course = json.loads(call.arguments).get("course")
    except (TypeError, json.JSONDecodeError, AttributeError):
        course = None
    result.tool_arguments.append(course if isinstance(course, str) else str(call.arguments))
    result.read_count += 1
    if not isinstance(course, str) or course not in materials:
        return UNKNOWN_COURSE
    result.materials_read.append(course)
    return materials[course].text.strip()


def _assistant_message(reply: ModelReply) -> dict:
    """The model's tool-calling reply, in the OpenAI chat format, so the next call sees what it asked for."""
    calls = [
        {"id": c.id, "type": "function", "function": {"name": c.name, "arguments": c.arguments}}
        for c in reply.tool_calls
    ]
    return {"role": "assistant", "content": reply.content, "tool_calls": calls}


class RouterReplyError(ValueError):
    pass


def parse_router_reply(reply: str, courses: set[str]) -> tuple[str, str]:
    """The reply must contain a JSON object naming a known Course or OUT_OF_SCOPE. No default Course.

    A code fence or text around the object is tolerated: the first JSON object in the reply is used.
    """
    try:
        route = json.loads(reply)
    except json.JSONDecodeError:
        route = _first_json_object(reply)
        if route is None:
            raise RouterReplyError(f"Router reply is not valid JSON: {reply[:200]!r}") from None
    if not isinstance(route, dict):
        raise RouterReplyError(f"Router reply is not a JSON object: {reply[:200]!r}")
    course = route.get("course")
    if not isinstance(course, str) or (course != OUT_OF_SCOPE and course not in courses):
        raise RouterReplyError(f"Router returned an unknown Course: {course!r}")
    evidence = route.get("evidence")
    return course, evidence if isinstance(evidence, str) else ""


def _first_json_object(text: str) -> dict | None:
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start != -1:
        try:
            value, _ = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict):
            return value
        start = text.find("{", start + 1)
    return None


def refusal_sentence(course: str) -> str:
    return f"This is not covered in the {course} material."


def is_refusal(answer: str, course: str) -> bool:
    return answer.strip() == refusal_sentence(course)


def extract_citations(answer: str) -> list[str]:
    found = []
    for bracket in BRACKET.findall(answer):
        for part in re.split(r"[,;]", bracket):
            if CITATION_LIKE.fullmatch(part.strip()):
                found.append(part.strip())
    return list(dict.fromkeys(found))


def _model_failure(step: str, error: Exception) -> str:
    return f"{step} model call failed: {type(error).__name__}: {error}"


def _messages(system: str, question: str) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": question}]
