#!/usr/bin/env python3
"""来源存档工具：把每个被读过并用于支撑结论的信息源落成可核查的记录。

设计见 .sources/README.md，工作区规则见 AGENTS.md。

用法：
  python _tools/sources.py add --json sources.json     # 新增/合并一条或多条来源
  python _tools/sources.py add --json -               # 从 stdin 读清单
  python _tools/sources.py check [--strict] [--ci]    # 校验存档（只读，绝不写盘）
  python _tools/sources.py list [--limit 20]          # 列出已存档来源
  python _tools/sources.py stats                      # 汇总
  python _tools/sources.py import-library             # 把 _unpublished/文库 的书目同步成来源记录（幂等）
  python _tools/sources.py library-add --file x.pdf --doi 10.1234/abcd --title "..." \
      --kind paper --reliability peer_reviewed        # 论文/报告全文入库 + 登记来源

清单格式（顶层是数组，或 {"records": [...]}）：
  [
    {
      "title": "Termite phylogeny ...",
      "source_type": "paper",              # web|paper|book|report|dataset|database|file|other
      "reliability": "peer_reviewed",      # primary|peer_reviewed|official|reference|secondary|unverified
      "url": "https://...",                # 或 doi / file_path（至少一个）
      "doi": "10.1234/xyz",
      "file_path": "_data/papers.json",    # 仅本地来源；自动算 sha256
      "authors": ["..."], "year": 2024, "publisher": "...", "lang": "en",
      "license": "CC-BY-4.0",
      "retrieved_via": "web_fetch",
      "evidence": [
        {"quote": "逐字摘录 <= 400 字", "locator": "p.3 ¶2", "note": "支撑：..."}
      ],
      "used_in": ["_posts/2026-11-05-xxx.md"],
      "notes": ""
    }
  ]

退出码：0 通过；1 校验失败（check）；2 用法/IO 错误。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ARCHIVE_DIR = ".sources"
INDEX_NAME = "index.json"
RECORDS_DIR = "records"
ID_RE = re.compile(r"^S\d{4,}$")
# 只认完整注释标记，避免文档里顺口写的 src:S0001 被当成引用
MARKER_RE = re.compile(r"<!--\s*src:(S\d{4,})\s*-->")
# 讲协议本身的文档不参与标记扫描（里面的示例 id 不一定存在）
META_FILES = {"AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md"}
SOURCE_TYPES = {"web", "paper", "book", "report", "dataset", "database", "file", "other"}
RELIABILITY = {"primary", "peer_reviewed", "official", "reference", "secondary", "unverified"}
REQUIRED = ("id", "title", "source_type", "reliability", "accessed", "canonical_key")
MAX_QUOTE = 400
# 标记只认 Markdown 正文（docx 等二进制交付物走 used_in + 文末来源表）
TEXT_SUFFIXES = {".md", ".markdown"}
SKIP_DIRS = {".git", "node_modules", "assets", "downloads", "photos", "_site", ".sources",
             "__pycache__", "vendor", "_tools", ".github"}


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_url(url: str) -> str:
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def make_key(rec: dict, root: Path) -> str:
    doi = (rec.get("doi") or "").strip()
    if doi:
        return "doi:" + doi.lower().replace("https://doi.org/", "").replace("http://doi.org/", "")
    if rec.get("url"):
        return "url:" + normalize_url(rec["url"])
    if rec.get("file_path"):
        fp = (root / rec["file_path"]).resolve()
        if fp.is_file():
            return f"file:{rel(root, fp)}@{sha256_file(fp)}"
        return "file:" + str(rec["file_path"])
    if rec.get("body_sha256"):
        return "sha256:" + rec["body_sha256"]
    return "title:" + sha256_text((rec.get("title") or "").strip().lower())[:16]


def archive_paths(root: Path) -> tuple[Path, Path]:
    base = root / ARCHIVE_DIR
    return base / INDEX_NAME, base / RECORDS_DIR


def load_index(root: Path) -> dict:
    idx_path, _ = archive_paths(root)
    if not idx_path.is_file():
        return {"meta": {"version": 1, "count": 0}, "sources": []}
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[sources] {ARCHIVE_DIR}/{INDEX_NAME} 不是合法 JSON：{exc}")
    data.setdefault("meta", {})
    data.setdefault("sources", [])
    return data


def save_index(root: Path, data: dict) -> None:
    idx_path, _ = archive_paths(root)
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    data["meta"]["count"] = len(data["sources"])
    data["meta"]["updated"] = now_iso()
    idx_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def next_id(sources: list[dict]) -> str:
    nums = [int(s["id"][1:]) for s in sources if ID_RE.match(str(s.get("id", "")))]
    return f"S{(max(nums) + 1) if nums else 1:04d}"


def render_record(rec: dict) -> str:
    lines = [
        "---",
        f"id: {rec['id']}",
        f"title: {json.dumps(rec['title'], ensure_ascii=False)}",
        f"source_type: {rec['source_type']}",
        f"reliability: {rec['reliability']}",
        f"accessed: {rec['accessed']}",
        f"canonical_key: {json.dumps(rec['canonical_key'], ensure_ascii=False)}",
    ]
    for key in ("url", "doi", "publisher", "lang", "license", "retrieved_via"):
        if rec.get(key):
            lines.append(f"{key}: {json.dumps(rec[key], ensure_ascii=False)}")
    if rec.get("year"):
        lines.append(f"year: {rec['year']}")
    if rec.get("authors"):
        lines.append("authors: " + json.dumps(rec["authors"], ensure_ascii=False))
    if rec.get("file_path"):
        lines.append(f"file_path: {json.dumps(rec['file_path'], ensure_ascii=False)}")
    if rec.get("body_sha256"):
        lines.append(f"body_sha256: {rec['body_sha256']}")
    if rec.get("chars"):
        lines.append(f"chars: {rec['chars']}")
    if rec.get("used_in"):
        lines.append("used_in: " + json.dumps(rec["used_in"], ensure_ascii=False))
    lines.append("---")
    lines.append("")
    lines.append(f"# {rec['id']} {rec['title']}")
    lines.append("")
    if rec.get("notes"):
        lines.append(rec["notes"].strip())
        lines.append("")
    if rec.get("evidence"):
        lines.append("## 摘录（逐字，不得改写）")
        lines.append("")
        for ev in rec["evidence"]:
            loc = ev.get("locator") or "位置未记录"
            lines.append(f"- **{loc}**：")
            lines.append("")
            lines.append("\n".join("  > " + ln for ln in ev["quote"].splitlines() or [""]))
            lines.append("")
            if ev.get("note"):
                lines.append(f"  说明：{ev['note'].strip()}")
                lines.append("")
    else:
        lines.append("## 摘录")
        lines.append("")
        lines.append("（未记录摘录：本条为读过但未直接引用的来源。）")
        lines.append("")
    if rec.get("library"):
        chunks = rec["library"].get("chunks") or []
        lines.append("## 全文" if len(chunks) == 1 else "## 分卷（按页切块）")
        lines.append("")
        for chunk in chunks:
            label = str(chunk.get("chunk") or "")
            if re.match(r"^\d{4}-\d{4}$", label):
                size = f"{label} 页，{chunk.get('chars')} 字符"
            else:
                size = f"{label}，{chunk.get('chars')} 字符"
            lines.append(f"- {chunk.get('txt')} — {size}")
        lines.append("")
    if rec.get("used_in"):
        lines.append("## 被用于")
        lines.append("")
        for path in rec["used_in"]:
            lines.append("- `" + path + "`")
        lines.append("")
    return "\n".join(lines)


def normalize_record(rec: dict, root: Path) -> dict:
    out = dict(rec)
    out["title"] = (out.get("title") or "").strip()
    out["source_type"] = (out.get("source_type") or "web").strip()
    out["reliability"] = (out.get("reliability") or "unverified").strip()
    out["accessed"] = out.get("accessed") or now_iso()
    out["evidence"] = [e for e in (out.get("evidence") or []) if (e.get("quote") or "").strip()]
    for ev in out["evidence"]:
        ev["quote"] = ev["quote"].strip()
        ev.setdefault("locator", "")
        ev.setdefault("note", "")
    out["used_in"] = sorted({str(p).strip() for p in (out.get("used_in") or []) if str(p).strip()})
    if out.get("authors") and isinstance(out["authors"], str):
        out["authors"] = [a.strip() for a in re.split(r"[;；]", out["authors"]) if a.strip()]
    if out.get("file_path"):
        fp = (root / out["file_path"]).resolve()
        if fp.is_file():
            out["file_path"] = rel(root, fp)
            out["body_sha256"] = sha256_file(fp)
            out["chars"] = len(fp.read_text(encoding="utf-8", errors="replace"))
    if out.get("body_text"):
        out["body_sha256"] = sha256_text(out["body_text"])
        out["chars"] = len(out["body_text"])
        out.pop("body_text", None)
    out["canonical_key"] = out.get("canonical_key") or make_key(out, root)
    return out


def merge(existing: dict, new: dict) -> tuple[dict, bool]:
    changed = False
    # 文库记录由 import-library 生成：分卷清单、字符数、来源说明都以 manifest 为准。
    # 重新导入时允许整段刷新，否则 manifest 重生成后记录会一直停在旧值。
    if new.get("library") and existing.get("library"):
        for key in ("notes", "accessed", "chars", "file_path", "retrieved_via", "library"):
            if new.get(key) is not None and existing.get(key) != new.get(key):
                existing[key] = new[key]
                changed = True
    # 先有网页/文件来源、后来补了全文：把 library 挂到已有记录上，不新开条目
    elif new.get("library") and not existing.get("library"):
        existing["library"] = new["library"]
        for key in ("file_path", "retrieved_via", "chars"):
            if new.get(key):
                existing[key] = new[key]
        # 旧的 file_path 指向单文件（PDF）时，body_sha256 会失效：改指文库后清掉
        if new.get("file_path"):
            existing.pop("body_sha256", None)
        if new.get("notes"):
            existing["notes"] = ((existing.get("notes") or "").rstrip("。；")
                                 + "；" + new["notes"].strip()).strip("；")
        changed = True
    for key in ("url", "doi", "publisher", "lang", "license", "retrieved_via", "year",
                "body_sha256", "chars", "notes"):
        if not existing.get(key) and new.get(key):
            existing[key] = new[key]
            changed = True
    # 标题只做「更完整」方向的替换，避免第二次 add 时用简称把长标题盖掉
    if new.get("title") and len(new["title"]) > len(existing.get("title") or ""):
        if new["title"] != existing["title"]:
            existing["title"] = new["title"]
            changed = True
    if new.get("authors") and not existing.get("authors"):
        existing["authors"] = new["authors"]
        changed = True
    seen = {(e.get("quote"), e.get("locator")) for e in existing.get("evidence", [])}
    for ev in new.get("evidence", []):
        if (ev.get("quote"), ev.get("locator")) not in seen:
            existing.setdefault("evidence", []).append(ev)
            changed = True
    merged_used = sorted(set(existing.get("used_in", [])) | set(new.get("used_in", [])))
    if merged_used != existing.get("used_in", []):
        existing["used_in"] = merged_used
        changed = True
    if new.get("accessed") and new["accessed"] > existing.get("accessed", ""):
        existing["accessed"] = new["accessed"]
        changed = True
    if not existing.get("file_path") and new.get("file_path"):
        existing["file_path"] = new["file_path"]
        changed = True
    return existing, changed


def cmd_add(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if args.json == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.json).read_text(encoding="utf-8-sig")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[sources] 清单不是合法 JSON：{exc}", file=sys.stderr)
        return 2
    records = payload.get("records") if isinstance(payload, dict) else payload
    if not isinstance(records, list) or not records:
        print("[sources] 清单必须是非空数组，或 {\"records\": [...]}", file=sys.stderr)
        return 2
    return _ingest(root, records, args.json_out)


def _ingest(root: Path, records: list, json_out: bool) -> int:
    data = load_index(root)
    _, records_dir = archive_paths(root)
    records_dir.mkdir(parents=True, exist_ok=True)
    by_key = {s.get("canonical_key"): s for s in data["sources"]}
    created, merged_ids = [], []

    for raw_rec in records:
        if not isinstance(raw_rec, dict):
            print("[sources] 清单里有非对象条目，已跳过", file=sys.stderr)
            continue
        rec = normalize_record(raw_rec, root)
        for ev in rec["evidence"]:
            if len(ev["quote"]) > MAX_QUOTE:
                print(f"[sources] 警告：{rec.get('title','?')[:40]} 有一处摘录 {len(ev['quote'])} 字，"
                      f"超过 {MAX_QUOTE} 字上限，check 会判失败（请拆成多段，只留支撑结论的那句）",
                      file=sys.stderr)
        key = rec["canonical_key"]
        hit = by_key.get(key)
        if hit is not None:
            _, changed = merge(hit, rec)
            merged_ids.append(hit["id"] + ("" if changed else "(no-op)"))
            (records_dir / f"{hit['id']}.md").write_text(render_record(hit), encoding="utf-8")
            continue
        rec["id"] = rec.get("id") or next_id(data["sources"])
        if not ID_RE.match(str(rec["id"])):
            print(f"[sources] id 格式不合法：{rec['id']}（应为 S0001）", file=sys.stderr)
            return 2
        if any(s["id"] == rec["id"] for s in data["sources"]):
            rec["id"] = next_id(data["sources"])
        data["sources"].append(rec)
        by_key[key] = rec
        (records_dir / f"{rec['id']}.md").write_text(render_record(rec), encoding="utf-8")
        created.append({"id": rec["id"], "title": rec["title"], "canonical_key": key,
                        "evidence": len(rec["evidence"])})

    data["sources"].sort(key=lambda s: int(s["id"][1:]) if ID_RE.match(str(s.get("id", ""))) else 0)
    save_index(root, data)

    if json_out:
        print(json.dumps({"created": created, "merged": merged_ids,
                          "total": len(data["sources"])}, ensure_ascii=False))
    else:
        print(f"[sources] 新增 {len(created)} 条，合并 {len(merged_ids)} 条，共 {len(data['sources'])} 条")
        for item in created:
            print(f"  + {item['id']}  {item['title'][:60]}  （摘录 {item['evidence']} 处）")
        for item in merged_ids:
            print(f"  ~ {item}")
    return 0


# ---------------------------------------------------------------- 文库（_unpublished/文库）

# 文库是本机的「全文库」：书 / 论文 / 报告 / 网页正文的抽取文本都放
# _unpublished/文库/<slug>/<分块>.txt；_unpublished/ 已被 .gitignore 排除，不进仓库、不发布。
# .sources/ 只记元数据 + 短摘录，全文一律指向这里。
LIBRARY_DEFAULT = "_unpublished/文库"
LIBRARY_PAGE_CHUNK = 200       # PDF 每 200 页切一块（与既有书目一致）
LIBRARY_TEXT_CHUNK = 200_000   # 非 PDF 文本每 20 万字符切一块

# 文库 manifest 只有文本层面的信息；书目元数据在这里补（依据文库 README，勿臆造）
LIBRARY_META: dict[str, dict] = {
    "白蚁学": {
        "authors": ["程冬保", "杨兆芬"], "year": 2014, "publisher": "科学出版社",
        "reliability": "reference", "lang": "zh",
        "notes": "中文教材，7 篇 22 章。",
    },
    "白蚁生物学现代研究合集": {
        "authors": ["黄求应 等（译）"], "publisher": "中译合集",
        "reliability": "reference", "lang": "zh",
        "notes": "原书 Biology of Termites: A Modern Synthesis（Bignell, Roisin, Lo 编）的中译合集。",
    },
    "中国动物志-昆虫纲-第十七卷-等翅目": {
        "authors": ["黄复生", "朱世模", "平正明", "何秀松", "李桂祥", "高道蓉"],
        "publisher": "科学出版社", "reliability": "primary", "lang": "zh",
        "notes": "中国等翅目分类志，物种阶元的一手依据。",
    },
    "Treatise-on-the-Isoptera": {
        "authors": ["Krishna K. et al."], "year": 2013, "publisher": "AMNH Bulletin 377",
        "reliability": "primary", "lang": "en",
        "notes": "全球等翅目总览，含文献目录与科属检索表。",
    },
    "Sands-1972-Soldierless-Termites-of-Africa": {
        "authors": ["Sands W.A."], "year": 1972,
        "publisher": "Bull. Br. Mus. Nat. Hist. (Ent.) Suppl. 18",
        "reliability": "peer_reviewed", "lang": "en",
        "notes": "非洲无兵蚁白蚁专著，9 图版、661 图。",
    },
}

LIBRARY_CAVEAT = ("文本由原书 DOCX/PDF 抽取或 OCR 而来，不是原书：拉丁学名、性别词尾、图注可能损坏，"
                  "正式引用前须核对纸本或原书 PDF。")
LIBRARY_CAVEAT_PAPER = ("文本由 PDF/XML 抽取，不是排版原貌：上标引文编号、表格、图注可能错位，"
                        "正式引用前须核对出版方原文。")

def _slugify(text: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|\r\n\t]+", "-", str(text))
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-{2,}", "-", s).strip("-.")
    return s[:80] or "untitled"


def _text_chunks(text: str, limit: int = LIBRARY_TEXT_CHUNK) -> list[tuple[str, str]]:
    limit = limit or LIBRARY_TEXT_CHUNK
    """按段落边界把长文本切成每块 <= limit 字符；短文本只有一块，名为 full。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip("\n") + "\n"
    if not text.strip():
        return []
    if len(text) <= limit:
        return [("full", text)]
    parts: list[str] = []
    buf: list[str] = []
    size = 0

    def flush() -> None:
        nonlocal buf, size
        if buf:
            parts.append("\n".join(buf) + "\n")
            buf, size = [], 0

    for line in text.split("\n"):
        line = line.rstrip()
        while len(line) > limit:
            flush()
            parts.append(line[:limit] + "\n")
            line = line[limit:]
        if size + len(line) + 1 > limit and buf:
            flush()
        buf.append(line)
        size += len(line) + 1
    flush()
    return [(f"part-{i:03d}", part) for i, part in enumerate(parts, 1)]


