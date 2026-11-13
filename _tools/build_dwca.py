#!/usr/bin/env python3
"""生成 Darwin Core Archive（DwC-A）：GBIF Data Validator / IPT / Zenodo 可直接上传的归档包。

输入（都是仓库内已生成的确定性数据，脚本不联网、不引入任何外部数据）：
  dataset/data/isoptera-taxonomy.json   支系→科→亚科→属→种/亚种 的完整树（含中文名与页面地址）
  dataset/data/isoptera-synonyms.csv    次异名长表（异名 → 接受名）
  dataset/metadata.json                 标题、作者、许可、DOI，以及 EML 用的发布方与联系人

输出（确定性，重复运行零改动）：
  dataset/dwca/taxon.csv             core：Taxon 核心表（科/亚科/属/种/亚种 + 异名行，
                                     异名行用 acceptedNameUsageID 指回接受名）
  dataset/dwca/vernacularname.csv    VernacularName 扩展：中文正名 + ISO 639-1 语言码
  dataset/dwca/meta.xml              metafile：core rowType = dwc:Taxon，一个扩展
  dataset/dwca/eml.xml               EML 2.1.1（GBIF Metadata Profile）资源元数据
  dataset/dwca/CHECKSUMS.sha256      上述四个文件的 SHA-256
  downloads/isoptera-checklist-v<版本>-dwca.zip  归档包（meta.xml / eml.xml / 两个 csv 在 zip 根）

依据（逐字摘录与 locator 见 .sources/）：
  S0436 Darwin Core text guide —— metafile 必须叫 meta.xml；<archive metadata> 给 EML 的 URL；
        <core> 的 rowType 必填；有扩展时 core 要 <id index="0"/>、扩展要 <coreid index="N"/>；
        默认 fieldsTerminatedBy="," linesTerminatedBy="\\n" ignoreHeaderLines="0"
  S0437 GBIF data quality recommendations —— checklist 必需 taxonID；推荐 scientificName /
        taxonRank / kingdom / parentNameUsageID / acceptedNameUsageID；taxonRank 只认主要林奈阶元
  S0438 IPT resource metadata —— EML 必需 title / description / publishing organization /
        type / license / contact / creator

约定（改动需同步 dataset/README.md）：
  * taxonID 一律是站点 URL：科 /family/{id}/、亚科 /subfamily/{id}/、属 /genus/{id}/、
    种与亚种用各自页面地址（pageUrl）、异名 /taxon/synonym/{slug}-{hash6}/。
    **它们是外部引用的外键：slug 一旦发布就不该再改**（非改不可时要留 301）。
  * 阶元只用 family / subfamily / genus / species / subspecies。支系（clade）不是林奈阶元，
    不单独出行，改写进 higherClassification。
  * 亚科与亚种保留原阶元（不压平）——GBIF 的 taxonRank 推荐值里没有这两级，Validator 可能
    提示；这是刻意取舍：宁可提示，也不丢分类信息。
  * 异名行去掉原文献页码（页码写进 taxonRemarks），命名人写进 scientificNameAuthorship；
    页面上不存在的名称不编造 URL。
  * 模式产地（typeLocality）在 Taxon 核心表里没有专用术语，写进 taxonRemarks。

用法：
  python _tools/build_dwca.py             # 只统计与自检，不写文件
  python _tools/build_dwca.py --write     # 写入全部产物
  python _tools/build_dwca.py --check     # 校验仓库内产物是否与生成结果一致
  python _tools/build_dwca.py --strict    # 计数与 metadata.json 的 expectedCounts 不符时失败
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "dataset"
DWCA_DIR = DATASET_DIR / "dwca"
DOWNLOADS_DIR = ROOT / "downloads"
TAXONOMY_JSON = DATASET_DIR / "data" / "isoptera-taxonomy.json"
SYNONYMS_CSV = DATASET_DIR / "data" / "isoptera-synonyms.csv"
META_PATH = DATASET_DIR / "metadata.json"

DWC = "http://rs.tdwg.org/dwc/terms/"
DCTERMS = "http://purl.org/dc/terms/"
GBIF_TERMS = "http://rs.gbif.org/terms/1.0/"
DWC_TEXT_NS = "http://rs.tdwg.org/dwc/text/"

# core 的列顺序=索引；taxonID 必须在 index 0（<id index="0"/> 指它）。
# 每个 term 都是 Darwin Core 的 Taxon 术语（rs.gbif.org 的 taxon 核心表里都有）。
CORE_COLUMNS = [
    "taxonID",
    "scientificName",
    "scientificNameAuthorship",
    "taxonRank",
    "taxonomicStatus",
    "acceptedNameUsageID",
    "parentNameUsageID",
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "subfamily",
    "genus",
    "higherClassification",
    "vernacularName",
    "taxonRemarks",
]

# 扩展的列顺序=索引；taxonID 在 index 0，用 <coreid index="0"/> 指回 core
EXT_COLUMNS = ["taxonID", "vernacularName", "language"]

TERM_URI = {
    "taxonID": DWC + "taxonID",
    "scientificName": DWC + "scientificName",
    "scientificNameAuthorship": DWC + "scientificNameAuthorship",
    "taxonRank": DWC + "taxonRank",
    "taxonomicStatus": DWC + "taxonomicStatus",
    "acceptedNameUsageID": DWC + "acceptedNameUsageID",
    "parentNameUsageID": DWC + "parentNameUsageID",
    "kingdom": DWC + "kingdom",
    "phylum": DWC + "phylum",
    "class": DWC + "class",
    "order": DWC + "order",
    "family": DWC + "family",
    "subfamily": DWC + "subfamily",
    "genus": DWC + "genus",
    "higherClassification": DWC + "higherClassification",
    # core 里也留一列中文名，方便只读核心表的工具；带语言码的同名数据在扩展里
    "vernacularName": DWC + "vernacularName",
    "taxonRemarks": DWC + "taxonRemarks",
}
# 两个表都有 vernacularName，但扩展里的那个是 GBIF 的扩展术语（带 language 才有意义）
EXT_TERM_URI = {
    "taxonID": DWC + "taxonID",
    "vernacularName": GBIF_TERMS + "vernacularName",
    "language": DCTERMS + "language",
}

RANKS = ("family", "subfamily", "genus", "species", "subspecies")
RANK_EXPECTED_KEY = (
    ("family", "families"),
    ("subfamily", "subfamilies"),
    ("genus", "genera"),
    ("species", "species"),
    ("subspecies", "subspecies"),
)

# 站点把 Isoptera 摆在蜚蠊目之下（现存等翅下目）；这几个上位阶元在站点数据里没有单独条目，
# 因此作为常量写在每行上，并同步写进 higherClassification。
UPPER_CLASSIFICATION = ["Animalia", "Arthropoda", "Insecta", "Blattodea"]

# 支系名照抄数据里的 latin；根支系在数据里写作短语式的 "Extant Isoptera"，
# 不是合法林奈学名，在 higherClassification 里用通行的 "Isoptera"。
CLADE_LATIN_ALIAS = {"Extant Isoptera": "Isoptera"}

YEAR_END = re.compile(r",\s*((?:1[6-9]|20)\d{2})\b")
AUTHORSHIP = re.compile(r"^(?P<name>.+?)\s+(?P<auth>[A-ZÀ-ÖØ-Þ][^,]*,\s*(?:1[6-9]|20)\d{2})$")
PAGE_REF = re.compile(r"^\s*[:;,]\s*\d[\d\s,.\-–]*$")
PAGE_HEAD = re.compile(r"^[\s:;,]+(?P<page>\d[\d\s,.\-–]*?)\s*(?=[A-Za-z(]|$)")
TRAILING_PAREN = re.compile(r"\s*\((?:[^()]*)\)\s*$")
SLUG_STRIP = re.compile(r"[^a-z0-9]+")


# ---------------------------------------------------------------- 小工具

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def title_case_family(latin: str) -> str:
    """数据里的科名是全大写（MASTOTERMITIDAE），Darwin Core 里要写成 Mastotermitidae。"""
    latin = latin.strip()
    if not latin:
        return ""
    return latin[0].upper() + latin[1:].lower()


def slugify(text: str, limit: int = 60) -> str:
    slug = SLUG_STRIP.sub("-", text.lower()).strip("-")
    return slug[:limit].strip("-") or "taxon"


def site_url(meta: dict) -> str:
    return meta["siteUrl"].rstrip("/")


def sha1_short(text: str, n: int = 6) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def zip_name_of(meta: dict) -> str:
    return f"isoptera-checklist-v{meta['version']}-dwca.zip"


def csv_text(columns: list[str], rows: list[dict]) -> str:
    """固定列顺序、固定 \\n 行尾、最小引号——同一输入永远得到同一字节串。"""
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row.get(name, "") for name in columns])
    return buf.getvalue()


def zip_bytes(files: dict[str, bytes]) -> bytes:
    """确定性 zip：成员名排序、时间戳归零，避免每次构建字节不同。"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, files[name])
    return buf.getvalue()


