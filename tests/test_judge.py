"""The LLM judge: the Answer Step with judge verdicts (Seam B) and the judge call itself, with fake models."""
import json
import unittest

from cases import EvaluationCase
from course_material import default_course_materials
from judge import ERROR, FAIL, PASS, UNKNOWN, Judgement, JudgeVerdict, judge_answer
from scoring import answer_step, needs_judge, score_run, score_trace
from tests.fakes import FakeChatModel
from tests.test_scoring import case
from tutor import TutorResult


def judged(supported=PASS, responsive=PASS):
    return Judgement(
        JudgeVerdict(supported, f"supported {supported}"), JudgeVerdict(responsive, f"responsive {responsive}")
    )


def verdict_reply(verdict, evidence="because"):
    return json.dumps({"evidence": evidence, "verdict": verdict})


ANSWER_CASE = case("p1", ["PEID"], expected_sections=["PEID-1.9"])
GOOD_ANSWER = TutorResult(
    question="q", course="PEID", answer="Models predict tokens [PEID-1.9].", citations=["PEID-1.9"],
    materials_read=["PEID"], read_count=1,
)
REFUSAL_CASE = case("r1", ["PEID"], "refusal", expect_refusal=True)
REFUSAL = TutorResult(
    question="q", course="PEID", answer="This is not covered in the PEID material.", is_refusal=True,
    materials_read=["PEID"], read_count=1,
)
OUT_OF_SCOPE_CASE = case("x1", ["OUT_OF_SCOPE"], "out_of_scope")
OUT_OF_SCOPE = TutorResult(question="q", course="OUT_OF_SCOPE")


class AnswerStepWithJudgeTest(unittest.TestCase):
    def test_an_expected_answer_cited_correctly_and_judged_supported_and_responsive_passes(self):
        self.assertTrue(answer_step(ANSWER_CASE, GOOD_ANSWER, judged()).passed)
        self.assertTrue(score_trace(ANSWER_CASE, GOOD_ANSWER, judged()).success)

    def test_a_negative_supported_verdict_fails_the_answer_step_and_end_to_end_success(self):
        verdict = answer_step(ANSWER_CASE, GOOD_ANSWER, judged(supported=FAIL))
        self.assertFalse(verdict.passed)
        self.assertIn("not Supported", verdict.reason)
        self.assertIn("supported FAIL", verdict.reason)  # the judge's evidence is kept
        score = score_trace(ANSWER_CASE, GOOD_ANSWER, judged(supported=FAIL))
        self.assertFalse(score.success)
        self.assertEqual(score.earliest_failure[0], "Answer")

    def test_a_negative_responsive_verdict_fails_the_answer_step(self):
        verdict = answer_step(ANSWER_CASE, GOOD_ANSWER, judged(responsive=FAIL))
        self.assertFalse(verdict.passed)
        self.assertIn("not Responsive", verdict.reason)

    def test_a_judge_error_or_an_unknown_verdict_is_never_a_pass(self):
        for supported, responsive, words in ((ERROR, PASS, "judge error"), (PASS, UNKNOWN, "could not decide")):
            with self.subTest(supported=supported, responsive=responsive):
                verdict = answer_step(ANSWER_CASE, GOOD_ANSWER, judged(supported, responsive))
                self.assertFalse(verdict.passed)
                self.assertIn(words, verdict.reason)

    def test_a_failed_code_check_is_the_reason_even_when_the_judge_passes(self):
        wrong_section = TutorResult(**{**GOOD_ANSWER.__dict__, "citations": ["PEID-1.1"]})
        verdict = answer_step(ANSWER_CASE, wrong_section, judged())
        self.assertFalse(verdict.passed)
        self.assertIn("cites no expected Section", verdict.reason)

    def test_an_expected_refusal_or_out_of_scope_passes_without_the_judge(self):
        self.assertFalse(needs_judge(REFUSAL_CASE, REFUSAL))
        self.assertFalse(needs_judge(OUT_OF_SCOPE_CASE, OUT_OF_SCOPE))
        self.assertTrue(answer_step(REFUSAL_CASE, REFUSAL, None).passed)
        self.assertTrue(answer_step(OUT_OF_SCOPE_CASE, OUT_OF_SCOPE, None).passed)
        self.assertTrue(needs_judge(ANSWER_CASE, GOOD_ANSWER))

    def test_without_a_judge_the_answer_step_is_code_checks_only(self):
        self.assertTrue(answer_step(ANSWER_CASE, GOOD_ANSWER).passed)


