#!/usr/bin/env python3
"""构建「命名差异与待核对」看板数据（/list/name-issues/）。

把已有缓存里的「本站名 vs 外部库」对照结果整理成结构化清单，供页面筛选、下载与程序化访问：

  _data/name_issues.json          页面用（site.data.name_issues）
  data/name-issues.json           公开副本（与 data/references.json 同一做法）
  downloads/isoptera-name-issues.csv  可下载对照表（UTF-8 BOM，Excel 直接打开不花屏）
  downloads/isoptera-synonym-groups.csv  异名→接受名长表（同样 UTF-8 BOM）

数据来源（均为仓库内已提交的缓存，不访问网络）：
  _data/authority_links.json   build_authority_links.py → GBIF / Catalogue of Life / Wikidata 匹配结果与 flags
  _data/bsf_links.json         build_bsf_links.py      → Blattodea Species File 半自动对照
  _species/*.md                front matter（中文正名、科、阶元、页面 slug）

三类问题（group）：
  conflict  名称差异：外部库把本站名当异名（给出接受名）
  match     匹配存疑：模糊匹配 / 多重候选，需要人工判断
  gap       覆盖缺口：仅匹配到上级阶元、外部库未收录、BSF 未检索到

名称差异还要逐对判定**关系类型**与**接收名方向**，对应「把异名记录到对应的接收名下面」：

  synonym_pairs[]    每对：本站名、外部库接受名、relation（synonym 异名 / combination 组合差异）、
                     direction（external 外部库名为接收名 / site 本站名为接收名 / disputed 待定）、
                     votes（各库判定）、disputed、recordable、recorded
  species_authority{} 物种页索引：incoming（外部库归入本种的异名）/ outgoing（外部库把本名放在哪个名字下）
  synonym_of_slug{}   已补录为异名的站内 slug → 它被补录到的接收名（物种页反向链接）
  meta.counts.*       关系/方向/可补录/已补录的统计口径

判定规则（详情见 _tools/外部权威库与一致性核对.md）：
  * 关系：属相同或加词不同 → synonym（异名）；同种异属（epithet 相同、属不同）→ combination（组合差异）。
    组合差异不是异名：GBIF 常按属级并系处理、把本站名写成它认为的「接受名」，方向容易写反。
  * 方向：逐个外部库按物种级结论投票（上位阶元 / 模糊 / 未收录不投票）。真异名：没人说本站名是
    接受名 → 外部接受名为接收名。组合差异：多数库用本站名 → 本站名为接收名，否则方向待定。
  * 可补录：只有「真异名 + 方向明确为外部接受名 + 至少两库一致 + 无相反票」才允许写进
    _species 的 authority_synonym_*；「已补录」仍以物种页 front matter 是否有该字段为准。
  downloads/isoptera-synonym-pairs.csv   同一批「名称差异对」长表（含关系、方向、接收名、补录状态）

外链基址读自 _config.yml 的 external.*：按 YAML 规则去掉行尾注释后再拼接，
否则会把「# + /<GBIF usageKey>」这类说明也拼进 URL，页面上的异名/接受名链接会变成坏地址。

只做整理，不改动任何站内分类数据；排序固定（先冲突、再存疑、再缺口，科内按学名），
输出确定性，可用 --check 校验仓库内产物是否最新。

用法：
  python .github/workflows/build_name_issues.py           # 只统计
  python .github/workflows/build_name_issues.py --write   # 写入三个产物
  python .github/workflows/build_name_issues.py --check   # 校验仓库内产物是否最新
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "_config.yml"
SPECIES_DIR = ROOT / "_species"
AUTHORITY = ROOT / "_data" / "authority_links.json"
BSF = ROOT / "_data" / "bsf_links.json"
DATA_OUT = ROOT / "_data" / "name_issues.json"
PUBLIC_OUT = ROOT / "data" / "name-issues.json"
CSV_OUT = ROOT / "downloads" / "isoptera-name-issues.csv"
SYN_CSV_OUT = ROOT / "downloads" / "isoptera-synonym-pairs.csv"

GROUP_ORDER = {"conflict": 0, "match": 1, "gap": 2}
SOURCE_ORDER = {"gbif": 0, "col": 1, "bsf": 2}
FM_RE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$")
# 接受名去掉命名人后剩下的规范学名：属 + 种 [+ 亚种小写加词]
CANON_RE = re.compile(
    r"^(?P<genus>[A-Z][A-Za-z\-]+)\s+(?P<species>[a-z][A-Za-z\-]+)"
    r"(?:\s+(?P<subspecies>[a-z][A-Za-z\-]+))?"
)
SYN_CSV_COLUMNS = [
    "ourName", "ourZh", "ourSlug", "externalName", "externalLatin",
    "relation", "direction", "receivingName", "receivingInSite", "receivingSlug",
    "disputed", "sources", "recorded", "ourUrl", "externalUrl",
]
SOURCE_LABELS = {"gbif": "GBIF", "col": "CoL", "bsf": "BSF"}


def config_value(key: str) -> str:
    """读 _config.yml 的单行标量，按 YAML 规则去掉行尾注释（空白 + # 之后）。"""
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"^\s*" + re.escape(key) + r":\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        sys.exit("error: 无法从 " + CONFIG.name + " 读取 " + key)
    value = re.split(r"\s+#", m.group(1), maxsplit=1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip().rstrip("/")


def url_base(key: str) -> str:
    """读外链基址，并确认它是干净的绝对 URL（防止行尾注释再次被拼进链接）。"""
    value = config_value(key)
    if not re.match(r"^https?://[^\s\"'#<>]+$", value):
        sys.exit("error: " + CONFIG.name + " 的 " + key + "=%r 不是合法 URL 基址" % value)
    return value


def parse_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---"):
        sys.exit("error: " + path.name + " 缺少 front matter")
    end = text.find("\n---", 3)
    if end < 0:
        sys.exit("error: " + path.name + " 的 front matter 未闭合")
    fields = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m or m.group("key") == "layout":
            continue
        value = m.group("value")
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fields[m.group("key")] = value
    return fields


def load_species() -> dict:
    out = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        latin = fm.get("latin", "")
        if not latin:
            continue
        out[latin] = {
            "zh": fm.get("zh", ""),
            "rank": "亚种" if fm.get("rank") == "subspecies" else "种",
            "family_zh": fm.get("family_zh", ""),
            "family_latin": fm.get("family_latin", ""),
            "slug": path.stem,
            # 已补录到本种「次异名」一节的外部权威库异名（front matter authority_synonyms）
            "authority_synonyms": [
                canonical_name(entry)
                for entry in (fm.get("authority_synonyms") or "").split(";")
                if entry.strip()
            ],
        }
    return out


def make_row(latin, sp, source, group, kind, theirs="", url=None, accepted=None,
             accepted_url=None, match=None, confidence=None, verified=False, note=""):
    return {
        "latin": latin,
        "zh": sp.get("zh", ""),
        "slug": sp.get("slug", ""),
        "rank": sp.get("rank", ""),
        "family_zh": sp.get("family_zh", ""),
        "family_latin": sp.get("family_latin", ""),
        "source": source,
        "group": group,
        "kind": kind,
        "theirs": theirs or "",
        "url": url or None,
        "accepted": accepted or None,
        "accepted_url": accepted_url or None,
        "match": match or None,
        "confidence": confidence if isinstance(confidence, int) else None,
        "verified": bool(verified),
        "note": (note or "").strip(),
    }


def canonical_name(label: str) -> str:
    """把带命名人的接受名压成规范学名：属 + 种 [+ 亚种加词]。

    「Amitermes wheeleri (Desneux, 1906)」→「Amitermes wheeleri」
    「Pericapritermes appellans metata Silvestri, 1914」→「Pericapritermes appellans metata」
    不同来源的接受名写法不完全一致，只有压成规范学名才能把同一个接受名的
    多条异名记录归到一组、并与 _species 的 latin 对齐。
    """
    text = re.sub(r"\s*\([^)]*\)\s*", " ", label or "").strip()
    m = CANON_RE.match(text)
    if not m:
        return (label or "").strip()
    parts = [m.group("genus"), m.group("species")]
    if m.group("subspecies"):
        parts.append(m.group("subspecies"))
    return " ".join(parts)


def annotate_accepted(row: dict, species: dict) -> dict:
    """给「外部库给出接受名」的条目补上接受名的规范学名与站内对应记录。

    这是「把异名记录到对应的接收名下面」的逐条版本：每条名称差异都能落到一个
    接收名（accepted）上；本名录也收录该名时，一并给出它的页面 slug 与中文名。
    """
    accepted = row.get("accepted")
    if not accepted:
        return row
    canonical = canonical_name(accepted)
    sp = species.get(canonical) or {}
    row = dict(row)
    row["accepted_latin"] = canonical
    if sp:
        row["accepted_in_site"] = True
        row["accepted_slug"] = sp.get("slug", "")
        row["accepted_zh"] = sp.get("zh", "")
    return row


def epithet_key(latin: str) -> tuple:
    """属之后各加词（去掉常见性别词尾），用来识别「同一物种、不同属」的组合差异。

    「Grigiotermes hageni」vs「Anoplotermes hageni」→ 同种异属（组合差异）；
    「Pericapritermes metatus」vs「Pericapritermes appellans metata」→ 加词不同（判为异名）；
    「Amitermes californicus」vs「Amitermes wheeleri」→ 异名。
    """
    parts = (latin or "").split()
    keys = []
    for epithet in parts[1:]:
        value = epithet.lower()
        for suffix in ("us", "a", "um", "is", "e", "i"):
            if value.endswith(suffix) and len(value) > len(suffix) + 3:
                value = value[: -len(suffix)]
                break
        keys.append(value)
    return tuple(keys)


def relation_kind(our_latin: str, accepted_latin: str) -> str:
    """"synonym" 真异名（加词不同）/"combination" 同种异属（组合差异）。"""
    if not our_latin or not accepted_latin:
        return "synonym"
    if our_latin.split()[0].lower() == accepted_latin.split()[0].lower():
        return "synonym"
    return "combination" if epithet_key(our_latin) == epithet_key(accepted_latin) else "synonym"


def vote_for(source: str, rec: dict, flags: list) -> str | None:
    """某个外部库对「本站名」的判定：accepted / synonym / None（不表态）。

    只看物种级结论：上位阶元、模糊匹配、未收录都记 None，避免把属级结果当成本种意见。
    """
    if source == "gbif":
        if "gbif_synonym" in flags:
            return "synonym"
        if any(flag in flags for flag in ("gbif_higherrank", "gbif_fuzzy", "gbif_missing", "gbif_doubtful")):
            return None
        return "accepted" if (rec.get("status") or "").upper() == "ACCEPTED" else None
    if source == "col":
        if "col_synonym" in flags:
            return "synonym"
        if any(flag in flags for flag in ("col_higherrank", "col_missing", "col_ambiguous")):
            return None
        return "accepted" if (rec.get("status") or "").lower() == "accepted" else None
    if source == "bsf":
        status = (rec.get("status") or "").lower()
        if status == "valid":
            return "accepted"
        if status == "synonym":
            return "synonym"
        return None
    return None


def resolve_direction(relation: str, synonym_votes: list, accepted_votes: list) -> str:
    """决定这一对的接收名在哪一侧。

    - 组合差异（同种异属）：多数外部库用本站名 → 本站名为接收名；否则方向待定。
    - 真异名：没有任何库说本站名是接受名 → 外部接受名为接收名；票数占优同样如此；否则待定。
    """
    if relation == "combination":
        return "site" if len(accepted_votes) > len(synonym_votes) else "disputed"
    if synonym_votes and not accepted_votes:
        return "external"
    if len(synonym_votes) > len(accepted_votes):
        return "external"
    return "disputed"


def build_synonym_pairs(rows: list, species: dict, votes_by_latin: dict) -> list:
    """把名称差异整理成「本站名 ↔ 外部库接受名」的一对一关系，并判定方向与关系类型。"""
    buckets: dict = {}
    for row in rows:
        if row["group"] != "conflict" or not row.get("accepted_latin"):
            continue
        key = (row["latin"], row["accepted_latin"])
        pair = buckets.get(key)
        if pair is None:
            pair = {
                "our": {
                    "latin": row["latin"],
                    "zh": row.get("zh", ""),
                    "slug": row.get("slug", ""),
                    "family_zh": row.get("family_zh", ""),
                    "family_latin": row.get("family_latin", ""),
                },
                "external": {"name": row["accepted"], "latin": row["accepted_latin"]},
                "sources": [],
                "our_links": [],
                "external_links": [],
            }
            buckets[key] = pair
        if row["source"] not in pair["sources"]:
            pair["sources"].append(row["source"])
        if row.get("url") and not any(link["source"] == row["source"] for link in pair["our_links"]):
            pair["our_links"].append({"source": row["source"], "url": row["url"]})
        if row.get("accepted_url") and not any(
                link["source"] == row["source"] for link in pair["external_links"]):
            pair["external_links"].append({"source": row["source"], "url": row["accepted_url"]})

    pairs = []
    for pair in buckets.values():
        pair["sources"].sort(key=lambda source: SOURCE_ORDER[source])
        pair["our_links"].sort(key=lambda link: SOURCE_ORDER[link["source"]])
        pair["external_links"].sort(key=lambda link: SOURCE_ORDER[link["source"]])
        votes = votes_by_latin.get(pair["our"]["latin"]) or {"synonym": [], "accepted": []}
        synonym_votes, accepted_votes = votes["synonym"], votes["accepted"]
        relation = relation_kind(pair["our"]["latin"], pair["external"]["latin"])
        direction = resolve_direction(relation, synonym_votes, accepted_votes)
        disputed = bool(synonym_votes) and bool(accepted_votes)
        receiving = None
        if direction == "external":
            ext_sp = species.get(pair["external"]["latin"]) or {}
            receiving = {
                "name": pair["external"]["name"],
                "latin": pair["external"]["latin"],
                "in_site": bool(ext_sp),
                "slug": ext_sp.get("slug"),
                "zh": ext_sp.get("zh"),
                "links": pair["external_links"],
            }
        elif direction == "site":
            receiving = {
                "name": pair["our"]["latin"],
                "latin": pair["our"]["latin"],
                "in_site": True,
                "slug": pair["our"]["slug"],
                "zh": pair["our"]["zh"],
                "links": pair["our_links"],
            }
        pair.update({
            "relation": relation,
            "direction": direction,
            "disputed": disputed,
            "receiving": receiving,
            "votes": {"synonym": synonym_votes, "accepted": accepted_votes},
            "recordable": (direction == "external" and relation == "synonym"
                           and not accepted_votes and len(synonym_votes) >= 2),
            "recorded": False,
        })
        pairs.append(pair)
    pairs.sort(key=lambda pair: (pair["our"]["latin"].casefold(), pair["external"]["latin"].casefold()))
    return pairs


def build_species_authority(pairs: list, species: dict) -> tuple:
    """生成物种页用索引：本种接收了哪些异名（incoming）/ 外部库把本名放在哪些名字下（outgoing）。"""
    index: dict = {}
    synonym_of_slug = {}
    for pair in pairs:
        if pair["direction"] == "external":
            accepted_sp = species.get(pair["external"]["latin"]) or {}
            pair["recorded"] = pair["our"]["latin"] in set(accepted_sp.get("authority_synonyms") or [])
            receiving = pair["receiving"] or {}
            if pair["recorded"] and pair["our"].get("slug"):
                synonym_of_slug[pair["our"]["slug"]] = {
                    "accepted": pair["external"]["name"],
                    "accepted_latin": pair["external"]["latin"],
                    "accepted_slug": receiving.get("slug"),
                    "accepted_zh": receiving.get("zh"),
                    "sources": pair["sources"],
                }
            if receiving.get("in_site") and receiving.get("slug"):
                entry = index.setdefault(receiving["slug"], {
                    "latin": receiving["latin"], "zh": receiving.get("zh") or "",
                    "incoming": [], "outgoing": [],
                })
                entry["incoming"].append({
                    "latin": pair["our"]["latin"],
                    "zh": pair["our"]["zh"],
                    "slug": pair["our"]["slug"],
                    "sources": pair["sources"],
                    "relation": pair["relation"],
                    "direction": pair["direction"],
                    "disputed": pair["disputed"],
                    "recorded": pair["recorded"],
                })
        else:
            entry = index.setdefault(pair["our"]["slug"], {
                "latin": pair["our"]["latin"], "zh": pair["our"]["zh"],
                "incoming": [], "outgoing": [],
            })
            entry["outgoing"].append({
                "latin": pair["external"]["latin"],
                "name": pair["external"]["name"],
                "sources": pair["sources"],
                "relation": pair["relation"],
                "direction": pair["direction"],
                "disputed": pair["disputed"],
                "links": pair["external_links"],
            })
    for entry in index.values():
        entry["incoming"].sort(key=lambda item: item["latin"].casefold())
        entry["outgoing"].sort(key=lambda item: item["latin"].casefold())
    return index, synonym_of_slug


def build() -> dict:
    auth = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    bsf = json.loads(BSF.read_text(encoding="utf-8"))
    species = load_species()

    gbif_base = url_base("gbif_species")
    col_base = url_base("col_taxon")
    bsf_base = url_base("bsf_otu")

    rows = []
    for latin in sorted(auth.get("taxa", {})):
        rec = auth["taxa"][latin]
        sp = species.get(latin, {})
        flags = rec.get("flags") or []
        gbif = rec.get("gbif") or {}
        col = rec.get("col") or {}

        if "gbif_synonym" in flags:
            acc = gbif.get("accepted") or {}
            rows.append(make_row(
                latin, sp, "gbif", "conflict", "synonym",
                theirs=gbif.get("name", ""),
                url=gbif_base + "/" + str(gbif.get("key")) if gbif.get("key") else None,
                accepted=acc.get("name"),
                accepted_url=gbif_base + "/" + str(acc.get("key")) if acc.get("key") else None,
                match=gbif.get("match"), confidence=gbif.get("confidence")))
        if "col_synonym" in flags:
            acc = col.get("accepted") or {}
            rows.append(make_row(
                latin, sp, "col", "conflict", "synonym",
                theirs=col.get("label") or latin,
                url=col_base + "/" + str(col.get("id")) if col.get("id") else None,
                accepted=acc.get("label"),
                accepted_url=col_base + "/" + str(acc.get("id")) if acc.get("id") else None,
                match="exact", confidence=None))
        if "gbif_fuzzy" in flags:
            rows.append(make_row(
                latin, sp, "gbif", "match", "fuzzy",
                theirs=gbif.get("name", ""),
                url=gbif_base + "/" + str(gbif.get("key")) if gbif.get("key") else None,
                match=gbif.get("match"), confidence=gbif.get("confidence")))
        if "gbif_higherrank" in flags:
            rows.append(make_row(
                latin, sp, "gbif", "gap", "higherrank",
                theirs=gbif.get("name", ""),
                match=gbif.get("match"), confidence=gbif.get("confidence")))
        if "col_higherrank" in flags:
            rows.append(make_row(
                latin, sp, "col", "gap", "higherrank",
                theirs=col.get("label") or "",
                match="higherrank"))
        if "col_missing" in flags:
            rows.append(make_row(latin, sp, "col", "gap", "missing"))

    bsf_verified_total = 0
    for latin in sorted(bsf.get("name_map", {})):
        rec = bsf["name_map"][latin]
        sp = species.get(latin, {})
        status = rec.get("status")
        verified = bool(rec.get("verified"))
        if verified:
            bsf_verified_total += 1
        note = rec.get("notes") or ""
        if status == "ambiguous":
            rows.append(make_row(latin, sp, "bsf", "match", "ambiguous",
                                 match=rec.get("match"), verified=verified, note=note))
        elif status == "missing":
            rows.append(make_row(latin, sp, "bsf", "gap", "missing",
                                 verified=verified, note=note))
        elif status == "synonym":
            # BSF 的 label 形如「异名 now 接受名」；接受名另有 accepted 字段，
            # 这里只保留异名本身，免得同一串名字在「外部记录」里出现两次。
            label = rec.get("label") or latin
            rows.append(make_row(
                latin, sp, "bsf", "conflict", "synonym",
                theirs=label.split(" now ", 1)[0].strip() or latin,
                url=rec.get("url"),
                accepted=rec.get("valid_label"),
                accepted_url=(bsf_base + "/" + str(rec.get("valid_otu")) + "/overview")
                if rec.get("valid_otu") else rec.get("url"),
                match=rec.get("match"), verified=verified, note=note))

    rows = [annotate_accepted(r, species) for r in rows]
    rows.sort(key=lambda r: (GROUP_ORDER[r["group"]], r["family_latin"].casefold(),
                             r["latin"].casefold(), SOURCE_ORDER[r["source"]], r["kind"]))

    by_group, by_source, by_kind, by_latin = {}, {}, {}, {}
    for r in rows:
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
        by_latin[r["latin"]] = by_latin.get(r["latin"], 0) + 1

    # 每个学名在三个外部库里的判定（accepted / synonym / 不表态），用于判定归并方向
    votes_by_latin = {}
    for latin in {row["latin"] for row in rows if row["group"] == "conflict"}:
        rec = auth.get("taxa", {}).get(latin) or {}
        flags = rec.get("flags") or []
        bsf_rec = bsf.get("name_map", {}).get(latin) or {}
        votes = {"synonym": [], "accepted": []}
        for source in ("gbif", "col", "bsf"):
            sub = rec.get(source) if source in ("gbif", "col") else bsf_rec
            vote = vote_for(source, sub or {}, flags)
            if vote:
                votes[vote].append(source)
        votes_by_latin[latin] = votes

    pairs = build_synonym_pairs(rows, species, votes_by_latin)
    species_authority, synonym_of_slug = build_species_authority(pairs, species)
    pair_by_key = {(pair["our"]["latin"], pair["external"]["latin"]): pair for pair in pairs}
    annotated_rows = []
    for row in rows:
        pair = pair_by_key.get((row["latin"], row.get("accepted_latin")))
        if row["group"] == "conflict" and pair:
            row = dict(row, relation=pair["relation"], direction=pair["direction"],
                       disputed=pair["disputed"], recordable=pair["recordable"],
                       recorded=pair["recorded"], receiving_latin=(pair["receiving"] or {}).get("latin"))
        annotated_rows.append(row)
    rows = annotated_rows

    payload = {
        "meta": {
            "title": "Isoptera checklist — name discrepancies and review queue",
            "scope": "本站每一物种/亚种与 GBIF Backbone、Catalogue of Life、Blattodea Species File 的对照结果中，"
                     "需要人工注意的条目；只提示，不改动站内分类数据。",
            "method": "由 .github/workflows/build_name_issues.py 从 _data/authority_links.json 与 "
                      "_data/bsf_links.json 生成；匹配规则见 _tools/外部权威库与一致性核对.md。",
            "cache_dates": {
                "authority": (auth.get("meta") or {}).get("generated"),
                "bsf": (bsf.get("meta") or {}).get("generated"),
            },
            "counts": {
                "total": len(rows),
                "by_group": by_group,
                "by_source": by_source,
                "by_kind": by_kind,
                "species_total": len(species),
                "species_with_issue": len({r["latin"] for r in rows}),
                "bsf_verified": bsf_verified_total,
                # 名称差异整理成「本站名 ↔ 外部库接受名」的对，并给出关系类型与接收名方向
                "conflict_species": len({r["latin"] for r in rows if r["group"] == "conflict"}),
                "conflict_pairs": len(pairs),
                "pairs_relation_synonym": sum(1 for p in pairs if p["relation"] == "synonym"),
                "pairs_relation_combination": sum(1 for p in pairs if p["relation"] == "combination"),
                "pairs_direction_external": sum(1 for p in pairs if p["direction"] == "external"),
                "pairs_direction_site": sum(1 for p in pairs if p["direction"] == "site"),
                "pairs_direction_disputed": sum(1 for p in pairs if p["direction"] == "disputed"),
                "pairs_disputed": sum(1 for p in pairs if p["disputed"]),
                "pairs_recordable": sum(1 for p in pairs if p["recordable"]),
                "pairs_recorded": sum(1 for p in pairs if p["recorded"]),
            },
            "by_latin": {k: by_latin[k] for k in sorted(by_latin)},
        },
        "issues": rows,
        "synonym_pairs": pairs,
        "species_authority": species_authority,
        "synonym_of_slug": synonym_of_slug,
    }
    return payload


def csv_text(payload: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["scientificName", "chineseName", "rank", "familyZh", "familyLatin",
                     "source", "group", "kind", "ourName", "externalName", "acceptedName",
                     "match", "confidence", "externalUrl", "acceptedUrl", "verified", "note"])
    for r in payload["issues"]:
        writer.writerow([r["latin"], r["zh"], r["rank"], r["family_zh"], r["family_latin"],
                         r["source"], r["group"], r["kind"], r["latin"], r["theirs"],
                         r["accepted"] or "", r["match"] or "",
                         r["confidence"] if r["confidence"] is not None else "",
                         r["url"] or "", r["accepted_url"] or "",
                         "yes" if r["verified"] else "no", r["note"]])
    return buf.getvalue()


def synonym_csv_text(payload: dict) -> str:
    """名称差异归并长表：一行一对「本站名 ↔ 外部库接受名」，含关系类型与接收名方向。"""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(SYN_CSV_COLUMNS)
    for pair in payload["synonym_pairs"]:
        receiving = pair["receiving"] or {}
        writer.writerow([
            pair["our"]["latin"], pair["our"]["zh"], pair["our"]["slug"],
            pair["external"]["name"], pair["external"]["latin"],
            pair["relation"], pair["direction"],
            receiving.get("name") or "", "yes" if receiving.get("in_site") else "no",
            receiving.get("slug") or "", "yes" if pair["disputed"] else "no",
            ";".join(pair["sources"]), "yes" if pair["recorded"] else "no",
            pair["our_links"][0]["url"] if pair["our_links"] else "",
            pair["external_links"][0]["url"] if pair["external_links"] else "",
        ])
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description="构建命名差异看板数据")
    parser.add_argument("--write", action="store_true", help="写入四个产物")
    parser.add_argument("--check", action="store_true", help="校验仓库内产物是否最新")
    args = parser.parse_args()

    for required in (AUTHORITY, BSF, CONFIG):
        if not required.is_file():
            sys.exit("error: 找不到 " + str(required.relative_to(ROOT)))

    payload = build()
    js = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    csv_content = csv_text(payload)
    synonym_csv_content = synonym_csv_text(payload)
    counts = payload["meta"]["counts"]

    print("条目 {total}（冲突 {conflict} / 存疑 {match} / 缺口 {gap}）；来源 "
          "GBIF {gbif} · COL {col} · BSF {bsf}；涉及物种 {species_with_issue}/{species_total}；"
          "BSF 已人工核对 {bsf_verified}".format(
              total=counts["total"], conflict=counts["by_group"].get("conflict", 0),
              match=counts["by_group"].get("match", 0), gap=counts["by_group"].get("gap", 0),
              gbif=counts["by_source"].get("gbif", 0), col=counts["by_source"].get("col", 0),
              bsf=counts["by_source"].get("bsf", 0),
              species_with_issue=counts["species_with_issue"],
              species_total=counts["species_total"], bsf_verified=counts["bsf_verified"]))
    print("名称差异整理成 {pairs} 对：关系 异名 {syn} · 组合差异 {comb}；方向 "
          "外部库名为接收名 {ext} · 本站名为接收名 {site} · 待定 {disp}；"
          "可补录 {recordable} 对，已补录 {recorded} 对；涉及本站名 {species} 个".format(
              pairs=counts["conflict_pairs"], syn=counts["pairs_relation_synonym"],
              comb=counts["pairs_relation_combination"],
              ext=counts["pairs_direction_external"], site=counts["pairs_direction_site"],
              disp=counts["pairs_direction_disputed"],
              recordable=counts["pairs_recordable"], recorded=counts["pairs_recorded"],
              species=counts["conflict_species"]))

    if args.check:
        problems = []
        if not DATA_OUT.is_file():
            problems.append(str(DATA_OUT.relative_to(ROOT)))
        elif DATA_OUT.read_text(encoding="utf-8") != js:
            problems.append(str(DATA_OUT.relative_to(ROOT)))
        if not PUBLIC_OUT.is_file():
            problems.append(str(PUBLIC_OUT.relative_to(ROOT)))
        elif PUBLIC_OUT.read_text(encoding="utf-8") != js:
            problems.append(str(PUBLIC_OUT.relative_to(ROOT)))
        if not CSV_OUT.is_file():
            problems.append(str(CSV_OUT.relative_to(ROOT)))
        elif CSV_OUT.read_text(encoding="utf-8-sig") != csv_content:
            problems.append(str(CSV_OUT.relative_to(ROOT)))
        if not SYN_CSV_OUT.is_file():
            problems.append(str(SYN_CSV_OUT.relative_to(ROOT)))
        elif SYN_CSV_OUT.read_text(encoding="utf-8-sig") != synonym_csv_content:
            problems.append(str(SYN_CSV_OUT.relative_to(ROOT)))
        if problems:
            print("error: 以下产物已过期，请运行 --write：" + "、".join(problems), file=sys.stderr)
            return 1
        print("校验通过：四个产物与生成结果一致")
        return 0

    if args.write:
        DATA_OUT.write_text(js, encoding="utf-8", newline="\n")
        PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC_OUT.write_text(js, encoding="utf-8", newline="\n")
        CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
        CSV_OUT.write_text(csv_content, encoding="utf-8-sig", newline="\n")
        SYN_CSV_OUT.write_text(synonym_csv_content, encoding="utf-8-sig", newline="\n")
        print("已写入 _data/name_issues.json、data/name-issues.json、"
              "downloads/isoptera-name-issues.csv、downloads/isoptera-synonym-pairs.csv")
    else:
        print("未写入（加 --write 写入文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
