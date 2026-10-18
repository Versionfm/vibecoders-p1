"""Probe candidate app models on the NVIDIA endpoint: Router and Course Tutor tasks, latency and compliance.

    .venv/Scripts/python evaluation/probes/app_model_probe.py . [model ...]

Uses router_v1 and tutor_v2. The probe questions below are throwaway checks, not Golden Set cases; never reuse them
in the Golden Set. Writes probe_results_seq.json next to this file. Needs the API key in .env.
"""
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REPO = sys.argv[1]
sys.path.insert(0, os.path.join(REPO, "src"))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(REPO, ".env"))
from openai import OpenAI  # noqa: E402

from course_material import load_all_course_materials  # noqa: E402
from prompts import fill, load_prompt  # noqa: E402

client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"], timeout=150, max_retries=0)
materials = load_all_course_materials()
ROUTER = load_prompt("router_v1")
TUTOR = load_prompt("tutor_v2")
NO_THINK = {"chat_template_kwargs": {"enable_thinking": False, "thinking": False}}

CANDIDATES = {
    "nvidia/nemotron-3.5-lightning-30b-a3b": NO_THINK,
    "nvidia/nemotron-3-super-120b-a12b": NO_THINK,
    "openai/gpt-oss-20b": {"reasoning_effort": "low"},
    "google/gemma-4-31b-it": None,
    "z-ai/glm-5.3-flash": NO_THINK,
    "z-ai/glm-5.3": NO_THINK,
    "deepseek-ai/deepseek-v4.1-flash": NO_THINK,
    "mistralai/mistral-large-2-instruct": None,
    "moonshotai/kimi-k2.6": NO_THINK,
    "nvidia/nemotron-3-ultra-550b-a55b": NO_THINK,
}

ROUTER_QS = [
    ("How does a perceptron update its weights after a wrong output?", "GAIF"),
    ("Why does putting key instructions in the middle of a long prompt hurt accuracy?", "PEID"),
    ("How should I check the sources an AI research assistant gives me before using them in a client report?", "AITB"),
    ("What is the difference between pricing an AI product per seat and per outcome?", "DTGS"),
    ("Is gradient descent with backpropagation how ChatGPT is trained?", "PEID"),
    ("What is a good recipe for a vegetarian lasagne?", "OUT_OF_SCOPE"),
]
TUTOR_QS = [
    ("PEID", "What is context engineering and who popularised the term?", "answer"),
    ("DTGS", "How do per-resolution prices for AI customer service differ between vendors?", "answer"),
    ("GAIF", "Calculate the output of a perceptron with weights 0.5 and -0.3, inputs 1 and 1, and threshold 0.", "refusal"),
    ("AITB", "What is the capital of Australia?", "refusal"),
]
BRACKET = re.compile(r"\[([^\[\]]{3,60})\]")
ID = re.compile(r"[A-Z]{2,6}-[\d.]+")


def call(model, extra, system, user):
    t = time.time()
    try:
        r = client.chat.completions.create(
            model=model, temperature=0, extra_body=extra,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return time.time() - t, (r.choices[0].message.content or ""), r.usage.completion_tokens, None
    except Exception as e:  # noqa: BLE001
        return time.time() - t, "", 0, f"{type(e).__name__}: {str(e)[:120]}"


def probe(model):
    extra = CANDIDATES[model]
    out = {"model": model, "router": [], "tutor": []}
    for q, expected in ROUTER_QS:
        secs, text, toks, err = call(model, extra, ROUTER, q)
        strict = lenient = None
        try:
            strict = json.loads(text)["course"]
        except Exception:  # noqa: BLE001
            m = re.search(r"\{.*\}", text, re.S)
            try:
                lenient = json.loads(m.group(0))["course"] if m else None
            except Exception:  # noqa: BLE001
                pass
        got = strict or lenient
        out["router"].append({"q": q[:40], "expected": expected, "got": got, "strict_json": strict is not None,
                              "secs": round(secs, 1), "toks": toks, "err": err})
    for code, q, kind in TUTOR_QS:
        m = materials[code]
        system = fill(TUTOR, COURSE_CODE=m.code, COURSE_NAME=m.name, COURSE_MATERIAL=m.text.strip())
        secs, text, toks, err = call(model, extra, system, q)
        ids = [i for b in BRACKET.findall(text) for i in ID.findall(b)]
        refusal = text.strip() == f"This is not covered in the {code} material."
        out["tutor"].append({"course": code, "kind": kind, "secs": round(secs, 1), "toks": toks, "err": err,
                             "refusal": refusal, "cites": sorted(set(ids)),
                             "invalid": sorted({i for i in ids if i not in m.sections}),
                             "answer": text.strip()[:600]})
    return out


if __name__ == "__main__":
    chosen = sys.argv[2:] or list(CANDIDATES)
    results = [probe(m) for m in chosen]
    path = os.path.join(os.path.dirname(__file__), "probe_results_seq.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=False)
    for r in results:
        rt = r["router"]
        tt = r["tutor"]
        ok = sum(x["got"] == x["expected"] for x in rt)
        strict = sum(x["strict_json"] for x in rt)
        rsecs = sorted(x["secs"] for x in rt)
        tsecs = sorted(x["secs"] for x in tt)
        errs = sum(bool(x["err"]) for x in rt + tt)
        tut = "; ".join(
            f"{x['course']}:{'REF' if x['refusal'] else (str(len(x['cites'])) + 'c/' + str(len(x['invalid'])) + 'inv')}"
            for x in tt)
        print(f"{r['model']:42} route {ok}/6 json {strict}/6 | router s med {rsecs[3]:.1f} max {rsecs[-1]:.1f} "
              f"| tutor s med {tsecs[2]:.1f} max {tsecs[-1]:.1f} | errs {errs} | {tut}")