def _pdf_pages(path: Path) -> list[str]:
    try:
        import pymupdf as fitz  # type: ignore
    except Exception:
        try:
            import fitz  # type: ignore
        except Exception as exc:  # pragma: no cover - 取决于本机环境
            raise RuntimeError(
                "没有可用的 PDF 抽取库（pymupdf/fitz）：请先用 pdf_extract_text 抽出文本，再用 --text 传入该 txt"
            ) from exc
    doc = fitz.open(str(path))
    try:
        pages = []
        for page in doc:
            try:
                # sort=True 按坐标重排，双栏排版的阅读顺序通常更接近原文
                pages.append(page.get_text("text", sort=True).strip())
            except TypeError:  # 老版本 pymupdf 不认 sort 参数
                pages.append(page.get_text("text").strip())
        return pages
    finally:
        doc.close()


def _pdf_chunks(path: Path) -> tuple[list[tuple[str, str]], dict]:
    pages = _pdf_pages(path)
    chunks: list[tuple[str, str]] = []
    for start in range(0, len(pages), LIBRARY_PAGE_CHUNK):
        group = pages[start:start + LIBRARY_PAGE_CHUNK]
        label = f"{start + 1:04d}-{start + len(group):04d}"
        chunks.append((label, "\f".join(group).strip("\n") + "\n"))
    return chunks, {"extraction": "pdf-text", "pages": len(pages)}


