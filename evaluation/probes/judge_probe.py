"""Probe candidate judge models: reliability, latency, JSON compliance, and whether they catch two broken answers.

    .venv/Scripts/python evaluation/probes/judge_probe.py <run folder> [model ...]

Uses the stored Traces of a run folder (its first Run) and the judge prompts through `judge_answer`, so the probe
calls the judge exactly as the evaluation does. Three kinds of item, each judged on both criteria:
- original: an answer as the tutor gave it (no hand label: the PASS share is reported, not an accuracy);
- wrong Section: the same answer with every cited Section swapped for a Section of another Course, which should be
  judged not Supported;
- wrong question: an answer paired with the question of another case from another Course, which should be judged
  not Responsive.
This is a check of the judge's plumbing and of gross errors only; calibration against hand labels is ticket #8.

Endpoints and keys come from environment variables: NVIDIA_BASE_URL / NVIDIA_API_KEY and COURSE_BASE_URL /
COURSE_API_KEY. Writes judge_probe.json next to this file.
"""
import json
import os
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from openai import OpenAI  # noqa: E402

from cases import load_cases  # noqa: E402
from course_material import COURSES, default_course_materials  # noqa: E402
from judge import ERROR, FAIL, PASS, UNKNOWN, judge_answer  # noqa: E402
from llm import OpenAIChatModel  # noqa: E402
from scoring import needs_judge  # noqa: E402
from tutor import TutorResult  # noqa: E402

# model -> (endpoint prefix of the env vars, thinking switch sent as in the app: False sends "off", None sends none)
CANDIDATES = {
    "course-chat": ("COURSE", None),
    "z-ai/glm-5.3": ("NVIDIA", False),
    "google/gemma-4-31b-it": ("NVIDIA", None),
    "openai/gpt-oss-20b": ("NVIDIA", None),
    "mistralai/mistral-large": ("NVIDIA", None),
}
ORIGINALS, CONTROLS = 8, 4
WORKERS_PER_MODEL = 3


class TimedModel:
    """Wraps a chat model and records the duration of every call."""

    def __init__(self, model):
        self.model, self.name, self.thinking, self.durations = model, model.name, model.thinking, []

    def complete(self, messages, temperature=0.0):
        start = time.perf_counter()
        try:
            return self.model.complete(messages, temperature)
        finally:
            self.durations.append(time.perf_counter() - start)


def items(run_dir: Path):
    run = json.loads((run_dir / "run_1.json").read_text(encoding="utf-8"))
    cases = {c.id: c for c in load_cases(REPO / run["case_file"])}
    materials = default_course_materials()
    answered = []
    for o in run["outputs"]:
        case = cases[o["case_id"]]
        result = TutorResult(question=case.question, course=o["course"], answer=o["answer"], citations=o["citations"],
                             is_refusal=o["is_refusal"], materials_read=o["materials_read"], error=o["error"])
        if needs_judge(case, result):
            answered.append((case, result))
    chosen = answered[:: max(1, len(answered) // ORIGINALS)][:ORIGINALS]
    out = [("original", case, result, None) for case, result in chosen]
    for case, result in chosen[:CONTROLS]:
        other = COURSES[(COURSES.index(result.course) + 1) % len(COURSES)]
        swap = {c: materials[other].section_ids_in_order[i % 5] for i, c in enumerate(result.citations)}
        text = re.sub(r"[A-Z]{4}-\d+\.\d+", lambda m: swap.get(m.group(0), m.group(0)), result.answer)
        broken = TutorResult(**{**result.__dict__, "answer": text, "citations": list(swap.values())})
        out.append(("wrong Section", case, broken, "supported"))
    for case, result in chosen[:CONTROLS]:
        other_case = next(c for c, r in answered if r.course != result.course)
        broken = TutorResult(**{**result.__dict__, "question": other_case.question})
        out.append(("wrong question", other_case, broken, "responsive"))
    return out, materials


def probe(model_name: str, prefix: str, thinking, probe_items, materials) -> dict:
    client = OpenAI(base_url=os.environ[f"{prefix}_BASE_URL"], api_key=os.environ[f"{prefix}_API_KEY"],
                    timeout=120, max_retries=0)
    model = TimedModel(OpenAIChatModel(client, model_name, thinking=thinking))
    with ThreadPoolExecutor(WORKERS_PER_MODEL) as pool:
        judgements = list(pool.map(lambda it: judge_answer(it[1], it[2], model, materials), probe_items))
    verdicts = [v for j in judgements for v in (j.supported, j.responsive)]
    rows = [
        {"kind": kind, "case_id": case.id, "supported": j.supported.verdict, "responsive": j.responsive.verdict,
         "supported_evidence": j.supported.evidence, "responsive_evidence": j.responsive.evidence}
        for (kind, case, _, _), j in zip(probe_items, judgements)
    ]

    def share(kind, criterion, verdict):
        picked = [r[criterion] for r in rows if r["kind"] == kind]
        return f"{sum(v == verdict for v in picked)}/{len(picked)}"

    durations = sorted(model.durations)
    return {
        "model": model_name,
        "calls": len(verdicts),
        "judge errors": sum(v.verdict == ERROR for v in verdicts),
        "UNKNOWN": sum(v.verdict == UNKNOWN for v in verdicts),
        "median s": round(statistics.median(durations), 1),
        "slowest s": round(durations[-1], 1),
        "original Supported PASS": share("original", "supported", PASS),
        "original Responsive PASS": share("original", "responsive", PASS),
        "wrong Section caught (Supported FAIL)": share("wrong Section", "supported", FAIL),
        "wrong question caught (Responsive FAIL)": share("wrong question", "responsive", FAIL),
        "first error": next((v.evidence for v in verdicts if v.verdict == ERROR), ""),
        "rows": rows,
    }


def main() -> None:
    run_dir = Path(sys.argv[1])
    names = sys.argv[2:] or list(CANDIDATES)
    probe_items, materials = items(run_dir)
    with ThreadPoolExecutor(len(names)) as pool:
        results = list(pool.map(lambda n: probe(n, *CANDIDATES[n], probe_items, materials), names))
    out = {"run_folder": run_dir.as_posix(), "items": len(probe_items), "results": results}
    (Path(__file__).parent / "judge_probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
    for r in results:
        print({k: v for k, v in r.items() if k != "rows"})


if __name__ == "__main__":
    main()
