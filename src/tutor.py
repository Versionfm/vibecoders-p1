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

    route = json.loads(
        model.complete(_messages(load_prompt(ROUTER_PROMPT_VERSION), question), ROUTER_TEMPERATURE)
    )
    result.course = route["course"]
    result.evidence = route.get("evidence", "")

    material = materials[result.course]
    system = fill(
        load_prompt(TUTOR_PROMPT_VERSION),
        COURSE_CODE=material.code,
        COURSE_NAME=material.name,
        COURSE_MATERIAL=material.text.strip(),
    )
    result.answer = model.complete(_messages(system, question), TUTOR_TEMPERATURE)
    result.citations = extract_citations(result.answer)
    return result


def extract_citations(answer: str) -> list[str]:
    return list(dict.fromkeys(CITATION.findall(answer)))


def _messages(system: str, question: str) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": question}]