def _docx_text(path: Path) -> tuple[str, dict]:
    """只用标准库读 docx：取 word/document.xml 里的段落文本。"""
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    tree = ET.fromstring(xml)
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    lines: list[str] = []
    for para in tree.iter(w + "p"):
        text = "".join(node.text or "" for node in para.iter(w + "t"))
        if text.strip():
            lines.append(text.rstrip())
    return "\n".join(lines) + "\n", {"extraction": "docx", "paragraphs": len(lines)}


class _HTMLText(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
             "section", "article", "table", "blockquote", "pre",
             # JATS/TEI 全文 XML：没有这些断行，期刊名、作者、日期会粘成一片
             "title", "sec", "caption", "fig", "table-wrap", "td", "th", "abstract",
             "ref", "kwd-group", "pub-date", "contrib", "aff", "body", "back"}
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def _markup_text(raw: str, extraction: str) -> tuple[str, dict]:
    parser = _HTMLText()
    parser.feed(raw)
    joined = "".join(parser.parts)
    lines = [re.sub(r"[ \t\u00a0]+", " ", line).strip() for line in joined.split("\n")]
    return "\n".join(line for line in lines if line) + "\n", {"extraction": extraction}


def _html_text(path: Path) -> tuple[str, dict]:
    return _markup_text(path.read_text(encoding="utf-8", errors="replace"), "html")


