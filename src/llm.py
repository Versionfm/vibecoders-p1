"""The one place where model access is configured. Settings come only from environment variables (or .env)."""
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol

# No default endpoint or model: .env names the provider (see .env.example), so a missing line fails loudly instead
# of silently calling another provider's model.
REQUIRED_SETTINGS = ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL")

# A hung service raises a timeout, which the tutor turns into an error result. With one retry the worst case for
# one model call is about 2 x 60 s (plus a short backoff), so about 4 minutes for a question (Router + Course Tutor).
REQUEST_TIMEOUT_SECONDS = 60.0
MAX_RETRIES = 1

# LLM_THINKING=on|off switches the app model's reasoning ("thinking") mode. Off by default: on Nemotron it made a
# Router call about ten times slower for the same label; on DeepSeek it is on unless switched off. Quality with thinking on is not compared yet.
# `none` sends no switch at all, for endpoints that reject it (the course endpoint answers HTTP 400).
THINKING_VALUES = {"on": True, "off": False, "none": None}


@dataclass(frozen=True)
class LlmSettings:
    api_key: str
    base_url: str
    app_model: str
    judge_model: str
    thinking: bool | None = False
    # The judge may sit on another provider than the app model (it must be another model family): its endpoint and key
    # default to the app's.
    judge_base_url: str = ""
    judge_api_key: str = ""
    judge_thinking: bool | None = False


def load_settings(env: Mapping[str, str] | None = None) -> LlmSettings:
    env = os.environ if env is None else env
    for name in REQUIRED_SETTINGS:
        if not env.get(name):
            raise RuntimeError(f"{name} not set. Check your .env file (see .env.example).")
    return LlmSettings(
        api_key=env["LLM_API_KEY"],
        base_url=env["LLM_BASE_URL"],
        app_model=env["LLM_MODEL"],
        judge_model=(env.get("LLM_JUDGE_MODEL") or "").strip(),  # empty: no judge; never the app model's family
        thinking=_thinking(env, "LLM_THINKING"),
        judge_base_url=env.get("LLM_JUDGE_BASE_URL") or env["LLM_BASE_URL"],
        judge_api_key=env.get("LLM_JUDGE_API_KEY") or env["LLM_API_KEY"],
        judge_thinking=_thinking(env, "LLM_JUDGE_THINKING"),
    )


def _thinking(env: Mapping[str, str], name: str) -> bool | None:
    value = (env.get(name) or "off").strip().lower()
    if value not in THINKING_VALUES:
        raise RuntimeError(f"{name} must be 'on', 'off' or 'none', not {value!r}. Check your .env file.")
    return THINKING_VALUES[value]


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str  # the raw JSON text the model gave


@dataclass(frozen=True)
class ModelReply:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)


class ChatModel(Protocol):
    name: str
    thinking: bool | None  # the model's reasoning mode switch; None when not set

    def complete(self, messages: list[dict], temperature: float = 0.0) -> str: ...

    def chat(self, messages: list[dict], temperature: float = 0.0, tools: list[dict] | None = None) -> ModelReply: ...


class OpenAIChatModel:
    """Adapter from an OpenAI-compatible client to the ChatModel interface used by the tutor.

    `thinking` True/False is sent both as the chat template switch `enable_thinking` (Nemotron) and as DeepSeek's
    `thinking` type; None sends nothing.
    """

    def __init__(self, client, name: str, thinking: bool | None = None):
        self._client = client
        self.name = name
        self.thinking = thinking

    def complete(self, messages: list[dict], temperature: float = 0.0) -> str:
        return self.chat(messages, temperature).content

    def chat(self, messages: list[dict], temperature: float = 0.0, tools: list[dict] | None = None) -> "ModelReply":
        """One call that may offer tools; the reply carries the text and any tool calls. No tools: none are sent."""
        request = {"model": self.name, "messages": messages, "temperature": temperature}
        if tools:
            request["tools"] = tools
        if self.thinking is not None:
            # Nemotron reads the chat template switch, DeepSeek reads `thinking` and silently ignores the other.
            request["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": self.thinking},
                "thinking": {"type": "enabled" if self.thinking else "disabled"},
            }
        message = self._client.chat.completions.create(**request).choices[0].message
        calls = getattr(message, "tool_calls", None) or []
        return ModelReply(message.content or "", [ToolCall(c.id, c.function.name, c.function.arguments) for c in calls])


def get_chat_model(model: str | None = None, env: Mapping[str, str] | None = None) -> OpenAIChatModel:
    """The app's chat model. Reads `.env` into the environment unless `env` is given."""
    settings = load_settings(_environment(env))
    client = _client(settings.base_url, settings.api_key)
    return OpenAIChatModel(client, model or settings.app_model, thinking=settings.thinking)


def get_judge_model(env: Mapping[str, str] | None = None) -> OpenAIChatModel | None:
    """The LLM judge's chat model, or None when `LLM_JUDGE_MODEL` is not set. Reads `.env` unless `env` is given."""
    env = _environment(env)
    settings = load_settings(env)
    if not settings.judge_model:
        return None
    if settings.judge_base_url != settings.base_url and not (env or os.environ).get("LLM_JUDGE_API_KEY"):
        # Never send the app provider's key to another provider.
        raise RuntimeError(
            "LLM_JUDGE_BASE_URL is another endpoint, so set LLM_JUDGE_API_KEY too. Check your .env file."
        )
    client = _client(settings.judge_base_url, settings.judge_api_key)
    return OpenAIChatModel(client, settings.judge_model, thinking=settings.judge_thinking)


def _environment(env: Mapping[str, str] | None) -> Mapping[str, str] | None:
    if env is None:
        from dotenv import load_dotenv

        load_dotenv()
    return env


def _client(base_url: str, api_key: str):
    from openai import OpenAI

    return OpenAI(base_url=base_url, api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=MAX_RETRIES)
