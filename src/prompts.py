"""Versioned prompt files. An evaluated prompt is never edited: add the next version instead."""
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

ROUTER_PROMPT_VERSION = "router_v2"
TUTOR_PROMPT_VERSION = "tutor_v2"
AGENTIC_TUTOR_PROMPT_VERSION = "agentic_tutor_v1"


def load_prompt(version: str, prompt_dir: Path = PROMPT_DIR) -> str:
    return (prompt_dir / f"{version}.md").read_text(encoding="utf-8")


def fill(template: str, **values: str) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template