def _xml_text(path: Path) -> tuple[str, dict]:
    """JATS/TEI 全文 XML：先丢掉 <front>（期刊、作者、版权等元数据，已另存记录字段），再抽正文。"""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # 摘要挂在 <front>/<article-meta> 下面，丢 front 之前先捞出来放回开头
    abstracts = re.findall(r"<abstract\b[\s\S]*?</abstract>", raw)
    raw = re.sub(r"<front[ >][\s\S]*?</front>", " ", raw)
    if abstracts:
        head = "" if all("<title" in a for a in abstracts) else "<title>Abstract</title>"
        raw = "<sec>" + head + "".join(abstracts) + "</sec>" + raw
    return _markup_text(raw, "xml-text")


def _extract_chunks(path: Path, limit: int = LIBRARY_TEXT_CHUNK) -> tuple[list[tuple[str, str]], dict]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _pdf_chunks(path)
    if suffix == ".docx":
        text, info = _docx_text(path)
    elif suffix in {".xml", ".rdf"}:
        # JATS / TEI 全文 XML 要去标签：直接读原文会留下 <p>、<xref> 之类的标记
        text, info = _xml_text(path)
    elif suffix in {".html", ".htm"}:
        text, info = _html_text(path)
    elif suffix in {".txt", ".md", ".markdown", ".csv", ".tsv", ".json"}:
        text, info = path.read_text(encoding="utf-8-sig", errors="replace"), {"extraction": "text"}
    else:
        raise RuntimeError(f"不认识的文件类型 {suffix}：请先转成 txt 再用 --text 传入")
    chunks = _text_chunks(text, limit)
    info.setdefault("paragraphs", text.count("\n"))
    return chunks, info