# ---------------------------------------------------------------- 分类树 → 行

def clade_chain(clades: dict[str, dict], clade_id: str) -> list[dict]:
    chain: list[dict] = []
    seen: set[str] = set()
    while clade_id:
        if clade_id in seen:  # 数据自环时不无限循环
            break
        seen.add(clade_id)
        node = clades.get(clade_id)
        if node is None:
            break
        chain.append(node)
        clade_id = node.get("parentId") or ""
    return list(reversed(chain))


def higher_classification(clades: dict[str, dict], clade_id: str) -> str:
    names = UPPER_CLASSIFICATION + [
        CLADE_LATIN_ALIAS.get(node["latin"], node["latin"]) for node in clade_chain(clades, clade_id)
    ]
    return " | ".join(names)


def base_row(**fields) -> dict:
    row = {name: "" for name in CORE_COLUMNS}
    row.update(fields)
    return row


def remarks_for_accepted(taxon: dict) -> str:
    """模式产地（typeLocality）在 Taxon 核心表里没有专用术语，放 taxonRemarks 保底。"""
    locality = (taxon.get("typeLocality") or "").strip()
    if not locality:
        return ""
    return f"type locality: {locality}"


def build_tree_rows(meta: dict, tax: dict) -> tuple[list[dict], dict[str, dict]]:
    """按站点的分类顺序（支系→科→亚科→属→种→亚种）产出接受名行。"""
    clades = {clade["id"]: clade for clade in tax["clades"]}
    rows: list[dict] = []

    for family in tax["families"]:
        higher = higher_classification(clades, family["cladeId"])
        family_latin = title_case_family(family["latin"])
        family_id = f"{site_url(meta)}/family/{family['id']}/"
        rows.append(
            base_row(
                taxonID=family_id,
                scientificName=family_latin,
                taxonRank="family",
                taxonomicStatus="accepted",
                family=family_latin,
                higherClassification=higher,
                vernacularName=family["zh"],
            )
        )

        subfamily_latin_by_id: dict[str, str] = {}
        for subfamily in family.get("subfamilies") or []:
            subfamily_latin = subfamily["latin"]
            subfamily_latin_by_id[subfamily["id"]] = subfamily_latin
            rows.append(
                base_row(
                    taxonID=f"{site_url(meta)}/subfamily/{subfamily['id']}/",
                    scientificName=subfamily_latin,
                    taxonRank="subfamily",
                    taxonomicStatus="accepted",
                    parentNameUsageID=family_id,
                    family=family_latin,
                    subfamily=subfamily_latin,
                    higherClassification=higher,
                    vernacularName=subfamily["zh"],
                )
            )

        for genus in family["genera"]:
            subfamily_latin = subfamily_latin_by_id.get(genus.get("subfamilyId") or "", "")
            parent = (
                f"{site_url(meta)}/subfamily/{genus['subfamilyId']}/" if subfamily_latin else family_id
            )
            genus_id = f"{site_url(meta)}/genus/{genus['id']}/"
            rows.append(
                base_row(
                    taxonID=genus_id,
                    scientificName=genus["latin"],
                    taxonRank="genus",
                    taxonomicStatus="accepted",
                    parentNameUsageID=parent,
                    family=family_latin,
                    subfamily=subfamily_latin,
                    genus=genus["latin"],
                    higherClassification=higher,
                    vernacularName=genus["zh"],
                )
            )

            for species in genus["species"]:
                species_id = species["pageUrl"]
                rows.append(
                    base_row(
                        taxonID=species_id,
                        scientificName=species["latin"],
                        scientificNameAuthorship=species.get("authorship") or "",
                        taxonRank="species",
                        taxonomicStatus="accepted",
                        parentNameUsageID=genus_id,
                        family=family_latin,
                        subfamily=subfamily_latin,
                        genus=genus["latin"],
                        higherClassification=higher,
                        vernacularName=species["zh"],
                        taxonRemarks=remarks_for_accepted(species),
                    )
                )
                for subspecies in species.get("subspecies") or []:
                    rows.append(
                        base_row(
                            taxonID=subspecies["pageUrl"],
                            scientificName=subspecies["latin"],
                            scientificNameAuthorship=subspecies.get("authorship") or "",
                            taxonRank="subspecies",
                            taxonomicStatus="accepted",
                            parentNameUsageID=species_id,
                            family=family_latin,
                            subfamily=subfamily_latin,
                            genus=genus["latin"],
                            higherClassification=higher,
                            vernacularName=subspecies["zh"],
                            taxonRemarks=remarks_for_accepted(subspecies),
                        )
                    )

    by_id: dict[str, dict] = {}
    for row in rows:
        if row["taxonID"] in by_id:
            raise SystemExit(f"[错误] taxonID 重复：{row['taxonID']}")
        by_id[row["taxonID"]] = row
    return rows, by_id


