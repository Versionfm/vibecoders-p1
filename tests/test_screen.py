"""What the screen does with an answer, without Streamlit: Markdown-safe text and calm failure handling."""
import contextlib
import io
import json
import unittest

from screen import answer_for_display, ask, markdown_safe, tutor_setting
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

    # The screen shows the retry message on an error, the Out of scope message when the course is OUT_OF_SCOPE,
    # and the Refusal box when is_refusal is set, for either tutor.
    def test_the_refusal_comes_back_as_a_refusal(self):
        model = FakeChatModel([reads("DTGS"), "This is not covered in the DTGS material."])
        result = ask("When is the exam?", lambda: model, tutor="agentic")
        self.assertTrue(result.is_refusal)
        self.assertIsNone(result.error)

    def test_the_out_of_scope_sentence_comes_back_as_out_of_scope(self):
        model = FakeChatModel(["This question is outside the four Courses."])
        result = ask("How do I bake bread?", lambda: model, tutor="agentic")
        self.assertEqual(result.course, "OUT_OF_SCOPE")

    def test_a_failed_model_call_mid_loop_comes_back_as_an_error_and_is_logged(self):
        model = FakeChatModel([reads("PEID"), TimeoutError("service did not answer")])
        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            result = ask("What is a prompt?", lambda: model, tutor="agentic")
        self.assertIsNotNone(result.error)
        self.assertIn("service did not answer", console.getvalue())

    def test_an_unknown_tutor_setting_gives_no_result_and_logs_the_reason(self):
        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            result = ask("What is a prompt?", lambda: FakeChatModel([]), tutor="hybrid")
        self.assertIsNone(result)
        self.assertIn("hybrid", console.getvalue())


class AnswerForDisplayTest(unittest.TestCase):
    def test_individual_repeated_adjacent_and_grouped_citations_are_hidden(self):
        for marker in (
            "[PEID-2.3]", "[PEID-2.3] [PEID-2.3]", "[PEID-2.3][PEID-2.5]",
            "[PEID-2.3, PEID-2.5]", "[PEID-2.3; PEID-2.5]", "[ UNKNOWN-999; GAIF-1 ]",
        ):
            with self.subTest(marker=marker):
                self.assertEqual(answer_for_display(f"A fact {marker}."), "A fact.")

    def test_ordinary_brackets_mixed_references_and_markdown_links_are_preserved(self):
        text = (
            "Keep [in simple terms], [1], [gaif-2.4], [GAIF 2.3] and [PEID-2.3, note].\n"
            "Read [PEID-2.3](https://example.test/course) and [course](https://example.test/).\n"
            "The fact [PEID-2.3]."
        )
        self.assertEqual(answer_for_display(text), text.replace("The fact [PEID-2.3].", "The fact."))

    def test_removed_markers_keep_word_separation_punctuation_and_list_structure(self):
        self.assertEqual(
            answer_for_display(
                "First [PEID-2.3] sentence [PEID-2.5] .\n\n"
                "  - Item [PEID-2.3].\n"
                "    [PEID-2.3]\n"
                "next[PEID-2.3]word; then [PEID-2.3] , done.\n"
                "Keep  these spaces."
            ),
            "First sentence.\n\n  - Item.\n\nnext word; then, done.\nKeep  these spaces.",
        )

    def test_escaped_markers_leave_no_stray_markdown_escapes(self):
        self.assertEqual(
            answer_for_display(r"A fact \[PEID-2.3\]; another \[PEID-2.3, PEID-2.5\]."),
            "A fact; another.",
        )

    def test_reference_links_and_citation_like_link_destinations_are_preserved(self):
        for text in (
            "Read [PEID-2.3][notes].\n\n[notes]: https://example.test/[PEID-2.5]",
            "Read [PEID-2.3][].\n\n[PEID-2.3]: https://example.test/course",
            "Read [PEID-2.3].\n\n[PEID-2.3]: https://example.test/course",
            "Read [PEID-2.3][PEID-2.5].\n\n[PEID-2.5]: https://example.test/course",
            "Read [notes][PEID-2.3].\n\n[PEID-2.3]: https://example.test/course",
            "Read [course](https://example.test/[PEID-2.3]) [PEID-2.5].",
        ):
            with self.subTest(text=text):
                expected = text.replace(
                    "(https://example.test/[PEID-2.3]) [PEID-2.5].",
                    "(https://example.test/[PEID-2.3]).",
                )
                self.assertEqual(answer_for_display(text), expected)

    def test_a_marker_before_indented_content_preserves_its_indentation(self):
        self.assertEqual(
            answer_for_display("    [PEID-2.3] - Nested item.\n  [PEID-2.5] Explanation."),
            "    - Nested item.\n  Explanation.",
        )

    def test_empty_and_uncited_text_is_unchanged(self):
        for text in ("", "Plain answer.\n\n  - A list with [an explanation].", "$5 and \\$6"):
            with self.subTest(text=text):
                self.assertEqual(answer_for_display(text), text)

    def test_display_citations_are_removed_before_dollar_escaping(self):
        self.assertEqual(
            markdown_safe(answer_for_display(r"It costs $5 and \$6 [DTGS-3.15].")),
            r"It costs \$5 and \$6.",
        )

    def test_removing_a_citation_preserves_surrounding_markdown_emphasis(self):
        for text, expected in (
            ("**A fact [PEID-2.3]**", "**A fact**"),
            ("*A fact [PEID-2.3]*", "*A fact*"),
            ("_A fact [PEID-2.3]_", "_A fact_"),
            ("A fact[PEID-2.3]**then emphasis**", "A fact **then emphasis**"),
        ):
            with self.subTest(text=text):
                self.assertEqual(answer_for_display(text), expected)


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
