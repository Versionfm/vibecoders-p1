import json
import tempfile
import unittest
from pathlib import Path

from cases import SAMPLE_CASE_FILE, CaseFileError, load_cases
from course_material import load_all_course_materials

VALID_CASE = {
    "id": "S1",
    "type": "overlap",
    "question": "What makes a request to an AI tool effective?",
    "accepted_courses": ["PEID", "AITB"],
    "expected_sections": ["PEID-2.3", "AITB-2.2"],
    "expect_refusal": False,
    "key_facts": ["A request names the task and the context."],
}


def write_case_file(cases):
    folder = tempfile.TemporaryDirectory()
    path = Path(folder.name) / "cases.json"
    path.write_text(json.dumps({"description": "test cases", "cases": cases}), encoding="utf-8")
    return folder, path


class LoadCasesTest(unittest.TestCase):
    def test_a_case_file_in_the_golden_set_format_loads_every_field(self):
        folder, path = write_case_file([VALID_CASE])
        with folder:
            [case] = load_cases(path)
        self.assertEqual(case.id, "S1")
        self.assertEqual(case.type, "overlap")
        self.assertEqual(case.accepted_courses, ["PEID", "AITB"])
        self.assertEqual(case.expected_sections, ["PEID-2.3", "AITB-2.2"])
        self.assertFalse(case.expect_refusal)
        self.assertEqual(case.key_facts, ["A request names the task and the context."])

    def test_a_case_with_a_missing_field_or_unknown_type_or_course_is_rejected(self):
        broken = [
            {k: v for k, v in VALID_CASE.items() if k != "accepted_courses"},
            {**VALID_CASE, "type": "tricky"},
            {**VALID_CASE, "accepted_courses": ["MATH"]},
        ]
        for case in broken:
            folder, path = write_case_file([case])
            with folder, self.subTest(case=case), self.assertRaises(CaseFileError):
                load_cases(path)

    def test_duplicate_case_ids_are_rejected(self):
        folder, path = write_case_file([VALID_CASE, VALID_CASE])
        with folder, self.assertRaises(CaseFileError):
            load_cases(path)

    def test_the_sample_case_file_covers_every_case_type(self):
        types = {case.type for case in load_cases(SAMPLE_CASE_FILE)}
        self.assertEqual(types, {"in_material", "near_miss", "overlap", "out_of_scope", "refusal"})

    def test_every_expected_section_in_the_sample_case_file_exists(self):
        known = {sid for m in load_all_course_materials().values() for sid in m.sections}
        for case in load_cases(SAMPLE_CASE_FILE):
            self.assertLessEqual(set(case.expected_sections), known, case.id)


if __name__ == "__main__":
    unittest.main()