def _library_record(root: Path, lib_dir: Path, manifest_path: Path, generated: str,
                    entry: dict) -> dict:
    """把 manifest 里的一条书目/文档变成 .sources 记录（导入与入库共用）。"""
    name = str(entry.get("book") or "").strip()
    kind = str(entry.get("kind") or "book")
    meta = dict(LIBRARY_META.get(name, {}))
    meta.update({k: v for k, v in (entry.get("meta") or {}).items() if v})
    extra_note = meta.pop("notes", "")
    reliability = meta.pop("reliability", "unverified")
    chunks = []
    for chunk in entry.get("chunks", []):
        out = str(chunk.get("out") or "").replace("\\", "/")
        if not out:
            out = rel(root, lib_dir / name / (str(chunk.get("chunk", "")) + ".txt"))
        txt = root / out
        item = {"chunk": chunk.get("chunk"), "txt": out, "chars": chunk.get("chars"),
                "paragraphs": chunk.get("paragraphs"), "table_rows": chunk.get("table_rows"),
                "source_file": chunk.get("source")}
        if txt.is_file():
            item["sha256"] = sha256_file(txt)
            item["bytes"] = txt.stat().st_size
        chunks.append(item)
    pages = entry.get("pages")
    where = rel(root, lib_dir / name)
    size = f"{pages} 页，{entry.get('chars')} 字符" if pages else f"{entry.get('chars')} 字符"
    notes = [
        f"全文存于 {where}（{size}），抽取：{entry.get('extraction') or '未知'}",
        LIBRARY_CAVEAT if kind == "book" else LIBRARY_CAVEAT_PAPER,
    ]
    if extra_note:
        notes.append(extra_note)
    notes_text = "；".join(n.rstrip("。；") for n in notes) + "。"

    rec = {
        "title": str(entry.get("title") or name),
        "source_type": kind if kind in SOURCE_TYPES else "other",
        "reliability": reliability,
        "canonical_key": entry.get("canonical_key") or "library:" + name,
        "file_path": where,
        "chars": entry.get("chars"),
        "retrieved_via": "文库（" + str(entry.get("extraction") or "抽取") + "）",
        "accessed": (generated + "+08:00") if re.match(r"^\d{4}-\d{2}-\d{2}T", str(generated or "")) else now_iso(),
        "notes": notes_text,
        "library": {"book": name, "manifest": rel(root, manifest_path),
                    "generated": generated, "chunks": chunks},
    }
    for key in ("authors", "year", "publisher", "lang", "license", "doi", "url"):
        if meta.get(key):
            rec[key] = meta[key]
    return rec



