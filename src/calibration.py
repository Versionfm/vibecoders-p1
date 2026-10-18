"""Judge calibration (#8): how far the LLM judge agrees with our own labels.

    python src/calibration.py export <run folder> [<run folder> ...]   # once: sample, split and labels.md
    python src/calibration.py report                                   # after labelling: report.md
    python src/calibration.py rejudge                                  # judge the sample again, current prompts
    python src/calibration.py report --labels labels_corrected.md --verdicts verdicts_<versions>.json --name v2

`export` draws a fixed sample of judged answers from stored Runs and splits it into a held-out set and a tuning set
before anyone labels (`items.json`). It writes `labels.md`: one file to read and fill in, with each answer's question,
key facts, answer text and cited Section text, and blank Supported and Responsive fields. The judge's verdicts are not
in it. One labeller (Gonçalo) labels. `report` compares those labels with the judge's stored verdicts, per criterion,
on each set: by default against the verdicts stored in the runs, or against a `rejudge` of the same answers with the
current judge prompts (a new prompt version is measured this way before it is used in an evaluation). The agreement
metrics are pure functions (Seam B). PASS is the positive class: TPR is the share of human PASSes the judge also
passed, TNR the share of human FAILs it caught.
"""
import argparse
import json
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from cases import load_cases
from course_material import default_course_materials
from judge import JUDGE_PROMPT_VERSIONS, PASS, cited_sections_text, judge_answer
from tutor import ChatModel, TutorResult

REPO = Path(__file__).resolve().parent.parent
CALIBRATION_DIR = REPO / "evaluation" / "calibration"
LABEL_FILE = "labels.md"
CRITERIA = ("supported", "responsive")
LABELLER = "Gonçalo Augusto"
SEED = 8  # ticket #8; fixed so the sample and the split can be drawn again
FLAGGED, PASSED = 15, 15  # answers the judge failed on a criterion, answers it passed on both
HELD_OUT_SHARE = 2 / 3
ENOUGH_AGREEMENT = 0.8
ACCEPTED = {"PASS": "PASS", "P": "PASS", "FAIL": "FAIL", "F": "FAIL"}


# --- Seam B: agreement metrics -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Agreement:
    n: int
    accuracy: float | None
    kappa: float | None  # Cohen's kappa; None when chance agreement is 1 (both raters gave one label only)
    tpr: float | None  # of the human PASSes, the share the judge also passed
    tnr: float | None  # of the human FAILs, the share the judge also failed ("human FAILs caught")
    human_fails: int


def agreement(human: list[str], judge: list[str]) -> Agreement:
    """Agreement of the judge with the human labels, item by item. Labels are PASS or FAIL; a judge verdict that is
    not PASS (UNKNOWN, ERROR) counts as FAIL, as in the Answer Step."""
    if len(human) != len(judge):
        raise ValueError("both raters must label the same items")
    h = [label == PASS for label in human]
    j = [label == PASS for label in judge]
    n = len(h)
    if n == 0:
        return Agreement(0, None, None, None, None, 0)
    p_observed = sum(a == b for a, b in zip(h, j)) / n
    p_chance = (sum(h) / n) * (sum(j) / n) + (1 - sum(h) / n) * (1 - sum(j) / n)
    kappa = None if p_chance == 1 else (p_observed - p_chance) / (1 - p_chance)
    passes = [b for a, b in zip(h, j) if a]
    fails = [not b for a, b in zip(h, j) if not a]
    return Agreement(
        n,
        p_observed,
        kappa,
        sum(passes) / len(passes) if passes else None,
        sum(fails) / len(fails) if fails else None,
        len(fails),
    )


# --- Sample and label file --------------------------------------------------------------------------------------------


def judged_answers(run_dirs: list[Path]) -> list[dict]:
    """Every judged Trace of the given run folders, one per distinct answer text (first occurrence kept)."""
    seen: dict[str, dict] = {}
    for run_dir in run_dirs:
        for path in sorted(Path(run_dir).glob("run_*.json")):
            run = json.loads(path.read_text(encoding="utf-8"))
            for o in run["outputs"]:
                if o.get("judge") and o["answer"] not in seen:
                    seen[o["answer"]] = {
                        "run_folder": Path(run_dir).name,
                        "run": run["run"],
                        "tutor": run["tutor"],
                        "case_id": o["case_id"],
                        "judge": {c: o["judge"][c]["verdict"] for c in CRITERIA},
                    }
    return list(seen.values())


