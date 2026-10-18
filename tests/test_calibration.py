"""Judge calibration (#8): agreement metrics on a hand-computed example (Seam B), and export -> labels.md -> report."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from calibration import LabelFileError, agreement, draw_sample, export, rejudge, report
from tests.fakes import FakeChatModel

P, F = "PASS", "FAIL"
GOLDEN_CASES = ["GS-01", "GS-02", "GS-03", "GS-04", "GS-06", "GS-07"]


class AgreementTest(unittest.TestCase):
    def test_a_hand_computed_example(self):
        # human:  P P P F F    judge: P P F F P
        # agree on 3 of 5; human PASSes 3, judge passed 2 of them; human FAILs 2, judge caught 1.
        # chance agreement: 0.6 * 0.6 + 0.4 * 0.4 = 0.52, so kappa = (0.6 - 0.52) / (1 - 0.52) = 1/6.
        a = agreement([P, P, P, F, F], [P, P, F, F, P])
        self.assertEqual(a.n, 5)
        self.assertAlmostEqual(a.accuracy, 0.6)
        self.assertAlmostEqual(a.kappa, 1 / 6)
        self.assertAlmostEqual(a.tpr, 2 / 3)
        self.assertAlmostEqual(a.tnr, 1 / 2)
        self.assertEqual(a.human_fails, 2)

    def test_an_unknown_verdict_or_a_judge_error_counts_as_fail(self):
        a = agreement([F, F], ["UNKNOWN", "ERROR"])
        self.assertEqual(a.accuracy, 1.0)
        self.assertEqual(a.tnr, 1.0)

    def test_kappa_is_undefined_when_both_raters_give_one_label_only(self):
        a = agreement([P, P, P], [P, P, P])
        self.assertEqual(a.accuracy, 1.0)
        self.assertIsNone(a.kappa)
        self.assertIsNone(a.tnr)  # no human FAIL to catch

    def test_perfect_agreement_with_both_labels_has_kappa_one(self):
        self.assertAlmostEqual(agreement([P, F, P, F], [P, F, P, F]).kappa, 1.0)


def fake_answer(case_id, flagged):
    return {"case_id": case_id, "judge": {"supported": F if flagged else P, "responsive": P}}


class SampleTest(unittest.TestCase):
    def test_the_sample_takes_both_kinds_splits_each_and_is_the_same_for_the_same_seed(self):
        answers = [fake_answer(f"C{i}", flagged=i < 6) for i in range(20)]
        first = draw_sample(answers, seed=3, flagged=6, passed=6)
        again = draw_sample(answers, seed=3, flagged=6, passed=6)

        self.assertEqual(first, again)
        self.assertEqual([i["item"] for i in first], [f"L{n:02d}" for n in range(1, 13)])
        flagged = [i for i in first if i["judge"]["supported"] == F]
        self.assertEqual(len(flagged), 6)
        self.assertEqual(sum(i["split"] == "held-out" for i in flagged), 4)
        self.assertEqual(sum(i["split"] == "held-out" for i in first), 8)


class ExportAndReportTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.runs, self.out = root / "runs", root / "calibration"
        self.run_dir = self.runs / "2026-10-18_000000_fake_routed"
        self.run_dir.mkdir(parents=True)
        outputs = []
        for n, case_id in enumerate(GOLDEN_CASES):
            outputs.append({
                "case_id": case_id, "answer": f"Answer {n} [GAIF-1.3].", "citations": ["GAIF-1.3"],
                "judge": {"supported": {"verdict": F if n < 3 else P, "evidence": f"JUDGE-EVIDENCE-{n}"},
                          "responsive": {"verdict": P, "evidence": "ok"}},
            })
        run = {"run": 1, "tutor": "routed", "case_file": "evaluation/golden_set.json", "outputs": outputs}
        (self.run_dir / "run_1.json").write_text(json.dumps(run), encoding="utf-8")
        export([self.run_dir], self.out)
        record = json.loads((self.out / "items.json").read_text(encoding="utf-8"))
        self.case_of = {k["item"]: k["case_id"] for k in record["items"]}

    def judge_supported(self, item):
        return F if GOLDEN_CASES.index(self.case_of[item]) < 3 else P

    def fill(self, supported, reasons=None):
        """Fill labels.md the way the labeller does: type after each field's colon."""
        reasons = reasons or {}
        path = self.out / "labels.md"
        text = path.read_text(encoding="utf-8")
        for item, label in supported.items():
            block = re.search(rf"^## {item}$.*?^Responsive reason: $", text, re.MULTILINE | re.DOTALL)
            reason = reasons.get(item, "not in it" if label in (F, "f") else "")
            filled = (
                block.group(0)
                .replace("Supported: \n", f"Supported: {label}\n")
                .replace("Supported reason: \n", f"Supported reason: {reason}\n")
                .replace("Responsive: \n", "Responsive: PASS\n")
            )
            text = text.replace(block.group(0), filled)
        path.write_text(text, encoding="utf-8")

    def test_the_label_file_shows_question_answer_and_cited_section_but_not_the_judge(self):
        text = (self.out / "labels.md").read_text(encoding="utf-8")
        self.assertIn("Searle", text)  # GS-01's question
        self.assertIn("Answer 0 [GAIF-1.3].", text)
        self.assertIn("Chinese Room", text)  # text of the cited Section GAIF-1.3
        self.assertNotIn("JUDGE-EVIDENCE", text)
        self.assertEqual(text.count("\nSupported: \n"), len(GOLDEN_CASES))
        self.assertNotIn("verdict", (self.out / "items.json").read_text(encoding="utf-8"))

    def test_the_sample_and_split_cannot_be_drawn_again_over_the_first(self):
        with self.assertRaises(FileExistsError):
            export([self.run_dir], self.out)

    def test_the_report_compares_the_labels_with_the_judge(self):
        labels = {item: self.judge_supported(item) for item in self.case_of}
        disagree = next(iter(self.case_of))
        labels[disagree] = P if labels[disagree] == F else F
        labels = {i: ("p" if v == P else "f") if i == disagree else v for i, v in labels.items()}  # short forms
        self.fill(labels, {disagree: "the claim is not in the Section"})

        text = report(self.out, self.runs)
        self.assertIn("Items where the judge and the labels differ", text)
        self.assertIn(f"| {disagree} |", text)
        self.assertIn("Labeller: Gonçalo Augusto", text)
        self.assertIn("FAIL reasons", text)

    def test_rejudged_verdicts_are_stored_and_a_report_can_use_them_and_another_label_file(self):
        items = list(self.case_of)
        # every sampled answer judged again: Supported FAIL for the first item only, PASS for the rest
        replies = []
        for n in range(len(items)):
            replies += [json.dumps({"evidence": "e", "verdict": F if n == 0 else P}), json.dumps({"verdict": P})]
        path = rejudge(FakeChatModel(replies, name="fake/judge"), self.out, self.runs)
        with self.assertRaisesRegex(FileExistsError, "--tag"):  # stored verdicts are never overwritten
            rejudge(FakeChatModel([], name="fake/judge"), self.out, self.runs)
        tagged = rejudge(FakeChatModel(replies, name="fake/judge"), self.out, self.runs, tag="rita")
        self.assertTrue(tagged.name.endswith("_rita.json"))
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(stored["judge_model"], "fake/judge")
        self.assertEqual(stored["items"][items[0]]["supported"]["verdict"], F)

        self.fill({i: F if i == items[0] else P for i in items})
        (self.out / "labels.md").rename(self.out / "labels_filled.md")

        text = report(self.out, self.runs, labels_file="labels_filled.md", verdicts_file=path.name, name="v2")
        self.assertTrue((self.out / "v2.md").exists())
        self.assertIn("`labels_filled.md`", text)
        self.assertIn("fake/judge", text)
        self.assertIn("| Supported | 100.0% |", text)  # the rejudged verdicts equal the labels

    def test_a_missing_label_or_a_fail_without_a_reason_is_refused(self):
        items = list(self.case_of)
        self.fill({i: P for i in items[1:]})
        with self.assertRaisesRegex(LabelFileError, items[0]):
            report(self.out, self.runs)
        self.fill({items[0]: F}, {items[0]: ""})
        with self.assertRaisesRegex(LabelFileError, "needs a reason"):
            report(self.out, self.runs)


if __name__ == "__main__":
    unittest.main()
