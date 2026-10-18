"""Judge calibration (#8): how far the LLM judge agrees with the group's own labels.

    python src/calibration.py export <run folder> [<run folder> ...]   # writes evaluation/calibration/
    python src/calibration.py report                                   # writes evaluation/calibration/report.md

`export` draws a fixed sample of judged answers from stored Runs, splits it into a tuning set and a held-out set
before anyone labels, and writes a labelling sheet that hides the judge's verdicts, with one blank label file per
labeller. `report` reads the label files, lists where the labellers disagree, and compares the agreed labels with the
judge's stored verdicts, per criterion, on each set. The agreement metrics are pure functions (Seam B). PASS is the
positive class: TPR is the share of human PASSes the judge also passed, TNR the share of human FAILs it caught.
"""
import argparse
import csv
import json
import random
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

from cases import load_cases
from course_material import default_course_materials
from html_report import page
from judge import PASS, cited_sections_text

REPO = Path(__file__).resolve().parent.parent
CALIBRATION_DIR = REPO / "evaluation" / "calibration"
CRITERIA = ("supported", "responsive")
LABELS = ("PASS", "FAIL")
LABELLERS = ("goncalo", "rodrigo")  # one label file each; `agreed` holds the labels after disagreements are resolved
AGREED = "agreed"
FIELDS = ("item", "supported", "supported_reason", "responsive", "responsive_reason")
SEED = 8  # ticket #8; fixed so the sample and the split can be drawn again
FLAGGED, PASSED = 15, 15  # answers the judge failed on a criterion, answers it passed on both
HELD_OUT_SHARE = 2 / 3
ENOUGH_AGREEMENT = 0.8


# --- Seam B: agreement metrics -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Agreement:
    n: int
    accuracy: float | None
    kappa: float | None  # Cohen's kappa; None when chance agreement is 1 (both raters gave one label only)
    tpr: float | None  # of the human PASSes, the share the other rater also passed
    tnr: float | None  # of the human FAILs, the share the other rater also failed ("human FAILs caught")
    human_fails: int


def agreement(human: list[str], other: list[str]) -> Agreement:
    """Agreement of `other` (the judge, or a second labeller) with `human`, label by label. Labels are PASS or FAIL;
    anything that is not PASS (UNKNOWN, ERROR) counts as FAIL, as in the Answer Step."""
    if len(human) != len(other):
        raise ValueError("both raters must label the same items")
    h = [label == PASS for label in human]
    o = [label == PASS for label in other]
    n = len(h)
    if n == 0:
        return Agreement(0, None, None, None, None, 0)
    agree = sum(a == b for a, b in zip(h, o))
    p_observed = agree / n
    p_chance = (sum(h) / n) * (sum(o) / n) + (1 - sum(h) / n) * (1 - sum(o) / n)
    kappa = None if p_chance == 1 else (p_observed - p_chance) / (1 - p_chance)
    passes = [b for a, b in zip(h, o) if a]
    fails = [not b for a, b in zip(h, o) if not a]
    return Agreement(
        n,
        p_observed,
        kappa,
        sum(passes) / len(passes) if passes else None,
        sum(fails) / len(fails) if fails else None,
        len(fails),
    )


# --- Sample and labelling sheet --------------------------------------------------------------------------------------


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
                        "case_file": run["case_file"],
                        "answer": o["answer"],
                        "citations": o["citations"],
                        "judge": {c: o["judge"][c]["verdict"] for c in CRITERIA},
                    }
    return list(seen.values())


def draw_sample(answers: list[dict], seed: int = SEED, flagged: int = FLAGGED, passed: int = PASSED) -> list[dict]:
    """A fixed sample: answers the judge failed on any criterion, then answers it passed on both, each split into
    held-out and tuning in the same proportion. Item ids are assigned in a shuffled order, so the sheet does not
    group the judge's FAILs together."""
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


