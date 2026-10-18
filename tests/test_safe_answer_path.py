import json
import unittest

from tests.fakes import FakeChatModel
from tutor import answer_question


def router_reply(course, evidence="phrase"):
    return json.dumps({"course": course, "evidence": evidence})


class OutOfScopeTest(unittest.TestCase):
    def test_out_of_scope_skips_the_course_tutor(self):
        model = FakeChatModel([router_reply("OUT_OF_SCOPE", "best pizza")])
        result = answer_question("Where is the best pizza in Lisbon?", model)
        self.assertEqual(len(model.calls), 1)
        self.assertEqual(result.course, "OUT_OF_SCOPE")
        self.assertEqual(result.evidence, "best pizza")
        self.assertEqual(result.answer, "")
        self.assertIsNone(result.error)
        self.assertFalse(result.is_refusal)


class RefusalTest(unittest.TestCase):
    def answer_with(self, tutor_reply, course="DTGS"):
        self.model = FakeChatModel([router_reply(course), tutor_reply])
        return answer_question("When is the DTGS exam?", self.model)

    def test_tutor_prompt_is_a_new_version_that_asks_for_the_exact_refusal_sentence(self):
        result = self.answer_with("This is not covered in the DTGS material.")
        self.assertEqual(result.tutor_prompt_version, "tutor_v2")
        self.assertIn("This is not covered in the DTGS material.", self.model.prompt_text(1))

    def test_the_exact_refusal_sentence_is_detected(self):
        result = self.answer_with("This is not covered in the DTGS material.")
        self.assertTrue(result.is_refusal)
        self.assertEqual(result.citations, [])
        self.assertIsNone(result.error)

    def test_surrounding_whitespace_does_not_hide_a_refusal(self):
        self.assertTrue(self.answer_with("\n This is not covered in the DTGS material. \n").is_refusal)

    def test_a_paraphrase_is_not_a_refusal(self):
        for paraphrase in (
            "This topic is not covered in the DTGS material.",
            "this is not covered in the dtgs material.",
            "This is not covered in the DTGS material",
            "Sorry. This is not covered in the DTGS material.",
        ):
            with self.subTest(paraphrase=paraphrase):
                self.assertFalse(self.answer_with(paraphrase).is_refusal)

    def test_the_refusal_must_name_the_routed_course(self):
        self.assertFalse(self.answer_with("This is not covered in the PEID material.").is_refusal)


class InvalidCitationTest(unittest.TestCase):
    def test_a_citation_to_a_non_existent_section_is_reported_as_invalid(self):
        model = FakeChatModel(
            [router_reply("PEID"), "Prompts have parts [PEID-2.3]. Made up [PEID-99.1]. Also [PEID-2.99]."]
        )
        result = answer_question("What are the parts of a prompt?", model)
        self.assertEqual(result.citations, ["PEID-2.3", "PEID-99.1", "PEID-2.99"])
        self.assertEqual(result.invalid_citations, ["PEID-99.1", "PEID-2.99"])
        self.assertIsNone(result.error)

    def test_malformed_or_unknown_code_identifiers_in_brackets_are_reported_as_invalid(self):
        model = FakeChatModel([router_reply("PEID"), "Parts [PEID-2.3]. Chapter only [PEID-2]. Unknown [XYZ-1.1]."])
        result = answer_question("What are the parts of a prompt?", model)
        self.assertEqual(result.citations, ["PEID-2.3", "PEID-2", "XYZ-1.1"])
        self.assertEqual(result.invalid_citations, ["PEID-2", "XYZ-1.1"])

    def test_a_section_of_another_course_is_invalid_for_the_routed_course(self):
        model = FakeChatModel([router_reply("PEID"), "Parts [PEID-2.3]. Tools [AITB-1.5]."])
        result = answer_question("What are the parts of a prompt?", model)
        self.assertEqual(result.citations, ["PEID-2.3", "AITB-1.5"])
        self.assertEqual(result.invalid_citations, ["AITB-1.5"])


class BrokenRouterReplyTest(unittest.TestCase):
    def test_malformed_or_unknown_router_reply_is_an_error_without_a_default_course(self):
        for reply in (
            "PEID",
            '{"course": "PEID"',
            '["PEID"]',
            '{"evidence": "prompt"}',
            '{"course": "MATH", "evidence": "integral"}',
            '{"course": "peid", "evidence": "prompt"}',
            '{"course": null, "evidence": "prompt"}',
            '{"course": ["PEID"], "evidence": "prompt"}',
            "",
        ):
            with self.subTest(reply=reply):
                model = FakeChatModel([reply, "should never be used"])
                result = answer_question("What is a prompt?", model)
                self.assertIsNotNone(result.error)
                self.assertIsNone(result.course)
                self.assertEqual(result.answer, "")
                self.assertEqual(len(model.calls), 1)


class WrappedRouterReplyTest(unittest.TestCase):
    def test_json_in_a_code_fence_or_surrounded_by_text_is_accepted(self):
        payload = '{"course": "PEID", "evidence": "prompt"}'
        for reply in (
            f"```json\n{payload}\n```",
            f"```\n{payload}\n```",
            f"\n  {payload}  \n",
            f"Here is my choice: {payload} Done.",
        ):
            with self.subTest(reply=reply):
                model = FakeChatModel([reply, "A prompt has parts [PEID-2.3]."])
                result = answer_question("What is a prompt?", model)
                self.assertIsNone(result.error)
                self.assertEqual(result.course, "PEID")
                self.assertEqual(result.evidence, "prompt")

    def test_a_wrapped_reply_with_an_unknown_course_is_still_an_error(self):
        model = FakeChatModel(['```json\n{"course": "MATH", "evidence": "integral"}\n```', "unused"])
        result = answer_question("What is an integral?", model)
        self.assertIsNotNone(result.error)
        self.assertIsNone(result.course)
        self.assertEqual(len(model.calls), 1)


class ModelFailureTest(unittest.TestCase):
    def test_a_router_call_that_times_out_becomes_an_error_result(self):
        model = FakeChatModel([TimeoutError("request timed out")])
        result = answer_question("What is a prompt?", model)
        self.assertIsNotNone(result.error)
        self.assertIsNone(result.course)
        self.assertEqual(result.answer, "")

    def test_a_course_tutor_call_that_raises_becomes_an_error_result(self):
        model = FakeChatModel([router_reply("PEID", "prompt"), ConnectionError("service unavailable")])
        result = answer_question("What is a prompt?", model)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.course, "PEID")
        self.assertEqual(result.answer, "")
        self.assertFalse(result.is_refusal)


if __name__ == "__main__":
    unittest.main()
