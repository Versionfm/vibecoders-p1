"""What the screen does with an answer, without Streamlit: Markdown-safe text and calm failure handling."""
import contextlib
import io
import json
import unittest

from screen import ask, markdown_safe, tutor_setting
from tests.fakes import FakeChatModel, reads


class TutorSettingTest(unittest.TestCase):
    def test_the_routed_tutor_is_the_default(self):
        self.assertEqual(tutor_setting({}), "routed")
        self.assertEqual(tutor_setting({"TUTOR": ""}), "routed")

    def test_the_setting_can_choose_the_agentic_tutor(self):
        self.assertEqual(tutor_setting({"TUTOR": " Agentic "}), "agentic")


class AskWithTheAgenticTutorTest(unittest.TestCase):
    def test_the_agentic_tutor_runs_when_chosen_and_reports_the_course_materials_read(self):
        model = FakeChatModel([reads("PEID"), "Parts [PEID-2.3]."])
        result = ask("What is a prompt?", lambda: model, tutor="agentic")
        self.assertEqual(result.tutor, "agentic")
        self.assertEqual(result.materials_read, ["PEID"])
        self.assertEqual(result.citations, ["PEID-2.3"])

    def test_an_unknown_tutor_setting_gives_no_result_and_logs_the_reason(self):
        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            result = ask("What is a prompt?", lambda: FakeChatModel([]), tutor="hybrid")
        self.assertIsNone(result)
        self.assertIn("hybrid", console.getvalue())


class MarkdownSafeTest(unittest.TestCase):
    def test_dollar_amounts_are_escaped_so_they_are_not_read_as_latex(self):
        self.assertEqual(
            markdown_safe("It costs $0.50 at HubSpot, $0.99 at Fin [DTGS-3.15]."),
            r"It costs \$0.50 at HubSpot, \$0.99 at Fin [DTGS-3.15].",
        )

    def test_an_already_escaped_dollar_is_not_escaped_twice(self):
        self.assertEqual(markdown_safe(r"\$5 and $6"), r"\$5 and \$6")

    def test_text_without_dollars_is_unchanged(self):
        self.assertEqual(markdown_safe("No money here [PEID-2.3]."), "No money here [PEID-2.3].")


class AskTest(unittest.TestCase):
    def test_a_model_that_cannot_be_created_gives_no_result_and_logs_the_reason(self):
        def missing_key():
            raise RuntimeError("LLM_API_KEY not set. Check your .env file.")

        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            result = ask("What is a prompt?", missing_key)
        self.assertIsNone(result)
        self.assertIn("LLM_API_KEY not set", console.getvalue())

    def test_an_error_result_is_logged_to_the_console(self):
        model = FakeChatModel([TimeoutError("service did not answer")])
        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            result = ask("What is a prompt?", lambda: model)
        self.assertIsNotNone(result.error)
        self.assertIn("service did not answer", console.getvalue())

    def test_a_good_answer_is_returned_without_console_noise(self):
        model = FakeChatModel([json.dumps({"course": "PEID", "evidence": "prompt"}), "Parts [PEID-2.3]."])
        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            result = ask("What is a prompt?", lambda: model)
        self.assertEqual(result.citations, ["PEID-2.3"])
        self.assertEqual(console.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
