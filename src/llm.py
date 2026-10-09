"""The one place where model access is configured. Settings come only from environment variables (or .env)."""
import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_APP_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
DEFAULT_JUDGE_MODEL = ""  # chosen later by a probe; must not be a Nemotron model
REQUEST_TIMEOUT_SECONDS = 60.0  # a hung service raises a timeout, which the tutor turns into an error result


@dataclass(frozen=True)
class LlmSettings:
    api_key: str
    base_url: str
    app_model: str
    judge_model: str


def load_settings(env: Mapping[str, str] | None = None) -> LlmSettings:
    env = os.environ if env is None else env
    api_key = env.get("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY not set. Check your .env file.")
    return LlmSettings(
        api_key=api_key,
        base_url=env.get("LLM_BASE_URL") or DEFAULT_BASE_URL,
        app_model=env.get("LLM_MODEL") or DEFAULT_APP_MODEL,
        judge_model=env.get("LLM_JUDGE_MODEL") or DEFAULT_JUDGE_MODEL,
    )


class OpenAIChatModel:
    """Adapter from an OpenAI-compatible client to the ChatModel interface used by the tutor."""

    def __init__(self, client, name: str):
        self._client = client
        self.name = name

    def complete(self, messages: list[dict], temperature: float = 0.0) -> str:
        response = self._client.chat.completions.create(
            model=self.name, messages=messages, temperature=temperature
        )
        return response.choices[0].message.content or ""


def get_chat_model(model: str | None = None) -> OpenAIChatModel:
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    settings = load_settings()
    client = OpenAI(
        base_url=settings.base_url, api_key=settings.api_key, timeout=REQUEST_TIMEOUT_SECONDS
    )
    return OpenAIChatModel(client, model or settings.app_model)