def cmd_import_library(args: argparse.Namespace) -> int:
    """把 _unpublished/文库 的书目导入为来源记录（幂等；已存在则补元数据）。"""
    root = Path(args.root).resolve()
    lib_dir = root / (args.library or LIBRARY_DEFAULT)
    manifest_path = lib_dir / "manifest.json"
    if not manifest_path.is_file():
        print(f"[sources] 找不到文库清单：{rel(root, manifest_path)}", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    generated = manifest.get("generated", "")
    records = [_library_record(root, lib_dir, manifest_path, generated, book)
               for book in manifest.get("books", []) if (book.get("book") or "").strip()]
    print(f"[sources] 从文库读到 {len(records)} 项，开始导入/更新……")
    return _ingest(root, records, args.json_out)



def cmd_library_add(args: argparse.Namespace) -> int:
    """把一篇论文 / 报告 / 网页正文的**全文**存进文库，并同步登记为来源记录。"""
    root = Path(args.root).resolve()
    lib_dir = root / (args.library or LIBRARY_DEFAULT)
    src = Path(args.file).expanduser()
    if not src.is_absolute():
        src = Path.cwd() / src
    src = src.resolve()
    if not src.is_file():
        print(f"[sources] 找不到文件：{src}", file=sys.stderr)
        return 2

    title = (args.title or src.stem).strip()
    slug = _slugify(args.slug or title)
    doc_dir = lib_dir / slug
    try:
        if args.text:
            text = Path(args.text).expanduser().resolve().read_text(encoding="utf-8-sig", errors="replace")
            chunks, info = _text_chunks(text, args.chunk_chars), {"extraction": "外部文本（--text）"}
        else:
            chunks, info = _extract_chunks(src, args.chunk_chars)
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        print(f"[sources] 抽取失败：{exc}", file=sys.stderr)
        return 2
    total = sum(len(text) for _, text in chunks)
    if total < 200:
        print("[sources] 警告：抽出的文本几乎是空的（扫描件？）。请先用 pdf_extract_text 或 OCR 得到文本，"
              "再用 --text 入库", file=sys.stderr)

    doc_dir.mkdir(parents=True, exist_ok=True)
    copied: Path | None = None
    if not args.no_copy and not str(src).lower().startswith(str(lib_dir).lower()):
        copied = doc_dir / "source" / src.name
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, copied)

    src_sha = sha256_file(src)
    src_bytes = src.stat().st_size
    chunk_records = []
    for label, text in chunks:
        out = doc_dir / f"{label}.txt"
        out.write_text(text, encoding="utf-8", newline="\n")
        chunk_records.append({
            "chunk": label, "source": str(src), "bytes": src_bytes, "sha256": src_sha,
            "paragraphs": text.count("\n"), "table_rows": 0, "chars": len(text),
            "out": rel(root, out),
        })
    # 重新入库（例如 PDF 换成 XML）时，旧的分卷文件要清掉，否则库里留双份
    keep = {label for label, _ in chunks}
    for old in doc_dir.glob("*.txt"):
        if old.stem not in keep:
            old.unlink()

    manifest_path = lib_dir / "manifest.json"
    manifest = (json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                if manifest_path.is_file() else {"books": []})
    generated = datetime.now().isoformat(timespec="seconds")
    doi = (args.doi or "").strip()
    url = (args.url or "").strip()
    authors = [a.strip() for a in re.split(r"[;；]", args.authors or "") if a.strip()]
    meta = {key: value for key, value in {
        "authors": authors,
        "year": args.year,
        "publisher": args.publisher,
        "lang": args.lang,
        "license": args.license,
        "doi": doi or None,
        "url": url or None,
        "reliability": args.reliability,
    }.items() if value}
    entry = {
        "book": slug,
        "kind": args.kind,
        "title": title,
        "chars": total,
        "canonical_key": (
            "doi:" + doi.lower().replace("https://doi.org/", "").replace("http://doi.org/", "")
            if doi else ("url:" + normalize_url(url) if url else "library:" + slug)
        ),
        "meta": meta,
        "source_file": rel(root, copied) if copied else str(src),
        "source_sha256": src_sha,
        "source_bytes": src_bytes,
        "extraction": info.get("extraction"),
        "pages": info.get("pages"),
        "chunks": chunk_records,
    }
    manifest["generated"] = generated
    manifest.setdefault("out_root", str(lib_dir))
    manifest["books"] = [b for b in manifest.get("books", []) if b.get("book") != slug] + [entry]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rec = _library_record(root, lib_dir, manifest_path, generated, entry)
    if args.notes:
        rec["notes"] = rec["notes"].rstrip("。") + "；" + args.notes.strip().rstrip("。") + "。"
    rec["used_in"] = list(args.used_in or [])
    if args.reliability == "unverified":
        print("[sources] 提示：可靠性记为 unverified；确认来源等级后用 add 覆盖", file=sys.stderr)
    print(f"[sources] 入库 {rel(root, doc_dir)}（{len(chunks)} 块，{total} 字符）")
    return _ingest(root, [rec], args.json_out)


