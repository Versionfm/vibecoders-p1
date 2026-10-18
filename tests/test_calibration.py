"""Judge calibration (#8): agreement metrics on a hand-computed example (Seam B), and export -> labels -> report."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from calibration import AGREED, LABELLERS, LabelFileError, agreement, draw_sample, export, report

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
    verdict = F if flagged else P
    return {"case_id": case_id, "answer": f"answer to {case_id}", "citations": ["GAIF-1.3"],
            "judge": {"supported": verdict, "responsive": P}}


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
        run_dir = self.runs / "2026-10-18_000000_fake_routed"
        run_dir.mkdir(parents=True)
        outputs = []
        for n, case_id in enumerate(GOLDEN_CASES):
            flagged = n < 3
            outputs.append({
                "case_id": case_id, "answer": f"Answer {n} [GAIF-1.3].", "citations": ["GAIF-1.3"],
                "judge": {"supported": {"verdict": F if flagged else P, "evidence": f"JUDGE-EVIDENCE-{n}"},
                          "responsive": {"verdict": P, "evidence": "ok"}},
            })
        run = {"run": 1, "tutor": "routed", "case_file": "evaluation/golden_set.json", "outputs": outputs}
        (run_dir / "run_1.json").write_text(json.dumps(run), encoding="utf-8")
        self.items = export([run_dir], self.out)
        self.ids = [i["item"] for i in self.items]

    def write_labels(self, name, supported, reasons=None):
        reasons = reasons or {}
        with open(self.out / f"labels_{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["item", "supported", "supported_reason", "responsive", "responsive_reason"])
            for item, label in supported.items():
                writer.writerow([item, label, reasons.get(item, "not in the Section" if label == F else ""), P, ""])

    def judge_supported(self):
        record = json.loads((self.out / "items.json").read_text(encoding="utf-8"))
        case_to_n = {c: n for n, c in enumerate(GOLDEN_CASES)}
        return {k["item"]: F if case_to_n[k["case_id"]] < 3 else P for k in record["items"]}

    def test_the_sheet_shows_question_answer_and_cited_section_but_not_the_judge(self):
        sheet = (self.out / "sheet.html").read_text(encoding="utf-8")
        self.assertIn("Searle", sheet)  # GS-01's question
        self.assertIn("Answer 0 [GAIF-1.3].", sheet)
        self.assertIn("Chinese Room", sheet)  # text of the cited Section GAIF-1.3
        self.assertNotIn("JUDGE-EVIDENCE", sheet)
        self.assertNotIn("verdict", json.dumps(json.loads((self.out / "items.json").read_text(encoding="utf-8"))))
        for name in (*LABELLERS, AGREED):
            self.assertTrue((self.out / f"labels_{name}.csv").exists())

    def test_the_sample_and_split_cannot_be_drawn_again_over_the_first(self):
        with self.assertRaises(FileExistsError):
            export([self.runs / "2026-10-18_000000_fake_routed"], self.out)

    def test_the_report_compares_the_agreed_labels_with_the_judge_and_records_disagreements(self):
        judge = self.judge_supported()
        first = dict(judge)
        second = dict(judge)
        flipped = self.ids[0]
        second[flipped] = P if judge[flipped] == F else F
        self.write_labels(LABELLERS[0], first)
        self.write_labels(LABELLERS[1], second)
        self.write_labels(AGREED, first, {flipped: "resolved together: the claim is in the Section"})

        text = report(self.out, self.runs)
        self.assertIn("Disagreements: 1.", text)
        self.assertIn("resolved together", text)
        self.assertIn("| Supported | 100.0% | 1.00 |", text)  # agreed labels equal the judge's verdicts

    def test_a_disagreement_without_a_resolution_is_refused(self):
        judge = self.judge_supported()
        second = dict(judge)
        second[self.ids[0]] = P if judge[self.ids[0]] == F else F
        self.write_labels(LABELLERS[0], judge)
        self.write_labels(LABELLERS[1], second)
        self.write_labels(AGREED, {i: P for i in self.ids})
        with self.assertRaisesRegex(LabelFileError, "resolved"):
            report(self.out, self.runs)

    def test_a_fail_without_a_reason_or_a_missing_item_is_refused(self):
        labels = {i: P for i in self.ids}
        labels[self.ids[0]] = F
        self.write_labels(LABELLERS[0], labels, {self.ids[0]: ""})
        self.write_labels(LABELLERS[1], {i: P for i in self.ids})
        self.write_labels(AGREED, {i: P for i in self.ids})
        with self.assertRaisesRegex(LabelFileError, "needs a reason"):
            report(self.out, self.runs)
        self.write_labels(LABELLERS[0], {i: P for i in self.ids[1:]})
        with self.assertRaisesRegex(LabelFileError, "missing items"):
            report(self.out, self.runs)


if __name__ == "__main__":
    unittest.main()
