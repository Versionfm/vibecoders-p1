"""What the screen needs besides Streamlit: one guarded answer call and Markdown-safe text. No Streamlit import."""
import os
import re
import sys
from collections.abc import Callable, Mapping

from tutor import ROUTED_TUTOR, ChatModel, TutorResult, answer_question

_UNESCAPED_DOLLAR = re.compile(r"(?<!\\)\$")


def tutor_setting(env: Mapping[str, str] | None = None) -> str:
    """The tutor the screen runs, from `TUTOR` in the environment (or .env): `routed` (default) or `agentic`."""
    env = os.environ if env is None else env
    return (env.get("TUTOR") or ROUTED_TUTOR).strip().lower()


def markdown_safe(text: str) -> str:
    """Escape `$` so Streamlit's Markdown shows amounts like $0.50 as text, not as LaTeX."""
    return _UNESCAPED_DOLLAR.sub(r"\\$", text)


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
