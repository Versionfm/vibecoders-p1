"""Loads the frozen Course Material files and splits them into citable Sections."""
import functools
import re
from dataclasses import dataclass, field
from pathlib import Path

COURSES = ("GAIF", "PEID", "AITB", "DTGS")
COURSE_NAMES = {
    "GAIF": "Generative AI Foundations",
    "PEID": "Prompt Engineering and Interaction Design",
    "AITB": "AI Tools for Business Professionals",
    "DTGS": "Digital Transformation and Generative AI Strategy",
}
MATERIAL_DIR = Path(__file__).resolve().parent.parent / "data" / "courses"

_SECTION_HEADING = re.compile(r"^### ([A-Z]{4}-\d+\.\d+) (.+?)\s*$")
_CHAPTER_HEADING = re.compile(r"^#{1,2} ")


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    text: str


@dataclass(frozen=True)
class CourseMaterial:
    code: str
    name: str
    text: str
    sections: dict[str, Section]
    section_ids_in_order: list[str] = field(default_factory=list)


def load_course_material(code: str, material_dir: Path = MATERIAL_DIR) -> CourseMaterial:
    if code not in COURSES:
        raise ValueError(f"Unknown Course: {code!r}")
    text = (material_dir / f"{code}.md").read_text(encoding="utf-8")
    ids, sections = _parse_sections(text)
    return CourseMaterial(code, COURSE_NAMES[code], text, sections, ids)


def load_all_course_materials(material_dir: Path = MATERIAL_DIR) -> dict[str, CourseMaterial]:
    return {code: load_course_material(code, material_dir) for code in COURSES}


@functools.cache
def default_course_materials() -> dict[str, CourseMaterial]:
    """The frozen Course Material, read from disk once per process and shared. Treat it as read-only."""
    return load_all_course_materials()


def _parse_sections(text: str) -> tuple[list[str], dict[str, Section]]:
    ids: list[str] = []
    sections: dict[str, Section] = {}
    current: tuple[str, str] | None = None
    body: list[str] = []

    def close() -> None:
        if current:
            ids.append(current[0])
            sections[current[0]] = Section(current[0], current[1], "\n".join(body).strip())

    for line in text.splitlines():
        match = _SECTION_HEADING.match(line)
        if match or _CHAPTER_HEADING.match(line) or line.strip() == "---":
            close()
            current, body = (match.group(1), match.group(2)) if match else None, []
        elif current:
            body.append(line)
    close()
    return ids, sections
