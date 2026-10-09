import unittest

from types import SimpleNamespace

from llm import OpenAIChatModel, load_settings


class FakeOpenAIClient:
    def __init__(self, content):
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        self._content = content

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class OpenAIChatModelTest(unittest.TestCase):
    def test_sends_model_name_messages_and_temperature_and_returns_the_text(self):
        client = FakeOpenAIClient("hello")
        model = OpenAIChatModel(client, "some/app-model")
        messages = [{"role": "user", "content": "hi"}]
        self.assertEqual(model.complete(messages, temperature=0), "hello")
        self.assertEqual(
            client.requests, [{"model": "some/app-model", "messages": messages, "temperature": 0}]
        )


class LlmSettingsTest(unittest.TestCase):
    def test_defaults_point_to_the_nvidia_endpoint_and_app_model(self):
        settings = load_settings({"LLM_API_KEY": "test-key"})
        self.assertEqual(settings.base_url, "https://integrate.api.nvidia.com/v1")
        self.assertEqual(settings.app_model, "nvidia/nemotron-3.5-lightning-30b-a3b")
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
        self.assertEqual(settings.app_model, "nvidia/nemotron-3.5-lightning-30b-a3b")

    def test_missing_api_key_is_reported_clearly(self):
        with self.assertRaisesRegex(RuntimeError, "LLM_API_KEY"):
            load_settings({})


if __name__ == "__main__":
    unittest.main()
