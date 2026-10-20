"""Actual tutor screens and conversation continuity, without an external LLM."""
import contextlib
import io
import json
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
            visible = [element.value for element in app.markdown]
            self.assertIn("Task and context.", visible)
            self.assertIn("Context describes the situation.", visible)
            self.assertNotIn("Task and context [PEID-2.3].", visible)
            self.assertEqual(
                [element.value for element in app.caption if element.value.startswith("Cited Sections:")],
                ["Cited Sections: PEID-2.3", "Cited Sections: PEID-2.3"],
            )
            history = model.calls[2]["messages"]
            self.assertEqual([m["role"] for m in history], ["system", "user", "assistant", "user"])
            self.assertEqual(history[1]["content"], "What are the parts of a prompt?")
            self.assertEqual(history[2]["content"], "Task and context [PEID-2.3].")
            self.assertEqual(history[3]["content"], "Explain the second part.")
            self.assertEqual(app.session_state.conversation[1]["result"].answer, "Task and context [PEID-2.3].")
            self.assertEqual(app.session_state.conversation[1]["content"], "Task and context [PEID-2.3].")
            app.run()
            self.assertIn("Task and context.", [element.value for element in app.markdown])
            app.button[0].click().run()
            self.assertEqual(len(app.chat_message), 0)

    def test_failed_recovery_shows_retry_and_preserves_only_completed_follow_up_history(self):
        unsupported = "I will read_file before answering."
        model = FakeChatModel([
            reads("PEID"), "Task and context [PEID-2.3].",
            unsupported, unsupported,
            reads("PEID"), "Context gives the background [PEID-2.3].",
        ])
        with patch.dict(os.environ, {"TUTOR": "agentic"}), patch("llm.get_chat_model", return_value=model), \
                contextlib.redirect_stderr(io.StringIO()):
            app = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "src/app.py")).run()
            app.chat_input[0].set_value("Explain the parts of a prompt.").run()
            app.chat_input[0].set_value("Who are you?").run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual([element.value for element in app.info], [
                "Something went wrong while preparing your answer. Please try again in a moment.",
            ])
            visible = [element.value for element in app.markdown]
            self.assertNotIn(unsupported, visible)
            self.assertNotIn("**Course:** Out of scope", visible)
            self.assertFalse(any("none" in text for text in visible))
            self.assertEqual(visible.count("**Answer**"), 1)
            self.assertEqual([element.value for element in app.caption if element.value.startswith("Cited Sections:")], [
                "Cited Sections: PEID-2.3",
            ])
            self.assertFalse(app.session_state.conversation[-2]["include_in_history"])
            self.assertFalse(app.session_state.conversation[-1]["include_in_history"])
            self.assertEqual(app.session_state.conversation[-1]["content"], "")
            app.chat_input[0].set_value("Explain the second part more simply.").run()
            self.assertEqual(model.calls[4]["messages"][1:], [
                {"role": "user", "content": "Explain the parts of a prompt."},
                {"role": "assistant", "content": "Task and context [PEID-2.3]."},
                {"role": "user", "content": "Explain the second part more simply."},
            ])
            self.assertIn("Context gives the background.", [element.value for element in app.markdown])