# ---------------------------------------------------------------- 异名 → 行

def parse_synonym(raw: str) -> tuple[str, str, str, str]:
    """把「学名 命名人, 年份: 页码」拆成 (学名, 命名人, 页码, 附注)。

    数据里的写法有「Froggatt, 1898: 733」「Haviland, 1898: 411 (imago)」
    「Luppova, 1958: 102, 104」以及没有页码的「He & Qui, 1992」；
    属名重定会带括号且括号内有空格，如「Hodotermes ( Anacanthotermes ) koenigi」。
    页码不是学名的一部分——留着会让 GBIF 的名称解析失败，所以剥离到 taxonRemarks。
    """
    text = " ".join(raw.split())
    match = YEAR_END.search(text)
    if not match:
        return text, "", "", ""

    head = text[: match.end()].strip()   # 学名 + 命名人 + 年份
    tail = text[match.end():].strip()    # 往往是 ": 733" 或 ": 411 (imago)"
    page = ""
    note = ""
    if tail:
        paren = TRAILING_PAREN.search(tail)
        if paren:
            note = paren.group(0).strip()
            tail = tail[: paren.start()].strip()
        if tail and PAGE_REF.match(tail):
            page = tail.lstrip(":;, ").strip()
        elif tail:
            # 「: 297, pl. facing 297」这类：前段是页码，后面才是附注
            lead = PAGE_HEAD.match(tail)
            if lead:
                page = lead.group("page").strip(" ,;:.")
                note = (note + " " + tail[lead.end():].strip()).strip()
            else:
                note = (note + " " + tail.strip(" :;,")).strip()

    name, authorship = split_name_authorship(head)
    return name, authorship, page, note


