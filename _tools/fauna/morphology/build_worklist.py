"""Build the genus-level morphology worklist for the site maintainer.

Inputs (all generated/curated in-repo):
  _data/taxonomy.json       — 326 genera, family/subfamily names
  _data/fauna_genera.json   — 35 genera already described from Fauna Sinica (2000)
  _data/genus_sources.json  — Treatise (2013) source pointers, not descriptions

Outputs:
  _reports/genus-morphology-worklist.md
  _reports/genus-morphology-worklist.csv

The report is a worklist, not prose: it says which genera still need a description,
where the original description is, and which references Treatise flags as containing
characters/keys. Treatise itself contains no morphological descriptions.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "_reports"
OUT_MD = OUT_DIR / "genus-morphology-worklist.md"
OUT_CSV = OUT_DIR / "genus-morphology-worklist.csv"

tax = json.load(open(ROOT / "_data/taxonomy.json", encoding="utf-8"))
sources = json.load(open(ROOT / "_data/genus_sources.json", encoding="utf-8"))
fauna = json.load(open(ROOT / "_data/fauna_genera.json", encoding="utf-8"))

families = {f["id"]: f for f in tax["families"]}
genera = sorted(tax["genera"], key=lambda g: (g["family"], g.get("subfamily") or "", g["latin"]))


def one_line(text, limit=220):
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def status_of(url):
    if url in fauna:
        return "已有动物志描述"
    if sources.get(url, {}).get("treatise"):
        return "待补（有 Treatise 线索）"
    return "待补（Treatise 无独立条目）"


def refs_cell(entry, limit=4):
    refs = entry.get("references") or []
    if not refs:
        return "—"
    parts = []
    for r in refs[:limit]:
        parts.append("%s — %s" % (r["ref"], one_line(r["note"], 90)))
    return "；".join(parts)


total = len(genera)
documented = [g for g in genera if "/genus/%s/" % g["id"] in fauna]
missing = [g for g in genera if "/genus/%s/" % g["id"] not in fauna]
no_entry = [g for g in missing if not sources.get("/genus/%s/" % g["id"], {}).get("treatise")]
no_ts = [g for g in missing if sources.get("/genus/%s/" % g["id"], {}).get("treatise")
         and not sources.get("/genus/%s/" % g["id"], {}).get("type_species")]

OUT_DIR.mkdir(exist_ok=True)

rows = []
for g in genera:
    url = "/genus/%s/" % g["id"]
    s = sources.get(url, {})
    fam = families.get(g["family"], {})
    rows.append({
        "科": fam.get("zh", g["family"]),
        "科（拉丁）": fam.get("latin", g["family"]).title(),
        "亚科": g.get("subfamily") or "",
        "属": g["zh"],
        "属（拉丁）": g["latin"],
        "属 ID": g["id"],
        "状态": status_of(url),
        "Treatise 条目": "有" if s.get("treatise") else "无",
        "原始描述（Treatise 记录）": one_line(s.get("citation"), 260),
        "模式种": one_line(s.get("type_species"), 200),
        "Treatise 标注的形态/检索文献": refs_cell(s),
        "Treatise 参考条数": s.get("nrefs", 0),
        "页面": "https://isoptera.lifemosaic.net/genus/%s/" % g["id"],
    })

with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

lines = []
lines.append("# 属级形态描述补写清单")
lines.append("")
lines.append("生成日期：2026-11-07。数据源：_data/taxonomy.json、_data/fauna_genera.json、_data/genus_sources.json。")
lines.append("")
lines.append("## 总览")
lines.append("")
lines.append("- 属页总数：**%d**。" % total)
lines.append("- 已有《中国动物志》属级描述（本次不动）：**%d**。" % len(documented))
lines.append("- 待补文献描述：**%d**。其中 %d 个在 Treatise 中有独立条目（可查到原始描述出处与模式种），%d 个没有独立条目（需另找发表文献）。"
             % (len(missing), len(missing) - len(no_entry), len(no_entry)))
lines.append("- 有 Treatise 条目但未提取到模式种的属：%d（不影响找原始文献，但补写时要先确认模式种）。" % len(no_ts))
lines.append("")
lines.append("> **Treatise 只是线索索引，不是形态描述。** 表中「原始描述」与「Treatise 标注的形态/检索文献」")
lines.append("> 均摘自 Krishna et al. (2013) 的属级条目；该书只登记原始发表信息、模式种和")
lines.append("> 「含 characters / key / diagnosis」的参考文献，本身没有描述正文。补写时必须取得并核对")
lines.append("> 原始文献，不得把 Treatise 的文献注记当作描述转述。")
lines.append("")
lines.append("## 优先补找：Treatise 无独立条目的 %d 属" % len(no_entry))
lines.append("")
lines.append("这些属在 Krishna et al. (2013) 中没有独立属级条目，连原始描述出处和模式种都要另查；")
lines.append("建议优先找原始发表（或最近的属级修订、地区名录）。")
lines.append("")
lines.append("| 科 | 属 | 页面 |")
lines.append("| --- | --- | --- |")
for g in no_entry:
    fam = families.get(g["family"], {})
    lines.append("| %s | %s *%s* | /genus/%s/ |" % (fam.get("zh", g["family"]), g["zh"], g["latin"], g["id"]))
lines.append("")
lines.append("## 各科进度")
lines.append("")
lines.append("| 科 | 属数 | 已有动物志描述 | 待补 | 其中 Treatise 无条目 |")
lines.append("| --- | ---: | ---: | ---: | ---: |")
for fid, fam in families.items():
    gs = [g for g in genera if g["family"] == fid]
    if not gs:
        continue
    doc = sum(1 for g in gs if "/genus/%s/" % g["id"] in fauna)
    miss = len(gs) - doc
    ne = sum(1 for g in gs if "/genus/%s/" % g["id"] not in fauna
             and not sources.get("/genus/%s/" % g["id"], {}).get("treatise"))
    lines.append("| %s %s | %d | %d | %d | %d |" % (fam["zh"], fam["latin"].title(), len(gs), doc, miss, ne))
lines.append("")

for fid, fam in families.items():
    gs = [g for g in genera if g["family"] == fid]
    if not gs:
        continue
    lines.append("## %s %s（%d 属）" % (fam["zh"], fam["latin"].title(), len(gs)))
    lines.append("")
    for g in gs:
        url = "/genus/%s/" % g["id"]
        s = sources.get(url, {})
        st = status_of(url)
        lines.append("### %s *%s* — %s" % (g["zh"], g["latin"], st))
        lines.append("")
        if st == "已有动物志描述":
            lines.append("已有《中国动物志》属级描述，页面不需要占位；如以后补写新描述，另起来源。")
        else:
            if s.get("treatise"):
                lines.append("- 原始描述：%s" % (s.get("citation") or "（未提取到）"))
                lines.append("- 模式种：%s" % (s.get("type_species") or "（未提取到，需查原始文献）"))
            else:
                lines.append("- Treatise 无独立属级条目；原始描述出处待查（可试原始发表、属级修订或地区名录）。")
            refs = s.get("references") or []
            if refs:
                lines.append("- 可先查的文献（Treatise 标注含形态/检索，非描述正文）：")
                for r in refs[:5]:
                    lines.append("  - %s — %s" % (r["ref"], r["note"]))
            else:
                lines.append("- Treatise 未标注可用的形态/检索文献。")
            lines.append("- 页面：https://isoptera.lifemosaic.net/genus/%s/" % g["id"])
        lines.append("")

OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT_MD.relative_to(ROOT), "and", OUT_CSV.relative_to(ROOT))
print("total", total, "documented", len(documented), "missing", len(missing), "no_entry", len(no_entry), "no_ts", len(no_ts))
