"""Seam A for the Agentic Tutor: scripted tool calls in, a Trace and a cited answer out."""
import unittest

from course_material import COURSES, load_course_material
from tests.fakes import FakeChatModel, reads
from tutor import answer_question

QUESTION = "What are the parts of a good prompt?"
ANSWER = "A good prompt names the task and gives context [PEID-2.3]."


class OneReadThenCitedAnswerTest(unittest.TestCase):
    def setUp(self):
        self.model = FakeChatModel([reads("PEID"), ANSWER], name="nvidia/test-model")
        self.result = answer_question(QUESTION, self.model, tutor="agentic")

    def test_the_answer_and_its_citations_come_back_without_error(self):
        self.assertEqual(self.result.answer, ANSWER)
        self.assertEqual(self.result.citations, ["PEID-2.3"])
        self.assertEqual(self.result.invalid_citations, [])
        self.assertIsNone(self.result.error)

    def test_the_trace_lists_the_course_read(self):
        self.assertEqual(self.result.tutor, "agentic")
        self.assertEqual(self.result.materials_read, ["PEID"])
        self.assertEqual(self.result.tool_arguments, ["PEID"])
        self.assertEqual(self.result.read_count, 1)
        self.assertFalse(self.result.read_limit_hit)
        self.assertEqual(self.result.course, "PEID")

    def test_read_file_is_offered_with_only_the_four_course_codes(self):
        [tool] = self.model.calls[0]["tools"]
        self.assertEqual(tool["function"]["name"], "read_file")
        self.assertEqual(tool["function"]["parameters"]["properties"]["course"]["enum"], list(COURSES))

    def test_the_read_returns_that_whole_course_material_to_the_model(self):
        self.assertEqual(len(self.model.calls), 2)
        second_call = self.model.prompt_text(1)
        self.assertIn(load_course_material("PEID").text.strip(), second_call)
        self.assertNotIn(load_course_material("AITB").text.strip(), second_call)
        self.assertNotIn(load_course_material("PEID").text.strip(), self.model.prompt_text(0))

    def test_the_question_is_sent_and_the_agentic_prompt_version_is_recorded(self):
        self.assertIn(QUESTION, self.model.prompt_text(0))
        self.assertEqual(self.result.tutor_prompt_version, "agentic_tutor_v1")
        self.assertEqual(self.result.model, "nvidia/test-model")


class CitationValidityTest(unittest.TestCase):
    def test_a_citation_to_a_course_material_not_read_is_invalid(self):
        model = FakeChatModel([reads("PEID"), "Task and context [PEID-2.3]. Name the task [AITB-2.2]."])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(result.citations, ["PEID-2.3", "AITB-2.2"])
        self.assertEqual(result.invalid_citations, ["AITB-2.2"])


if __name__ == "__main__":
    unittest.main()