def split_name_authorship(head: str) -> tuple[str, str]:
    """在「属名 [(亚属)] 种加词 [亚种加词] 命名人, 年份」里找到学名与命名人的分界。

    不能简单取「最后一个大写开头的片段」：亚属括号里的属名也是大写，
    「Hodotermes ( Anacanthotermes ) koenigi Holmgren & Holmgren, 1917」会被切坏。
    改用词法：属名 → 可选 (亚属) → 若干小写开头的加词 → 其余是命名人。
    """
    tokens = head.split()
    if not tokens:
        return head, ""
    index = 1  # 属名
    while index < len(tokens) and tokens[index] == "(":
        while index < len(tokens) and tokens[index] != ")":
            index += 1
        index += 1  # 跳过 ")"
    while index < len(tokens) and tokens[index][:1].islower():
        index += 1
    name = " ".join(tokens[:index]).strip()
    authorship = " ".join(tokens[index:]).strip()
    # 括号内的属名照通行写法收紧：「( Anacanthotermes )」→「(Anacanthotermes)」
    name = re.sub(r"\(\s+", "(", name)
    name = re.sub(r"\s+\)", ")", name)
    if not authorship:
        return name, ""
    # 没切出年份说明词法没命中，整串当学名，宁可没有命名人也不乱切
    if not YEAR_END.search(authorship):
        return head, ""
    return name, authorship


def synonym_rank(name: str) -> str:
    """按词数猜异名阶元：括号里的属名重定不计数，2 词=种，≥3 词=亚种。"""
    stripped = re.sub(r"\([^()]*\)", " ", name)
    words = [word for word in stripped.split() if word]
    return "subspecies" if len(words) >= 3 else "species"


