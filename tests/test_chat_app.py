"""Two turns through the actual Agentic Tutor screen, without an external LLM."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from tests.fakes import FakeChatModel, reads


class AgenticChatTest(unittest.TestCase):
    def test_follow_up_keeps_messages_and_sends_history_to_the_model(self):
        model = FakeChatModel([
            reads("PEID"), "Task and context [PEID-2.3].",
            reads("PEID"), "Context describes the situation [PEID-2.3].",
        ])
        with patch.dict(os.environ, {"TUTOR": "agentic"}), patch("llm.get_chat_model", return_value=model):
            app = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "src/app.py")).run()
            self.assertEqual(len(app.chat_input), 1)
            app.chat_input[0].set_value("What are the parts of a prompt?").run()
            app.chat_input[0].set_value("Explain the second part.").run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.chat_message), 4)
            history = model.calls[2]["messages"]
            self.assertEqual([m["role"] for m in history], ["system", "user", "assistant", "user"])
            self.assertEqual(history[1]["content"], "What are the parts of a prompt?")
            self.assertEqual(history[2]["content"], "Task and context [PEID-2.3].")
            self.assertEqual(history[3]["content"], "Explain the second part.")
            app.button[0].click().run()
            self.assertEqual(len(app.chat_message), 0)


if __name__ == "__main__":
    unittest.main()
