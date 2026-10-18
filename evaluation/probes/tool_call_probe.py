"""Probe whether the endpoint returns real tool calls for the `read_file(course)` tool of the Agentic Tutor (ADR 0001).

    .venv/bin/python evaluation/probes/tool_call_probe.py

Sends one throwaway question (not a Golden Set case; never reuse it there) to each model below, thinking off, and
writes tool_call_probe.json next to this file. Needs the API key in .env.
"""
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src"))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(REPO, ".env"))
from openai import OpenAI  # noqa: E402

from llm import load_settings  # noqa: E402

settings = load_settings()
client = OpenAI(base_url=settings.base_url, api_key=settings.api_key, timeout=150, max_retries=0)

# gpt-oss has no "thinking off" switch; low reasoning effort is the closest setting.
MODELS = {
    "nvidia/nemotron-3-super-120b-a12b": {"chat_template_kwargs": {"enable_thinking": False, "thinking": False}},
    "openai/gpt-oss-120b": {"reasoning_effort": "low"},
}
SYSTEM = ("You are a tutor for four Courses: GAIF (Generative AI Foundations), PEID (Prompt Engineering and "
          "Interaction Design), AITB (AI Tools for Business Professionals) and DTGS (Digital Transformation and "
          "Generative AI Strategy). Read the Course Material you need with the read_file tool before answering.")
QUESTION = "What does few-shot prompting mean, and when is it worth adding examples to a prompt?"
TOOLS = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Return the whole Course Material of one Course.",
        "parameters": {
            "type": "object",
            "properties": {"course": {"type": "string", "enum": ["GAIF", "PEID", "AITB", "DTGS"]}},
            "required": ["course"],
        },
    },
}]


def probe(model, extra):
    t = time.time()
    try:
        r = client.chat.completions.create(
            model=model, temperature=0, extra_body=extra, tools=TOOLS,
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": QUESTION}],
        )
    except Exception as e:  # noqa: BLE001
        return {"model": model, "outcome": "error", "arguments": [], "secs": round(time.time() - t, 1),
                "error": f"{type(e).__name__}: {str(e)[:300]}", "content": ""}
    msg = r.choices[0].message
    content = msg.content or ""
    calls = msg.tool_calls or []
    if calls:
        outcome = "tool_calls"
    elif "read_file" in content or '"course"' in content:
        outcome = "tool_call_as_text"
    else:
        outcome = "no_tool_call"
    return {"model": model, "outcome": outcome, "secs": round(time.time() - t, 1), "error": None,
            "arguments": [{"name": c.function.name, "arguments": c.function.arguments} for c in calls],
            "finish_reason": r.choices[0].finish_reason, "content": content[:600]}


if __name__ == "__main__":
    results = [probe(m, extra) for m, extra in MODELS.items()]
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tool_call_probe.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=False)
    for r in results:
        print(f"{r['model']:40} {r['outcome']:18} {r['secs']:6.1f}s {r['arguments'] or r['error'] or ''}")