def build_synonym_rows(meta: dict, by_id: dict[str, dict]) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    with SYNONYMS_CSV.open(encoding="utf-8", newline="") as handle:
        for record in csv.DictReader(handle):
            accepted_id = record["taxonID"]
            parent = by_id.get(accepted_id)
            if parent is None:
                raise SystemExit(f"[错误] 异名指向了不存在的接受名：{accepted_id}")
            raw_synonym = (record.get("synonym") or "").strip()
            if not raw_synonym:
                continue
            name, authorship, page, note = parse_synonym(raw_synonym)
            if not name:
                raise SystemExit(f"[错误] 异名解析为空：{raw_synonym}")

            ident = f"{slugify(name)}-{sha1_short(f'{accepted_id}|{raw_synonym}')}"
            synonym_id = f"{site_url(meta)}/taxon/synonym/{ident}/"
            if synonym_id in seen:
                continue
            seen.add(synonym_id)

            remarks = []
            if page:
                remarks.append(f"original page reference: {page}")
            if note:
                remarks.append(f"as published: {note}")
            locality = (record.get("synonymTypeLocality") or "").strip()
            if locality:
                remarks.append(f"type locality: {locality}")

            rows.append(
                base_row(
                    taxonID=synonym_id,
                    scientificName=name,
                    scientificNameAuthorship=authorship,
                    taxonRank=synonym_rank(name),
                    taxonomicStatus="synonym",
                    acceptedNameUsageID=accepted_id,
                    family=parent["family"],
                    subfamily=parent["subfamily"],
                    genus=parent["genus"],
                    higherClassification=parent["higherClassification"],
                    taxonRemarks="; ".join(remarks),
                )
            )
    return rows


# ---------------------------------------------------------------- meta.xml / eml.xml

def core_field_lines() -> list[str]:
    lines = []
    for index, name in enumerate(CORE_COLUMNS):
        if index == 0:
            continue  # taxonID 由 <id index="0"/> 声明
        lines.append(f'    <field index="{index}" term="{TERM_URI[name]}"/>')
    return lines


def extension_field_lines() -> list[str]:
    lines = []
    for index, name in enumerate(EXT_COLUMNS):
        if index == 0:
            continue  # taxonID 由 <coreid index="0"/> 声明
        lines.append(f'    <field index="{index}" term="{EXT_TERM_URI[name]}"/>')
    return lines


def meta_xml(meta: dict) -> str:
    eml_url = f"{site_url(meta)}/dataset/dwca/eml.xml"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<archive xmlns="{DWC_TEXT_NS}" metadata="{eml_url}">',
        '  <!-- core：Taxon。taxonID 在 index 0，与 <id index="0"/> 对应；'
        "异名行用 acceptedNameUsageID 指回接受名。 -->",
        '  <core encoding="UTF-8" fieldsEnclosedBy="&quot;" fieldsTerminatedBy=","'
        ' linesTerminatedBy="\\n" ignoreHeaderLines="1"'
        f' rowType="{DWC}Taxon">',
        "    <files>",
        "      <location>taxon.csv</location>",
        "    </files>",
        '    <id index="0"/>',
        *core_field_lines(),
        "  </core>",
        '  <!-- extension：中文正名（VernacularName），带 ISO 639-1 语言码 zh。 -->',
        '  <extension encoding="UTF-8" fieldsEnclosedBy="&quot;" fieldsTerminatedBy=","'
        ' linesTerminatedBy="\\n" ignoreHeaderLines="1"'
        f' rowType="{GBIF_TERMS}VernacularName">',
        "    <files>",
        "      <location>vernacularname.csv</location>",
        "    </files>",
        '    <coreid index="0"/>',
        *extension_field_lines(),
        "  </extension>",
        "</archive>",
        "",
    ]
    return "\n".join(lines)


def orcid_id(value: str) -> str:
    """ORCID 只写裸 ID：`https://orcid.org/0000-…` 或带尾斜杠的都归一成 `0000-…`。

    eml.xml 里这个值会写进 `<userId directory="https://orcid.org">`，整条 URL 塞进去
    会变成 https://orcid.org/https://orcid.org/…，validator 判不出来但读者点不开。
    """
    text = (value or "").strip()
    for prefix in ("https://orcid.org/", "http://orcid.org/", "orcid.org/"):
        if text.lower().startswith(prefix):
            text = text[len(prefix):]
            break
    return text.strip().rstrip("/")


