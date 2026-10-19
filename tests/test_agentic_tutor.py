"""Seam A for the Agentic Tutor: scripted tool calls in, a Trace and a cited answer out."""
import copy
import unittest

from course_material import COURSES, load_course_material
from llm import ModelReply, ToolCall
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
        self.assertEqual(self.result.read_arguments, ["PEID"])
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


def tool_results(model, call_index):
    return [m["content"] for m in model.calls[call_index]["messages"] if m["role"] == "tool"]


class ToolCallTest(unittest.TestCase):
    def test_an_argument_that_is_not_a_course_returns_unknown_course_and_is_recorded(self):
        model = FakeChatModel([reads("../.env"), reads("PEID"), ANSWER])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(tool_results(model, 1), ["Unknown Course."])
        self.assertEqual(result.read_arguments, ["../.env", "PEID"])
        self.assertEqual(result.materials_read, ["PEID"])
        self.assertEqual(result.read_count, 2)
        self.assertEqual(result.answer, ANSWER)

    def test_malformed_arguments_are_unknown_course_and_never_raise(self):
        bad = ModelReply("", [ToolCall("a", "read_file", "not json"), ToolCall("b", "read_file", None),
                              ToolCall("c", "read_file", '{"course": ["PEID"]}'), ToolCall("d", "read_file", "[1]")])
        model = FakeChatModel([bad, ANSWER])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(tool_results(model, 1), ["Unknown Course."] * 4)
        self.assertEqual(result.read_count, 4)
        self.assertEqual(len(result.read_arguments), 4)
        self.assertEqual(result.materials_read, [])

    def test_a_repeated_read_is_recorded_each_time(self):
        model = FakeChatModel([reads("PEID"), reads("PEID"), ANSWER])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(result.materials_read, ["PEID", "PEID"])
        self.assertEqual(result.read_count, 2)
        self.assertEqual(result.answer, ANSWER)

    def test_two_tool_calls_in_one_reply_are_both_handled_and_counted(self):
        model = FakeChatModel([reads("PEID", "AITB"), ANSWER])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(len(tool_results(model, 1)), 2)
        self.assertEqual(result.materials_read, ["PEID", "AITB"])
        self.assertEqual(result.read_count, 2)

    def test_two_reads_for_an_overlap_case_allow_citations_from_both(self):
        model = FakeChatModel([reads("PEID"), reads("AITB"), "Task [PEID-2.3] and agent [AITB-2.2]."])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(result.materials_read, ["PEID", "AITB"])
        self.assertEqual(result.invalid_citations, [])
        self.assertFalse(result.read_limit_hit)


OUT_OF_SCOPE_SENTENCE = "This question is outside the four Courses."


class FixedSentenceTest(unittest.TestCase):
    def test_the_out_of_scope_sentence_with_no_read_is_out_of_scope(self):
        result = answer_question("How do I bake bread?", FakeChatModel([OUT_OF_SCOPE_SENTENCE]), tutor="agentic")
        self.assertEqual(result.course, "OUT_OF_SCOPE")
        self.assertEqual(result.materials_read, [])
        self.assertFalse(result.is_refusal)
        self.assertIsNone(result.error)

    def test_the_refusal_after_a_read_names_the_course_read(self):
        model = FakeChatModel([reads("DTGS"), "This is not covered in the DTGS material."])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertTrue(result.is_refusal)
        self.assertEqual(result.course, "DTGS")

    def test_a_refusal_naming_a_course_not_read_is_not_the_refusal(self):
        model = FakeChatModel([reads("DTGS"), "This is not covered in the PEID material."])
        self.assertFalse(answer_question(QUESTION, model, tutor="agentic").is_refusal)

    def test_the_refusal_may_name_either_course_read(self):
        model = FakeChatModel([reads("PEID", "AITB"), "This is not covered in the AITB material."])
        self.assertTrue(answer_question(QUESTION, model, tutor="agentic").is_refusal)

    def test_the_out_of_scope_sentence_after_a_read_is_not_out_of_scope(self):
        model = FakeChatModel([reads("GAIF"), OUT_OF_SCOPE_SENTENCE])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(result.course, "GAIF")
        self.assertFalse(result.is_refusal)
        self.assertEqual(result.answer, OUT_OF_SCOPE_SENTENCE)


class FailedModelCallTest(unittest.TestCase):
    def test_a_failed_call_mid_loop_gives_an_error_result_with_the_trace_so_far(self):
        model = FakeChatModel([reads("PEID"), TimeoutError("service did not answer")])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertIn("service did not answer", result.error)
        self.assertEqual(result.materials_read, ["PEID"])
        self.assertEqual(result.answer, "")


