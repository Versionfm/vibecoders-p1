"""Evaluation cases in the Golden Set format (spec #1, "Golden Set"), loaded from a JSON case file."""
import json
from dataclasses import dataclass
from pathlib import Path

from course_material import COURSES

CASE_TYPES = ("in_material", "near_miss", "overlap", "out_of_scope", "refusal")
ROUTING_CLASSES = (*COURSES, "OUT_OF_SCOPE")
FIELDS = ("id", "type", "question", "accepted_courses", "expected_sections", "expect_refusal", "key_facts")
SAMPLE_CASE_FILE = Path(__file__).resolve().parent.parent / "evaluation" / "sample_cases.json"


class CaseFileError(ValueError):
    pass


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    type: str
    question: str
    accepted_courses: list[str]
    expected_sections: list[str]
    expect_refusal: bool
    key_facts: list[str]


def load_cases(path: Path) -> list[EvaluationCase]:
    """A case file is a JSON object with a "cases" list; each case has exactly the Golden Set fields."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = [_parse_case(raw) for raw in data["cases"]]
    ids = [c.id for c in cases]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise CaseFileError(f"Duplicate case ids: {duplicates}")
    return cases


def _parse_case(raw: dict) -> EvaluationCase:
    missing = [f for f in FIELDS if f not in raw]
    if missing:
        raise CaseFileError(f"Case {raw.get('id')!r} is missing fields: {missing}")
    case = EvaluationCase(**{f: raw[f] for f in FIELDS})
    if case.type not in CASE_TYPES:
        raise CaseFileError(f"Case {case.id!r} has unknown type {case.type!r}")
    unknown = [c for c in case.accepted_courses if c not in ROUTING_CLASSES]
    if not case.accepted_courses or unknown:
        raise CaseFileError(f"Case {case.id!r} has invalid Accepted Courses: {case.accepted_courses}")
    return case
