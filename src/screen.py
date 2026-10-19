"""What the screen needs besides Streamlit: one guarded answer call and Markdown-safe text. No Streamlit import."""
import os
import re
import sys
from collections.abc import Callable, Mapping

from tutor import BRACKET, CITATION_LIKE, ROUTED_TUTOR, ChatModel, TutorResult, answer_question

_UNESCAPED_DOLLAR = re.compile(r"(?<!\\)\$")
_LINK_SUFFIX = re.compile(
    r"\((?:\\.|[^()\\]|\([^()]*\))*\)"
    r"|\[(?P<reference>[^\]\n]*)\]"
)
_LINK_DEFINITION = re.compile(r"(?m)^ {0,3}\[([^\]\n]+)\]:[ \t]+\S[^\n]*")


def tutor_setting(env: Mapping[str, str] | None = None) -> str:
    """The tutor the screen runs, from `TUTOR` in the environment (or .env): `routed` (default) or `agentic`."""
    env = os.environ if env is None else env
    return (env.get("TUTOR") or ROUTED_TUTOR).strip().lower()


def markdown_safe(text: str) -> str:
    """Escape `$` so Streamlit's Markdown shows amounts like $0.50 as text, not as LaTeX."""
    return _UNESCAPED_DOLLAR.sub(r"\\$", text)


def answer_for_display(answer: str) -> str:
    """Hide inline Section markers in a display copy, keeping the original answer as evidence."""
    definitions = list(_LINK_DEFINITION.finditer(answer))
    labels = {definition.group(1).casefold() for definition in definitions}
    protected = [definition.span() for definition in definitions]
    openings = []
    for bracket in re.finditer(r"\\.|[\[\]]", answer):
        if bracket.group() == "[":
            openings.append(bracket.start())
        if bracket.group() != "]" or not openings:
            continue
        start = openings.pop()
        suffix = _LINK_SUFFIX.match(answer, bracket.end())
        if suffix is None:
            continue
        reference = suffix.group("reference")
        if (
            reference is None or reference.casefold() in labels
            or not (_citation_only(answer[start + 1:bracket.start()]) and _citation_only(reference))
        ):
            protected.append((start, suffix.end()))
    for bracket in reversed(list(BRACKET.finditer(answer))):
        if (
            _citation_only(bracket.group(1)) and bracket.group(1).casefold() not in labels
            and not any(start <= bracket.start() < end for start, end in protected)
        ):
            start, end = bracket.span()
            if start > 0 and answer[start - 1] == "\\":
                start -= 1
            marker_start = start
            while start > 0 and answer[start - 1] in " \t":
                start -= 1
            while end < len(answer) and answer[end] in " \t":
                end += 1
            left, right = answer[:start], answer[end:]
            space = " " if left and right and left[-1] not in "\r\n([{" and right[0] not in "\r\n.,;:!?)]}" else ""
            emphasis = re.match(r"\*+|_+", right)
            paragraph = re.split(r"\n[ \t]*\n", left)[-1]
            paragraph = re.sub(r"(?m)^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", "", paragraph)
            if emphasis and paragraph.count(emphasis.group()) % 2:
                space = ""
            if (not left or left[-1] in "\r\n") and right and right[0] not in "\r\n":
                space = answer[start:marker_start]
            if right.startswith(("\n", "\r\n")):
                space = answer[bracket.end():end]
            answer = left + space + right
    return answer


def _citation_only(text: str) -> bool:
    return all(CITATION_LIKE.fullmatch(part.strip()) for part in re.split(r"[,;]", text.removesuffix("\\")))


def ask(
    question: str, get_model: Callable[[], ChatModel], tutor: str = ROUTED_TUTOR,
    history: list[dict] | None = None,
) -> TutorResult | None:
    """Answer for the screen. Never raises: a failure is printed to the console and the screen shows a calm retry.

    Returns None when no answer could be attempted (e.g. the model could not be created, or the tutor is unknown).
    """
    try:
        result = answer_question(question, get_model(), tutor=tutor, history=history)
    except Exception as error:
        _log(f"{type(error).__name__}: {error}")
        return None
    if result.error:
        _log(result.error)
    return result


def _log(message: str) -> None:
    print(f"Course Tutor error: {message}", file=sys.stderr)