def render_sheet(items: list[dict], cases: dict, materials) -> str:
    """The labelling sheet: question, key facts, answer and the text of the cited Sections. No judge verdicts and no
    tutor or run, so the labeller sees only what the judge saw."""
    rows = []
    for item in items:
        case = cases[item["case_id"]]
        facts = "".join(f"<li>{escape(f)}</li>" for f in case.key_facts)
        sections = cited_sections_text(item["citations"], materials)
        rows.append(
            f'<section class="panel" id="{item["item"]}" style="margin:16px 0"><h2>{item["item"]}</h2>'
            f"<p><b>Question:</b> {escape(case.question)}</p>"
            f"<details><summary>Key facts (what the question is about)</summary><ul>{facts}</ul></details>"
            f'<h3>Answer</h3><div style="white-space:pre-wrap">{escape(item["answer"])}</div>'
            f'<details open><summary>Cited Sections</summary><div style="white-space:pre-wrap"><small>'
            f"{escape(sections)}</small></div></details></section>"
        )
    intro = f"""
<h1>Judge calibration: labelling sheet</h1>
<p class="meta">{len(items)} answers given by the Course Tutor on the Golden Set. Label each one on your own, without
looking at the other labeller's file, in <code>labels_&lt;your name&gt;.csv</code>.</p>
<div class="panel">
<p><b>Supported</b>: every claim in the answer is found in the Section it cites. PASS when every claim is stated
(paraphrase is fine) in a Section cited in the same sentence or bullet; FAIL when at least one claim is not, goes
beyond it (a number, name, cause or condition that is not there) or contradicts it. Use only the Section text below,
not your own knowledge.</p>
<p><b>Responsive</b>: the answer addresses what the question actually asked. It need not be complete or mention every
key fact; FAIL when it answers another question, gives only background, or ignores one part of a two-part
question.</p>
<p>Write PASS or FAIL in each column, and one sentence in the reason column for every FAIL.</p>
</div>
"""
    return page("Judge calibration: labelling sheet", intro + "".join(rows))


