#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建分类树结构化数据（isoptera-data.json / data/）与三语统计页（stats.md）。

唯一数据源（只读，不改任何源文件）：
  _data/taxonomy.json     分类层级（支系→科→亚科→属）与文档顺序
  _species/*.md           front matter（中文名、模式种标记、分布、亚种、所属属与科）
  _config.yml             base_url、dataset.version
  dataset/metadata.json   发布日期（dates.created / dates.updated）
  data/references.json    参考文献条数

生成（确定性输出，换行统一 LF，可重复生成逐字节一致）：
  isoptera-data.json                        完整分类树（模式种、分布、亚种）
  data/index.json                           分类树 + 文件清单（含计数与字节数）
  data/mastotermitidae.json、data/kalotermitidae.json    单科文件
  data/teletisoptera.json                   远等翅类合辑（4 科）
  data/neoisoptera-excl-termitidae.json     新等翅类（除白蚁科）合辑（6 科）
  data/termitidae/<subfamily>.json          白蚁科 18 个亚科文件
  stats.md / en/stats.md / es/stats.md      三语统计页

用法：
  python _tools/build_taxonomy_data.py            # 只报告统计（不写文件）
  python _tools/build_taxonomy_data.py --write    # 写入全部产物
  python _tools/build_taxonomy_data.py --check    # 校验磁盘产物与生成结果一致
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_JSON = ROOT / "_data" / "taxonomy.json"
SPECIES_DIR = ROOT / "_species"
CONFIG = ROOT / "_config.yml"
METADATA = ROOT / "dataset" / "metadata.json"
REFERENCES = ROOT / "data" / "references.json"

FM_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$')

CLADE_PARENT = {
    "isoptera": None,
    "euisoptera": "isoptera",
    "teletisoptera": "euisoptera",
    "icoisoptera": "euisoptera",
    "neoisoptera": "icoisoptera",
    "geoisoptera": "neoisoptera",
}
TELETERM_AGG = {"id": "teletisoptera", "zh": "远等翅类", "latin": "Teletisoptera",
                "file": "data/teletisoptera.json"}
NEOTERM_AGG = {"id": "neoisoptera-excl-termitidae", "zh": "新等翅类（除白蚁科）",
               "latin": "Neoisoptera excl. Termitidae", "file": "data/neoisoptera-excl-termitidae.json"}
KEYWORDS = ["白蚁", "等翅目", "Isoptera", "学名", "中文名", "分类", "Termitidae", "名录"]
CREATOR = {"@type": "Person", "name": "班奈特格林"}
LICENSE = "https://creativecommons.org/licenses/by/4.0/"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def dump_json(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8")


class Site:
    def __init__(self) -> None:
        cfg = read_text(CONFIG)
        self.base_url = ""
        for line in cfg.splitlines():
            m = re.match(r"^base_url:\s*(\S.*)$", line)
            if m:
                self.base_url = m.group(1).strip().strip('"').strip("'").rstrip("/")
        m = re.search(r'^dataset:\s*$[\s\S]*?^\s{2}version:\s*"?([^"\n]+)"?', cfg, re.MULTILINE)
        self.version = m.group(1).strip() if m else ""
        meta = json.loads(read_text(METADATA))
        dates = meta.get("dates") or {}
        self.created = dates.get("created") or ""
        self.modified = dates.get("updated") or self.created
        refs = json.loads(read_text(REFERENCES))
        self.reference_count = int(((refs.get("meta") or {}).get("counts") or {}).get("total") or 0)
        self.index_name = "现存等翅下目（白蚁）拉丁学名—中文正名对照名录（%s）" % self.version
        self.index_url = self.base_url + "/data/index.json"


def parse_front_matter(path: Path) -> dict:
    text = read_text(path).lstrip("\ufeff")
    if not text.startswith("---"):
        sys.exit("error: %s 缺少 front matter" % path.name)
    end = text.find("\n---", 3)
    if end < 0:
        sys.exit("error: %s 的 front matter 未闭合" % path.name)
    fields = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m:
            continue
        value = m.group(2).strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fields[m.group(1)] = value
    return fields


def load_species() -> dict:
    out = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        latin = (fm.get("latin") or "").strip()
        if not latin:
            sys.exit("error: %s 缺 latin" % path.name)
        out[latin] = {
            "slug": path.stem,
            "zh": (fm.get("zh") or "").strip(),
            "type": (fm.get("type") or "").strip().lower() == "true",
            "rank": (fm.get("rank") or "species").strip(),
            "distribution_zh": (fm.get("distribution_zh") or "").strip(),
            "parent_latin": (fm.get("parent_latin") or "").strip(),
            "genus_id": (fm.get("genus_id") or "").strip(),
        }
    return out


def attach_subspecies(species: dict) -> dict:
    subs = {}
    for latin, fm in species.items():
        if fm["rank"] == "subspecies" and fm["parent_latin"]:
            subs.setdefault(fm["parent_latin"], []).append(
                {"etym": latin.split(" ")[-1], "zh": fm["zh"], "latin": latin})
    for key in subs:
        subs[key].sort(key=lambda x: x["latin"])
    return subs


def load_list(species: dict) -> dict:
    """按 _data/taxonomy.json 重建分类树，再把 _species 里的种挂到各自的属上。

    名录页（list.md）已改为索引页，不再逐条罗列物种，因此层级与顺序一律取
    taxonomy.json；种与亚种的归属取 _species front matter 的 genus_id / parent_latin。
    """
    taxonomy = json.loads(read_text(TAXONOMY_JSON))
    families = {family["id"]: family for family in taxonomy["families"]}
    genera = {genus["id"]: genus for genus in taxonomy["genera"]}
    subfamilies = {sub["id"]: sub for sub in taxonomy["subfamilies"]}

    species_by_genus: dict[str, list[str]] = {}
    for latin, fm in species.items():
        if fm["rank"] == "subspecies":
            continue
        genus_id = fm.get("genus_id") or ""
        if genus_id not in genera:
            sys.exit("error: %s 的 genus_id（%s）不在 taxonomy.json 的属表里" % (latin, genus_id))
        species_by_genus.setdefault(genus_id, []).append(latin)

    clades, events = [], []
    for clade in taxonomy["clades"]:
        clade_node = {"id": clade["id"], "zh": clade["zh"], "latin": clade["latin"], "families": []}
        clades.append(clade_node)
        events.append(("clade", clade_node))
        for family_id in clade["families"]:
            family = families[family_id]
            family_node = {"id": family_id, "zh": family["zh"], "latin": family["latin"],
                           "clade": clade["id"], "subfamilies": [], "genera": []}
            clade_node["families"].append(family_node)
            events.append(("family", family_node))
            sub_nodes = {}
            for sub_id in family["subfamilies"]:
                sub = subfamilies[sub_id]
                sub_node = {"id": sub_id, "zh": sub["zh"], "latin": sub["latin"],
                            "genera": [], "family": family_node}
                sub_nodes[sub_id] = sub_node
                family_node["subfamilies"].append(sub_node)
            family_genera = list(family["genera"])
            for sub_id in family["subfamilies"]:
                family_genera.extend(subfamilies[sub_id]["genera"])
            for genus_id in sorted(set(family_genera),
                                   key=lambda gid: genera[gid]["latin"].lower()):
                genus = genera[genus_id]
                sub_node = sub_nodes.get(genus.get("subfamily") or "")
                genus_node_ = {
                    "id": genus_id,
                    "zh": genus["zh"],
                    "latin": genus["latin"],
                    "species": [{"latin": latin, "fm": species[latin]}
                                for latin in sorted(species_by_genus.get(genus_id, []),
                                                    key=lambda name: name.lower())],
                    "family": family_node,
                    "subfamily": sub_node,
                }
                (sub_node["genera"] if sub_node else family_node["genera"]).append(genus_node_)
    if not clades:
        sys.exit("error: taxonomy.json 中没有任何支系")
    return {"clades": clades, "events": events}


def species_node(sp: dict, subs: dict) -> dict:
    fm = sp["fm"]
    children = subs.get(sp["latin"])
    return {
        "latin": sp["latin"],
        "zh": fm["zh"],
        "type": fm["type"],
        "distribution": fm["distribution_zh"],
        "subspecies": [{"epithet": c["etym"], "zh": c["zh"]} for c in children] if children else None,
    }


def genus_node(g: dict, subs: dict) -> dict:
    nodes = [species_node(sp, subs) for sp in g["species"]]
    types = [n["latin"] for n in nodes if n["type"]]
    return {"zh": g["zh"], "latin": g["latin"], "id": g["id"],
            "species_count": len(nodes), "type_species": types[0] if types else "",
            "species": nodes}


def genus_stats(g: dict, subs: dict) -> dict:
    return {"species": len(g["species"]),
            "subspecies": sum(len(subs.get(sp["latin"], [])) for sp in g["species"])}


def subfamily_stats(sub: dict, subs: dict) -> dict:
    gs = [genus_stats(g, subs) for g in sub["genera"]]
    return {"genera": len(sub["genera"]),
            "species": sum(x["species"] for x in gs),
            "subspecies": sum(x["subspecies"] for x in gs)}


def family_stats(fam: dict, subs: dict) -> dict:
    if fam["subfamilies"]:
        parts = [subfamily_stats(s, subs) for s in fam["subfamilies"]]
        return {"genera": sum(p["genera"] for p in parts),
                "species": sum(p["species"] for p in parts),
                "subspecies": sum(p["subspecies"] for p in parts),
                "subfamilies": len(fam["subfamilies"])}
    gs = [genus_stats(g, subs) for g in fam["genera"]]
    return {"genera": len(fam["genera"]),
            "species": sum(x["species"] for x in gs),
            "subspecies": sum(x["subspecies"] for x in gs),
            "subfamilies": 0}


def all_genera(fam: dict):
    if fam["subfamilies"]:
        return [(g, s) for s in fam["subfamilies"] for g in s["genera"]]
    return [(g, None) for g in fam["genera"]]


def summarize(doc, subs) -> dict:
    totals = {"clades": len(doc["clades"]), "families": len(doc["events"]) and 0,
              "subfamilies": 0, "genera": 0, "species": 0, "subspecies": 0}
    fams = [obj for kind, obj in doc["events"] if kind == "family"]
    totals["families"] = len(fams)
    for fam in fams:
        st = family_stats(fam, subs)
        totals["subfamilies"] += st["subfamilies"]
        totals["genera"] += st["genera"]
        totals["species"] += st["species"]
        totals["subspecies"] += st["subspecies"]
    return totals


def build_tree(site: Site, doc, subs):
    clade_nodes = {}
    children = {}
    for cid in [obj["id"] for kind, obj in doc["events"] if kind == "clade"]:
        clade_nodes[cid] = None
        children[cid] = []
    root = None
    for kind, obj in doc["events"]:
        if kind == "clade":
            node = {"type": "clade", "id": obj["id"], "zh": obj["zh"], "latin": obj["latin"],
                    "children": children[obj["id"]]}
            clade_nodes[obj["id"]] = node
            parent = CLADE_PARENT.get(obj["id"])
            if parent:
                children[parent].append(node)
            else:
                root = node
        else:
            fam = obj
            node = {"type": "family", "id": fam["id"], "zh": fam["zh"], "latin": fam["latin"],
                    "counts": family_stats(fam, subs), "file": data_file_for(fam)}
            if fam["subfamilies"]:
                node["subfamilies"] = [
                    {"type": "subfamily", "id": s["id"], "zh": s["zh"], "latin": s["latin"],
                     "counts": subfamily_stats(s, subs),
                     "file": "data/termitidae/%s.json" % s["id"]}
                    for s in fam["subfamilies"]]
            children[fam["clade"]].append(node)
    if root is None:
        sys.exit("error: 未找到根支系 isoptera")
    return root


def data_file_for(fam: dict) -> str:
    if fam["id"] == "termitidae":
        return "data/termitidae/"
    if fam["clade"] == "teletisoptera":
        return TELETERM_AGG["file"]
    if fam["clade"] in ("neoisoptera", "geoisoptera"):
        return NEOTERM_AGG["file"]
    return "data/%s.json" % fam["id"]


def display_name(fam: dict) -> str:
    return "%s %s" % (fam["zh"], fam["latin"].capitalize())


def family_payload(site: Site, fam: dict, subs: dict) -> dict:
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": display_name(fam), "version": site.version,
        "isPartOf": {"@id": site.index_url, "name": site.index_name},
        "cladeIds": [{"family": fam["id"], "clade": fam["clade"]}],
        "counts": family_stats(fam, subs),
        "families": [{"zh": fam["zh"], "latin": fam["latin"], "id": fam["id"],
                      "genera": [genus_node(g, subs) for g in fam["genera"]]}],
    }


def aggregate_payload(site: Site, agg: dict, fams: list, subs: dict) -> dict:
    counts = {"families": len(fams), "genera": 0, "species": 0, "subspecies": 0, "subfamilies": 0}
    payload_fams = []
    clade_ids = []
    for fam in fams:
        st = family_stats(fam, subs)
        counts["genera"] += st["genera"]
        counts["species"] += st["species"]
        counts["subspecies"] += st["subspecies"]
        clade_ids.append({"family": fam["id"], "clade": fam["clade"]})
        payload_fams.append({"zh": fam["zh"], "latin": fam["latin"], "id": fam["id"],
                             "genera": [genus_node(g, subs) for g in fam["genera"]]})
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "%s %s" % (agg["zh"], agg["latin"]), "version": site.version,
        "isPartOf": {"@id": site.index_url, "name": site.index_name},
        "cladeIds": clade_ids, "counts": counts, "families": payload_fams,
    }


def subfamily_payload(site: Site, fam: dict, sub: dict, subs: dict) -> dict:
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "%s %s" % (sub["zh"], sub["latin"]), "version": site.version,
        "isPartOf": {"@id": site.index_url,
                     "family": {"id": fam["id"], "zh": fam["zh"], "latin": fam["latin"]}},
        "familyId": fam["id"], "subfamilyId": sub["id"],
        "counts": {"subfamilies": 1, **subfamily_stats(sub, subs)},
        "subfamily": {"zh": sub["zh"], "latin": sub["latin"], "id": sub["id"],
                      "genera": [genus_node(g, subs) for g in sub["genera"]]},
    }


def build_payloads(site: Site, doc, subs):
    fams = [obj for kind, obj in doc["events"] if kind == "family"]
    totals = summarize(doc, subs)
    files = {}
    tele = [f for f in fams if f["clade"] == "teletisoptera"]
    neo = [f for f in fams if f["clade"] in ("neoisoptera", "geoisoptera") and f["id"] != "termitidae"]
    termitidae = next((f for f in fams if f["id"] == "termitidae"), None)
    singles = [f for f in fams if f["id"] in ("mastotermitidae", "kalotermitidae")]
    for fam in singles:
        files[data_file_for(fam)] = (display_name(fam), family_stats(fam, subs), family_payload(site, fam, subs))
    files[TELETERM_AGG["file"]] = ("%s %s" % (TELETERM_AGG["zh"], TELETERM_AGG["latin"]),
                                   _agg_counts(tele, subs), aggregate_payload(site, TELETERM_AGG, tele, subs))
    files[NEOTERM_AGG["file"]] = ("%s %s" % (NEOTERM_AGG["zh"], NEOTERM_AGG["latin"]),
                                  _agg_counts(neo, subs), aggregate_payload(site, NEOTERM_AGG, neo, subs))
    if termitidae is not None:
        for sub in termitidae["subfamilies"]:
            st = subfamily_stats(sub, subs)
            files["data/termitidae/%s.json" % sub["id"]] = (
                "%s %s" % (sub["zh"], sub["latin"]),
                {"subfamilies": 1, **st},
                subfamily_payload(site, termitidae, sub, subs))
    ordered = []
    for fam in singles:
        ordered.append((data_file_for(fam), files[data_file_for(fam)]))
    ordered.append((TELETERM_AGG["file"], files[TELETERM_AGG["file"]]))
    ordered.append((NEOTERM_AGG["file"], files[NEOTERM_AGG["file"]]))
    if termitidae is not None:
        for sub in termitidae["subfamilies"]:
            path = "data/termitidae/%s.json" % sub["id"]
            ordered.append((path, files[path]))
    files = dict(ordered)

    file_list = []
    for path, (name, counts, payload) in files.items():
        file_list.append({"path": path, "name": name, "counts": counts,
                          "bytes": len(dump_json(payload))})

    clades = [{"id": obj["id"], "zh": obj["zh"], "latin": obj["latin"],
               "parent": CLADE_PARENT.get(obj["id"])}
              for kind, obj in doc["events"] if kind == "clade"]
    family_clade = {fam["id"]: fam["clade"] for fam in fams}
    tree = build_tree(site, doc, subs)
    index = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": site.index_name,
        "alternateName": "Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List",
        "version": site.version,
        "description": "现存等翅下目（白蚁）全部现生类群的拉丁学名—中文正名对照名录，收录 13 科 %d 属 %d 种 %d 亚种，含模式种标记、分布信息与 %d 篇参考文献。"
                       % (totals["genera"], totals["species"], totals["subspecies"], site.reference_count),
        "creator": CREATOR,
        "license": LICENSE,
        "inLanguage": "zh-CN",
        "datePublished": site.created,
        "dateModified": site.modified,
        "counts": totals,
        "clades": clades,
        "familyClade": family_clade,
        "tree": tree,
        "files": file_list,
    }
    data = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": site.index_name,
        "alternateName": "Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List",
        "description": index["description"],
        "creator": CREATOR,
        "datePublished": site.created,
        "dateModified": site.modified,
        "version": site.version,
        "inLanguage": "zh-CN",
        "license": LICENSE,
        "isAccessibleForFree": True,
        "keywords": KEYWORDS,
        "counts": {"families": totals["families"], "genera": totals["genera"],
                   "species": totals["species"], "subspecies": totals["subspecies"]},
        "source_file": "index.md",
        "clades_in_document_order": ["%s %s" % (c["zh"], c["latin"]) for c in clades],
        "families": [_family_node_lite(f, subs) for kind, f in doc["events"] if kind == "family"],
    }
    return files, file_list, index, data, totals


def _agg_counts(fams, subs):
    counts = {"families": len(fams), "genera": 0, "species": 0, "subspecies": 0, "subfamilies": 0}
    for fam in fams:
        st = family_stats(fam, subs)
        counts["genera"] += st["genera"]
        counts["species"] += st["species"]
        counts["subspecies"] += st["subspecies"]
    return counts


def _family_node_lite(fam: dict, subs: dict) -> dict:
    node = {"zh": fam["zh"], "latin": fam["latin"], "id": fam["id"]}
    if fam["subfamilies"]:
        node["subfamilies"] = [
            {"zh": s["zh"], "latin": s["latin"], "id": s["id"],
             "genera": [genus_node(g, subs) for g in s["genera"]]}
            for s in fam["subfamilies"]]
    else:
        node["genera"] = [genus_node(g, subs) for g in fam["genera"]]
    return node


# ------------------------------------------------------------------ 统计页
def stats_payloads(site: Site, doc, subs, totals):
    fams = [obj for kind, obj in doc["events"] if kind == "family"]
    termitidae = next((f for f in fams if f["id"] == "termitidae"), None)
    G, S, SS = totals["genera"], totals["species"], totals["subspecies"]

    def fam_rows():
        rows = []
        for fam in fams:
            st = family_stats(fam, subs)
            rows.append('<tr><td><a href="%s/family/%s/">%s</a></td><td>%s</td>'
                        '<td class="num">%d</td><td class="num">%d</td><td class="num">%d</td></tr>'
                        % (site.base_url, fam["id"], fam["zh"], fam["latin"],
                           st["genera"], st["species"], st["subspecies"]))
        return rows

    def sub_rows():
        rows = []
        for sub in (termitidae["subfamilies"] if termitidae else []):
            st = subfamily_stats(sub, subs)
            rows.append('<tr><td><a href="%s/subfamily/%s/">%s</a></td><td>%s</td>'
                        '<td class="num">%d</td><td class="num">%d</td><td class="num">%d</td></tr>'
                        % (site.base_url, sub["id"], sub["zh"], sub["latin"],
                           st["genera"], st["species"], st["subspecies"]))
        return rows

    def genus_rows(lang):
        items = []
        for fam in fams:
            for g, sub in all_genera(fam):
                st = genus_stats(g, subs)
                if sub is not None:
                    parent = sub["zh"] if lang == "zh-CN" else sub["latin"]
                else:
                    parent = fam["zh"] if lang == "zh-CN" else fam["latin"].capitalize()
                items.append((-st["species"], g["latin"].lower(), parent, g, st))
        items.sort(key=lambda x: (x[0], x[1]))
        rows = []
        for _, _, parent, g, st in items:
            rows.append('<tr><td>%s</td><td><a href="%s/genus/%s/">%s</a></td><td>%s</td>'
                        '<td class="num">%d</td><td class="num">%d</td></tr>'
                        % (parent, site.base_url, g["id"], g["latin"], g["zh"],
                           st["species"], st["subspecies"]))
        return rows

    def overview(labels):
        return ['<tr><td>%s</td><td class="num">%d</td></tr>' % (labels[0], 13),
                '<tr><td>%s</td><td class="num">%d</td></tr>' % (labels[1], 18),
                '<tr><td>%s</td><td class="num">%d</td></tr>' % (labels[2], G),
                '<tr><td>%s</td><td class="num">%d</td></tr>' % (labels[3], S),
                '<tr><td>%s</td><td class="num">%d</td></tr>' % (labels[4], SS)]

    TABLE = '<table class="stats-table">'

    def page(lang, cfg):
        out = []
        out += ['---', 'layout: default', 'title: ' + cfg['title'],
                'description: ' + cfg['description'], 'lang: ' + lang,
                'author: ' + cfg['author'], 'permalink: ' + cfg['permalink'], '---', '',
                '# ' + cfg['h1'], '', '## ' + cfg['overview_h'], '', TABLE,
                '<thead><tr><th>%s</th><th>%s</th></tr></thead>' % tuple(cfg['overview_head']),
                '<tbody>']
        out += overview(cfg['overview_labels'])
        out += ['</tbody>', '</table>', '', '## ' + cfg['family_h'], '', TABLE,
                '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>'
                % tuple(cfg['fam_head']), '<tbody>']
        out += fam_rows()
        out += ['</tbody>', '</table>', '', '## ' + cfg['sub_h'], '', TABLE,
                '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>'
                % tuple(cfg['sub_head']), '<tbody>']
        out += sub_rows()
        out += ['</tbody>', '</table>', '', '## ' + cfg['genus_h'], '',
                '<details class="genus-details">', '<summary>' + cfg['genus_summary'] + '</summary>',
                TABLE,
                '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>'
                % tuple(cfg['genus_head']), '<tbody>']
        out += genus_rows(lang)
        out += ['</tbody>', '</table>', '</details>']
        return ("\n".join(out) + "\n").encode("utf-8")

    zh = {
        'title': '统计 — 现存等翅下目（白蚁）各阶元物种数',
        'description': '"按分类阶元统计物种数：13 科、18 亚科、%d 属、%d 种、%d 亚种的概览，以及科级、亚科级、属级明细表，可横向对比不同类群的多样性。｜本站《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》（%s 最终版），全站收录 13 科、18 亚科、%d 属、%d 种、%d 亚种的现生类群。"' % (G, S, SS, site.version, G, S, SS),
        'author': '班奈特格林', 'permalink': '/stats/',
        'h1': '统计：各阶元物种数',
        'overview_h': '总览', 'overview_head': ('阶元', '数量'),
        'overview_labels': ('科', '亚科', '属', '种', '亚种'),
        'family_h': '科级（13 科）',
        'fam_head': ('中文名', '拉丁名', '属数', '种数', '亚种数'),
        'sub_h': '亚科级（白蚁科 18 亚科）',
        'sub_head': ('中文名', '拉丁名', '属数', '种数', '亚种数'),
        'genus_h': '属级（%d 属，按种数降序）' % G,
        'genus_summary': '展开/收起属级明细表',
        'genus_head': ('所属', '拉丁名', '中文名', '种数', '亚种数'),
    }
    en = {
        'title': 'Statistics — species counts by rank',
        'description': '"Species counts for the extant Isoptera checklist: 13 families, 18 subfamilies, %d genera, %s species, %d subspecies, with family and genus tables."' % (G, format(S, ','), SS),
        'author': '班奈特格林 (Bennet Green)', 'permalink': '/en/stats/',
        'h1': 'Statistics: species counts by rank',
        'overview_h': 'Overview', 'overview_head': ('Rank', 'Count'),
        'overview_labels': ('Family', 'Subfamily', 'Genus', 'Species', 'Subspecies'),
        'family_h': 'Families (13)',
        'fam_head': ('Chinese name', 'Latin name', 'Genera', 'Species', 'Subspecies'),
        'sub_h': 'Subfamilies (Termitidae, 18)',
        'sub_head': ('Chinese name', 'Latin name', 'Genera', 'Species', 'Subspecies'),
        'genus_h': 'Genera (%d, by species count)' % G,
        'genus_summary': 'Show / hide genus table',
        'genus_head': ('Parent', 'Latin name', 'Chinese name', 'Species', 'Subspecies'),
    }
    es = {
        'title': 'Estadísticas — número de especies por rango',
        'description': '"Recuento de especies del listado de isópteros actuales: 13 familias, 18 subfamilias, %d géneros, %s especies y %d subespecies, con tablas detalladas."' % (G, format(S, ',').replace(',', '.'), SS),
        'author': '班奈特格林 (Bennet Green)', 'permalink': '/es/stats/',
        'h1': 'Estadísticas: número de especies por rango',
        'overview_h': 'Resumen', 'overview_head': ('Rango', 'Número'),
        'overview_labels': ('Familia', 'Subfamilia', 'Género', 'Especie', 'Subespecie'),
        'family_h': 'Familias (13)',
        'fam_head': ('Nombre chino', 'Nombre latino', 'Géneros', 'Especies', 'Subespecies'),
        'sub_h': 'Subfamilias (Termitidae, 18)',
        'sub_head': ('Nombre chino', 'Nombre latino', 'Géneros', 'Especies', 'Subespecies'),
        'genus_h': 'Géneros (%d, por número de especies)' % G,
        'genus_summary': 'Mostrar / ocultar la tabla de géneros',
        'genus_head': ('Taxón superior', 'Nombre latino', 'Nombre chino', 'Especies', 'Subespecies'),
    }
    return {
        'stats.md': page('zh-CN', zh),
        'en/stats.md': page('en', en),
        'es/stats.md': page('es', es),
    }


# ------------------------------------------------------------------ 主流程
def main() -> int:
    ap = argparse.ArgumentParser(description='构建分类树数据与三语统计页')
    ap.add_argument('--write', action='store_true', help='写入全部产物')
    ap.add_argument('--check', action='store_true', help='校验磁盘产物与生成结果一致')
    args = ap.parse_args()

    site = Site()
    species = load_species()
    doc = load_list(species)
    subs = attach_subspecies(species)
    files, file_list, index, data, totals = build_payloads(site, doc, subs)
    payloads = {}
    for path, (name, counts, payload) in files.items():
        payloads[path] = dump_json(payload)
    payloads['data/index.json'] = dump_json(index)
    payloads['isoptera-data.json'] = dump_json(data)
    payloads.update(stats_payloads(site, doc, subs, totals))

    print('分类单元：科 %d / 亚科 %d / 属 %d / 种 %d / 亚种 %d；数据文件 %d 个'
          % (totals['families'], totals['subfamilies'], totals['genera'],
             totals['species'], totals['subspecies'], len(files)))

    problems = []
    for path, content in payloads.items():
        target = ROOT / path
        if args.check:
            if not target.is_file():
                problems.append('%s 不存在' % path)
            elif target.read_bytes() != content:
                problems.append('%s 与生成结果不一致' % path)
    if args.check:
        if problems:
            print('校验失败：')
            for item in problems:
                print('  - ' + item)
            return 1
        print('校验通过：%d 个产物与生成结果逐字节一致' % len(payloads))
        return 0

    if args.write:
        for path, content in payloads.items():
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        print('已写入 %d 个文件' % len(payloads))
    else:
        for path in payloads:
            print('  ' + path)
        print('未写入（加 --write 写入；加 --check 校验）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
