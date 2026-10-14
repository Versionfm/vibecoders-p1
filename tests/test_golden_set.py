"""The frozen Golden Set file (issue #5): composition, labels and isolation from the prompts. No API key, no network."""
import json
import unittest
from collections import Counter
from pathlib import Path

from cases import load_cases
from course_material import COURSES, default_course_materials

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_SET_FILE = ROOT / "evaluation" / "golden_set.json"
OUT_OF_SCOPE = "OUT_OF_SCOPE"
COMPOSITION = {"in_material": 16, "near_miss": 4, "overlap": 8, "out_of_scope": 4, "refusal": 4}
OVERLAP_PAIRS = Counter({"AITB/PEID": 6, "AITB/DTGS": 2})


def section_course(section_id: str) -> str:
    return section_id.split("-")[0]


class GoldenSetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(GOLDEN_SET_FILE)
        cls.sections = {s for m in default_course_materials().values() for s in m.sections}

    def test_the_file_records_its_version_date_and_reviewers(self):
        data = json.loads(GOLDEN_SET_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 1)
        self.assertTrue(data["frozen_on"])
        self.assertTrue(data["agreed_by"])

    def test_36_cases_with_unique_ids_and_the_agreed_composition(self):
        self.assertEqual(len(self.cases), 36)
        self.assertEqual(len({c.id for c in self.cases}), 36)
        self.assertEqual(Counter(c.type for c in self.cases), COMPOSITION)

    def test_five_in_material_cases_per_course(self):
        per_course = Counter(c.accepted_courses[0] for c in self.cases if c.type in ("in_material", "near_miss"))
        self.assertEqual(per_course, Counter({code: 5 for code in COURSES}))

    def test_near_miss_cases_have_one_accepted_course(self):
        # The Course a Near-miss Case only sounds like is not a field; the pairs are in golden_set_review.md.
        for case in self.cases:
            if case.type == "near_miss":
                self.assertEqual(len(case.accepted_courses), 1, case.id)

    def test_overlap_cases_have_two_accepted_courses_in_the_agreed_pairs(self):
        overlaps = [c for c in self.cases if c.type == "overlap"]
        for case in overlaps:
            self.assertEqual(len(case.accepted_courses), 2, case.id)
            cited = {section_course(s) for s in case.expected_sections}
            self.assertEqual(cited, set(case.accepted_courses), case.id)
        self.assertEqual(Counter("/".join(sorted(c.accepted_courses)) for c in overlaps), OVERLAP_PAIRS)

    def test_answer_cases_expect_existing_sections_of_their_accepted_courses_and_have_key_facts(self):
        for case in self.cases:
            if case.type not in ("in_material", "near_miss", "overlap"):
                continue
            self.assertTrue(case.expected_sections, case.id)
            self.assertTrue(case.key_facts, case.id)
            self.assertFalse(case.expect_refusal, case.id)
            for section_id in case.expected_sections:
                self.assertIn(section_id, self.sections, case.id)
                self.assertIn(section_course(section_id), case.accepted_courses, case.id)

    def test_refusal_and_out_of_scope_cases_have_no_expected_sections_or_key_facts(self):
        for case in self.cases:
            if case.type == "refusal":
                self.assertTrue(case.expect_refusal, case.id)
                self.assertEqual(len(case.accepted_courses), 1, case.id)
                self.assertIn(case.accepted_courses[0], COURSES, case.id)
            elif case.type == "out_of_scope":
                self.assertFalse(case.expect_refusal, case.id)
                self.assertEqual(case.accepted_courses, [OUT_OF_SCOPE], case.id)
            else:
                continue
            self.assertEqual(case.expected_sections, [], case.id)
            self.assertEqual(case.key_facts, [], case.id)

    def test_no_golden_set_question_appears_in_any_prompt(self):
        prompts = " ".join(p.read_text(encoding="utf-8").lower() for p in (ROOT / "prompts").glob("*.md"))
        for case in self.cases:
            self.assertNotIn(case.question.lower(), prompts, case.id)


if __name__ == "__main__":
    unittest.main()
