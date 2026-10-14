"""The one place where model access is configured. Settings come only from environment variables (or .env)."""
import os
from collections.abc import Mapping
from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_APP_MODEL = "deepseek-flash"
DEFAULT_JUDGE_MODEL = ""  # chosen later by a probe; must not be a DeepSeek model

# A hung service raises a timeout, which the tutor turns into an error result. With one retry the worst case for
# one model call is about 2 x 60 s (plus a short backoff), so about 4 minutes for a question (Router + Course Tutor).
REQUEST_TIMEOUT_SECONDS = 60.0
MAX_RETRIES = 1

# LLM_THINKING=on|off switches the app model's reasoning ("thinking") mode. Off by default: on Nemotron it made a
# Router call about ten times slower for the same label; on DeepSeek it is on unless switched off. Quality with thinking on is not compared yet.
THINKING_VALUES = {"on": True, "off": False}


@dataclass(frozen=True)
class LlmSettings:
    api_key: str
    base_url: str
    app_model: str
    judge_model: str
    thinking: bool = False


def load_settings(env: Mapping[str, str] | None = None) -> LlmSettings:
    env = os.environ if env is None else env
    api_key = env.get("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY not set. Check your .env file.")
    thinking = (env.get("LLM_THINKING") or "off").strip().lower()
    if thinking not in THINKING_VALUES:
        raise RuntimeError(f"LLM_THINKING must be 'on' or 'off', not {thinking!r}. Check your .env file.")
    return LlmSettings(
        api_key=api_key,
        base_url=env.get("LLM_BASE_URL") or DEFAULT_BASE_URL,
        app_model=env.get("LLM_MODEL") or DEFAULT_APP_MODEL,
        judge_model=env.get("LLM_JUDGE_MODEL") or DEFAULT_JUDGE_MODEL,
        thinking=THINKING_VALUES[thinking],
    )


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str  # the raw JSON text the model gave


@dataclass(frozen=True)
class ModelReply:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)


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
    from openai import OpenAI

    if env is None:
        from dotenv import load_dotenv

        load_dotenv()
    settings = load_settings(env)
    client = OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )
    return OpenAIChatModel(client, model or settings.app_model, thinking=settings.thinking)