class JudgeRatesTest(unittest.TestCase):
    def test_rates_are_over_the_judged_answers_and_undecided_counts_unknown_and_errors(self):
        cases = [ANSWER_CASE, ANSWER_CASE, ANSWER_CASE, REFUSAL_CASE]
        results = [GOOD_ANSWER, GOOD_ANSWER, GOOD_ANSWER, REFUSAL]
        judgements = [judged(), judged(supported=FAIL), judged(UNKNOWN, ERROR), None]
        metrics = score_run(cases, results, judgements)

        self.assertAlmostEqual(metrics["Supported rate"], 1 / 3)
        self.assertAlmostEqual(metrics["Responsive rate"], 2 / 3)
        self.assertAlmostEqual(metrics["Judge undecided rate"], 2 / 6)
        self.assertAlmostEqual(metrics["Answer Step"], 2 / 4)  # one good answer and the Refusal
        self.assertAlmostEqual(metrics["End-to-end Success"], 2 / 4)

    def test_without_a_judge_the_judge_rates_are_left_out(self):
        metrics = score_run([ANSWER_CASE], [GOOD_ANSWER])
        self.assertNotIn("Supported rate", metrics)
        self.assertEqual(metrics["Answer Step"], 1.0)


class JudgeCallTest(unittest.TestCase):
    def setUp(self):
        self.materials = default_course_materials()
        self.case = EvaluationCase(
            "p1", "in_material", "q", ["PEID"], ["PEID-1.9"], False, ["A key fact about tokens."]
        )

    def test_one_call_per_criterion_at_temperature_zero_with_the_verdicts_parsed(self):
        judge = FakeChatModel([verdict_reply(PASS, "found in PEID-1.9"), verdict_reply("fail", "off the question")])
        judgement = judge_answer(self.case, GOOD_ANSWER, judge, self.materials)

        self.assertEqual(judgement.supported, JudgeVerdict(PASS, "found in PEID-1.9"))
        self.assertEqual(judgement.responsive, JudgeVerdict(FAIL, "off the question"))
        self.assertEqual([c["temperature"] for c in judge.calls], [0.0, 0.0])
        self.assertTrue(all(c["tools"] is None for c in judge.calls))

    def test_the_supported_call_sees_the_cited_section_text_and_the_responsive_call_the_key_facts(self):
        judge = FakeChatModel([verdict_reply(PASS), verdict_reply(PASS)])
        judge_answer(self.case, GOOD_ANSWER, judge, self.materials)

        section = self.materials["PEID"].sections["PEID-1.9"]
        self.assertIn(section.text, judge.prompt_text(0))
        self.assertIn(GOOD_ANSWER.answer, judge.prompt_text(0))
        self.assertIn("A key fact about tokens.", judge.prompt_text(1))
        self.assertNotIn(section.text, judge.prompt_text(1))

    def test_an_unparseable_reply_or_a_missing_verdict_is_a_judge_error(self):
        for reply in ("PASS, looks fine", json.dumps({"evidence": "x", "verdict": "MAYBE"}), json.dumps(["PASS"])):
            with self.subTest(reply=reply):
                judgement = judge_answer(self.case, GOOD_ANSWER, FakeChatModel([reply, reply]), self.materials)
                self.assertEqual(judgement.supported.verdict, ERROR)
                self.assertFalse(judgement.supported.passed)

    def test_a_failed_judge_call_is_a_judge_error_and_does_not_raise(self):
        judge = FakeChatModel([TimeoutError("judge did not answer"), verdict_reply(PASS)])
        judgement = judge_answer(self.case, GOOD_ANSWER, judge, self.materials)
        self.assertEqual(judgement.supported.verdict, ERROR)
        self.assertIn("TimeoutError", judgement.supported.evidence)
        self.assertTrue(judgement.responsive.passed)

    def test_a_verdict_wrapped_in_a_code_fence_is_read(self):
        reply = "```json\n" + verdict_reply(UNKNOWN, "cannot tell") + "\n```"
        judgement = judge_answer(self.case, GOOD_ANSWER, FakeChatModel([reply, reply]), self.materials)
        self.assertEqual(judgement.supported, JudgeVerdict(UNKNOWN, "cannot tell"))


if __name__ == "__main__":
    unittest.main()