def eml_config(meta: dict) -> dict:
    config = meta.get("eml") or {}
    contact = config.get("contact") or {}
    creator = (meta.get("creators") or [{}])[0]
    return {
        "publishing_organization": (config.get("publishingOrganization") or "").strip(),
        "contact_name": contact.get("name") or creator.get("nameEn", ""),
        "contact_email": (contact.get("email") or "").strip(),
        "contact_orcid": orcid_id(contact.get("orcid") or ""),
        "creator_name_en": creator.get("nameEn", ""),
        "creator_orcid": orcid_id(creator.get("orcid") or ""),
    }


def split_person(name: str) -> tuple[str, str]:
    """「Bennet Green」→（givenName, surName）。只用于 EML 的 individualName。"""
    parts = [part for part in name.split() if part]
    if len(parts) <= 1:
        return "", (parts[0] if parts else "")
    return " ".join(parts[:-1]), parts[-1]


def eml_xml(meta: dict) -> str:
    config = eml_config(meta)
    doi = meta.get("doi", {}).get("version", "") or ""
    license_info = meta.get("license", {})
    site = site_url(meta)
    given, surname = split_person(config["creator_name_en"])
    contact_given, contact_surname = split_person(config["contact_name"])
    abstract = " ".join(meta["description"]["en"].split())

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- 用 GBIF Metadata Profile（EML 2.1.1 派生）。发布方与联系人来自 '
        "dataset/metadata.json 的 eml 区块；邮箱 / ORCID 留空时不出现在这里，"
        "GBIF Data Validator 会提示补全。 -->",
        '<eml:eml xmlns:eml="eml://ecoinformatics.org/eml-2.1.1"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        f' xmlns:dc="{DCTERMS}"'
        f" packageId={quoteattr('doi:' + doi if doi else 'extant-isoptera-checklist')}"
        ' system="https://doi.org"'
        ' xsi:schemaLocation="eml://ecoinformatics.org/eml-2.1.1'
        ' http://rs.gbif.org/schema/eml-gbif-profile/1.1/eml-gbif-profile.xsd"'
        ' xml:lang="en">',
        "  <dataset>",
    ]

    if doi:
        lines.append(f"    <alternateIdentifier>{escape('https://doi.org/' + doi)}</alternateIdentifier>")
    lines.append(f'    <title xml:lang="en">{escape(meta["title"]["en"])}</title>')
    lines.append(f'    <title xml:lang="zh">{escape(meta["title"]["zh"])}</title>')

    lines.append('    <creator id="creator-1">')
    lines.append("      <individualName>")
    if given:
        lines.append(f"        <givenName>{escape(given)}</givenName>")
    lines.append(f"        <surName>{escape(surname)}</surName>")
    lines.append("      </individualName>")
    if config["creator_orcid"]:
        lines.append(
            f'      <userId directory="https://orcid.org">{escape(config["creator_orcid"])}</userId>'
        )
    lines.append("    </creator>")

    organization = config["publishing_organization"] or "Extant Isoptera Checklist"
    lines.append('    <metadataProvider id="org-1">')
    lines.append(f"      <organizationName>{escape(organization)}</organizationName>")
    lines.append(f"      <onlineUrl>{escape(site + '/')}</onlineUrl>")
    lines.append("    </metadataProvider>")
    lines.append("    <associatedParty>")
    lines.append(f"      <organizationName>{escape(organization)}</organizationName>")
    lines.append("      <role>publisher</role>")
    lines.append("    </associatedParty>")

    lines.append(f"    <pubDate>{escape(meta['dates']['issued'])}</pubDate>")
    lines.append("    <language>en</language>")
    lines.append("    <abstract>")
    lines.append(f"      <para>{escape(abstract)}</para>")
    lines.append("    </abstract>")

    lines.append("    <keywordSet>")
    for keyword in meta["keywords"]["en"]:
        lines.append(f"      <keyword>{escape(keyword)}</keyword>")
    lines.append("    </keywordSet>")
    # 中文关键词单独成组。EML 的 keywordSet 没有语言属性，keywordThesaurus 又必须指向
    # 一个真实存在的受控词表——这里没有可指的词表，宁可留空，也不编一个不存在的名称。
    lines.append("    <!-- 中文关键词 / Chinese keywords -->")
    lines.append("    <keywordSet>")
    for keyword in meta["keywords"]["zh"]:
        lines.append(f"      <keyword>{escape(keyword)}</keyword>")
    lines.append("    </keywordSet>")

    lines.append("    <intellectualRights>")
    lines.append(
        "      <para>"
        + escape(f"{license_info.get('name', '')} ({license_info.get('identifier', '')})")
        + "</para>"
    )
    lines.append("      <para>")
    lines.append(
        f"        <ulink url={quoteattr(license_info.get('url', ''))}>"
        f"{escape(license_info.get('url', ''))}</ulink>"
    )
    lines.append("      </para>")
    lines.append("    </intellectualRights>")

    lines.append("    <distribution>")
    lines.append("      <online>")
    lines.append(f'        <url function="information">{escape(site + "/")}</url>')
    lines.append("      </online>")
    lines.append("    </distribution>")

    lines.append('    <contact id="contact-1">')
    lines.append("      <individualName>")
    if contact_given:
        lines.append(f"        <givenName>{escape(contact_given)}</givenName>")
    lines.append(f"        <surName>{escape(contact_surname)}</surName>")
    lines.append("      </individualName>")
    if config["contact_email"]:
        lines.append(
            f"      <electronicMailAddress>{escape(config['contact_email'])}</electronicMailAddress>"
        )
    if config["contact_orcid"]:
        lines.append(
            f'      <userId directory="https://orcid.org">{escape(config["contact_orcid"])}</userId>'
        )
    lines.append("    </contact>")
    lines.append("  </dataset>")
    lines.append("</eml:eml>")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- 校验