def iter_text_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            path = Path(dirpath) / name
            if name in META_FILES:
                continue
            if path.suffix.lower() in TEXT_SUFFIXES and path.is_file():
                try:
                    if path.stat().st_size > 2_000_000:
                        continue
                except OSError:
                    continue
                yield path


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    data = load_index(root)
    sources = data["sources"]
    _, records_dir = archive_paths(root)

    ids, keys = {}, {}
    for rec in sources:
        sid = str(rec.get("id", ""))
        label = f"{sid or '<无 id>'} {str(rec.get('title', ''))[:40]}"
        if not ID_RE.match(sid):
            errors.append(f"[E003] {label}: id 不是 S0001 形式")
        elif sid in ids:
            errors.append(f"[E002] {label}: id 重复（{sid}）")
        ids[sid] = rec

        for field in REQUIRED:
            if not rec.get(field) and field != "accessed":
                errors.append(f"[E004] {label}: 缺少必填字段 {field}")
        if rec.get("source_type") not in SOURCE_TYPES:
            errors.append(f"[E005] {label}: source_type 不在枚举里：{rec.get('source_type')!r}")
        if rec.get("reliability") not in RELIABILITY:
            errors.append(f"[E005] {label}: reliability 不在枚举里：{rec.get('reliability')!r}")
        if rec.get("accessed") and not re.match(r"^\d{4}-\d{2}-\d{2}", str(rec["accessed"])):
            warnings.append(f"[W004] {label}: accessed 不是 ISO 日期：{rec['accessed']!r}")

        key = rec.get("canonical_key")
        if key:
            if key in keys:
                errors.append(f"[E006] {label}: canonical_key 与 {keys[key]} 重复（{key}）")
            keys[key] = sid

        for ev in rec.get("evidence") or []:
            quote = (ev.get("quote") or "").strip()
            if not quote:
                warnings.append(f"[W002] {label}: 有空的摘录条目")
            elif len(quote) > MAX_QUOTE:
                errors.append(f"[E007] {label}: 摘录 {len(quote)} 字，超过 {MAX_QUOTE} 字上限")
            if quote and not (ev.get("locator") or "").strip():
                warnings.append(f"[W002] {label}: 摘录缺少 locator（页码/段落/标题）")
        if rec.get("used_in") and not rec.get("evidence"):
            warnings.append(f"[W003] {label}: 被引用但没有摘录，无法核查")
        if not rec.get("evidence") and not rec.get("notes"):
            warnings.append(f"[W003] {label}: 既无摘录也无 notes")

        for target in rec.get("used_in") or []:
            target = str(target)
            if os.path.isabs(target) or target.startswith("../"):
                errors.append(f"[E008] {label}: used_in 必须是仓库内相对路径：{target}")
                continue
            if not (root / target).exists():
                warnings.append(f"[W001] {label}: used_in 指向的文件不存在：{target}")

        for chunk in (rec.get("library") or {}).get("chunks", []):
            if chunk.get("sha256") and chunk.get("txt"):
                fp = root / str(chunk["txt"])
                if fp.is_file() and sha256_file(fp) != chunk["sha256"]:
                    warnings.append(f"[W006] {label}: 分卷文本已变（sha256 不符）：{chunk['txt']}")

        if rec.get("file_path") and rec.get("body_sha256"):
            fp = root / str(rec["file_path"])
            if fp.is_file() and sha256_file(fp) != rec["body_sha256"]:
                warnings.append(f"[W005] {label}: 本地文件内容已变（sha256 不符），摘录可能过期：{rec['file_path']}")

        md = records_dir / f"{sid}.md"
        if not md.is_file() or md.stat().st_size == 0:
            errors.append(f"[E009] {label}: 缺少记录文件 {ARCHIVE_DIR}/{RECORDS_DIR}/{sid}.md")

    # 正文里的 <!-- src:S0001 --> 标记必须能解析
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in MARKER_RE.finditer(text):
            sid = match.group(1)
            if sid not in ids:
                errors.append(f"[E010] {rel(root, path)}: 引用了未存档的来源 {sid}")
                break

    strict = args.strict
    if strict:
        promote = ("[W002]", "[W003]", "[W005]", "[W006]")
        errors.extend(w.replace("[W", "[E-W", 1) for w in warnings if w.startswith(promote))
        warnings = [w for w in warnings if not w.startswith(promote)]

    if args.json_out:
        print(json.dumps({"sources": len(sources), "errors": errors, "warnings": warnings,
                          "strict": strict, "ok": not errors}, ensure_ascii=False, indent=2))
    else:
        print(f"[sources] 已存档来源 {len(sources)} 条；错误 {len(errors)}，提示 {len(warnings)}")
        for line in errors:
            print("  " + line)
        for line in warnings:
            print("  " + line)
        if not errors:
            print("  OK")
    return 1 if errors else 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    sources = load_index(root)["sources"]
    if args.json_out:
        print(json.dumps(sources, ensure_ascii=False, indent=2))
        return 0
    shown = sources[-args.limit:] if args.limit else sources
    for rec in shown:
        used = len(rec.get("used_in") or [])
        ev = len(rec.get("evidence") or [])
        print(f"{rec['id']}  {rec.get('reliability','?'):<14} {str(rec.get('year','')):<6} "
              f"{str(rec.get('title',''))[:70]}  [摘录 {ev} / 用于 {used}]")
    print(f"共 {len(sources)} 条")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    sources = load_index(root)["sources"]
    by_rel: dict[str, int] = {}
    by_type: dict[str, int] = {}
    used = 0
    for rec in sources:
        by_rel[rec.get("reliability", "?")] = by_rel.get(rec.get("reliability", "?"), 0) + 1
        by_type[rec.get("source_type", "?")] = by_type.get(rec.get("source_type", "?"), 0) + 1
        used += 1 if rec.get("used_in") else 0
    print(f"总量 {len(sources)}；支撑过结论 {used}")
    print("按可靠性：" + "，".join(f"{k} {v}" for k, v in sorted(by_rel.items())))
    print("按类型：" + "，".join(f"{k} {v}" for k, v in sorted(by_type.items())))
    return 0


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="来源存档工具（见 AGENTS.md / .sources/README.md）")
    parser.add_argument("--root", default=".", help="仓库根目录，默认当前目录")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="新增或合并来源记录")
    p_add.add_argument("--json", required=True, help="清单 JSON 路径，- 表示 stdin")
    p_add.add_argument("--json-out", action="store_true", help="输出机器可读结果")
    p_add.set_defaults(func=cmd_add)

    p_check = sub.add_parser("check", help="校验存档（只读）")
    p_check.add_argument("--strict", action="store_true", help="摘录/notes 缺失也判失败")
    p_check.add_argument("--ci", action="store_true", help="CI 模式（同默认校验）")
    p_check.add_argument("--json-out", action="store_true", help="输出机器可读结果")
    p_check.set_defaults(func=cmd_check)

    p_list = sub.add_parser("list", help="列出已存档来源")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--json-out", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_lib = sub.add_parser("import-library", help="把 _unpublished/文库 的书目导入为来源记录（幂等）")
    p_lib.add_argument("--library", default=LIBRARY_DEFAULT, help="文库目录，默认 _unpublished/文库")
    p_lib.add_argument("--json-out", action="store_true", help="输出机器可读结果")
    p_lib.set_defaults(func=cmd_import_library)

    p_ladd = sub.add_parser("library-add", help="把论文/报告/网页正文的全文存进 _unpublished/文库 并登记来源")
    p_ladd.add_argument("--file", required=True, help="原始文件（pdf / docx / html / txt / md）")
    p_ladd.add_argument("--text", help="已抽好的纯文本；PDF 无文字层时用它")
    p_ladd.add_argument("--title")
    p_ladd.add_argument("--slug", help="文库子目录名，默认由标题生成")
    p_ladd.add_argument("--kind", default="paper",
                        choices=["paper", "book", "report", "web", "dataset", "other"])
    p_ladd.add_argument("--reliability", default="unverified", choices=sorted(RELIABILITY))
    p_ladd.add_argument("--authors", help="分号分隔")
    p_ladd.add_argument("--year", type=int)
    p_ladd.add_argument("--publisher")
    p_ladd.add_argument("--lang")
    p_ladd.add_argument("--license")
    p_ladd.add_argument("--doi")
    p_ladd.add_argument("--url")
    p_ladd.add_argument("--notes")
    p_ladd.add_argument("--used-in", dest="used_in", action="append", default=[])
    p_ladd.add_argument("--chunk-chars", dest="chunk_chars", type=int, default=LIBRARY_TEXT_CHUNK)
    p_ladd.add_argument("--no-copy", dest="no_copy", action="store_true", help="不复制原始 PDF/文件")
    p_ladd.add_argument("--library", default=LIBRARY_DEFAULT)
    p_ladd.add_argument("--json-out", action="store_true")
    p_ladd.set_defaults(func=cmd_library_add)

    p_stats = sub.add_parser("stats", help="汇总")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
