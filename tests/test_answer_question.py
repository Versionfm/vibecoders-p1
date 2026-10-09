import json
import unittest

from course_material import load_course_material
from tests.fakes import FakeChatModel
from tutor import answer_question

QUESTION = "What are the parts of a good prompt?"
TUTOR_REPLY = (
    "A good prompt has six parts, including the task and the context [PEID-2.3]. "
    "Few-shot examples show the expected output [PEID-2.5]."
)


def router_reply(course, evidence):
    return json.dumps({"course": course, "evidence": evidence})


class HappyPathTest(unittest.TestCase):
    def setUp(self):
        self.model = FakeChatModel(
            [router_reply("PEID", "parts of a good prompt"), TUTOR_REPLY], name="nvidia/test-model"
        )
        self.result = answer_question(QUESTION, self.model)

    def test_valid_router_json_leads_to_one_tutor_call_with_that_courses_material(self):
        self.assertEqual(len(self.model.calls), 2)
        tutor_prompt = self.model.prompt_text(1)
        self.assertIn(load_course_material("PEID").text.strip(), tutor_prompt)
        self.assertNotIn(load_course_material("AITB").text.strip(), tutor_prompt)
        self.assertIn(QUESTION, tutor_prompt)

    def test_router_sees_the_question_and_runs_at_temperature_zero(self):
        self.assertIn(QUESTION, self.model.prompt_text(0))
        self.assertEqual(self.model.calls[0]["temperature"], 0)

    def test_result_carries_course_evidence_and_answer(self):
        self.assertEqual(self.result.course, "PEID")
        self.assertEqual(self.result.evidence, "parts of a good prompt")
        self.assertEqual(self.result.answer, TUTOR_REPLY)

    def test_citations_are_extracted_from_the_answer(self):
        self.assertEqual(self.result.citations, ["PEID-2.3", "PEID-2.5"])

    def test_happy_path_is_not_a_refusal_and_has_no_error_or_invalid_citations(self):
        self.assertFalse(self.result.is_refusal)
        self.assertEqual(self.result.invalid_citations, [])
        self.assertIsNone(self.result.error)

    def test_result_records_prompt_versions_and_model(self):
        self.assertEqual(self.result.router_prompt_version, "router_v1")
        self.assertEqual(self.result.tutor_prompt_version, "tutor_v2")
        self.assertEqual(self.result.model, "nvidia/test-model")


class CitationPatternTest(unittest.TestCase):
    def answer_with(self, tutor_reply, course="GAIF"):
        model = FakeChatModel([router_reply(course, "neurons"), tutor_reply])
        return answer_question("How do neurons fire?", model)

    def test_repeated_citations_are_listed_once_in_order_of_first_appearance(self):
        result = self.answer_with("A [GAIF-2.2]. B [GAIF-2.1]. C [GAIF-2.2].")
        self.assertEqual(result.citations, ["GAIF-2.2", "GAIF-2.1"])

    def test_text_that_does_not_match_the_fixed_pattern_is_not_a_citation(self):
        result = self.answer_with("See GAIF-2.2 and (GAIF-2.1) and [GAIF 2.3] and [gaif-2.4].")
        self.assertEqual(result.citations, [])


if __name__ == "__main__":
    unittest.main()