def draw_sample(answers: list[dict], seed: int = SEED, flagged: int = FLAGGED, passed: int = PASSED) -> list[dict]:
    """A fixed sample: answers the judge failed on any criterion, then answers it passed on both, each split into
    held-out and tuning in the same proportion. Item ids are assigned in a shuffled order, so the judge's FAILs are
    not grouped together."""
    rng = random.Random(seed)
    groups = [
        [a for a in answers if any(v != PASS for v in a["judge"].values())],
        [a for a in answers if all(v == PASS for v in a["judge"].values())],
    ]
    sample = []
    for group, size in zip(groups, (flagged, passed)):
        chosen = rng.sample(group, min(size, len(group)))
        held_out = round(len(chosen) * HELD_OUT_SHARE)
        sample += [{**a, "split": "held-out" if i < held_out else "tuning"} for i, a in enumerate(chosen)]
    rng.shuffle(sample)
    return [{"item": f"L{i:02d}", **a} for i, a in enumerate(sample, 1)]


def stored_output(key: dict, runs_dir: Path) -> dict:
    run = json.loads((runs_dir / key["run_folder"] / f"run_{key['run']}.json").read_text(encoding="utf-8"))
    return next(o for o in run["outputs"] if o["case_id"] == key["case_id"])


def render_label_file(record: dict, runs_dir: Path) -> str:
    """labels.md: instructions, then per item the question, key facts, answer and cited Section text, and the four
    fields to fill in. No judge verdicts, tutor or run, so the labeller sees only what the judge saw."""
    cases = {c.id: c for c in load_cases(REPO / record["case_file"])}
    materials = default_course_materials()
    parts = [
        "# Judge calibration: labels",
        "",
        f"Labeller: {LABELLER}. {len(record['items'])} answers given by the Course Tutor on the Golden Set.",
        "",
        "For each item, read the answer and the cited Sections, then fill in the four lines at its end: write PASS",
        "or FAIL (or P or F) after `Supported:` and `Responsive:`, and for every FAIL one sentence after its",
        "`reason:` line. Leave a reason empty when the label is PASS. Do not change anything else in this file.",
        "",
        "- **Supported**: every claim in the answer is found in the Section it cites. PASS when every claim is",
        "  stated (paraphrase is fine) in a Section cited in the same sentence or bullet; FAIL when at least one claim",
        "  is not, goes beyond it (a number, name, cause or condition that is not there) or contradicts it. Use only",
        "  the Section text given, not your own knowledge.",
        "- **Responsive**: the answer addresses what the question actually asked. It need not be complete or mention",
        "  every key fact; FAIL when it answers another question, gives only background, or ignores one part of a",
        "  two-part question.",
    ]
    for key in record["items"]:
        case = cases[key["case_id"]]
        output = stored_output(key, runs_dir)
        parts += [
            "",
            "---",
            "",
            f"## {key['item']}",
            "",
            f"**Question:** {case.question}",
            "",
            "**Key facts** (what the question is about):",
            "",
            *(f"- {fact}" for fact in case.key_facts),
            "",
            "**Answer:**",
            "",
            *(f"> {line}" for line in output["answer"].strip().splitlines()),
            "",
            "**Cited Sections:**",
            "",
            *(f"> {line}" for line in cited_sections_text(output["citations"], materials).splitlines()),
            "",
            "Supported: ",
            "Supported reason: ",
            "Responsive: ",
            "Responsive reason: ",
        ]
    return "\n".join(parts) + "\n"


