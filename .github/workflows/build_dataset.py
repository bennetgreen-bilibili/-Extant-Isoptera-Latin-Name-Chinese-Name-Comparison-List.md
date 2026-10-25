#!/usr/bin/env python3
"""构建带 DOI 的归档数据集包 dataset/（Zenodo / ScienceDB / GBIF 上传与站内下载用）。

数据集从仓库现有来源生成，不引入任何外部数据：
  _species/*.md            3071 个物种/亚种页的 front matter（拉丁学名、中文正名、命名人年份、
                           模式产地、分布中英、次异名及其模式产地、分类层级）
  data/index.json          支系—科—亚科 的层级与排序（数据集沿用站点的分类顺序）
  dataset/metadata.json    标题、描述、作者、关键词、许可、相关标识符、DOI 等元数据（唯一来源）
  <名录单文件>.md           文末 77 条参考文献（含 DOI）

生成（全部确定性输出，重复运行零改动）：
  dataset/data/isoptera-checklist.csv     逐条分类单元表（3071 行，Darwin Core 风格列名）
  dataset/data/isoptera-taxonomy.json     完整分类树（支系→科→亚科→属→种/亚种，含计数）
  dataset/data/isoptera-synonyms.csv      次异名长表
  dataset/data/isoptera-counts.csv        科/亚科级分类单元计数
  dataset/data/isoptera-references.csv    参考文献（含 DOI）
  dataset/datapackage.json                Frictionless Data Package 描述（含字段字典）
  dataset/datacite-metadata.xml           DataCite Metadata Schema 4.6 记录
  dataset/CITATION.cff、仓库根 CITATION.cff Citation File Format（GitHub「Cite this repository」）
  仓库根 .zenodo.json                     Zenodo GitHub 集成元数据
  dataset/CHECKSUMS.sha256                各数据文件的 SHA-256
  dataset/README.md                       仅更新 AUTO:BEGIN 与 AUTO:END 之间的区块
  downloads/isoptera-checklist-v<版本>.zip 可直接上传 Zenodo 的归档包

用法：
  python .github/workflows/build_dataset.py             # 只统计与自检，不写文件
  python .github/workflows/build_dataset.py --write     # 写入全部产物
  python .github/workflows/build_dataset.py --check     # 校验仓库内产物是否与生成结果一致
  python .github/workflows/build_dataset.py --strict    # 计数与 metadata.json 不符时直接失败

DOI 流程见 _tools/数据集DOI与归档发布指南.md：铸造 DOI 后把 DOI 填进 dataset/metadata.json
的 doi.version / doi.concept，再运行 --write，DataCite XML、CITATION.cff、.zenodo.json 会一起更新。
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
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "dataset"
DATA_DIR = DATASET_DIR / "data"
META_PATH = DATASET_DIR / "metadata.json"
README_PATH = DATASET_DIR / "README.md"
SPECIES_DIR = ROOT / "_species"
INDEX_JSON = ROOT / "data" / "index.json"
DOWNLOADS_DIR = ROOT / "downloads"

DATACITE_NS = "http://datacite.org/schema/kernel-4"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
XML_NS = "http://www.w3.org/XML/1998/namespace"
AUTO_BEGIN = "<!-- AUTO:BEGIN -->"
AUTO_END = "<!-- AUTO:END -->"
DOI_BEGIN = "<!-- DOI:BEGIN -->"
DOI_END = "<!-- DOI:END -->"
BT = "\u0060"  # 反引号：Markdown 行内代码标记

LIST_MD_PATTERN = "*Latin Name * Chinese Name Comparison List.md"

CHECKLIST_FIELDS = [
    ("taxonID", "URL", "站点物种页永久地址，同时作为本数据集的分类单元标识符。Stable identifier (species page URL)."),
    ("scientificName", "string", "拉丁学名（属名 + 种加词 [+ 亚种加词]）。Latin scientific name."),
    ("authorship", "string", "命名人与发表年份。Authorship as given in the source."),
    ("taxonRank", "string", "分类等级：species 或 subspecies。Taxon rank."),
    ("parentNameUsage", "string", "亚种所属的种（种级记录为空）。Parent species for subspecies."),
    ("genus", "string", "属（拉丁）。Genus."),
    ("genusZh", "string", "属（中文）。Genus in Chinese."),
    ("subfamily", "string", "亚科（拉丁，无亚科者留空）。Subfamily."),
    ("subfamilyZh", "string", "亚科（中文）。Subfamily in Chinese."),
    ("family", "string", "科（拉丁）。Family."),
    ("familyZh", "string", "科（中文）。Family in Chinese."),
    ("clade", "string", "所属支系（拉丁）。Clade."),
    ("cladeZh", "string", "所属支系（中文）。Clade in Chinese."),
    ("vernacularName", "string", "中文正名（Darwin Core vernacularName）。Chinese standard name."),
    ("isTypeSpecies", "string", "是否为该属模式种：yes / no。Whether the taxon is its genus type species."),
    ("typeLocality", "string", "模式产地，沿用原始数据写法。Type locality as recorded."),
    ("distributionZh", "string", "分布（中文）。Distribution in Chinese."),
    ("distributionEn", "string", "分布（英文；仅种级有记录）。Distribution in English."),
    ("synonymCount", "integer", "次异名条数。Number of synonyms."),
    ("synonyms", "string", "全部次异名，分号分隔。All synonyms, semicolon-separated."),
    ("synonymLocalities", "string", "次异名模式产地，分号分隔。Type localities of synonyms."),
    ("pageUrl", "string", "对应站点页面 URL。Corresponding project page."),
]

SYNONYM_FIELDS = [
    ("taxonID", "string", "接受名的分类单元标识符。taxonID of the accepted taxon."),
    ("scientificName", "string", "接受名（拉丁）。Accepted scientific name."),
    ("synonym", "string", "次异名（含命名人与年份、页码）。Synonym with authorship."),
    ("synonymTypeLocality", "string", "次异名模式产地；仅当 localityAlignment = matched 时逐条对应，否则留空。Type locality of the synonym."),
    ("localityAlignment", "string", "模式产地与次异名的对应状态：matched 可逐条对齐；unmatched 原数据条数不等（完整模式产地见 isoptera-checklist.csv 的 synonymLocalities 列）；absent 原数据无模式产地。"),
]

REFERENCE_FIELDS = [
    ("referenceID", "integer", "名录正文中的文献编号。Reference number used in the checklist."),
    ("citation", "string", "文献著录（已去除 doi 字段）。Full citation without the DOI."),
    ("doi", "string", "DOI；无 DOI 时为空白。DOI, empty when unavailable."),
]

COUNTS_FIELDS = [
    ("clade", "string", "支系（拉丁）。Clade."),
    ("family", "string", "科（拉丁）。Family."),
    ("familyZh", "string", "科（中文）。Family in Chinese."),
    ("subfamily", "string", "亚科（拉丁；科级汇总行为空）。Subfamily."),
    ("subfamilyZh", "string", "亚科（中文）。Subfamily in Chinese."),
    ("genera", "integer", "属数。Number of genera."),
    ("species", "integer", "种数。Number of species."),
    ("subspecies", "integer", "亚种数。Number of subspecies."),
    ("total", "integer", "种 + 亚种。Species plus subspecies."),
]


# ---------------------------------------------------------------- 读取来源

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_front_matter(path: Path) -> dict:
    """解析 _species/*.md 的 front matter（字段均为单行标量，不引入 PyYAML 依赖）。"""
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---"):
        sys.exit(f"error: {path.name} 缺少 front matter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        sys.exit(f"error: {path.name} front matter 未闭合")
    data: dict = {}
    for line in parts[1].splitlines():
        m = re.match(r"^([a-z_0-9]+):\s*(.*)$", line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if len(raw) >= 2 and raw[0] == raw[-1] == '"':
            value = raw[1:-1].replace('\\"', '"')
        elif raw == "true":
            value = True
        elif raw == "false":
            value = False
        elif re.fullmatch(r"-?\d+", raw):
            value = int(raw)
        else:
            value = raw
        data[key] = value
    return data


@dataclass
class Taxon:
    slug: str
    latin: str
    zh: str
    rank: str
    genus_latin: str
    genus_zh: str
    genus_id: str
    subfamily_latin: str
    subfamily_zh: str
    subfamily_id: str
    family_latin: str
    family_zh: str
    family_id: str
    clade_latin: str
    clade_zh: str
    authorship: str
    type_locality: str
    distribution_zh: str
    distribution_en: str
    is_type_species: bool
    parent_latin: str
    parent_slug: str
    synonyms: str
    synonym_localities: str
    synonym_count: int
    page_url: str


def load_species(site_url: str) -> list:
    if not SPECIES_DIR.is_dir():
        sys.exit("error: 找不到 _species/ 目录")
    taxa = []
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        missing = [k for k in ("latin", "zh", "rank", "genus_latin", "genus_id", "family_id", "clade_latin") if not fm.get(k)]
        if missing:
            sys.exit(f"error: {path.name} 缺少字段 {missing}")
        taxa.append(
            Taxon(
                slug=path.stem,
                latin=str(fm["latin"]),
                zh=str(fm["zh"]),
                rank=str(fm["rank"]),
                genus_latin=str(fm["genus_latin"]),
                genus_zh=str(fm.get("genus_zh", "")),
                genus_id=str(fm["genus_id"]),
                subfamily_latin=str(fm.get("subfamily_latin", "")),
                subfamily_zh=str(fm.get("subfamily_zh", "")),
                subfamily_id=str(fm.get("subfamily_id", "")),
                family_latin=str(fm["family_latin"]),
                family_zh=str(fm["family_zh"]),
                family_id=str(fm["family_id"]),
                clade_latin=str(fm["clade_latin"]),
                clade_zh=str(fm.get("clade_zh", "")),
                authorship=str(fm.get("author_year", "")),
                type_locality=str(fm.get("type_locality", "")),
                distribution_zh=str(fm.get("distribution_zh", "")),
                distribution_en=str(fm.get("distribution_en", "")),
                is_type_species=bool(fm.get("type", False)),
                parent_latin=str(fm.get("parent_latin", "")),
                parent_slug=str(fm.get("parent_slug", "")),
                synonyms=str(fm.get("synonyms", "")),
                synonym_localities=str(fm.get("synonym_localities", "")),
                synonym_count=int(fm.get("synonym_count", 0) or 0),
                page_url=f"{site_url}/species/{path.stem}/",
            )
        )
    if not taxa:
        sys.exit("error: _species/ 为空")
    return taxa


def load_tree() -> tuple:
    """从 data/index.json 读取支系链路与「科→所属支系」顺序。"""
    if not INDEX_JSON.is_file():
        sys.exit(f"error: 找不到 {INDEX_JSON.relative_to(ROOT)}")
    index = read_json(INDEX_JSON)
    clades = []
    families = []

    def walk(node: dict, chain: list) -> None:
        node_type = node.get("type")
        if node_type == "clade":
            clades.append(
                {
                    "id": node["id"],
                    "zh": node.get("zh", ""),
                    "latin": node.get("latin", ""),
                    "parentId": chain[-1]["id"] if chain else "",
                }
            )
            for child in node.get("children", []):
                walk(child, chain + [node])
        elif node_type == "family":
            families.append((node, chain))

    walk(index["tree"], [])
    if not clades or not families:
        sys.exit("error: data/index.json 的 tree 结构不完整")
    return clades, families


def load_references() -> list:
    matches = sorted(ROOT.glob(LIST_MD_PATTERN))
    if not matches:
        sys.exit(f"error: 找不到名录单文件（匹配 {LIST_MD_PATTERN}）")
    lines = matches[0].read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## 参考文献")
    except StopIteration:
        sys.exit(f"error: {matches[0].name} 中未找到「## 参考文献」")
    entries = []
    current = None
    for line in lines[start + 1:]:
        m = re.match(r"^\s{0,3}(\d{1,3})\.\s+(.*)$", line)
        if m:
            if current:
                entries.append(current)
            current = {"id": int(m.group(1)), "text": m.group(2).strip()}
        elif current is not None and line.strip():
            current["text"] += " " + line.strip()
        elif current is not None and not line.strip():
            entries.append(current)
            current = None
    if current:
        entries.append(current)
    if not entries:
        sys.exit("error: 参考文献解析结果为空")

    for entry in entries:
        text = re.sub(r"\s+", " ", entry["text"]).strip()
        doi = ""
        m = re.search(r"10\.\d{4,9}/\S+", text)
        if m:
            doi = m.group(0).rstrip(".,;:")
            # SICI 型 DOI 自身含分号（…2.0.CO;2），\S+ 会在分号处截断，按原文补全
            sici = re.match(r"^\s*(\d+)\.?\s*$", text[m.end():])
            if sici and doi.upper().endswith(".CO"):
                doi = f"{doi};{sici.group(1)}"
        entry["doi"] = doi
        entry["citation"] = re.split(r"\sdoi:\s", text)[0].strip()
    return entries


# ---------------------------------------------------------------- 组装数据

def csv_bytes(header: list, rows: list) -> bytes:
    """UTF-8、无 BOM、RFC 4180 换行的 CSV（pandas/R 可直接读，不经 Excel 转码）。"""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def order_records(taxa: list, clades: list, families: list, warnings: list) -> list:
    """按站点分类顺序（支系→科→亚科→属）与拉丁名字母序排好全部记录。"""
    family_order = {node["id"]: i for i, (node, _) in enumerate(families)}
    subfamily_order = {}
    for node, _ in families:
        for i, sub in enumerate(node.get("subfamilies", [])):
            subfamily_order[sub["id"]] = i

    by_family = {}
    orphan = []
    for taxon in taxa:
        if taxon.family_id in family_order:
            by_family.setdefault(taxon.family_id, []).append(taxon)
        else:
            orphan.append(taxon)
            warnings.append(f"{taxon.latin}：科 {taxon.family_id} 不在 data/index.json 的树中，已排到末尾")

    ordered = []
    for node, _ in families:
        members = by_family.get(node["id"], [])
        if not members:
            warnings.append(f"科 {node['id']} 在树中但没有任何物种页记录")
            continue
        members.sort(
            key=lambda t: (
                subfamily_order.get(t.subfamily_id, -1),
                t.subfamily_id,
                t.genus_latin.casefold(),
                t.rank != "species",
                t.latin.casefold(),
            )
        )
        ordered.extend(members)

    subspecies_by_parent = {}
    for taxon in ordered:
        if taxon.rank == "subspecies":
            subspecies_by_parent.setdefault(taxon.parent_slug, []).append(taxon)
    final = []
    emitted = set()
    for taxon in ordered:
        if taxon.rank == "subspecies":
            continue
        final.append(taxon)
        emitted.add(taxon.slug)
        children = sorted(subspecies_by_parent.get(taxon.slug, []), key=lambda t: t.latin.casefold())
        final.extend(children)
        emitted.update(child.slug for child in children)
    for taxon in ordered:
        if taxon.rank == "subspecies" and taxon.parent_slug not in emitted:
            warnings.append(f"{taxon.latin}：母种 {taxon.parent_slug} 没有对应物种页，亚种已排到末尾")
            final.append(taxon)
    final.extend(orphan)
    if len(final) != len(taxa):
        sys.exit(f"error: 排序后记录数 {len(final)} 与读取到的 {len(taxa)} 不一致")
    return final


def taxonomy_tree(meta: dict, clades: list, families: list, records: list, warnings: list) -> dict:
    by_family = {}
    for taxon in records:
        by_family.setdefault(taxon.family_id, []).append(taxon)

    counts = {"clades": len(clades), "families": 0, "subfamilies": 0, "genera": 0, "species": 0, "subspecies": 0}
    family_nodes = []
    for node, chain in families:
        members = by_family.get(node["id"], [])
        subfamilies = node.get("subfamilies", [])
        subfamily_ids = [sub["id"] for sub in subfamilies]
        counts["families"] += 1
        counts["subfamilies"] += len(subfamilies)

        genera = {}
        for taxon in members:
            if taxon.rank == "subspecies":
                continue
            genus = genera.setdefault(
                taxon.genus_id,
                {
                    "id": taxon.genus_id,
                    "latin": taxon.genus_latin,
                    "zh": taxon.genus_zh,
                    "subfamilyId": taxon.subfamily_id,
                    "typeSpecies": "",
                    "counts": {"species": 0, "subspecies": 0},
                    "species": [],
                },
            )
            genus["counts"]["species"] += 1
            if taxon.is_type_species:
                genus["typeSpecies"] = taxon.latin
            genus["species"].append(
                {
                    "latin": taxon.latin,
                    "zh": taxon.zh,
                    "authorship": taxon.authorship,
                    "isTypeSpecies": taxon.is_type_species,
                    "typeLocality": taxon.type_locality,
                    "distributionZh": taxon.distribution_zh,
                    "distributionEn": taxon.distribution_en,
                    "pageUrl": taxon.page_url,
                    "subspecies": [],
                }
            )

        species_by_latin = {}
        for genus in genera.values():
            for species in genus["species"]:
                species_by_latin[species["latin"]] = species

        for taxon in members:
            if taxon.rank != "subspecies":
                continue
            parent = species_by_latin.get(taxon.parent_latin)
            if parent is None:
                warnings.append(f"{taxon.latin}：分类树中未找到母种 {taxon.parent_latin}，亚种未挂载")
                continue
            parent["subspecies"].append(
                {
                    "latin": taxon.latin,
                    "zh": taxon.zh,
                    "authorship": taxon.authorship,
                    "typeLocality": taxon.type_locality,
                    "pageUrl": taxon.page_url,
                }
            )
            for genus in genera.values():
                if parent in genus["species"]:
                    genus["counts"]["subspecies"] += 1
                    break

        genus_list = sorted(
            genera.values(),
            key=lambda g: (
                subfamily_ids.index(g["subfamilyId"]) if g["subfamilyId"] in subfamily_ids else -1,
                g["latin"].casefold(),
            ),
        )
        for genus in genus_list:
            counts["genera"] += 1
            counts["species"] += genus["counts"]["species"]
            counts["subspecies"] += genus["counts"]["subspecies"]

        family_nodes.append(
            {
                "id": node["id"],
                "zh": node.get("zh", ""),
                "latin": node.get("latin", ""),
                "cladeId": chain[-1]["id"] if chain else "",
                "subfamilies": [{"id": sub["id"], "zh": sub.get("zh", ""), "latin": sub.get("latin", "")} for sub in subfamilies],
                "genera": genus_list,
            }
        )

    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": meta["title"]["zh"],
        "alternateName": meta["name"],
        "version": meta["version"],
        "description": meta["description"]["zh"],
        "inLanguage": meta["language"],
        "license": meta["license"]["url"],
        "creator": {"@type": "Person", "name": meta["creators"][0]["name"]},
        "datePublished": meta["dates"]["issued"],
        "dateModified": meta["dates"]["updated"],
        "counts": counts,
        "clades": clades,
        "families": family_nodes,
    }


# ---------------------------------------------------------------- 生成元数据文件

def datapackage(meta: dict, file_stats: list, counts: dict) -> dict:
    field_sets = {
        "isoptera-checklist.csv": CHECKLIST_FIELDS,
        "isoptera-synonyms.csv": SYNONYM_FIELDS,
        "isoptera-references.csv": REFERENCE_FIELDS,
        "isoptera-counts.csv": COUNTS_FIELDS,
    }
    resources = []
    for path, description, rows, size in file_stats:
        name = Path(path).name
        resource = {
            "name": Path(path).stem.replace("-", "_"),
            "path": path,
            "title": description,
            "format": "json" if path.endswith(".json") else "csv",
            "bytes": size,
            "rows": rows,
            "profile": "tabular-data-resource" if path.endswith(".csv") else "data-resource",
        }
        if name in field_sets:
            resource["schema"] = {
                "fields": [{"name": name_, "type": type_, "description": description_} for name_, type_, description_ in field_sets[name]],
                "missingValues": [""],
            }
            resource["dialect"] = {
                "csvddfVersion": 1.2,
                "delimiter": ",",
                "lineTerminator": "\r\n",
                "header": True,
                "encoding": "utf-8",
            }
        resources.append(resource)

    return {
        "profile": "tabular-data-package",
        "name": meta["name"],
        "title": meta["title"]["zh"],
        "version": meta["version"],
        "description": meta["description"]["zh"],
        "id": (meta["doi"]["resolver"].rstrip("/") + "/" + meta["doi"]["version"]) if meta["doi"]["version"] else meta["siteUrl"],
        "homepage": meta["siteUrl"],
        "created": meta["dates"]["created"],
        "keywords": meta["keywords"]["zh"] + meta["keywords"]["en"],
        "licenses": [{"name": meta["license"]["identifier"], "title": meta["license"]["name"], "path": meta["license"]["url"]}],
        "contributors": [{"title": meta["creators"][0]["name"], "role": "author"}],
        "sources": [{"title": source} for source in meta["sources"]],
        "counts": counts,
        "resources": resources,
    }


def xml_sub(parent: ET.Element, tag: str, text: str = None, lang: str = None, **attrs: str) -> ET.Element:
    element = ET.SubElement(parent, f"{{{DATACITE_NS}}}{tag}", attrs)
    if text is not None:
        element.text = text
    if lang:
        element.set(f"{{{XML_NS}}}lang", lang)
    return element


def datacite_xml(meta: dict, counts: dict, total_bytes: int) -> str:
    doi = meta["doi"]["version"] or "10.5281/zenodo.XXXXXXX"
    ET.register_namespace("", DATACITE_NS)
    ET.register_namespace("xsi", XSI_NS)
    root = ET.Element(
        f"{{{DATACITE_NS}}}resource",
        {f"{{{XSI_NS}}}schemaLocation": f"{DATACITE_NS} https://schema.datacite.org/meta/kernel-4.6/metadata.xsd"},
    )
    xml_sub(root, "identifier", doi, identifierType="DOI")

    creators = xml_sub(root, "creators")
    for creator in meta["creators"]:
        node = ET.SubElement(creators, f"{{{DATACITE_NS}}}creator")
        xml_sub(node, "creatorName", creator["name"], nameType=creator.get("nameType", "Personal"))
        if creator.get("affiliation"):
            xml_sub(node, "affiliation", creator["affiliation"])
        if creator.get("orcid"):
            identifier = ET.SubElement(
                node,
                f"{{{DATACITE_NS}}}nameIdentifier",
                {"schemeURI": "https://orcid.org", "nameIdentifierScheme": "ORCID"},
            )
            identifier.text = creator["orcid"]

    titles = xml_sub(root, "titles")
    xml_sub(titles, "title", meta["title"]["zh"], lang="zh")
    xml_sub(titles, "title", meta["title"]["en"], lang="en", titleType="AlternativeTitle")
    xml_sub(root, "publisher", meta["publisher"])
    xml_sub(root, "publicationYear", str(meta["publicationYear"]))
    xml_sub(root, "resourceType", "Taxonomic checklist (Darwin Core aligned CSV + JSON)", resourceTypeGeneral=meta["resourceType"])

    subjects = xml_sub(root, "subjects")
    for keyword in meta["keywords"]["zh"]:
        xml_sub(subjects, "subject", keyword, lang="zh", subjectScheme="keywords")
    for keyword in meta["keywords"]["en"]:
        xml_sub(subjects, "subject", keyword, lang="en", subjectScheme="keywords")

    dates = xml_sub(root, "dates")
    xml_sub(dates, "date", meta["dates"]["created"], dateType="Created")
    xml_sub(dates, "date", meta["dates"]["updated"], dateType="Updated")

    xml_sub(root, "language", meta["language"])

    alternate = xml_sub(root, "alternateIdentifiers")
    xml_sub(alternate, "alternateIdentifier", meta["repository"], alternateIdentifierType="URL")

    related = xml_sub(root, "relatedIdentifiers")
    if meta["doi"]["concept"]:
        xml_sub(related, "relatedIdentifier", meta["doi"]["concept"], relatedIdentifierType="DOI", relationType="IsVersionOf")
    for item in meta["relatedIdentifiers"]:
        xml_sub(
            related,
            "relatedIdentifier",
            item["relatedIdentifier"],
            relatedIdentifierType=item["relatedIdentifierType"],
            relationType=item["relationType"],
        )

    xml_sub(root, "sizes", f"{counts['species'] + counts['subspecies']} taxon records; {total_bytes} bytes in data files")
    formats = xml_sub(root, "formats")
    xml_sub(formats, "format", "text/csv")
    xml_sub(formats, "format", "application/json")
    xml_sub(root, "version", meta["version"])

    rights = xml_sub(root, "rightsList")
    xml_sub(rights, "rights", meta["license"]["name"], lang="en", rightsURI=meta["license"]["url"])
    xml_sub(rights, "rights", "CC BY 4.0", rightsIdentifier=meta["license"]["identifier"], rightsIdentifierScheme="SPDX")

    descriptions = xml_sub(root, "descriptions")
    xml_sub(descriptions, "description", meta["description"]["zh"], lang="zh", descriptionType="Abstract")
    xml_sub(descriptions, "description", meta["description"]["en"], lang="en", descriptionType="Abstract")
    xml_sub(
        descriptions,
        "description",
        "数据来源：Krishna et al. 2013（Treatise on the Isoptera of the world）、Hellemans et al. 2024（Nat Commun 15:6724）等 77 篇文献，"
        "以及 termitologia.net、GBIF、《白蚁学》《世界白蚁中文名录》《中国动物志》等中文资料。中文正名为编者拟定或沿用既有译名，"
        "正式使用前建议核对原始文献。生成脚本为仓库内 .github/workflows/build_dataset.py，数据可完全重建。",
        lang="zh",
        descriptionType="Methods",
    )

    geo = xml_sub(root, "geoLocations")
    xml_sub(geo, "geoLocationPlace", "Global (all extant termite lineages)")

    ET.indent(root, space=" ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def citation_cff(meta: dict) -> str:
    first = meta["creators"][0]
    abstract = meta["description"]["en"].replace('"', "'")
    lines = [
        "cff-version: 1.2.0",
        'message: "If you use this checklist, please cite it as below. 中文引用格式见项目网站与 dataset/README.md。"',
        "type: dataset",
        f'title: "{meta["title"]["en"]}"',
        f'abstract: "{abstract}"',
        "authors:",
        f'  - family-names: "{first["name"]}"',
    ]
    if first.get("orcid"):
        lines.append(f'    orcid: "{first["orcid"]}"')
    if first.get("website"):
        lines.append(f'    website: "{first["website"]}"')
    lines += [
        f'version: "{meta["version"]}"',
        f'date-released: "{meta["dates"]["issued"]}"',
        'license: "CC-BY-4.0"',
        "keywords:",
    ]
    for keyword in meta["keywords"]["en"]:
        lines.append(f'  - "{keyword}"')
    lines += [
        f'repository-code: "{meta["repository"]}"',
        f'url: "{meta["siteUrl"]}"',
    ]
    if meta["doi"]["version"]:
        lines.append(f'doi: "{meta["doi"]["version"]}"')
    return "\n".join(lines) + "\n"


def zenodo_json(meta: dict) -> str:
    first = meta["creators"][0]
    payload = {
        "title": meta["title"]["en"],
        "description": (
            f"<p>{meta['description']['en']}</p>"
            f"<p><strong>Project website / 项目网站:</strong> <a href=\"{meta['siteUrl']}\">{meta['siteUrl']}</a></p>"
        ),
        "creators": [{"name": first["name"], "affiliation": first.get("affiliation", "") or "Independent researcher"}],
        "upload_type": "dataset",
        "publication_date": meta["dates"]["issued"],
        "access_right": "open",
        "license": meta["license"]["identifier"].lower(),
        "version": meta["version"],
        "language": "zho",
        "keywords": meta["keywords"]["en"] + meta["keywords"]["zh"],
        "related_identifiers": [
            {"identifier": meta["siteUrl"], "relation": "isDocumentedBy", "scheme": "url"},
            {"identifier": meta["repository"], "relation": "isSupplementedBy", "scheme": "url"},
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=1) + "\n"


# ---------------------------------------------------------------- 输出

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_readme_auto(meta: dict, counts: dict, file_stats: list, hashes: dict, references: list, notes: list) -> str:
    lines = [
        AUTO_BEGIN,
        "## 文件清单 Files",
        "",
        "| 文件 File | 内容 Content | 记录数 Rows | 字节 Bytes | SHA-256 |",
        "|---|---|---|---|---|",
    ]
    for path, description, rows, size in file_stats:
        lines.append(f"| {BT}{path}{BT} | {description} | {rows if rows else '—'} | {size} | {BT}{hashes[path][:16]}…{BT} |")
    with_doi = sum(1 for reference in references if reference["doi"])
    lines += [
        "",
        f"统计 Counts：{counts['clades']} 支系 · {counts['families']} 科 · {counts['subfamilies']} 亚科 · "
        f"{counts['genera']} 属 · {counts['species']} 种 · {counts['subspecies']} 亚种，"
        f"合计 {counts['species'] + counts['subspecies']} 条分类单元记录（每条均含中文正名）；"
        f"参考文献 {len(references)} 条，其中 {with_doi} 条带 DOI。",
        "",
        f"版本 Version：{meta['version']}　生成 Generator：.github/workflows/build_dataset.py（可由仓库来源完全重建）　"
        "本区块由脚本自动生成，请勿手工编辑；标记外的手写内容不受影响。",
        AUTO_END,
    ]
    if notes:
        lines.insert(1, "")
        lines.insert(1, "> 构建提示 Build notes：" + "；".join(notes))
    return "\n".join(lines)


def render_doi_block(meta: dict) -> str:
    first = meta["creators"][0]
    year = meta["dates"]["issued"][:4]
    if not meta["doi"]["version"]:
        return "\n".join(
            [
                DOI_BEGIN,
                "> **DOI：待铸造。** 在 Zenodo 上传页点击 Get a DOI now! 预留 DOI，把 DOI 填进 dataset/metadata.json，"
                "重新运行 build_dataset.py --write，本区块（DOI、引用格式、BibTeX）会自动更新；步骤见 "
                "_tools/数据集DOI与归档发布指南.md。",
                DOI_END,
            ]
        )
    doi = meta["doi"]["version"]
    resolver = meta["doi"]["resolver"].rstrip("/") + "/" + doi
    concept = meta["doi"]["concept"]
    fence = BT * 3
    lines = [
        DOI_BEGIN,
        f"**DOI**：[{doi}]({resolver})" + (f"（概念 DOI / 全部版本：{concept}）" if concept else ""),
        "",
        "**引用格式 Citation（中文 / APA 7）**",
        "",
        f"> {first['name']}. ({year}). 《{meta['title']['zh']}》(版本 {meta['version']}) [Data set]. {meta['publisher']}. {resolver}",
        "",
        "**Citation (English, APA 7)**",
        "",
        f"> {first.get('nameEn', first['name'])}. ({year}). {meta['title']['en']} (Version {meta['version']}) [Data set]. {meta['publisher']}. {resolver}",
        "",
        "**BibTeX**",
        "",
        fence + "bibtex",
        f"@misc{{{meta['name'].replace('-', '')}{year},",
        f"  author    = {{{first['name']}}},",
        f"  title     = {{{meta['title']['en']}}},",
        f"  year      = {{{year}}},",
        f"  version   = {{{meta['version']}}},",
        f"  publisher = {{{meta['publisher']}}},",
        f"  doi       = {{{doi}}},",
        f"  url       = {{{resolver}}}",
        "}",
        fence,
        DOI_END,
    ]
    return "\n".join(lines)


def replace_block(text: str, begin: str, end: str, block: str, filename: str) -> str:
    if begin not in text or end not in text:
        sys.exit(f"error: {filename} 缺少 {begin} / {end} 标记")
    head, rest = text.split(begin, 1)
    tail = rest.split(end, 1)[1]
    return head + block + tail


def build_zip(payload: dict, version: str) -> bytes:
    """确定性 zip：固定时间戳、固定成员顺序，重复运行字节一致。"""
    buffer = io.BytesIO()
    root_dir = f"isoptera-checklist-{version}"
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(payload):
            info = zipfile.ZipInfo(f"{root_dir}/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload[name])
    return buffer.getvalue()


def zip_manifest(data: bytes) -> list:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return [(info.filename, archive.read(info.filename)) for info in archive.infolist()]


def main() -> int:
    parser = argparse.ArgumentParser(description="构建带 DOI 的归档数据集包 dataset/")
    parser.add_argument("--write", action="store_true", help="写入产物（默认只统计与自检）")
    parser.add_argument("--check", action="store_true", help="校验仓库内产物与生成结果一致（不写文件）")
    parser.add_argument("--strict", action="store_true", help="计数与 dataset/metadata.json 的 expectedCounts 不符时失败")
    args = parser.parse_args()
    if args.write and args.check:
        parser.error("--write 与 --check 不能同时使用")

    meta = read_json(META_PATH)
    site_url = meta["siteUrl"].rstrip("/")
    taxa = load_species(site_url)
    clades, families = load_tree()
    references = load_references()

    warnings = []
    tree_orphans = [taxon for taxon in taxa if taxon.family_id not in {node["id"] for node, _ in families}]
    records = order_records(taxa, clades, families, warnings)
    tree = taxonomy_tree(meta, clades, families, records, warnings)

    counts = tree["counts"]
    expected = meta["expectedCounts"]
    mismatched = {key: (expected[key], counts[key]) for key in expected if expected.get(key) != counts.get(key)}
    if mismatched:
        message = "计数与 dataset/metadata.json 的 expectedCounts 不一致：" + "，".join(
            f"{key} 期望 {old} 实际 {new}" for key, (old, new) in mismatched.items()
        )
        if args.strict:
            print(f"error: {message}", file=sys.stderr)
            return 1
        warnings.append(message)

    checklist_rows = [
        [
            taxon.page_url,
            taxon.latin,
            taxon.authorship,
            taxon.rank,
            taxon.parent_latin,
            taxon.genus_latin,
            taxon.genus_zh,
            taxon.subfamily_latin,
            taxon.subfamily_zh,
            taxon.family_latin,
            taxon.family_zh,
            taxon.clade_latin,
            taxon.clade_zh,
            taxon.zh,
            yes_no(taxon.is_type_species),
            taxon.type_locality,
            taxon.distribution_zh,
            taxon.distribution_en,
            taxon.synonym_count,
            taxon.synonyms,
            taxon.synonym_localities,
            taxon.page_url,
        ]
        for taxon in records
    ]

    synonym_rows = []
    unaligned_taxa = 0
    for taxon in records:
        if not taxon.synonyms:
            continue
        names = [item.strip() for item in taxon.synonyms.split(";") if item.strip()]
        localities = [item.strip() for item in taxon.synonym_localities.split(";") if item.strip()]
        if not localities:
            status = "absent"
        elif len(names) == len(localities):
            status = "matched"
        else:
            status = "unmatched"
            unaligned_taxa += 1
            warnings.append(
                f"{taxon.latin}：次异名 {len(names)} 条、模式产地 {len(localities)} 条，无法逐条对齐（完整模式产地保留在主表 synonymLocalities 列）"
            )
        for index, name in enumerate(names):
            locality = localities[index] if status == "matched" else ""
            synonym_rows.append([taxon.page_url, taxon.latin, name, locality, status])

    counts_rows = []
    clade_latin = {clade["id"]: clade["latin"] for clade in clades}
    family_clade = {family["id"]: family["cladeId"] for family in tree["families"]}
    for family in tree["families"]:
        genera = family["genera"]
        family_species = sum(genus["counts"]["species"] for genus in genera)
        family_subspecies = sum(genus["counts"]["subspecies"] for genus in genera)
        counts_rows.append(
            [
                clade_latin.get(family_clade[family["id"]], ""),
                family["latin"],
                family["zh"],
                "",
                "",
                len(genera),
                family_species,
                family_subspecies,
                family_species + family_subspecies,
            ]
        )
        for sub in family["subfamilies"]:
            sub_genera = [genus for genus in genera if genus["subfamilyId"] == sub["id"]]
            sub_species = sum(genus["counts"]["species"] for genus in sub_genera)
            sub_subspecies = sum(genus["counts"]["subspecies"] for genus in sub_genera)
            counts_rows.append(
                [
                    clade_latin.get(family_clade[family["id"]], ""),
                    family["latin"],
                    family["zh"],
                    sub["latin"],
                    sub["zh"],
                    len(sub_genera),
                    sub_species,
                    sub_subspecies,
                    sub_species + sub_subspecies,
                ]
            )

    reference_rows = [[reference["id"], reference["citation"], reference["doi"]] for reference in references]

    data_files = {
        "data/isoptera-checklist.csv": csv_bytes([field[0] for field in CHECKLIST_FIELDS], checklist_rows),
        "data/isoptera-taxonomy.json": (json.dumps(tree, ensure_ascii=False, indent=1) + "\n").encode("utf-8"),
        "data/isoptera-synonyms.csv": csv_bytes([field[0] for field in SYNONYM_FIELDS], synonym_rows),
        "data/isoptera-counts.csv": csv_bytes([field[0] for field in COUNTS_FIELDS], counts_rows),
        "data/isoptera-references.csv": csv_bytes([field[0] for field in REFERENCE_FIELDS], reference_rows),
    }
    data_bytes = sum(len(content) for content in data_files.values())

    file_stats = [
        ("data/isoptera-checklist.csv", "逐条分类单元表（Darwin Core 风格列名；含中文正名、模式产地、分布、次异名）", len(checklist_rows), len(data_files["data/isoptera-checklist.csv"])),
        ("data/isoptera-taxonomy.json", "完整分类树（支系—科—亚科—属—种/亚种，含各级计数与页面链接）", counts["species"] + counts["subspecies"], len(data_files["data/isoptera-taxonomy.json"])),
        ("data/isoptera-synonyms.csv", "次异名长表（一行一次异名，含其模式产地）", len(synonym_rows), len(data_files["data/isoptera-synonyms.csv"])),
        ("data/isoptera-counts.csv", "科/亚科级分类单元计数", len(counts_rows), len(data_files["data/isoptera-counts.csv"])),
        ("data/isoptera-references.csv", "参考文献清单（有 DOI 者随条目给出）", len(reference_rows), len(data_files["data/isoptera-references.csv"])),
    ]
    hashes = {path: sha256(content) for path, content in data_files.items()}

    meta_files = {
        "datapackage.json": (json.dumps(datapackage(meta, file_stats, counts), ensure_ascii=False, indent=1) + "\n").encode("utf-8"),
        "datacite-metadata.xml": datacite_xml(meta, counts, data_bytes).encode("utf-8"),
        "CITATION.cff": citation_cff(meta).encode("utf-8"),
    }
    checksums = ("\n".join(f"{sha256(content)}  {path}" for path, content in {**data_files, **meta_files}.items()) + "\n").encode("utf-8")

    if not README_PATH.is_file():
        print(f"error: 缺少 {README_PATH.relative_to(ROOT).as_posix()}（其中 AUTO / DOI 标记区块由本脚本填充）", file=sys.stderr)
        return 1
    notes = []
    if unaligned_taxa:
        notes.append(
            f"{unaligned_taxa} 个分类单元的次异名与模式产地条数不等，无法逐条对齐（见 isoptera-synonyms.csv 的 localityAlignment 列）"
        )
    if tree_orphans:
        notes.append(f"{len(tree_orphans)} 条记录所属的科不在站点分类树中")
    if mismatched:
        notes.append("计数与 metadata.json 的 expectedCounts 不一致，已按实际数据生成")
    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_block(
        readme, AUTO_BEGIN, AUTO_END, render_readme_auto(meta, counts, file_stats, hashes, references, notes), README_PATH.name
    )
    readme = replace_block(readme, DOI_BEGIN, DOI_END, render_doi_block(meta), README_PATH.name)
    new_readme = readme.encode("utf-8")

    archive_members = {**data_files, **meta_files, "README.md": new_readme, "CHECKSUMS.sha256": checksums}
    for name in ("LICENSE", "CHANGELOG.md"):
        path = DATASET_DIR / name
        if path.is_file():
            archive_members[name] = path.read_bytes()
    zip_bytes = build_zip(archive_members, meta["version"])
    zip_path = f"downloads/isoptera-checklist-v{meta['version']}.zip"

    outputs = {DATASET_DIR / path: content for path, content in {**data_files, **meta_files}.items()}
    outputs[DATASET_DIR / "CHECKSUMS.sha256"] = checksums
    outputs[README_PATH] = new_readme
    outputs[DOWNLOADS_DIR / Path(zip_path).name] = zip_bytes
    outputs[ROOT / "CITATION.cff"] = meta_files["CITATION.cff"]
    outputs[ROOT / ".zenodo.json"] = zenodo_json(meta).encode("utf-8")

    with_doi = sum(1 for reference in references if reference["doi"])
    print(
        f"记录 {len(records)} 条（种 {counts['species']}，亚种 {counts['subspecies']}）；属 {counts['genera']}；"
        f"科 {counts['families']}；亚科 {counts['subfamilies']}；支系 {counts['clades']}"
    )
    print(f"次异名 {len(synonym_rows)} 条；参考文献 {len(references)} 条（含 DOI {with_doi} 条）")
    print(f"数据文件合计 {data_bytes} 字节；归档包 {zip_path} {len(zip_bytes)} 字节；产物 {len(outputs)} 个")
    for warning in warnings:
        print(f"warn: {warning}", file=sys.stderr)
    if not meta["doi"]["version"]:
        print("warn: metadata.json 的 doi.version 为空，DataCite XML 使用占位 DOI 10.5281/zenodo.XXXXXXX", file=sys.stderr)

    if args.check:
        problems = []
        for path, content in outputs.items():
            rel = path.relative_to(ROOT).as_posix()
            if path.suffix == ".zip":
                current = path.read_bytes() if path.is_file() else b""
                try:
                    if zip_manifest(current) != zip_manifest(content):
                        problems.append(rel)
                except zipfile.BadZipFile:
                    problems.append(rel)
                continue
            current = path.read_bytes() if path.is_file() else b""
            if current != content:
                problems.append(rel)
        if problems:
            print("error: 以下产物已过期，请运行 build_dataset.py --write 重新生成：", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
        print(f"ok: 全部 {len(outputs)} 个产物与生成结果一致")
        return 0

    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print(f"written: {path.relative_to(ROOT).as_posix()}")
        return 0

    print("\n未写入任何文件（dry-run）。加 --write 写入，--check 校验仓库产物。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
