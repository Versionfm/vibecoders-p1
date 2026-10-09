"""Seam A: answer one question. Router call, then one Course Tutor call, with the chat model injected."""
import json
import re
from dataclasses import dataclass, field
from typing import Protocol

from course_material import CourseMaterial, load_all_course_materials
from prompts import ROUTER_PROMPT_VERSION, TUTOR_PROMPT_VERSION, fill, load_prompt

OUT_OF_SCOPE = "OUT_OF_SCOPE"
CITATION = re.compile(r"\[((?:GAIF|PEID|AITB|DTGS)-\d+\.\d+)\]")
ROUTER_TEMPERATURE = 0.0
TUTOR_TEMPERATURE = 0.0


class ChatModel(Protocol):
    name: str

    def complete(self, messages: list[dict], temperature: float = 0.0) -> str: ...


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
    router_prompt_version: str = ROUTER_PROMPT_VERSION
    tutor_prompt_version: str = TUTOR_PROMPT_VERSION
    model: str = ""


def answer_question(
    question: str,
    model: ChatModel,
    materials: dict[str, CourseMaterial] | None = None,
) -> TutorResult:
    materials = materials or load_all_course_materials()
    result = TutorResult(question=question, model=model.name)

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
    known_sections = {sid for m in materials.values() for sid in m.sections}
    result.invalid_citations = [c for c in result.citations if c not in known_sections]
    result.is_refusal = is_refusal(result.answer, material.code)
    return result


class RouterReplyError(ValueError):
    pass


def parse_router_reply(reply: str, courses: set[str]) -> tuple[str, str]:
    """Strict: the reply must be a JSON object naming a known Course or OUT_OF_SCOPE. No default Course."""
    try:
        route = json.loads(reply)
    except json.JSONDecodeError as error:
        raise RouterReplyError(f"Router reply is not valid JSON: {reply[:200]!r}") from error
    if not isinstance(route, dict):
        raise RouterReplyError(f"Router reply is not a JSON object: {reply[:200]!r}")
    course = route.get("course")
    if not isinstance(course, str) or (course != OUT_OF_SCOPE and course not in courses):
        raise RouterReplyError(f"Router returned an unknown Course: {course!r}")
    evidence = route.get("evidence")
    return course, evidence if isinstance(evidence, str) else ""


def refusal_sentence(course: str) -> str:
    return f"This is not covered in the {course} material."


def is_refusal(answer: str, course: str) -> bool:
    return answer.strip() == refusal_sentence(course)


def extract_citations(answer: str) -> list[str]:
    return list(dict.fromkeys(CITATION.findall(answer)))


def _model_failure(step: str, error: Exception) -> str:
    return f"{step} model call failed: {type(error).__name__}: {error}"


def _messages(system: str, question: str) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": question}]