class CitationDisplayTest(unittest.TestCase):
    def show_answer(self, tutor, replies, question="What is a prompt?"):
        model = FakeChatModel(replies)
        with patch.dict(os.environ, {"TUTOR": tutor}), patch("llm.get_chat_model", return_value=model):
            app = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "src/app.py")).run()
            if tutor == "agentic":
                app.chat_input[0].set_value(question).run()
            else:
                app.text_area[0].set_value(question)
                app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        return app, model

    def replies(self, tutor, answer):
        route = reads("PEID") if tutor == "agentic" else json.dumps({"course": "PEID", "evidence": "prompt"})
        return [route, answer]

    def test_both_tutors_show_clean_answers_complete_footers_and_invalid_citation_warnings(self):
        answer = "Task [PEID-2.3, PEID-2.5].\n\n  - Cost $5 [PEID-2.3]; extra [UNKNOWN-9]."
        for tutor in ("agentic", "routed"):
            with self.subTest(tutor=tutor):
                app, _ = self.show_answer(tutor, self.replies(tutor, answer))
                self.assertIn("Task.\n\n  - Cost \\$5; extra.", [element.value for element in app.markdown])
                self.assertIn(
                    "Cited Sections: PEID-2.3, PEID-2.5, UNKNOWN-9",
                    [element.value for element in app.caption],
                )
                self.assertEqual([element.value for element in app.warning], [
                    "These cited Sections are not Sections of the Course Material read: UNKNOWN-9",
                ])

    def test_both_tutors_omit_the_footer_when_the_answer_has_no_citations(self):
        for tutor in ("agentic", "routed"):
            with self.subTest(tutor=tutor):
                app, _ = self.show_answer(tutor, self.replies(tutor, "An uncited answer [in simple terms]."))
                self.assertIn("An uncited answer [in simple terms].", [element.value for element in app.markdown])
                self.assertFalse(any(element.value.startswith("Cited Sections:") for element in app.caption))

    def test_agentic_user_messages_keep_their_citations_and_dollar_amounts(self):
        question = "Explain [PEID-2.3] with a $5 example [in simple terms]."
        app, model = self.show_answer("agentic", self.replies("agentic", "Task [PEID-2.3]."), question)
        self.assertIn("Explain [PEID-2.3] with a \\$5 example [in simple terms].", [e.value for e in app.markdown])
        self.assertEqual(app.session_state.conversation[0]["content"], question)
        self.assertEqual(model.calls[0]["messages"][1]["content"], question)

    def test_both_tutors_show_only_the_shared_purpose_notice_for_out_of_scope(self):
        for tutor in ("agentic", "routed"):
            with self.subTest(tutor=tutor):
                replies = ["This question is outside the four Courses."] if tutor == "agentic" else [
                    json.dumps({"course": "OUT_OF_SCOPE", "evidence": "Who are you?"}),
                ]
                app, _ = self.show_answer(tutor, replies, "Who are you?")
                self.assertEqual([element.value for element in app.info], [
                    "This tutor answers questions about GAIF, PEID, AITB and DTGS. "
                    "Please ask a question about one of these Courses.",
                ])
                visible = [element.value for element in app.markdown]
                self.assertNotIn("**Answer**", visible)
                self.assertFalse(any("Course Materials read:" in text for text in visible))
                self.assertFalse(any("read_file" in text for text in visible))
                self.assertFalse(any(element.value.startswith("Cited Sections:") for element in app.caption))

    def test_both_tutors_preserve_refusal_out_of_scope_and_retry_notices(self):
        for tutor in ("agentic", "routed"):
            outcomes = (
                (self.replies(tutor, "This is not covered in the PEID material."), "warning",
                 "**Refusal.** The Course Material does not cover this question, so there is no answer to show."),
                (["This question is outside the four Courses."] if tutor == "agentic" else [
                    json.dumps({"course": "OUT_OF_SCOPE", "evidence": "pizza"})
                 ], "info", "This tutor answers questions about GAIF, PEID, AITB and DTGS. "
                 "Please ask a question about one of these Courses."),
                ([TimeoutError("service did not answer")], "info",
                 "Something went wrong while preparing your answer. Please try again in a moment."),
            )
            for replies, notice, expected in outcomes:
                with self.subTest(tutor=tutor, notice=expected), contextlib.redirect_stderr(io.StringIO()):
                    app, _ = self.show_answer(tutor, replies)
                    self.assertIn(expected, [element.value for element in app.get(notice)])
                    self.assertFalse(any(element.value.startswith("Cited Sections:") for element in app.caption))


if __name__ == "__main__":
    unittest.main()
