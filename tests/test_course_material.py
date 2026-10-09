import re
import unittest

from course_material import COURSES, default_course_materials, load_course_material

SECTION_ID = re.compile(r"^(GAIF|PEID|AITB|DTGS)-\d+\.\d+$")


class CourseMaterialLoadingTest(unittest.TestCase):
    def test_all_four_course_materials_parse_into_sections(self):
        self.assertEqual(set(COURSES), {"GAIF", "PEID", "AITB", "DTGS"})
        for code in COURSES:
            material = load_course_material(code)
            self.assertEqual(material.code, code)
            self.assertGreater(len(material.sections), 5, code)

    def test_section_identifiers_are_well_formed_and_belong_to_their_course(self):
        for code in COURSES:
            for section_id in load_course_material(code).sections:
                self.assertRegex(section_id, SECTION_ID)
                self.assertTrue(section_id.startswith(code + "-"), section_id)

    def test_section_identifiers_are_unique_across_all_courses(self):
        seen = []
        for code in COURSES:
            seen.extend(load_course_material(code).section_ids_in_order)
        self.assertEqual(len(seen), len(set(seen)))

    def test_known_section_is_keyed_by_identifier_with_its_title_and_text(self):
        section = load_course_material("PEID").sections["PEID-2.3"]
        self.assertEqual(section.title, "The six parts of a good prompt")
        self.assertTrue(section.text.strip())
        self.assertNotIn("PEID-2.4 Two principles", section.text)

    def test_material_keeps_the_whole_text(self):
        material = load_course_material("GAIF")
        self.assertIn("### GAIF-2.5 The McCulloch-Pitts neuron (1943)", material.text)


class DefaultCourseMaterialsTest(unittest.TestCase):
    def test_the_frozen_course_material_is_loaded_once_and_reused(self):
        first = default_course_materials()
        self.assertIs(default_course_materials(), first)
        self.assertEqual(set(first), set(COURSES))
        self.assertEqual(first["PEID"].sections, load_course_material("PEID").sections)


if __name__ == "__main__":
    unittest.main()
