"""Merge subagent literature-search results into review reports.

Inputs:
  _tmp/lit/manifest.json               — batch list (created by the Lead)
  _tmp/lit/batches/<batch>.json        — assigned genera
  _tmp/lit/results/<batch>.jsonl       — one JSON object per genus, written by subagents

Outputs:
  _reports/genus-literature-candidates.json
  _reports/genus-literature-candidates.csv
  _reports/genus-literature-candidates.md

This is a review aid, not a site data source. Nothing here is promoted to
_data/ until the citation and the quoted evidence have been checked by hand.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIT = ROOT / "_tmp" / "lit"
OUT = ROOT / "_reports"
OUT.mkdir(exist_ok=True)

manifest = json.load(open(LIT / "manifest.json", encoding="utf-8"))
batch_meta = {}
for item in manifest:
    data = json.load(open(LIT / "batches" / (item["batch"] + ".json"), encoding="utf-8"))
    for g in data["genera"]:
        batch_meta[g["id"]] = {**g, "batch": item["batch"]}

records = {}
missing_files = []
for item in manifest:
    name = item["batch"]
    path = LIT / "results" / (name + ".jsonl")
    if not path.exists():
        missing_files.append(name)
        continue
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print("skip bad jsonl", name, exc)
            continue
        gid = obj.get("id")
        if not gid:
            continue
        base = batch_meta.get(gid, {})
        obj["_batch"] = name
        obj["_family"] = base.get("family", "")
        obj["_family_zh"] = base.get("family_zh", "")
        obj["_subfamily"] = base.get("subfamily", "")
        obj["_zh"] = base.get("zh", "")
        obj["_status_expected"] = base.get("status", "")
        records[gid] = obj

for gid, base in batch_meta.items():
    if gid not in records:
        records[gid] = {
            "id": gid,
            "latin": base.get("latin", ""),
            "status": "missing_result",
            "best": None,
            "candidates": [],
            "queries": [],
            "notes": "subagent produced no row for this genus",
            "_batch": base.get("batch", ""),
            "_family": base.get("family", ""),
            "_family_zh": base.get("family_zh", ""),
            "_subfamily": base.get("subfamily", ""),
            "_zh": base.get("zh", ""),
            "_status_expected": base.get("status", ""),
        }

order = list(batch_meta.keys())
ordered = [records[gid] for gid in order if gid in records]
(OUT / "genus-literature-candidates.json").write_text(
    json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
)

STATUSES = ["found_fulltext", "found_metadata_only", "not_found", "uncertain", "missing_result"]


def best_citation(best):
    if not best:
        return ""
    parts = []
    if best.get("authors"):
        parts.append(best["authors"])
    if best.get("year"):
        parts.append(str(best["year"]))
    if best.get("title"):
        parts.append(best["title"])
    if best.get("journal"):
        parts.append(best["journal"])
    vol = best.get("volume") or ""
    pages = best.get("pages") or ""
    if vol or pages:
        parts.append((vol + (":" if pages else "") + pages).strip())
    return ". ".join(p for p in parts if p)


rows = []
for r in ordered:
    b = r.get("best") or {}
    rows.append({
        "科": r.get("_family_zh", ""),
        "亚科": r.get("_subfamily", ""),
        "属": r.get("_zh", ""),
        "属（拉丁）": r.get("latin", ""),
        "检索状态": r.get("status", ""),
        "最佳文献": best_citation(b),
        "DOI": b.get("doi") or "",
        "URL": b.get("url") or "",
        "PDF": b.get("pdf_url") or "",
        "获取": b.get("access") or "",
        "含形态": "" if b.get("has_morphology") is None else ("是" if b.get("has_morphology") else "否"),
        "类群": b.get("kind") or "",
        "置信度": b.get("confidence") or "",
        "证据": b.get("evidence") or "",
        "候选数": len(r.get("candidates") or []),
        "批次": r.get("_batch", ""),
        "备注": r.get("notes") or "",
    })

with open(OUT / "genus-literature-candidates.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

counts = {s: sum(1 for r in ordered if r.get("status") == s) for s in STATUSES}
by_family = {}
for r in ordered:
    fam = r.get("_family_zh") or r.get("_family") or "?"
    by_family.setdefault(fam, {s: 0 for s in STATUSES})
    by_family[fam][r.get("status", "missing_result")] += 1

lines = []
lines.append("# 属级形态描述文献候选汇总")
lines.append("")
lines.append("生成日期：2026-11-07。输入：_tmp/lit/results/*.jsonl（子智能体检索结果）。")
lines.append("")
lines.append("> 本表是**待核对的检索结果**，不是已存档来源。题录、DOI、全文链接在写入站点前必须逐条打开核对；")
lines.append("> evidence 只是子智能体看到的摘要/页面片段，不能当作描述正文。")
lines.append("")
lines.append("## 总览")
lines.append("")
lines.append("- 分配属数：**%d**。" % len(ordered))
for s in STATUSES:
    lines.append("- %s：**%d**。" % (s, counts[s]))
if missing_files:
    lines.append("- 尚未产出结果文件的批次：%s。" % "、".join("'%s'" % x for x in missing_files))
lines.append("")
lines.append("## 各科进度")
lines.append("")
lines.append("| 科 | 合计 | 全文可得 | 仅题录 | 未找到 | 不确定 / 缺结果 |")
lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
for fam, c in by_family.items():
    lines.append("| %s | %d | %d | %d | %d | %d |" % (
        fam, sum(c.values()), c["found_fulltext"], c["found_metadata_only"],
        c["not_found"], c["uncertain"] + c["missing_result"]))
lines.append("")
lines.append("## 可直接读全文的候选")
lines.append("")
any_full = False
for r in ordered:
    if r.get("status") != "found_fulltext":
        continue
    any_full = True
    b = r.get("best") or {}
    lines.append("- **%s** *%s* — %s；%s；%s" % (
        r.get("_zh", ""), r.get("latin", ""), best_citation(b) or "（题录不全）",
        ("DOI: %s" % b["doi"]) if b.get("doi") else "",
        ("PDF: %s" % b["pdf_url"]) if b.get("pdf_url") else (("URL: %s" % b["url"]) if b.get("url") else "")))
if not any_full:
    lines.append("（暂无）")
lines.append("")
lines.append("## 仍缺文献的属")
lines.append("")
for r in ordered:
    if r.get("status") in ("not_found", "uncertain", "missing_result"):
        lines.append("- %s *%s*（%s，%s）" % (
            r.get("_zh", ""), r.get("latin", ""), r.get("_family_zh", ""), r.get("status")))
lines.append("")
(OUT / "genus-literature-candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("records", len(ordered))
print("counts", counts)
print("missing_files", missing_files)
print("wrote", (OUT / "genus-literature-candidates.md").relative_to(ROOT))
