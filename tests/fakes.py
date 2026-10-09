class FakeChatModel:
    """Stands in for the real chat model: returns scripted replies and records every call."""

    def __init__(self, replies, name="fake-model"):
        self.name = name
        self._replies = list(replies)
        self.calls = []

    def complete(self, messages, temperature=0.0):
        self.calls.append({"messages": messages, "temperature": temperature})
        return self._replies.pop(0)

    def prompt_text(self, call_index):
        return "\n".join(m["content"] for m in self.calls[call_index]["messages"])
