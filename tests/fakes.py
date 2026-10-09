class FakeChatModel:
    """Stands in for the real chat model: returns scripted replies and records every call.

    A reply that is an exception instance is raised instead of returned, to simulate a failing model service.
    """

    def __init__(self, replies, name="fake-model", thinking=None):
        self.thinking = thinking
        self.name = name
        self._replies = list(replies)
        self.calls = []

    def complete(self, messages, temperature=0.0):
        self.calls.append({"messages": messages, "temperature": temperature})
        reply = self._replies.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        return reply

    def prompt_text(self, call_index):
        return "\n".join(m["content"] for m in self.calls[call_index]["messages"])


class QuestionScriptedModel:
    """Stands in for the real chat model across many questions and repeated runs.

    `script` maps each question to the replies the model gives for it, in call order (Router, then Course Tutor).
    The replies cycle, so a question asked again in the next run gets the next replies in its list.
    """

    def __init__(self, script, name="fake-model", thinking=None):
        self.thinking = thinking
        self.name = name
        self._script = script
        self._calls_per_question = {}

    def complete(self, messages, temperature=0.0):
        question = messages[-1]["content"]
        replies = self._script[question]
        index = self._calls_per_question.get(question, 0)
        self._calls_per_question[question] = index + 1
        reply = replies[index % len(replies)]
        if isinstance(reply, BaseException):
            raise reply
        return reply

    def calls_for(self, question):
        return self._calls_per_question.get(question, 0)
