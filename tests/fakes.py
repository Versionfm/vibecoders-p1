import json

from llm import ModelReply, ToolCall


def reads(*courses):
    """A scripted model reply that Reads each Course through `read_file`, in one reply."""
    calls = [ToolCall(f"call-{i}", "read_file", json.dumps({"course": c})) for i, c in enumerate(courses, 1)]
    return ModelReply("", calls)


def _as_reply(reply):
    if isinstance(reply, BaseException):
        raise reply
    return reply if isinstance(reply, ModelReply) else ModelReply(reply)


class FakeChatModel:
    """Stands in for the real chat model: returns scripted replies and records every call.

    A reply that is an exception instance is raised instead of returned, to simulate a failing model service.
    A reply that is a `ModelReply` (e.g. from `reads(...)`) scripts tool calls; a string is a text reply.
    """

    def __init__(self, replies, name="fake-model", thinking=None):
        self.thinking = thinking
        self.name = name
        self._replies = list(replies)
        self.calls = []

    def complete(self, messages, temperature=0.0):
        return self.chat(messages, temperature).content

    def chat(self, messages, temperature=0.0, tools=None):
        self.calls.append({"messages": list(messages), "temperature": temperature, "tools": tools})
        return _as_reply(self._replies.pop(0))

    def prompt_text(self, call_index):
        return "\n".join(m["content"] or "" for m in self.calls[call_index]["messages"])


class QuestionScriptedModel:
    """Stands in for the real chat model across many questions and repeated runs.

    `script` maps each question to the replies the model gives for it, in call order (Router, then Course Tutor;
    or the Agentic Tutor's Reads, then its answer). The question is the user message, so the lookup survives tool
    round trips. The replies cycle, so a question asked again in the next run gets the next replies in its list.
    """

    def __init__(self, script, name="fake-model", thinking=None):
        self.thinking = thinking
        self.name = name
        self._script = script
        self._calls_per_question = {}

    def complete(self, messages, temperature=0.0):
        return self.chat(messages, temperature).content

    def chat(self, messages, temperature=0.0, tools=None):
        question = next(m["content"] for m in messages if m["role"] == "user")
        replies = self._script[question]
        index = self._calls_per_question.get(question, 0)
        self._calls_per_question[question] = index + 1
        return _as_reply(replies[index % len(replies)])

    def calls_for(self, question):
        return self._calls_per_question.get(question, 0)
