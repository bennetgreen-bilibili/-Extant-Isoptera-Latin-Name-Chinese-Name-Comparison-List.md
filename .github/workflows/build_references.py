#!/usr/bin/env python3
"""文献增强（feature 5）：从名录单文件解析 77 条参考文献，用 Crossref 补全元数据，
生成站点用 _data/references.json 与公开下载副本 data/references.json。

输入（只读，不改动）：
  名录单文件 *Latin Name * Chinese Name Comparison List.md 的 "## 参考文献" 区块
  （解析规则与 .github/workflows/build_dataset.py 的 load_references() 完全一致：
    3 级以内编号行 + 续行合并、10.xxxx/… 的 DOI 正则、SICI 型 DOI 的 ";2" 补全）

输出（确定性，重复运行零改动）：
  _data/references.json   站点模板用（Liquid: site.data.references）
  data/references.json    公开下载副本（字节完全相同）

Crossref：https://api.crossref.org/works/<doi>（带 mailto + 描述性 User-Agent）
  约 2 req/s；429/5xx 指数退避；_tmp/references-cache.json 断点续跑，命中缓存不再联网。

用法：
  python .github/workflows/build_references.py             # 只统计，不写文件（会用缓存）
  python .github/workflows/build_references.py --write     # 写入两个 JSON
  python .github/workflows/build_references.py --check     # 校验仓库内 JSON 与生成结果一致
  python .github/workflows/build_references.py --write --bhl       # 额外补 BHL 原始描述
  python .github/workflows/build_references.py --write --offline   # 只用缓存，不联网
  python .github/workflows/build_references.py --write --time-budget 120

环境变量：
  CROSSREF_MAILTO   Crossref 礼仪要求的联系邮箱（默认本仓库 GitHub noreply 地址）
  BHL_API_KEY       BHL（Biodiversity Heritage Library）免费 API key；缺失时 --bhl 自动降级

许可：Crossref 元数据为事实性数据（Crossref 服务条款允许再利用）；BHL 页面内容版权归原藏馆，
本脚本只保存书目级元数据与链接，不下载扫描件。
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
LIST_MD_PATTERN = "*Latin Name * Chinese Name Comparison List.md"
DATA_OUT = ROOT / "_data" / "references.json"
PUBLIC_OUT = ROOT / "data" / "references.json"
CACHE_PATH = ROOT / "_tmp" / "references-cache.json"

PROJECT_URL = "https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/"
CROSSREF_MAILTO = os.environ.get("CROSSREF_MAILTO", "bennetgreen-bilibili@users.noreply.github.com")
USER_AGENT = (
    "extant-isoptera-checklist-references/1.0 "
    f"(+{PROJECT_URL}; mailto:{CROSSREF_MAILTO}) Python-urllib"
)
CROSSREF_API = "https://api.crossref.org/works"
BHL_API = "https://www.biodiversitylibrary.org/api3"

RATE_LIMIT_SECONDS = 0.5          # ≈2 req/s，对公共 API 友好
MAX_ATTEMPTS = 4
AUTO_MATCH_SIMILARITY = 0.90      # 自动匹配阈值（归一化标题相似度）
CANDIDATE_MIN_SIMILARITY = 0.55   # 低于此值的查询结果不入候选清单


# ---------------------------------------------------------------- 解析参考文献

def load_references() -> list:
    """与 build_dataset.py 的 load_references() 逐行等价的解析（勿改 list.md）。"""
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


# ---------------------------------------------------------------- 小工具

def clean_text(value) -> str:
    """去 HTML/JATS 标签、解实体、折叠空白。Crossref 标题里常有 <i>、<sub> 与 &amp;。"""
    if value is None:
        return ""
    if isinstance(value, list):
        value = value[0] if value else ""
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def ascii_fold(text: str) -> str:
    """去变音符号并小写，用于相似度与 BibTeX key。"""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.casefold()


def norm_title(text: str) -> str:
    text = ascii_fold(clean_text(text))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    na, nb = norm_title(a), norm_title(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    ratio = SequenceMatcher(None, na, nb).ratio()
    # 短标题（如 "Termites"）用包含关系兜底，避免比例虚高
    if na in nb or nb in na:
        ratio = max(ratio, min(len(na), len(nb)) / max(len(na), len(nb)) * 0.95)
    return round(ratio, 4)


def match_similarity(citation: str, title: str) -> float:
    """候选标题与整条引用文本的匹配度。

    标题只占引用的一小段，纯字符比例会被作者/刊名/页码稀释，因此取两者较大值：
      ① 归一化字符相似度；
      ② 候选标题的词被引用文本覆盖的比例（候选标题 ≥ 5 个词时才用，避免短标题误配）。
    """
    if not title:
        return 0.0
    char_ratio = SequenceMatcher(None, norm_title(citation), norm_title(title)).ratio()
    tokens = [t for t in norm_title(title).split() if t]
    if len(tokens) < 5:
        return round(char_ratio, 4)
    haystack = set(norm_title(citation).split())
    overlap = sum(1 for t in tokens if t in haystack) / len(tokens)
    return round(max(char_ratio, overlap), 4)


def citation_year(text: str) -> str:
    m = re.search(r"\b(1[5-9]\d{2}|20[0-3]\d)\b", text)
    return m.group(1) if m else ""


def doi_url(doi: str) -> str:
    return "https://doi.org/" + quote(doi, safe="/:;()") if doi else ""


def crossref_url(doi: str) -> str:
    return CROSSREF_API + "/" + quote(doi, safe="/:;()") if doi else ""


def search_url(text: str) -> str:
    return "https://search.crossref.org/?q=" + quote(text[:400], safe="")


# ---------------------------------------------------------------- Crossref 抓取

class Fetcher:
    def __init__(self, cache_path: Path, offline: bool = False, budget: float = 0.0, log=print):
        self.path = cache_path
        self.offline = offline
        self.budget = budget
        self.started = time.monotonic()
        self.log = log
        self.cache = {}
        self.network_calls = 0
        self.from_cache = 0
        self.last_call = 0.0
        self.budget_exceeded = False
        if cache_path.exists():
            try:
                self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:  # 缓存损坏 → 重新抓取
                self.log(f"warn: 缓存不可读（{exc}），将重新联网获取")
                self.cache = {}

    # -- 缓存持久化（每次新增后立即落盘，进程被中断也能续跑）
    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.part")
        tmp.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1, sort_keys=True),
                       encoding="utf-8", newline="\n")
        tmp.replace(self.path)

    def get(self, url: str):
        """返回 (status, payload)。status < 0 表示网络层失败。"""
        key = url
        cached = self.cache.get(key)
        if cached is not None:
            self.from_cache += 1
            return cached.get("status", -1), cached.get("data")
        if self.offline:
            return -2, None
        if self.budget and (time.monotonic() - self.started) > self.budget:
            self.budget_exceeded = True
            return -3, None

        self._throttle()
        status, data = self._fetch(url)
        self.cache[key] = {"status": status, "data": data}
        self.save()
        return status, data

    def _throttle(self) -> None:
        wait = RATE_LIMIT_SECONDS - (time.monotonic() - self.last_call)
        if wait > 0:
            time.sleep(wait)
        self.last_call = time.monotonic()

    def _fetch(self, url: str):
        delay = 1.0
        for attempt in range(1, MAX_ATTEMPTS + 1):
            req = Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Accept-Encoding": "identity",
            })
            try:
                with urlopen(req, timeout=45) as resp:
                    self.network_calls += 1
                    raw = resp.read()
                    if not raw.strip():
                        # 空 2xx（BHL 无 key 时就是这样）不是网络错误，不重试
                        return resp.status, None
                    try:
                        return resp.status, json.loads(raw.decode("utf-8", "replace"))
                    except ValueError:
                        return resp.status, None
            except HTTPError as exc:
                self.network_calls += 1
                body = ""
                try:
                    body = exc.read().decode("utf-8", "replace")[:200]
                except Exception:  # noqa: BLE001 - 仅用于日志
                    pass
                if exc.code in (429, 500, 502, 503, 504) and attempt < MAX_ATTEMPTS:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    sleep_for = float(retry_after) if (retry_after or "").isdigit() else delay
                    self.log(f"warn: HTTP {exc.code}，{sleep_for:.0f}s 后重试（{attempt}/{MAX_ATTEMPTS}）")
                    time.sleep(sleep_for)
                    delay = min(delay * 2, 30)
                    continue
                if exc.code == 404:
                    return 404, None
                self.log(f"warn: HTTP {exc.code} - {url}{(' ' + body) if body else ''}")
                return exc.code, None
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                self.network_calls += 1
                if attempt < MAX_ATTEMPTS:
                    self.log(f"warn: 网络错误 {exc}，{delay:.0f}s 后重试（{attempt}/{MAX_ATTEMPTS}）")
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                self.log(f"warn: 网络错误 {exc} - {url}")
                return -1, None
        return -1, None


# ---------------------------------------------------------------- Crossref 元数据

def tidy_name(value: str) -> str:
    """仅把「整串全大写」的姓名还原为首字母大写（Crossref 少数记录的录入习惯），
    大小写混合的原样保留，不做任何改写或翻译。"""
    text = clean_text(value)
    if not text or not re.search(r"[A-Z]", text) or re.search(r"[a-z]", text):
        return text
    words = []
    for word in text.split():
        words.append("-".join(part[:1].upper() + part[1:].lower() for part in word.split("-")))
    return " ".join(words)


def date_parts(value):
    parts = (value or {}).get("date-parts") or []
    parts = parts[0] if parts and isinstance(parts[0], list) else []
    return [int(p) for p in parts if isinstance(p, int)]


def summarize_crossref(msg: dict) -> dict:
    """只保留事实字段；缺失一律空串/空数组，绝不填充猜测值。"""
    issued = msg.get("issued") or msg.get("published") or {}
    parts = date_parts(issued)
    # 年卷期以纸本/定稿日期为准（issued 常是 online-first，会比卷期年份早一年）
    published = date_parts(msg.get("published-print")) or date_parts(msg.get("published")) or parts
    authors = []
    for author in msg.get("author") or []:
        entry = {}
        if author.get("family") or author.get("given"):
            entry["family"] = tidy_name(author.get("family"))
            raw_given = clean_text(author.get("given"))
            # 纯大写 2–4 字母（JAL / DH）是缩写，保留原样，交给 initials() 拆字
            entry["given"] = raw_given if re.fullmatch(r"[A-Z]{2,4}", raw_given) else tidy_name(raw_given)
        if author.get("name"):
            entry["name"] = tidy_name(author.get("name"))
        if entry:
            authors.append(entry)
    return {
        "doi": (msg.get("DOI") or "").strip(),
        "title": clean_text(msg.get("title")),
        "authors": authors,
        "container_title": clean_text(msg.get("container-title")),
        "volume": clean_text(msg.get("volume")),
        "issue": clean_text(msg.get("issue")),
        "page": clean_text(msg.get("page")),
        "article_number": clean_text(msg.get("article-number")),
        "issued_parts": parts,
        "published_parts": published,
        "publisher": clean_text(msg.get("publisher")),
        "type": clean_text(msg.get("type")),
        "issn": [clean_text(i) for i in (msg.get("ISSN") or []) if clean_text(i)],
        "url": clean_text(msg.get("URL")),
        "is_referenced_by_count": int(msg.get("is-referenced-by-count") or 0),
        "language": clean_text(msg.get("language")),
    }


def crossref_by_doi(fetcher: Fetcher, doi: str):
    url = f"{CROSSREF_API}/{quote(doi, safe='/:;()')}?mailto={quote(CROSSREF_MAILTO, safe='')}"
    status, payload = fetcher.get(url)
    if status == 200 and isinstance(payload, dict) and payload.get("message"):
        return summarize_crossref(payload["message"]), 200
    return None, status


def crossref_search(fetcher: Fetcher, citation: str, year: str) -> list:
    query = urlencode({
        "query.bibliographic": citation[:400],
        "rows": 3,
        "mailto": CROSSREF_MAILTO,
    })
    url = f"{CROSSREF_API}?{query}"
    status, payload = fetcher.get(url)
    if status != 200 or not isinstance(payload, dict):
        return []
    items = (payload.get("message") or {}).get("items") or []
    proposals = []
    for item in items:
        msg = summarize_crossref(item)
        doi = msg["doi"]
        if not doi:
            continue
        title = msg["title"] or ""
        sim = match_similarity(citation, title)
        item_year = str(msg["issued_parts"][0]) if msg["issued_parts"] else ""
        year_match = bool(year and item_year and year == item_year)
        proposals.append({
            "doi": doi,
            "title": title,
            "container_title": msg["container_title"],
            "year": item_year,
            "type": msg["type"],
            "similarity": sim,
            "year_match": year_match,
            "links": {"doi": doi_url(doi), "crossref": crossref_url(doi)},
        })
    proposals.sort(key=lambda p: (-p["similarity"], p["doi"]))
    return [p for p in proposals if p["similarity"] >= CANDIDATE_MIN_SIMILARITY]


def pick_auto_match(proposals: list):
    """高置信度自动匹配：标题相似度 ≥ 0.9 且年份一致；否则只留候选待人工核对。"""
    for proposal in proposals:
        if proposal["similarity"] >= AUTO_MATCH_SIMILARITY and proposal["year_match"]:
            return proposal
    return None


# ---------------------------------------------------------------- 引用格式化

TYPE_MARKER = {
    "journal-article": "J",
    "book": "M",
    "monograph": "M",
    "edited-book": "M",
    "reference-book": "M",
    "book-chapter": "M",
    "reference-entry": "M",
    "proceedings-article": "C",
    "dissertation": "D",
    "report": "R",
    "dataset": "DS",
    "posted-content": "Z",
    "standard": "S",
    "other": "Z",
}
CSL_TYPE = {
    "journal-article": "article-journal",
    "book": "book",
    "monograph": "book",
    "edited-book": "book",
    "reference-book": "book",
    "book-chapter": "chapter",
    "reference-entry": "chapter",
    "proceedings-article": "paper-conference",
    "dissertation": "thesis",
    "report": "report",
    "dataset": "dataset",
    "posted-content": "article",
}
BIBTEX_TYPE = {
    "journal-article": "article",
    "book": "book",
    "monograph": "book",
    "edited-book": "book",
    "reference-book": "book",
    "book-chapter": "incollection",
    "reference-entry": "incollection",
    "proceedings-article": "inproceedings",
    "dissertation": "phdthesis",
    "report": "techreport",
    "dataset": "misc",
    "posted-content": "unpublished",
}
RIS_TYPE = {
    "journal-article": "JOUR",
    "book": "BOOK",
    "monograph": "BOOK",
    "edited-book": "BOOK",
    "reference-book": "BOOK",
    "book-chapter": "CHAP",
    "reference-entry": "CHAP",
    "proceedings-article": "CONF",
    "dissertation": "THES",
    "report": "RPRT",
    "dataset": "DATA",
    "posted-content": "UNPB",
}


def initials(given: str, dots: bool = False, spaced: bool = False) -> str:
    """"Jean-Luc" → "JL"；dots=True 得 "J. L."（APA），spaced 控制是否加空格。"""
    if not given:
        return ""
    words = [part for part in re.split(r"[\s\-.]+", given) if part and part[0].isalpha()]
    # Crossref 里偶见把缩写直接连写（given = "JAL"）：整体当首字母串处理
    if len(words) == 1 and words[0].isupper() and len(words[0]) <= 4:
        letters = list(words[0])
    else:
        letters = [part[0] for part in words]
    if dots:
        return (" " if spaced else "").join(f"{letter}." for letter in letters)
    return (" " if spaced else "").join(letters)


def author_label(author: dict) -> str:
    if author.get("name"):
        return author["name"]
    family = author.get("family", "")
    given = author.get("given", "")
    return f"{family}, {given}" if family and given else (family or given)


def gbt_authors(authors: list) -> str:
    """GB/T 7714-2015：姓 + 名首字母，>3 人取前 3 加 et al.。"""
    names = []
    for author in authors:
        if author.get("name"):
            names.append(author["name"])
            continue
        family, given = author.get("family", ""), author.get("given", "")
        label = f"{family} {initials(given)}".strip() if family else given
        if label:
            names.append(label)
    if not names:
        return ""
    if len(names) > 3:
        return ", ".join(names[:3]) + ", et al"
    return ", ".join(names)


def apa_authors(authors: list) -> str:
    """APA 7：Family, G. G.（≤20 人全列；≥21 人前 19 … 末位）。"""
    names = []
    for author in authors:
        if author.get("name"):
            names.append(author["name"])
            continue
        family, given = author.get("family", ""), author.get("given", "")
        label = f"{family}, {initials(given, dots=True, spaced=True)}".strip(", ") if family else given
        if label:
            names.append(label)
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:19]) + ", … " + names[-1]


def vancouver_authors(authors: list) -> str:
    """Vancouver（ICMJE）：姓 + 名首字母无句点，>6 人取前 6 加 et al.。"""
    names = []
    for author in authors:
        if author.get("name"):
            names.append(author["name"])
            continue
        family, given = author.get("family", ""), author.get("given", "")
        label = f"{family} {initials(given)}".strip() if family else given
        if label:
            names.append(label)
    if not names:
        return ""
    if len(names) > 6:
        return ", ".join(names[:6]) + ", et al"
    return ", ".join(names)


def ref_year(crossref: dict) -> str:
    parts = crossref.get("published_parts") or crossref.get("issued_parts") or []
    return str(parts[0]) if parts else ""


def format_gbt(crossref: dict, doi: str) -> str:
    marker = TYPE_MARKER.get(crossref.get("type", ""), "J")
    authors = gbt_authors(crossref.get("authors") or [])
    title = crossref.get("title") or ""
    head = ". ".join(part for part in (authors, f"{title}[{marker}]" if title else "") if part)
    segments = []
    venue = crossref.get("container_title") or ""
    year = ref_year(crossref)
    volume = crossref.get("volume") or ""
    issue = crossref.get("issue") or ""
    pages = crossref.get("page") or crossref.get("article_number") or ""
    if venue:
        segments.append(venue)
    if year:
        segments.append(year)
    if volume:
        segments.append(f"{volume}({issue})" if issue else volume)
    elif issue:
        segments.append(f"({issue})")
    text = head + ("." if head else "")
    if segments:
        text += " " + ", ".join(segments)
    if pages:
        text += f": {pages}"
    text = text.strip()
    if text and not text.endswith("."):
        text += "."
    if doi:
        text += f" doi: {doi}."
    return text


MONOGRAPH_TYPES = {
    "book", "monograph", "edited-book", "reference-book", "book-chapter",
    "reference-entry", "report", "dataset", "dissertation", "standard",
}

def apa_pages(page: str) -> str:
    """APA 的页码范围用连接号（en dash）：406-421 → 406–421。"""
    return re.sub(r"^(\S*\d)-(\S*\d)$", lambda m: f"{m.group(1)}–{m.group(2)}", page or "")


def format_apa(crossref: dict, doi: str) -> str:
    authors = apa_authors(crossref.get("authors") or [])
    year = ref_year(crossref)
    title = crossref.get("title") or ""
    venue = crossref.get("container_title") or ""
    volume = crossref.get("volume") or ""
    issue = crossref.get("issue") or ""
    pages = crossref.get("page") or crossref.get("article_number") or ""
    prefix = authors
    if year:
        prefix += f" ({year})."
    elif authors:
        prefix += "."
    text = prefix
    if title:
        text += (" " if prefix else "") + (title if title.endswith((".", "?", "!")) else title + ".")
    segment = ""
    if venue:
        segment = venue
        if volume:
            segment += f", {volume}"
        if issue:
            segment += f"({issue})"
    elif volume:
        segment = f"{volume}({issue})" if issue else volume
    elif issue:
        segment = f"({issue})"
    if pages:
        segment = f"{segment}, {apa_pages(pages)}" if segment else apa_pages(pages)
    if segment:
        text += f" {segment}."
    if crossref.get("publisher") and crossref.get("type") in MONOGRAPH_TYPES:
        text += f" {crossref['publisher']}."
    if doi:
        text += f" https://doi.org/{doi}"
    return re.sub(r"\s+", " ", text).strip()


def format_vancouver(crossref: dict, doi: str) -> str:
    authors = vancouver_authors(crossref.get("authors") or [])
    title = crossref.get("title") or ""
    venue = crossref.get("container_title") or ""
    year = ref_year(crossref)
    volume = crossref.get("volume") or ""
    issue = crossref.get("issue") or ""
    pages = crossref.get("page") or crossref.get("article_number") or ""
    text = ""
    if authors:
        text += authors + ". "
    if title:
        text += title.rstrip(".") + ". "
    if venue:
        text += venue + ". "
    if year:
        text += year
        if volume:
            text += f";{volume}"
            if issue:
                text += f"({issue})"
        if pages:
            text += f":{pages}"
        text += "."
    elif pages:
        text += pages + "."
    if doi:
        text += f" doi: {doi}."
    return re.sub(r"\s+", " ", text).strip()


def bibtex_key(crossref: dict, ref_id: int) -> str:
    family = ""
    for author in crossref.get("authors") or []:
        if author.get("family"):
            family = author["family"]
            break
        if author.get("name"):
            family = author["name"].split()[0]
            break
    year = ref_year(crossref)
    word = ""
    for token in norm_title(crossref.get("title") or "").split():
        if len(token) > 3:
            word = token
            break
    key = re.sub(r"[^a-z0-9]", "", ascii_fold(f"{family}{year}{word}"))
    if not key:
        return f"ref{ref_id}"
    return key if key[0].isalpha() else f"ref{key}"


def format_bibtex(crossref: dict, ref_id: int, doi: str) -> str:
    entry_type = BIBTEX_TYPE.get(crossref.get("type", ""), "misc")
    fields = []
    authors = crossref.get("authors") or []
    if authors:
        parts = []
        for author in authors:
            if author.get("name"):
                parts.append("{" + author["name"] + "}")
            elif author.get("family"):
                parts.append(f"{author['family']}, {author.get('given','')}".strip(", "))
        if parts:
            fields.append(("author", " and ".join(parts)))
    if crossref.get("title"):
        fields.append(("title", "{" + crossref["title"] + "}"))
    venue_key = "journal" if entry_type == "article" else (
        "booktitle" if entry_type in ("incollection", "inproceedings") else "howpublished")
    if crossref.get("container_title"):
        fields.append((venue_key, crossref["container_title"]))
    if ref_year(crossref):
        fields.append(("year", ref_year(crossref)))
    if crossref.get("volume"):
        fields.append(("volume", crossref["volume"]))
    if crossref.get("issue"):
        fields.append(("number", crossref["issue"]))
    if crossref.get("page"):
        fields.append(("pages", crossref["page"].replace("-", "--")))
    if crossref.get("publisher"):
        fields.append(("publisher", crossref["publisher"]))
    if doi:
        fields.append(("doi", doi))
        fields.append(("url", doi_url(doi)))
    elif crossref.get("url"):
        fields.append(("url", crossref["url"]))
    if crossref.get("issn"):
        fields.append(("issn", crossref["issn"][0]))
    body = ",\n".join(f"  {name} = {{{value}}}" for name, value in fields)
    return f"@{entry_type}{{{bibtex_key(crossref, ref_id)},\n{body}\n}}"


def format_bibtex_fallback(ref_id: int, citation: str, doi: str) -> str:
    fields = [f"  note = {{{citation}}}"]
    if doi:
        fields.append(f"  doi = {{{doi}}}")
        fields.append(f"  url = {{{doi_url(doi)}}}")
    return "@misc{ref%d,\n%s\n}" % (ref_id, ",\n".join(fields))


def split_pages(page: str):
    m = re.match(r"^\s*([A-Za-z]?\d+)\s*[-–—]\s*([A-Za-z]?\d+)\s*$", page or "")
    if m:
        return m.group(1), m.group(2)
    return (page or ""), ""


def format_ris(crossref: dict, doi: str) -> str:
    entry_type = RIS_TYPE.get(crossref.get("type", ""), "GEN")
    lines = [f"TY  - {entry_type}"]
    if crossref.get("title"):
        lines.append(f"TI  - {crossref['title']}")
    for author in crossref.get("authors") or []:
        lines.append(f"AU  - {author_label(author)}")
    if crossref.get("container_title"):
        lines.append(("T2  - " if entry_type in ("CHAP", "CONF") else "JO  - ") + crossref["container_title"])
    if ref_year(crossref):
        lines.append(f"PY  - {ref_year(crossref)}")
    if crossref.get("volume"):
        lines.append(f"VL  - {crossref['volume']}")
    if crossref.get("issue"):
        lines.append(f"IS  - {crossref['issue']}")
    start, end = split_pages(crossref.get("page") or "")
    if start:
        lines.append(f"SP  - {start}")
    if end:
        lines.append(f"EP  - {end}")
    if crossref.get("publisher"):
        lines.append(f"PB  - {crossref['publisher']}")
    if crossref.get("issn"):
        lines.append(f"SN  - {crossref['issn'][0]}")
    if doi:
        lines.append(f"DO  - {doi}")
        lines.append(f"UR  - {doi_url(doi)}")
    elif crossref.get("url"):
        lines.append(f"UR  - {crossref['url']}")
    lines.append("ER  - ")
    return "\n".join(lines)


def format_ris_fallback(citation: str, doi: str) -> str:
    lines = ["TY  - GEN", f"N1  - {citation}"]
    if doi:
        lines.append(f"DO  - {doi}")
        lines.append(f"UR  - {doi_url(doi)}")
    lines.append("ER  - ")
    return "\n".join(lines)


def to_csl(crossref: dict, ref_id: int, doi: str) -> dict:
    # 与三种引用格式保持同一年份（纸本优先），避免导出 CSL 与页面显示不一致
    parts = crossref.get("published_parts") or crossref.get("issued_parts") or []
    node = {
        "id": doi or f"ref-{ref_id}",
        "type": CSL_TYPE.get(crossref.get("type", ""), "article"),
        "title": crossref.get("title") or "",
    }
    if crossref.get("container_title"):
        node["container-title"] = crossref["container_title"]
    for key, csl_key in (("volume", "volume"), ("issue", "issue"), ("page", "page")):
        if crossref.get(key):
            node[csl_key] = crossref[key]
    if parts:
        node["issued"] = {"date-parts": [parts]}
    if crossref.get("publisher"):
        node["publisher"] = crossref["publisher"]
    authors = []
    for author in crossref.get("authors") or []:
        if author.get("name"):
            authors.append({"literal": author["name"]})
        elif author.get("family") or author.get("given"):
            item = {}
            if author.get("family"):
                item["family"] = author["family"]
            if author.get("given"):
                item["given"] = author["given"]
            authors.append(item)
    if authors:
        node["author"] = authors
    if crossref.get("issn"):
        node["ISSN"] = crossref["issn"]
    if doi:
        node["DOI"] = doi
        node["URL"] = doi_url(doi)
    elif crossref.get("url"):
        node["URL"] = crossref["url"]
    return node


# ---------------------------------------------------------------- BHL（可选）

def bhl_lookup(fetcher: Fetcher, api_key: str, citation: str, title_hint: str):
    """BHL API v3 TitleSearch：只取书目级元数据，不下载扫描件。失败一律返回 None。"""
    if not api_key:
        return None
    query = urlencode({
        "op": "TitleSearch",
        "title": (title_hint or citation)[:200],
        "format": "json",
        "apikey": api_key,
    })
    status, payload = fetcher.get(f"{BHL_API}?{query}")
    if status != 200 or not isinstance(payload, dict):
        return None
    results = payload.get("Result") or []
    if not isinstance(results, list) or not results:
        return None
    best = None
    best_ratio = 0.0
    for item in results[:5]:
        candidate_title = clean_text(item.get("FullTitle") or item.get("ShortTitle") or "")
        ratio = similarity(title_hint or citation, candidate_title)
        if ratio > best_ratio:
            best_ratio, best = ratio, item
    if not best or best_ratio < 0.60:
        return None
    title_id = best.get("TitleID")
    if not title_id:
        return None
    return {
        "title_id": title_id,
        "title": clean_text(best.get("FullTitle") or best.get("ShortTitle") or ""),
        "publication_date": clean_text(best.get("PublicationDate") or ""),
        "url": f"https://www.biodiversitylibrary.org/bibliography/{title_id}",
        "match": "auto",
        "similarity": round(best_ratio, 4),
    }


# ---------------------------------------------------------------- 组装

def build(entries: list, fetcher: Fetcher, bhl: bool, bhl_key: str, limit: int, log=print) -> dict:
    references = []
    auto_matched, bhl_found, unresolved = [], [], []
    for index, entry in enumerate(entries):
        ref_id = entry["id"]
        doi = entry["doi"]
        citation = entry["citation"]
        year = citation_year(citation)
        proposals, crossref, crossref_error = [], None, ""
        doi_status = "original" if doi else "none"
        status = None

        def note_failure(status, was_original):
            """记录 Crossref 查询失败原因；离线/预算跳过不算"DOI 未解析"。"""
            reason = {-2: "offline_cache_miss", -3: "skipped_budget"}.get(status, "")
            if not reason:
                reason = "not_found" if status == 404 else f"http_{status}"
            if was_original and status not in (-2, -3):
                unresolved.append(ref_id)
            return reason

        do_network = (limit <= 0 or index < limit)
        if do_network:
            if doi:
                crossref, status = crossref_by_doi(fetcher, doi)
                if crossref is None:
                    crossref_error = note_failure(status, doi_status == "original")
            else:
                proposals = crossref_search(fetcher, citation, year)
                match = pick_auto_match(proposals)
                if match:
                    doi = match["doi"]
                    doi_status = "matched_candidate"
                    auto_matched.append(ref_id)
                    crossref, status = crossref_by_doi(fetcher, doi)
                    if crossref is None:
                        crossref_error = note_failure(status, False)

        formatted = {
            "gbt": format_gbt(crossref, doi) if crossref else citation,
            "apa": format_apa(crossref, doi) if crossref else citation,
            "vancouver": format_vancouver(crossref, doi) if crossref else citation,
        }
        if crossref:
            bibtex = format_bibtex(crossref, ref_id, doi)
            ris = format_ris(crossref, doi)
            csl = to_csl(crossref, ref_id, doi)
        else:
            bibtex = format_bibtex_fallback(ref_id, citation, doi)
            ris = format_ris_fallback(citation, doi)
            csl = {"id": doi or f"ref-{ref_id}", "type": "article", "title": "", "note": citation}
            if doi:
                csl["DOI"] = doi
                csl["URL"] = doi_url(doi)

        bhl_node = None
        if bhl and bhl_key and do_network:
            title_hint = (crossref or {}).get("title") or citation
            bhl_node = bhl_lookup(fetcher, bhl_key, citation, title_hint)
            if bhl_node:
                bhl_found.append(ref_id)

        record = {
            "id": ref_id,
            "citation": citation,
            "doi": doi,
            "doi_status": doi_status,
            "doi_note": "自动匹配待核对" if doi_status == "matched_candidate" else "",
            "year": int(ref_year(crossref)) if (crossref and ref_year(crossref).isdigit()) else (int(year) if year else None),
            "candidates": proposals,
            "crossref": crossref,
            "crossref_error": crossref_error,
            "formatted": formatted,
            "bibtex": bibtex,
            "ris": ris,
            "csl": csl,
            "bhl": bhl_node,
            "links": {
                "doi": doi_url(doi),
                "crossref": crossref_url(doi) if doi else "",
                "search": "" if doi else search_url(citation),
            },
        }
        references.append(record)

    with_doi = sum(1 for r in references if r["doi"])
    resolved = sum(1 for r in references if r["crossref"])
    candidates = sum(1 for r in references if r["candidates"])
    bhl_count = sum(1 for r in references if r["bhl"])
    notes = []
    if unresolved:
        notes.append("以下条目自带 DOI 但 Crossref 未返回记录（保留原 DOI，不做任何补写）：" +
                     ", ".join(str(i) for i in unresolved))
    if auto_matched:
        notes.append("自动匹配（相似度 ≥ 0.90 且年份一致）待人工核对：" + ", ".join(str(i) for i in auto_matched))
    # 以下只是本次运行的条件，不属于数据属性：只打印，不写进 meta.notes
    # （否则 --offline / --bhl 这类开关会让 --check 误报"数据不一致"）
    if fetcher.offline:
        log("note: 离线模式：仅使用本地缓存，未联网。")
    if fetcher.budget_exceeded:
        log("note: 已达 --time-budget 时间上限：其余条目未联网补全，重新运行会从缓存继续。")
    if bhl and not bhl_key:
        log("note: 未设置 BHL_API_KEY：bhl 字段保持 null；设置后加 --bhl 重跑即可补全。")

    meta = {
        "generated": os.environ.get("SOURCE_DATE_EPOCH_DATE") or time.strftime("%Y-%m-%d", time.gmtime()),
        "source": "list.md 参考文献 + Crossref",
        "counts": {
            "total": len(references),
            "with_doi": with_doi,
            "crossref_resolved": resolved,
            "candidates": candidates,
            "auto_matched": len(auto_matched),
            "bhl": bhl_count,
        },
        "mailto": CROSSREF_MAILTO,
        "notes": notes,
    }
    return {"meta": meta, "references": references}


def dumps(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def strip_generated(document: dict) -> dict:
    clone = json.loads(json.dumps(document, ensure_ascii=False))
    clone.get("meta", {}).pop("generated", None)
    return clone


def verify_document() -> int:
    """离线自检：不联网、不重算，只检查仓库里这两份 JSON 自身是否自洽。

    CI 的"离线校验"步骤用它（几百毫秒），(--check) 则留给本地/有缓存时做逐字段回归。
    """
    problems = []
    if not DATA_OUT.exists():
        print("error: _data/references.json 不存在（先运行 --write）")
        return 1
    try:
        document = json.loads(DATA_OUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: _data/references.json 不是合法 JSON：{exc}")
        return 1
    if PUBLIC_OUT.exists():
        if DATA_OUT.read_bytes() != PUBLIC_OUT.read_bytes():
            problems.append("data/references.json 与 _data/references.json 字节不同")
    else:
        problems.append("data/references.json 不存在")

    meta = document.get("meta") or {}
    refs = document.get("references") or []
    if not refs:
        problems.append("references 为空")
    counts = meta.get("counts") or {}
    recomputed = {
        "total": len(refs),
        "with_doi": sum(1 for r in refs if r.get("doi")),
        "crossref_resolved": sum(1 for r in refs if r.get("crossref")),
        "candidates": sum(1 for r in refs if r.get("candidates")),
        "auto_matched": sum(1 for r in refs if r.get("doi_status") == "matched_candidate"),
        "bhl": sum(1 for r in refs if r.get("bhl")),
    }
    for key, value in recomputed.items():
        if counts.get(key) != value:
            problems.append(f"meta.counts.{key} 为 {counts.get(key)!r}，实际 {value}")

    for expected, record in enumerate(refs, start=1):
        rid = record.get("id")
        label = f"第 {rid} 条"
        if rid != expected:
            problems.append(f"编号不连续：第 {expected} 个条目 id={rid!r}")
        if not str(record.get("citation") or "").strip():
            problems.append(f"{label}：citation 为空")
        status = record.get("doi_status")
        if status not in ("original", "matched_candidate", "none"):
            problems.append(f"{label}：doi_status={status!r} 非法")
        if status == "none" and record.get("doi"):
            problems.append(f"{label}：doi_status=none 却带 DOI")
        if status in ("original", "matched_candidate") and not record.get("doi"):
            problems.append(f"{label}：doi_status={status} 却没有 DOI")
        formatted = record.get("formatted") or {}
        for style in ("gbt", "apa", "vancouver"):
            if not str(formatted.get(style) or "").strip():
                problems.append(f"{label}：formatted.{style} 为空")
        for field in ("bibtex", "ris", "csl", "links", "candidates"):
            if field not in record:
                problems.append(f"{label}：缺字段 {field}")
        links = record.get("links") or {}
        if record.get("doi") and not str(links.get("doi") or "").startswith("https://doi.org/"):
            problems.append(f"{label}：links.doi 不是 https://doi.org/ 开头")
        if record.get("doi") and not str(links.get("crossref") or "").startswith(CROSSREF_API):
            problems.append(f"{label}：links.crossref 不是 Crossref API 地址")
        crossref = record.get("crossref")
        if crossref is not None:
            for field in ("doi", "title", "authors", "container_title", "issued_parts",
                          "published_parts", "publisher", "type", "issn", "url",
                          "is_referenced_by_count"):
                if field not in crossref:
                    problems.append(f"{label}：crossref 缺字段 {field}")
        bhl = record.get("bhl")
        if bhl is not None and not str(bhl.get("url") or "").startswith("https://www.biodiversitylibrary.org/"):
            problems.append(f"{label}：bhl.url 不是 BHL 地址")
        for candidate in record.get("candidates") or []:
            if not candidate.get("doi"):
                problems.append(f"{label}：candidate 缺 doi")
    if problems:
        for problem in problems[:40]:
            print("error: " + problem)
        if len(problems) > 40:
            print(f"error: 另有 {len(problems) - 40} 条问题未列出")
        return 1
    print(f"ok: {recomputed['total']} 条参考文献自洽（带 DOI {recomputed['with_doi']}，"
          f"Crossref 记录 {recomputed['crossref_resolved']}，候选 {recomputed['candidates']}，"
          f"BHL {recomputed['bhl']}）；两份 JSON 字节相同")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="用 Crossref（可选 BHL）补全 77 条参考文献并生成 JSON")
    parser.add_argument("--write", action="store_true", help="写入 _data/references.json 与 data/references.json")
    parser.add_argument("--check", action="store_true", help="校验仓库内 JSON 与重新生成的结果一致（忽略 meta.generated）")
    parser.add_argument("--verify", action="store_true", help="只做离线自检：不联网，检查已提交 JSON 自身是否自洽（CI 用）")
    parser.add_argument("--bhl", action="store_true", help="额外查询 BHL（需要环境变量 BHL_API_KEY）")
    parser.add_argument("--offline", action="store_true", help="只用 _tmp 缓存，不联网")
    parser.add_argument("--limit", type=int, default=0, help="仅前 N 条联网（调试用；不影响输出条数）")
    parser.add_argument("--time-budget", type=float, default=0.0, help="联网时间上限（秒），0 = 不限")
    parser.add_argument("--quiet", action="store_true", help="少打印")
    args = parser.parse_args()
    log = (lambda *a, **k: None) if args.quiet else print

    if args.verify:
        return verify_document()

    entries = load_references()
    if len(entries) != 77:
        log(f"warn: 解析到 {len(entries)} 条参考文献（预期 77 条），请检查名录单文件的「## 参考文献」区块")

    bhl_key = os.environ.get("BHL_API_KEY", "").strip()
    fetcher = Fetcher(CACHE_PATH, offline=args.offline, budget=args.time_budget, log=log)
    document = build(entries, fetcher, args.bhl, bhl_key, args.limit, log=log)

    counts = document["meta"]["counts"]
    log(f"参考文献 {counts['total']} 条；带 DOI {counts['with_doi']} 条"
        f"（Crossref 解析 {counts['crossref_resolved']} 条）；候选待核对 {counts['candidates']} 条；"
        f"BHL {counts['bhl']} 条")
    log(f"网络请求 {fetcher.network_calls} 次，缓存命中 {fetcher.from_cache} 次")
    for note in document["meta"]["notes"]:
        log("note: " + note)

    if args.check:
        problems = []
        for path in (DATA_OUT, PUBLIC_OUT):
            if not path.exists():
                problems.append(f"{path.relative_to(ROOT)} 不存在")
                continue
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                problems.append(f"{path.relative_to(ROOT)} 不是合法 JSON：{exc}")
                continue
            if strip_generated(existing) != strip_generated(document):
                problems.append(f"{path.relative_to(ROOT)} 与生成结果不一致（请运行 --write）")
        if DATA_OUT.exists() and PUBLIC_OUT.exists() and DATA_OUT.read_bytes() != PUBLIC_OUT.read_bytes():
            problems.append("_data/references.json 与 data/references.json 字节不同")
        if problems:
            for problem in problems:
                print("error: " + problem)
            return 1
        print("ok: 两份 JSON 与生成结果一致")
        return 0

    if args.write:
        text = dumps(document)
        # generated 保持稳定：内容未变时沿用旧时间戳，避免 CI 里每天产生无意义 diff
        if DATA_OUT.exists():
            try:
                previous = json.loads(DATA_OUT.read_text(encoding="utf-8"))
                if strip_generated(previous) == strip_generated(document):
                    document["meta"]["generated"] = previous.get("meta", {}).get("generated") or document["meta"]["generated"]
                    text = dumps(document)
            except (json.JSONDecodeError, OSError):
                pass
        DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)
        for path in (DATA_OUT, PUBLIC_OUT):
            path.write_text(text, encoding="utf-8", newline="\n")
        print(f"write: {DATA_OUT.relative_to(ROOT)} / {PUBLIC_OUT.relative_to(ROOT)}"
              f"（{len(text.encode('utf-8'))} 字节）")
        return 0

    print("（未写文件；加 --write 生成，--check 校验）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
