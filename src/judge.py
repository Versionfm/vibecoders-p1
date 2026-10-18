"""The LLM judge: what code cannot check about an answer. One call per criterion, Supported then Responsive.

Each call has its own versioned prompt, runs at temperature 0, and must reply with JSON that gives the evidence before
the verdict (PASS, FAIL or UNKNOWN). A failed call or an unparseable reply is a judge error, never a pass.
"""
import json
from dataclasses import dataclass

from cases import EvaluationCase
from course_material import CourseMaterial
from prompts import JUDGE_RESPONSIVE_PROMPT_VERSION, JUDGE_SUPPORTED_PROMPT_VERSION, fill, load_prompt
from tutor import ChatModel, TutorResult, first_json_object

PASS, FAIL, UNKNOWN, ERROR = "PASS", "FAIL", "UNKNOWN", "ERROR"
VERDICTS = (PASS, FAIL, UNKNOWN)  # what the judge may answer; ERROR is ours
JUDGE_TEMPERATURE = 0.0
JUDGE_PROMPT_VERSIONS = {
    "judge_supported": JUDGE_SUPPORTED_PROMPT_VERSION,
    "judge_responsive": JUDGE_RESPONSIVE_PROMPT_VERSION,
}
NO_CITED_SECTION = "(no cited Section exists in the Course Material)"


@dataclass(frozen=True)
class JudgeVerdict:
    verdict: str  # PASS, FAIL, UNKNOWN, or ERROR for a failed call or an unparseable reply
    evidence: str = ""

    @property
    def passed(self) -> bool:
        return self.verdict == PASS


@dataclass(frozen=True)
class Judgement:
    supported: JudgeVerdict
    responsive: JudgeVerdict


def judge_answer(
    case: EvaluationCase, result: TutorResult, judge: ChatModel, materials: dict[str, CourseMaterial]
) -> Judgement:
    """Judge one answer on both criteria. Never raises: a failure becomes an ERROR verdict."""
    supported = fill(
        load_prompt(JUDGE_SUPPORTED_PROMPT_VERSION),
        QUESTION=result.question,
        ANSWER=result.answer.strip(),
        CITED_SECTIONS=cited_sections_text(result.citations, materials),
    )
    responsive = fill(
        load_prompt(JUDGE_RESPONSIVE_PROMPT_VERSION),
        QUESTION=result.question,
        KEY_FACTS="\n".join(f"- {fact}" for fact in case.key_facts) or "(none given)",
        ANSWER=result.answer.strip(),
    )
    return Judgement(_ask(judge, supported), _ask(judge, responsive))


def cited_sections_text(citations: list[str], materials: dict[str, CourseMaterial]) -> str:
    """The text of every cited Section that exists, each under its identifier and title."""
    sections = {sid: s for m in materials.values() for sid, s in m.sections.items()}
    found = [sections[c] for c in citations if c in sections]
    return "\n\n".join(f"[{s.id}] {s.title}\n{s.text}" for s in found) or NO_CITED_SECTION


def parse_judge_reply(reply: str) -> JudgeVerdict:
    """The first JSON object in the reply, with a verdict of PASS, FAIL or UNKNOWN; anything else is an ERROR."""
    try:
        value = json.loads(reply)
    except json.JSONDecodeError:
        value = first_json_object(reply)
    if not isinstance(value, dict):
        return JudgeVerdict(ERROR, f"unparseable judge reply: {reply[:200]!r}")
    verdict = value.get("verdict")
    verdict = verdict.strip().upper() if isinstance(verdict, str) else None
    if verdict not in VERDICTS:
        return JudgeVerdict(ERROR, f"judge reply has no valid verdict: {reply[:200]!r}")
    evidence = value.get("evidence")
    return JudgeVerdict(verdict, evidence.strip() if isinstance(evidence, str) else "")


def _ask(judge: ChatModel, prompt: str) -> JudgeVerdict:
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": "Give your verdict as JSON."}]
    try:
        reply = judge.complete(messages, JUDGE_TEMPERATURE)
    except Exception as error:
        return JudgeVerdict(ERROR, f"judge model call failed: {type(error).__name__}: {error}")
    return parse_judge_reply(reply)