def validate(meta: dict, rows: list[dict], ext_rows: list[dict], strict: bool) -> list[str]:
    problems: list[str] = []
    ids = [row["taxonID"] for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = sorted({taxon for taxon in ids if ids.count(taxon) > 1})
        problems.append(f"taxonID 不唯一（{len(duplicates)} 个）：{duplicates[:3]}")
    id_set = set(ids)

    for row in rows:
        for field in ("taxonID", "scientificName", "taxonRank"):
            if not row[field]:
                problems.append(f"{field} 为空：{row['taxonID'] or row['scientificName']}")
        if row["taxonRank"] not in RANKS:
            problems.append(f"taxonRank 非法（{row['taxonRank']}）：{row['taxonID']}")
        for field in ("parentNameUsageID", "acceptedNameUsageID"):
            value = row[field]
            if value and value not in id_set:
                problems.append(f"{field} 指向不存在的条目（{value}）：{row['taxonID']}")
        if row["taxonomicStatus"] not in ("accepted", "synonym"):
            problems.append(f"taxonomicStatus 非法：{row['taxonID']}")
        if row["taxonomicStatus"] == "synonym" and not row["acceptedNameUsageID"]:
            problems.append(f"异名行缺少 acceptedNameUsageID：{row['taxonID']}")
        for field in ("scientificName", "taxonRemarks", "vernacularName"):
            value = row[field]
            if "\\N" in value or value.strip().upper() == "NULL":
                problems.append(f"{field} 里出现了 verbatim null：{row['taxonID']}")

    for row in ext_rows:
        if row["taxonID"] not in id_set:
            problems.append(f"扩展里的 taxonID 在 core 里不存在：{row['taxonID']}")
        if row["language"] != "zh":
            problems.append(f"语言码应为 ISO 639-1 的 zh：{row['taxonID']}")
        if not row["vernacularName"]:
            problems.append(f"扩展行没有 vernacularName：{row['taxonID']}")

    counts = {rank: 0 for rank in RANKS}
    for row in rows:
        if row["taxonomicStatus"] == "accepted":
            counts[row["taxonRank"]] += 1
    expected = meta.get("expectedCounts") or {}
    for rank, key in RANK_EXPECTED_KEY:
        if key in expected and counts[rank] != expected[key]:
            message = (
                f"计数不符：{rank}={counts[rank]}，"
                f"metadata.json 的 expectedCounts.{key}={expected[key]}"
            )
            if strict:
                problems.append(message)
            else:
                print(f"[提醒] {message}")
    return problems


def build_all(meta: dict, strict: bool) -> tuple[dict[str, bytes], dict[str, int]]:
    tax = read_json(TAXONOMY_JSON)
    rows, by_id = build_tree_rows(meta, tax)
    accepted = len(rows)
    rows.extend(build_synonym_rows(meta, by_id))

    ext_rows = [
        {"taxonID": row["taxonID"], "vernacularName": row["vernacularName"], "language": "zh"}
        for row in rows
        if row["vernacularName"]
    ]

    problems = validate(meta, rows, ext_rows, strict)
    if problems:
        for problem in problems:
            print(f"[错误] {problem}", file=sys.stderr)
        raise SystemExit(1)

    taxon_csv = csv_text(CORE_COLUMNS, rows).encode("utf-8")
    ext_csv = csv_text(EXT_COLUMNS, ext_rows).encode("utf-8")
    meta_bytes = meta_xml(meta).encode("utf-8")
    eml_bytes = eml_xml(meta).encode("utf-8")

    for name, payload in (("meta.xml", meta_bytes), ("eml.xml", eml_bytes)):
        try:
            ET.fromstring(payload)
        except ET.ParseError as error:
            raise SystemExit(f"[错误] 生成的 {name} 不是合法 XML：{error}") from error

    checksums = "".join(
        f"{hashlib.sha256(payload).hexdigest()}  {name}\n"
        for name, payload in (
            ("taxon.csv", taxon_csv),
            ("vernacularname.csv", ext_csv),
            ("meta.xml", meta_bytes),
            ("eml.xml", eml_bytes),
        )
    ).encode("utf-8")

    files = {
        "taxon.csv": taxon_csv,
        "vernacularname.csv": ext_csv,
        "meta.xml": meta_bytes,
        "eml.xml": eml_bytes,
        "CHECKSUMS.sha256": checksums,
        f"downloads/{zip_name_of(meta)}": zip_bytes(
            {
                "taxon.csv": taxon_csv,
                "vernacularname.csv": ext_csv,
                "meta.xml": meta_bytes,
                "eml.xml": eml_bytes,
            }
        ),
    }
    stats = {
        "core": len(rows),
        "accepted": accepted,
        "synonyms": len(rows) - accepted,
        "vernacular": len(ext_rows),
    }
    return files, stats


def target_path(name: str) -> Path:
    if name.startswith("downloads/"):
        return DOWNLOADS_DIR / name.split("/", 1)[1]
    return DWCA_DIR / name


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="生成 Darwin Core Archive（DwC-A）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="写入全部产物")
    group.add_argument("--check", action="store_true", help="校验仓库内产物是否与生成结果一致")
    parser.add_argument("--strict", action="store_true", help="计数与 metadata.json 不符时直接失败")
    args = parser.parse_args(argv)

    meta = read_json(META_PATH)
    files, stats = build_all(meta, args.strict)

    print(
        f"core 行：{stats['core']}（接受名 {stats['accepted']} + 异名 {stats['synonyms']}）"
        f"，VernacularName 扩展 {stats['vernacular']} 行"
    )
    for name in ("taxon.csv", "vernacularname.csv", "meta.xml", "eml.xml", f"downloads/{zip_name_of(meta)}"):
        print(f"  {name}  {len(files[name]):,} B")

    # 元数据缺项不报错（缺就是不编造），但每次跑都提一句该补哪几个键，
    # 免得只有 GBIF Data Validator 才告诉用户 eml.xml 缺联系人。
    config = eml_config(meta)
    missing = []
    if not config["contact_email"]:
        missing.append("eml.contact.email")
    if not config["contact_orcid"]:
        missing.append("eml.contact.orcid")
    if not (meta.get("creators") or [{}])[0].get("orcid"):
        missing.append("creators[0].orcid")
    if missing:
        print("[待补] dataset/metadata.json：" + "、".join(missing)
              + "（留空不进 eml.xml，GBIF Data Validator 会提示补全）")

    if args.write:
        DWCA_DIR.mkdir(parents=True, exist_ok=True)
        for name, payload in files.items():
            target = target_path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            print(f"写出 {target.relative_to(ROOT)}")
        return 0

    if args.check:
        stale = []
        for name, payload in files.items():
            target = target_path(name)
            if not target.exists():
                stale.append(f"{name}（缺失）")
            elif target.read_bytes() != payload:
                stale.append(f"{name}（内容不一致）")
        if stale:
            for item in stale:
                print(f"[过期] {item}", file=sys.stderr)
            print("跑 `python _tools/build_dwca.py --write` 重新生成。", file=sys.stderr)
            return 1
        print("DwC-A 产物与生成结果一致。")
        return 0

    print("（dry-run：未写入；加 --write 落盘，--check 校验）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
