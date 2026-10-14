import importlib.util
import unittest

from types import SimpleNamespace

from llm import OpenAIChatModel, ToolCall, get_chat_model, load_settings

READ_FILE_TOOL = {"type": "function", "function": {"name": "read_file", "parameters": {"type": "object"}}}


class FakeOpenAIClient:
    def __init__(self, content, tool_calls=None):
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        self._content = content
        self._tool_calls = tool_calls

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        message = SimpleNamespace(content=self._content, tool_calls=self._tool_calls)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def openai_tool_call(call_id, name, arguments):
    return SimpleNamespace(id=call_id, type="function", function=SimpleNamespace(name=name, arguments=arguments))


class ToolOfferTest(unittest.TestCase):
    def test_tools_are_sent_when_offered(self):
        client = FakeOpenAIClient("hello")
        OpenAIChatModel(client, "some/app-model").chat([{"role": "user", "content": "hi"}], tools=[READ_FILE_TOOL])
        self.assertEqual(client.requests[0]["tools"], [READ_FILE_TOOL])

    def test_tools_are_not_sent_when_not_offered(self):
        client = FakeOpenAIClient("hello")
        reply = OpenAIChatModel(client, "some/app-model").chat([{"role": "user", "content": "hi"}])
        self.assertNotIn("tools", client.requests[0])
        self.assertEqual((reply.content, reply.tool_calls), ("hello", []))

    def test_tool_calls_in_a_response_become_tool_calls_in_the_reply(self):
        client = FakeOpenAIClient(None, [openai_tool_call("call-1", "read_file", '{"course": "PEID"}')])
        model = OpenAIChatModel(client, "some/app-model")
        reply = model.chat([{"role": "user", "content": "hi"}], tools=[READ_FILE_TOOL])
        self.assertEqual(reply.content, "")
        self.assertEqual(reply.tool_calls, [ToolCall("call-1", "read_file", '{"course": "PEID"}')])


class OpenAIChatModelTest(unittest.TestCase):
    def test_sends_model_name_messages_and_temperature_and_returns_the_text(self):
        client = FakeOpenAIClient("hello")
        model = OpenAIChatModel(client, "some/app-model")
        messages = [{"role": "user", "content": "hi"}]
        self.assertEqual(model.complete(messages, temperature=0), "hello")
        self.assertEqual(
            client.requests, [{"model": "some/app-model", "messages": messages, "temperature": 0}]
        )

    def test_thinking_off_or_on_is_sent_as_both_the_chat_template_and_the_deepseek_switch(self):
        for thinking, deepseek_type in ((False, "disabled"), (True, "enabled")):
            with self.subTest(thinking=thinking):
                client = FakeOpenAIClient("hello")
                model = OpenAIChatModel(client, "some/app-model", thinking=thinking)
                model.complete([{"role": "user", "content": "hi"}])
                self.assertEqual(
                    client.requests[0]["extra_body"],
                    {"chat_template_kwargs": {"enable_thinking": thinking}, "thinking": {"type": deepseek_type}},
                )
                self.assertIs(model.thinking, thinking)


@unittest.skipUnless(importlib.util.find_spec("openai"), "openai is not installed")
class GetChatModelTest(unittest.TestCase):
    def test_the_client_has_a_bounded_timeout_and_at_most_one_retry(self):
        model = get_chat_model(env={"LLM_API_KEY": "test-key"})
        self.assertEqual(model._client.max_retries, 1)
        self.assertEqual(model._client.timeout, 60.0)

    def test_the_thinking_setting_reaches_the_chat_model(self):
        self.assertIs(get_chat_model(env={"LLM_API_KEY": "k"}).thinking, False)
        self.assertIs(get_chat_model(env={"LLM_API_KEY": "k", "LLM_THINKING": "on"}).thinking, True)


class LlmSettingsTest(unittest.TestCase):
    def test_defaults_point_to_the_nvidia_endpoint_and_app_model(self):
        settings = load_settings({"LLM_API_KEY": "test-key"})
        self.assertEqual(settings.base_url, "https://integrate.api.nvidia.com/v1")
        self.assertEqual(settings.app_model, "nvidia/nemotron-3-super-120b-a12b")
        self.assertEqual(settings.api_key, "test-key")

    def test_every_setting_comes_from_the_environment(self):
        settings = load_settings(
            {
                "LLM_API_KEY": "k",
                "LLM_BASE_URL": "https://example.test/v1",
                "LLM_MODEL": "some/app-model",
                "LLM_JUDGE_MODEL": "other/judge-model",
            }
        )
        self.assertEqual(settings.base_url, "https://example.test/v1")
        self.assertEqual(settings.app_model, "some/app-model")
        self.assertEqual(settings.judge_model, "other/judge-model")

    def test_empty_values_fall_back_to_defaults(self):
        settings = load_settings({"LLM_API_KEY": "k", "LLM_BASE_URL": "", "LLM_MODEL": ""})
        self.assertEqual(settings.base_url, "https://integrate.api.nvidia.com/v1")
        self.assertEqual(settings.app_model, "nvidia/nemotron-3-super-120b-a12b")

    def test_thinking_is_off_unless_switched_on(self):
        self.assertFalse(load_settings({"LLM_API_KEY": "k"}).thinking)
        self.assertFalse(load_settings({"LLM_API_KEY": "k", "LLM_THINKING": ""}).thinking)
        for value in ("off", "OFF", "Off"):
            self.assertFalse(load_settings({"LLM_API_KEY": "k", "LLM_THINKING": value}).thinking)
        for value in ("on", "ON", " on "):
            self.assertTrue(load_settings({"LLM_API_KEY": "k", "LLM_THINKING": value}).thinking)

    def test_an_unknown_thinking_value_is_reported_clearly(self):
        with self.assertRaisesRegex(RuntimeError, "LLM_THINKING"):
            load_settings({"LLM_API_KEY": "k", "LLM_THINKING": "maybe"})

    def test_missing_api_key_is_reported_clearly(self):
        with self.assertRaisesRegex(RuntimeError, "LLM_API_KEY"):
            load_settings({})


if __name__ == "__main__":
    unittest.main()
