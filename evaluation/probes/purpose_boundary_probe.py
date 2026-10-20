"""Live purpose-boundary probe for the Agentic Tutor (#25): does the real app model choose the agreed outcomes?

    .venv/bin/python evaluation/probes/purpose_boundary_probe.py [repetitions]

Runs every case of evaluation/purpose_boundary_cases.json (not Golden Set cases) through the app's own answer
function, with the case's supplied conversation history, `repetitions` times (default 3). Every raw model reply,
including a reply that was sent back for recovery, is recorded. A case passes when the Trace passes the code-check
Steps (no judge) and the answer does not mention `read_file`. Writes purpose_boundary_probe.json next to this file.
Needs the API key in .env; the key is never written.
"""
import json
import os
import sys
import time
from dataclasses import asdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src"))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(REPO, ".env"))

from cases import load_cases  # noqa: E402
from llm import get_chat_model  # noqa: E402
from prompts import AGENTIC_TUTOR_PROMPT_VERSION  # noqa: E402
from scoring import score_trace  # noqa: E402
from tutor import answer_question  # noqa: E402

CASE_FILE = os.path.join(REPO, "evaluation", "purpose_boundary_cases.json")


class RecordingModel:
    """The app model, recording the text and tool calls of every reply."""

    def __init__(self, model):
        self.model, self.name, self.thinking = model, model.name, model.thinking
        self.replies = []

    def chat(self, messages, temperature=0.0, tools=None):
        reply = self.model.chat(messages, temperature, tools=tools)
        self.replies.append({"content": reply.content, "tool_calls": [asdict(c) for c in reply.tool_calls]})
        return reply

    def complete(self, messages, temperature=0.0):
        return self.chat(messages, temperature).content


def main(repetitions: int) -> None:
    histories = json.load(open(CASE_FILE, encoding="utf-8")).get("histories", {})
    model = get_chat_model()
    records = []
    for case in load_cases(CASE_FILE):
        for repetition in range(1, repetitions + 1):
            recording = RecordingModel(model)
            started = time.monotonic()
            result = answer_question(case.question, recording, tutor="agentic", history=histories.get(case.id))
            score = score_trace(case, result)
            leaked = "read_file" in result.answer
            records.append({
                "case_id": case.id, "repetition": repetition, "question": case.question,
                "history": histories.get(case.id, []),
                "expected": {"type": case.type, "accepted_courses": case.accepted_courses,
                             "expected_sections": case.expected_sections},
                "replies": recording.replies,
                "answer": result.answer, "course": result.course, "error": result.error,
                "materials_read": result.materials_read, "read_arguments": result.read_arguments,
                "citations": result.citations, "invalid_citations": result.invalid_citations,
                "is_refusal": result.is_refusal,
                "earliest_failing_step": score.earliest_failure and list(score.earliest_failure),
                "mentions_read_file": leaked,
                "verdict": "PASS" if score.success and not leaked else "FAIL",
                "seconds": round(time.monotonic() - started, 1),
            })
            print(case.id, repetition, records[-1]["verdict"], result.course, result.materials_read,
                  (result.error or result.answer)[:70].replace("\n", " "))
    passed = sum(r["verdict"] == "PASS" for r in records)
    out = {
        "probe": "purpose_boundary", "date": time.strftime("%Y-%m-%d"), "case_file": "evaluation/purpose_boundary_cases.json",
        "model": model.name, "thinking": model.thinking, "agentic_tutor_prompt": AGENTIC_TUTOR_PROMPT_VERSION,
        "repetitions": repetitions, "passed": passed, "total": len(records), "records": records,
    }
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "purpose_boundary_probe.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{passed}/{len(records)} passed; written to {path}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