def export(run_dirs: list[Path], out_dir: Path = CALIBRATION_DIR) -> list[dict]:
    """Write items.json (sample, split and Trace keys; the judge's verdicts are read again only by `report`),
    sheet.html, one blank label file per labeller and a blank `labels_agreed.csv` to fill once the two are compared.
    Refuses to overwrite an existing sample."""
    out_dir = Path(out_dir)
    if (out_dir / "items.json").exists():
        raise FileExistsError(f"{out_dir / 'items.json'} exists: the sample and split are fixed once drawn")
    answers = judged_answers(run_dirs)
    items = draw_sample(answers)
    cases = {c.id: c for c in load_cases(REPO / items[0]["case_file"])} if items else {}
    out_dir.mkdir(parents=True, exist_ok=True)
    keys = [{k: item[k] for k in ("item", "split", "run_folder", "run", "tutor", "case_id")} for item in items]
    record = {"seed": SEED, "run_folders": [Path(d).name for d in run_dirs], "items": keys}
    (out_dir / "items.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (out_dir / "sheet.html").write_text(render_sheet(items, cases, default_course_materials()), encoding="utf-8")
    for name in (*LABELLERS, AGREED):
        with open(out_dir / f"labels_{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)
            writer.writerows([[item["item"], "", "", "", ""] for item in items])
    return items


# --- Labels and report ---------------------------------------------------------------------------------------------


class LabelFileError(ValueError):
    pass


def load_labels(path: Path, item_ids: list[str]) -> dict[str, dict]:
    """One complete label file: every item once, PASS or FAIL on both criteria, a reason for every FAIL."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    labels = {}
    for row in rows:
        item = (row.get("item") or "").strip()
        values = {c: (row.get(c) or "").strip().upper() for c in CRITERIA}
        for criterion, value in values.items():
            if value not in LABELS:
                raise LabelFileError(f"{Path(path).name} {item}: {criterion} must be PASS or FAIL, not {value!r}")
            if value == "FAIL" and not (row.get(f"{criterion}_reason") or "").strip():
                raise LabelFileError(f"{Path(path).name} {item}: a FAIL on {criterion} needs a reason")
        labels[item] = {**values, **{f"{c}_reason": (row.get(f"{c}_reason") or "").strip() for c in CRITERIA}}
    missing = [i for i in item_ids if i not in labels]
    unknown = [i for i in labels if i not in item_ids]
    if missing or unknown:
        raise LabelFileError(f"{Path(path).name}: missing items {missing}, unknown items {unknown}")
    return labels


def disagreements(first: dict[str, dict], second: dict[str, dict]) -> list[tuple[str, str]]:
    """(item, criterion) where the two labellers gave different labels."""
    return [(i, c) for i in first for c in CRITERIA if first[i][c] != second[i][c]]


def judge_verdicts(record: dict, runs_dir: Path) -> dict[str, dict[str, str]]:
    """The judge's stored verdicts for each sampled item, read from its run file."""
    verdicts = {}
    for key in record["items"]:
        run = json.loads((runs_dir / key["run_folder"] / f"run_{key['run']}.json").read_text(encoding="utf-8"))
        output = next(o for o in run["outputs"] if o["case_id"] == key["case_id"])
        verdicts[key["item"]] = {c: output["judge"][c]["verdict"] for c in CRITERIA}
    return verdicts


def render_report(record: dict, labels: dict[str, dict[str, dict]], verdicts: dict[str, dict[str, str]]) -> str:
    items = [k["item"] for k in record["items"]]
    split = {k["item"]: k["split"] for k in record["items"]}
    first, second = (labels[name] for name in LABELLERS)
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
        f"- Labellers: {', '.join(LABELLERS)}; agreed labels in `labels_{AGREED}.csv`.",
        "- PASS is the positive class. TPR: human PASSes the judge passed. TNR: human FAILs the judge caught.",
        "",
        "## Labellers against each other (all items)",
        "",
        "| Criterion | n | Accuracy | Cohen's kappa |",
        "|---|---|---|---|",
    ]
    for c in CRITERIA:
        a = agreement([first[i][c] for i in items], [second[i][c] for i in items])
        lines.append(f"| {c.capitalize()} | {a.n} | {_pct(a.accuracy)} | {_num(a.kappa)} |")
    split_disagreements = disagreements(first, second)
    lines += ["", f"Disagreements: {len(split_disagreements)}."]
    if split_disagreements:
        agreed = labels[AGREED]
        header = f"| Item | Criterion | {' | '.join(LABELLERS)} | Agreed | Resolution |"
        lines += ["", header, "|---|---|---|---|---|---|"]
        for item, c in split_disagreements:
            reason = agreed[item][f"{c}_reason"] or "-"
            lines.append(f"| {item} | {c} | {first[item][c]} | {second[item][c]} | {agreed[item][c]} | {reason} |")
    for set_name in ("held-out", "tuning"):
        ids = [i for i in items if split[i] == set_name]
        lines += [
            "",
            f"## Judge against the agreed labels: {set_name} ({len(ids)} items)",
            "",
            "| Criterion | Accuracy | Cohen's kappa | TPR | TNR (human FAILs caught) | Human FAILs | Accuracy >= 80% |",
            "|---|---|---|---|---|---|---|",
        ]
        for c in CRITERIA:
            a = agreement([labels[AGREED][i][c] for i in ids], [verdicts[i][c] for i in ids])
            enough = "n/a" if a.accuracy is None else ("yes" if a.accuracy >= ENOUGH_AGREEMENT else "no")
            lines.append(
                f"| {c.capitalize()} | {_pct(a.accuracy)} | {_num(a.kappa)} | {_pct(a.tpr)} | {_pct(a.tnr)} | "
                f"{a.human_fails} | {enough} |"
            )
    lines += [
        "",
        "## Items where the judge and the agreed labels differ",
        "",
        "| Item | Set | Case | Criterion | Agreed | Judge | Agreed reason |",
        "|---|---|---|---|---|---|---|",
    ]
    case_of = {k["item"]: k["case_id"] for k in record["items"]}
    for i in items:
        for c in CRITERIA:
            if (labels[AGREED][i][c] == PASS) != (verdicts[i][c] == PASS):
                reason = labels[AGREED][i][f"{c}_reason"] or "-"
                lines.append(
                    f"| {i} | {split[i]} | {case_of[i]} | {c} | {labels[AGREED][i][c]} | {verdicts[i][c]} | {reason} |"
                )
    return "\n".join(lines) + "\n"


def report(out_dir: Path = CALIBRATION_DIR, runs_dir: Path | None = None) -> str:
    out_dir = Path(out_dir)
    record = json.loads((out_dir / "items.json").read_text(encoding="utf-8"))
    items = [k["item"] for k in record["items"]]
    labels = {name: load_labels(out_dir / f"labels_{name}.csv", items) for name in (*LABELLERS, AGREED)}
    for item, c in disagreements(labels[LABELLERS[0]], labels[LABELLERS[1]]):
        if not labels[AGREED][item][f"{c}_reason"]:
            raise LabelFileError(f"labels_{AGREED}.csv {item}: write how the disagreement on {c} was resolved")
    runs_dir = runs_dir or out_dir.parent / "runs"
    text = render_report(record, labels, judge_verdicts(record, runs_dir))
    (out_dir / "report.md").write_text(text, encoding="utf-8")
    return text


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _num(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Judge calibration: export a labelling sheet, or report agreement.")
    sub = parser.add_subparsers(dest="command", required=True)
    export_parser = sub.add_parser("export", help="draw the sample and write the labelling sheet")
    export_parser.add_argument("run_folders", nargs="+", type=Path)
    export_parser.add_argument("--out", type=Path, default=CALIBRATION_DIR)
    report_parser = sub.add_parser("report", help="compare the labels with the judge")
    report_parser.add_argument("--out", type=Path, default=CALIBRATION_DIR)
    args = parser.parse_args(argv)
    if args.command == "export":
        items = export(args.run_folders, args.out)
        print(f"{len(items)} items. Sheet: {args.out / 'sheet.html'}; label files: labels_<name>.csv in {args.out}")
    else:
        report(args.out)
        print(f"Report: {args.out / 'report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