class ReadLimitTest(unittest.TestCase):
    def test_after_the_fourth_read_one_final_call_with_tools_off_forces_the_answer(self):
        model = FakeChatModel([reads("PEID"), reads("AITB"), reads("GAIF"), reads("DTGS"), "Forced [PEID-2.3]."])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(len(model.calls), 5)
        self.assertIsNone(model.calls[-1]["tools"])
        self.assertEqual(result.answer, "Forced [PEID-2.3].")
        self.assertEqual(result.read_count, 4)
        self.assertTrue(result.read_limit_hit)
        self.assertIsNone(result.error)

    def test_tool_calls_in_the_forced_reply_are_not_followed(self):
        model = FakeChatModel([reads("PEID", "AITB", "GAIF", "DTGS"), reads("PEID"), "never asked"])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(len(model.calls), 2)
        self.assertEqual(result.read_count, 4)
        self.assertTrue(result.read_limit_hit)

    def test_tool_calls_past_the_fourth_read_in_one_reply_are_not_read(self):
        model = FakeChatModel(
            [reads("PEID"), reads("AITB"), reads("GAIF"), reads("DTGS", "PEID", "AITB"), "Forced [PEID-2.3]."]
        )
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(result.read_count, 4)
        self.assertEqual(result.materials_read, ["PEID", "AITB", "GAIF", "DTGS"])
        self.assertTrue(result.read_limit_hit)
        self.assertEqual(len(model.calls), 5)
        self.assertIsNone(model.calls[-1]["tools"])
        tool_results = [m["content"] for m in model.calls[-1]["messages"] if m["role"] == "tool"]
        self.assertEqual(tool_results[-2:], ["Read limit reached.", "Read limit reached."])
        self.assertEqual(result.answer, "Forced [PEID-2.3].")


class ConversationProtocolTest(unittest.TestCase):
    def test_every_read_result_matches_the_assistant_tool_call_id(self):
        model = FakeChatModel([reads("PEID", "AITB"), ANSWER])
        answer_question(QUESTION, model, tutor="agentic")
        messages = model.calls[1]["messages"]
        assistant = messages[2]
        self.assertEqual(assistant["role"], "assistant")
        self.assertEqual(
            [call["id"] for call in assistant["tool_calls"]],
            [message["tool_call_id"] for message in messages[3:]],
        )
        self.assertEqual([message["role"] for message in messages[3:]], ["tool", "tool"])

    def test_follow_up_preserves_history_and_checks_only_material_read_this_turn(self):
        history = [
            {"role": "user", "content": QUESTION},
            {"role": "assistant", "content": ANSWER},
        ]
        original = copy.deepcopy(history)
        model = FakeChatModel([reads("AITB"), "Compare [AITB-2.2] and [PEID-2.3]."])
        result = answer_question("How does that compare to business tools?", model, tutor="agentic", history=history)
        self.assertEqual(model.calls[0]["messages"][1:3], original)
        self.assertEqual(history, original)
        self.assertEqual(result.materials_read, ["AITB"])
        self.assertEqual(result.invalid_citations, ["PEID-2.3"])


class ReadBeforeAnswerTest(unittest.TestCase):
    HISTORY = [{"role": "user", "content": QUESTION}, {"role": "assistant", "content": ANSWER}]

    def test_a_follow_up_answered_without_a_read_is_sent_back_to_read_first(self):
        model = FakeChatModel(["From memory [PEID-2.3].", reads("PEID"), ANSWER])
        result = answer_question("Explain the second part.", model, tutor="agentic", history=self.HISTORY)
        self.assertEqual(len(model.calls), 3)
        sent_back = model.calls[1]["messages"]
        self.assertEqual(sent_back[-2], {"role": "assistant", "content": "From memory [PEID-2.3]."})
        self.assertEqual(sent_back[-1]["role"], "user")
        self.assertEqual(model.calls[1]["tools"], model.calls[0]["tools"])
        self.assertEqual(result.answer, ANSWER)
        self.assertEqual(result.materials_read, ["PEID"])
        self.assertEqual(result.invalid_citations, [])

    def test_it_is_sent_back_only_once(self):
        model = FakeChatModel(["From memory [PEID-2.3].", "Still from memory [PEID-2.3]."])
        result = answer_question(QUESTION, model, tutor="agentic")
        self.assertEqual(len(model.calls), 2)
        self.assertEqual(result.answer, "Still from memory [PEID-2.3].")
        self.assertEqual(result.invalid_citations, ["PEID-2.3"])

    def test_out_of_scope_without_a_read_is_not_sent_back(self):
        model = FakeChatModel([OUT_OF_SCOPE_SENTENCE])
        result = answer_question("How do I bake bread?", model, tutor="agentic", history=self.HISTORY)
        self.assertEqual(len(model.calls), 1)
        self.assertEqual(result.course, "OUT_OF_SCOPE")


if __name__ == "__main__":
    unittest.main()