def export(run_dirs: list[Path], out_dir: Path = CALIBRATION_DIR, runs_dir: Path | None = None) -> list[dict]:
    """Write items.json (sample, split and Trace keys, without the judge's verdicts) and labels.md. Refuses to
    overwrite an existing sample: the split is fixed once drawn."""
    out_dir = Path(out_dir)
    if (out_dir / "items.json").exists():
        raise FileExistsError(f"{out_dir / 'items.json'} exists: the sample and split are fixed once drawn")
    items = draw_sample(judged_answers(run_dirs))
    first_run = json.loads(next(Path(run_dirs[0]).glob("run_*.json")).read_text(encoding="utf-8"))
    keys = [{k: item[k] for k in ("item", "split", "run_folder", "run", "tutor", "case_id")} for item in items]
    record = {
        "seed": SEED,
        "case_file": first_run["case_file"],
        "run_folders": [Path(d).name for d in run_dirs],
        "items": keys,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "items.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    runs_dir = runs_dir or Path(run_dirs[0]).parent
    (out_dir / LABEL_FILE).write_text(render_label_file(record, runs_dir), encoding="utf-8")
    return items


# --- Labels and report ------------------------------------------------------------------------------------------------


class LabelFileError(ValueError):
    pass


ITEM_HEADING = re.compile(r"^## (L\d{2})\s*$", re.MULTILINE)
FIELD = re.compile(r"^(Supported|Responsive)( reason)?:[ \t]*(.*)$", re.MULTILINE)


def parse_labels(text: str, item_ids: list[str]) -> dict[str, dict]:
    """The labels in labels.md: every item PASS or FAIL on both criteria, with a reason for every FAIL."""
    headings = list(ITEM_HEADING.finditer(text))
    labels = {}
    for heading, following in zip(headings, [*headings[1:], None]):
        item = heading.group(1)
        block = text[heading.end() : following.start() if following else len(text)]
        fields = {}
        for match in FIELD.finditer(block):  # the last occurrence wins: the fields close the item
            name = match.group(1).lower() + ("_reason" if match.group(2) else "")
            fields[name] = match.group(3).strip()
        entry = {}
        for criterion in CRITERIA:
            value = ACCEPTED.get(fields.get(criterion, "").upper())
            if value is None:
                raise LabelFileError(f"{item}: write PASS or FAIL after '{criterion.capitalize()}:'")
            reason = fields.get(f"{criterion}_reason", "")
            if value == "FAIL" and not reason:
                raise LabelFileError(f"{item}: a FAIL on {criterion.capitalize()} needs a reason")
            entry[criterion], entry[f"{criterion}_reason"] = value, reason
        labels[item] = entry
    missing = [i for i in item_ids if i not in labels]
    if missing:
        raise LabelFileError(f"items missing from {LABEL_FILE}: {missing}")
    return labels


def rejudge(judge: ChatModel, out_dir: Path = CALIBRATION_DIR, runs_dir: Path | None = None) -> Path:
    """Judge every sampled answer again with the current judge prompts; store the verdicts beside the sample."""
    out_dir = Path(out_dir)
    runs_dir = runs_dir or out_dir.parent / "runs"
    record = json.loads((out_dir / "items.json").read_text(encoding="utf-8"))
    cases = {c.id: c for c in load_cases(REPO / record["case_file"])}
    materials = default_course_materials()
    verdicts = {}
    for key in record["items"]:
        output, case = stored_output(key, runs_dir), cases[key["case_id"]]
        result = TutorResult(question=case.question, answer=output["answer"], citations=output["citations"])
        judgement = judge_answer(case, result, judge, materials)
        verdicts[key["item"]] = {
            c: {"verdict": getattr(judgement, c).verdict, "evidence": getattr(judgement, c).evidence} for c in CRITERIA
        }
    path = out_dir / f"verdicts_{'_'.join(JUDGE_PROMPT_VERSIONS.values())}.json"
    stored = {"judge_model": judge.name, "prompt_versions": JUDGE_PROMPT_VERSIONS, "items": verdicts}
    path.write_text(json.dumps(stored, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def judge_verdicts(record: dict, runs_dir: Path) -> dict[str, dict[str, str]]:
    """The judge's stored verdicts for each sampled item, read from its run file."""
    return {
        key["item"]: {c: stored_output(key, runs_dir)["judge"][c]["verdict"] for c in CRITERIA}
        for key in record["items"]
    }


def render_report(
    record: dict,
    labels: dict[str, dict],
    verdicts: dict[str, dict[str, str]],
    labels_file: str = LABEL_FILE,
    verdict_source: str = "the verdicts stored in the runs",
) -> str:
    items = [k["item"] for k in record["items"]]
    split = {k["item"]: k["split"] for k in record["items"]}
    case_of = {k["item"]: k["case_id"] for k in record["items"]}
    flagged = sum(any(v != PASS for v in verdicts[i].values()) for i in items)
    lines = [
        "# Judge calibration report",
        "",
        f"- Sample: {len(items)} judged answers from {', '.join(f'`{d}`' for d in record['run_folders'])} "
        f"(seed {record['seed']}): {flagged} the judge failed on at least one criterion and {len(items) - flagged} it "
        "passed on both, so both labels occur. The sample is enriched with the judge's FAILs: the numbers describe "
        "this sample, not every answer.",
        f"- Split, fixed before labelling: {sum(s == 'held-out' for s in split.values())} held-out, "
        f"{sum(s == 'tuning' for s in split.values())} tuning (used only to revise the judge prompt).",
        f"- Labeller: {LABELLER}, alone, without seeing the judge's verdicts. With one labeller there is no "
        "agreement between labellers to report.",
        f"- Labels: `{labels_file}`. Judge: {verdict_source}.",
        "- PASS is the positive class. TPR: human PASSes the judge passed. TNR: human FAILs the judge caught.",
    ]
    for set_name in ("held-out", "tuning"):
        ids = [i for i in items if split[i] == set_name]
        lines += [
            "",
            f"## Judge against the labels: {set_name} ({len(ids)} items)",
            "",
            "| Criterion | Accuracy | Cohen's kappa | TPR | TNR (human FAILs caught) | Human FAILs | Accuracy >= 80% |",
            "|---|---|---|---|---|---|---|",
        ]
        for c in CRITERIA:
            a = agreement([labels[i][c] for i in ids], [verdicts[i][c] for i in ids])
            enough = "n/a" if a.accuracy is None else ("yes" if a.accuracy >= ENOUGH_AGREEMENT else "no")
            lines.append(
                f"| {c.capitalize()} | {_pct(a.accuracy)} | {_num(a.kappa)} | {_pct(a.tpr)} | {_pct(a.tnr)} | "
                f"{a.human_fails} | {enough} |"
            )
    lines += [
        "",
        "## Items where the judge and the labels differ",
        "",
        "| Item | Set | Case | Criterion | Label | Judge | Label reason |",
        "|---|---|---|---|---|---|---|",
    ]
    for i in items:
        for c in CRITERIA:
            if (labels[i][c] == PASS) != (verdicts[i][c] == PASS):
                reason = labels[i][f"{c}_reason"] or "-"
                row = f"| {i} | {split[i]} | {case_of[i]} | {c} | {labels[i][c]} | {verdicts[i][c]} | {reason} |"
                lines.append(row)
    lines += ["", "## FAIL reasons (input for the failure taxonomy)", "", "| Item | Case | Criterion | Reason |"]
    lines.append("|---|---|---|---|")
    for i in items:
        for c in CRITERIA:
            if labels[i][c] == "FAIL":
                lines.append(f"| {i} | {case_of[i]} | {c} | {labels[i][f'{c}_reason']} |")
    return "\n".join(lines) + "\n"


def report(
    out_dir: Path = CALIBRATION_DIR,
    runs_dir: Path | None = None,
    labels_file: str = LABEL_FILE,
    verdicts_file: str | None = None,
    name: str = "report",
) -> str:
    """Write `<name>.md`: the labels in `labels_file` against the judge's stored verdicts, or against the verdicts
    of a `rejudge` when `verdicts_file` is given."""
    out_dir = Path(out_dir)
    record = json.loads((out_dir / "items.json").read_text(encoding="utf-8"))
    items = [k["item"] for k in record["items"]]
    labels = parse_labels((out_dir / labels_file).read_text(encoding="utf-8"), items)
    if verdicts_file:
        stored = json.loads((out_dir / verdicts_file).read_text(encoding="utf-8"))
        verdicts = {i: {c: v[c]["verdict"] for c in CRITERIA} for i, v in stored["items"].items()}
        versions = ", ".join(stored["prompt_versions"].values())
        source = f"`{stored['judge_model']}` with {versions}, judged again (`{verdicts_file}`)"
    else:
        verdicts = judge_verdicts(record, runs_dir or out_dir.parent / "runs")
        source = "the verdicts stored in the runs"
    text = render_report(record, labels, verdicts, labels_file, source)
    (out_dir / f"{name}.md").write_text(text, encoding="utf-8")
    return text


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _num(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Judge calibration: export a label file, or report agreement.")
    sub = parser.add_subparsers(dest="command", required=True)
    export_parser = sub.add_parser("export", help="draw the sample and split, and write labels.md")
    export_parser.add_argument("run_folders", nargs="+", type=Path)
    export_parser.add_argument("--out", type=Path, default=CALIBRATION_DIR)
    report_parser = sub.add_parser("report", help="compare the labels with the judge")
    report_parser.add_argument("--out", type=Path, default=CALIBRATION_DIR)
    report_parser.add_argument("--labels", default=LABEL_FILE, help=f"label file in --out (default {LABEL_FILE})")
    report_parser.add_argument("--verdicts", help="verdicts file from rejudge (default: the verdicts in the runs)")
    report_parser.add_argument("--name", default="report", help="report file name, without .md")
    rejudge_parser = sub.add_parser("rejudge", help="judge the sample again with the current judge prompts")
    rejudge_parser.add_argument("--out", type=Path, default=CALIBRATION_DIR)
    args = parser.parse_args(argv)
    if args.command == "export":
        items = export(args.run_folders, args.out)
        print(f"{len(items)} items. Fill in: {args.out / LABEL_FILE}")
    elif args.command == "rejudge":
        from llm import get_judge_model

        judge = get_judge_model()
        if judge is None:
            raise SystemExit("LLM_JUDGE_MODEL is not set. Check your .env file.")
        print(f"Verdicts: {rejudge(judge, args.out)}")
    else:
        report(args.out, labels_file=args.labels, verdicts_file=args.verdicts, name=args.name)
        print(f"Report: {args.out / (args.name + '.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
