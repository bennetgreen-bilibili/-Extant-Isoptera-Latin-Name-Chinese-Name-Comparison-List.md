#!/usr/bin/env python3
"""文献检索器的属级缓存（/papers/ 页面 + 物种页「相关文献」）。

数据源（只用开放元数据，不抓出版社页面 / PDF）：
  OpenAlex  https://api.openalex.org/works
            filter=title_and_abstract.search:"属名",type:article|review|book-chapter|preprint
            取每个属相关度最高的 12 条；摘要来自 abstract_inverted_index（按词位置还原）。
  Crossref  https://api.crossref.org/works
            可选补充：按属名检索 20 条，把 Crossref 提供的 JATS 摘要按 DOI 填到
            OpenAlex 缺摘要的同一条记录上。

输出（确定性、可 --check）：
  _data/papers.json    Jekyll 模板用（site.data.papers）
  papers-index.json    公开副本（字节完全相同），/papers/ 页面断网时的兜底缓存
  两者都包含完整摘要（超过 MAX_ABSTRACT_CHARS 才截断，并标记 abstract_truncated）。

用法：
  python .github/workflows/build_papers.py --check
  python .github/workflows/build_papers.py --write
  python .github/workflows/build_papers.py --write --force
  python .github/workflows/build_papers.py --write --refresh --stale-days 180 --time-budget 300
  python .github/workflows/build_papers.py --write --no-crossref
  python .github/workflows/build_papers.py --write --genus coptotermes
  python .github/workflows/build_papers.py --write --offline

环境变量：
  OPENALEX_MAILTO / CROSSREF_MAILTO   礼貌池联系邮箱（默认本仓库 GitHub noreply 地址）
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SEARCH_INDEX = ROOT / "search-index.json"
DATA_OUT = ROOT / "_data" / "papers.json"
PUBLIC_OUT = ROOT / "papers-index.json"
CACHE_PATH = ROOT / "_tmp" / "papers-cache.json"

PROJECT_URL = "https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/"
MAILTO = (
    os.environ.get("OPENALEX_MAILTO")
    or os.environ.get("CROSSREF_MAILTO")
    or "bennetgreen-bilibili@users.noreply.github.com"
)
OPENALEX_API_KEY = os.environ.get("OPENALEX_API_KEY", "").strip()
FORCE_CROSSREF = False
USER_AGENT = (
    "extant-isoptera-checklist-papers/1.0 "
    f"(+{PROJECT_URL}; mailto:{MAILTO}) Python-urllib"
)
OPENALEX_API = "https://api.openalex.org/works"
CROSSREF_API = "https://api.crossref.org/works"

PER_GENUS = 12
MAX_ABSTRACT_CHARS = 20000
OPENALEX_SLEEP = 0.45
CROSSREF_SLEEP = 0.35
MAX_ATTEMPTS = 4
SELECT_FIELDS = (
    "id,doi,title,publication_year,publication_date,authorships,primary_location,type,"
    "language,cited_by_count,open_access,biblio,abstract_inverted_index"
)
TYPE_FILTER = "type:article|review|book-chapter|preprint"


# ---------------------------------------------------------------- 基础工具

def clean_text(value) -> str:
    """去 HTML/JATS 标签、解实体、折叠空白。"""
    if value is None:
        return ""
    if isinstance(value, list):
        value = value[0] if value else ""
    raw = str(value)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html_lib.unescape(raw)
    return re.sub(r"\s+", " ", raw).strip()


def strip_abstract_label(value: str) -> str:
    value = clean_text(value)
    return re.sub(r"^\s*Abstract\b[\s:.-]*", "", value, flags=re.IGNORECASE).strip()


def reconstruct_abstract(inverted) -> str:
    """OpenAlex abstract_inverted_index -> 文本（按词位置排序后拼接）。"""
    if not isinstance(inverted, dict) or not inverted:
        return ""
    positions: list = []
    for word, indexes in inverted.items():
        if not isinstance(indexes, list):
            continue
        for i in indexes:
            if isinstance(i, int):
                positions.append((i, str(word)))
    positions.sort(key=lambda item: item[0])
    value = " ".join(word for _, word in positions)
    value = html_lib.unescape(value)
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    return re.sub(r"\s+", " ", value).strip()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(payload, encoding="utf-8", newline="\n")
    tmp.replace(path)


def load_genera() -> list:
    if not SEARCH_INDEX.is_file():
        sys.exit(f"error: 找不到 {SEARCH_INDEX.name}（先运行 build_search_index.py）")
    entries = read_json(SEARCH_INDEX)
    genera = []
    for e in entries:
        if not isinstance(e, dict) or e.get("r") != "属":
            continue
        gid = str(e.get("h") or "").strip()
        latin = str(e.get("l") or "").strip()
        if not gid or not latin:
            continue
        genera.append({"id": gid, "latin": latin, "zh": str(e.get("z") or "").strip()})
    genera.sort(key=lambda g: g["id"])
    if not genera:
        sys.exit("error: search-index.json 里没有属级条目")
    return genera


# ---------------------------------------------------------------- 网络请求

def http_json(url: str, sleep_before: float = 0.0):
    """返回 (ok, data)；429/5xx/网络错误指数退避，最终失败返回 (False, None)。"""
    if sleep_before > 0:
        time.sleep(sleep_before)
    delay = 1.5
    for attempt in range(1, MAX_ATTEMPTS + 1):
        req = Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        })
        try:
            with urlopen(req, timeout=45) as resp:
                raw = resp.read()
                if not raw.strip():
                    return False, None
                return True, json.loads(raw.decode("utf-8", "replace"))
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", "replace")[:200]
            except Exception:  # noqa: BLE001
                pass
            if exc.code == 429 and "Insufficient budget" in body:
                global FORCE_CROSSREF
                FORCE_CROSSREF = True
                print("  warn: OpenAlex 每日免费额度已用尽，后续改用 Crossref 回退", file=sys.stderr, flush=True)
                return False, None
            if exc.code in (429, 500, 502, 503, 504) and attempt < MAX_ATTEMPTS:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                # OpenAlex 偶尔返回极大的 Retry-After（例如 29383s）；绝不能真的睡 8 小时。
                if exc.code == 429:
                    wait = min(float(retry_after), 30.0) if (retry_after or "").isdigit() else min(delay, 30.0)
                else:
                    wait = float(retry_after) if (retry_after or "").isdigit() else delay
                wait = min(wait, 60.0)
                print(f"  warn: HTTP {exc.code}，{wait:.0f}s 后重试（{attempt}/{MAX_ATTEMPTS}）", file=sys.stderr, flush=True)
                time.sleep(wait)
                delay = min(delay * 2, 30)
                continue
            print(f"  warn: HTTP {exc.code} {body} - {url}", file=sys.stderr, flush=True)
            return False, None
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            if attempt < MAX_ATTEMPTS:
                print(f"  warn: 网络错误 {exc}，{delay:.0f}s 后重试（{attempt}/{MAX_ATTEMPTS}）", file=sys.stderr, flush=True)
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            print(f"  warn: 网络错误 {exc} - {url}", file=sys.stderr, flush=True)
            return False, None
    return False, None


def openalex_url(genus_latin: str) -> str:
    filter_value = f'title_and_abstract.search:"{genus_latin}",{TYPE_FILTER}'
    params = {
        "filter": filter_value,
        "per-page": str(PER_GENUS),
        "select": SELECT_FIELDS,
        "mailto": MAILTO,
    }
    if OPENALEX_API_KEY:
        params["api_key"] = OPENALEX_API_KEY
    return OPENALEX_API + "?" + urlencode(params)


def crossref_url(genus_latin: str) -> str:
    params = {
        "query.bibliographic": genus_latin,
        "rows": "20",
        "filter": "type:journal-article",
        "mailto": MAILTO,
    }
    return CROSSREF_API + "?" + urlencode(params)


# ---------------------------------------------------------------- 归一化

def openalex_pages(biblio: dict) -> str:
    if not isinstance(biblio, dict):
        return ""
    first = clean_text(biblio.get("first_page"))
    last = clean_text(biblio.get("last_page"))
    if first and last:
        return f"{first}-{last}"
    return first or last or ""


def normalize_openalex_work(work: dict, crossref_abstracts: dict) -> dict:
    doi = clean_text(work.get("doi")).replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi_lower = doi.lower()
    oa_abstract = strip_abstract_label(reconstruct_abstract(work.get("abstract_inverted_index")))
    crossref_abstract = strip_abstract_label(crossref_abstracts.get(doi_lower, "")) if doi_lower else ""
    abstract = oa_abstract or crossref_abstract
    abstract_source = "openalex" if oa_abstract else ("crossref" if crossref_abstract else "")
    truncated = False
    if len(abstract) > MAX_ABSTRACT_CHARS:
        abstract = abstract[:MAX_ABSTRACT_CHARS].rsplit(" ", 1)[0].rstrip(" ,.;:") + "…"
        truncated = True

    authors = []
    for authorship in (work.get("authorships") or []):
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author") or {}
        name = clean_text(author.get("display_name"))
        if name:
            authors.append(name)
    authors = authors[:12]

    location = work.get("primary_location") or {}
    source = (location.get("source") or {}) if isinstance(location, dict) else {}
    venue = clean_text(source.get("display_name")) if isinstance(source, dict) else ""
    biblio = work.get("biblio") or {}
    open_access = work.get("open_access") or {}

    year = work.get("publication_year")
    try:
        year = int(year) if year is not None else ""
    except (TypeError, ValueError):
        year = ""

    return {
        "id": clean_text(work.get("id")),
        "openalex_url": clean_text(work.get("id")),
        "doi": doi,
        "doi_url": ("https://doi.org/" + doi) if doi else "",
        "title": clean_text(work.get("title")) or "Untitled",
        "year": year,
        "date": clean_text(work.get("publication_date")),
        "authors": authors,
        "venue": venue,
        "type": clean_text(work.get("type")),
        "language": clean_text(work.get("language")),
        "cited_by": int(work.get("cited_by_count") or 0),
        "oa_url": clean_text(open_access.get("oa_url")) if isinstance(open_access, dict) else "",
        "volume": clean_text(biblio.get("volume")) if isinstance(biblio, dict) else "",
        "issue": clean_text(biblio.get("issue")) if isinstance(biblio, dict) else "",
        "pages": openalex_pages(biblio),
        "abstract": abstract,
        "abstract_source": abstract_source,
        "abstract_chars": len(abstract),
        "abstract_truncated": truncated,
    }


def fetch_crossref_abstracts(genus_latin: str, log=print) -> dict:
    ok, data = http_json(crossref_url(genus_latin), sleep_before=CROSSREF_SLEEP)
    if not ok or not isinstance(data, dict):
        return {}
    items = ((data.get("message") or {}).get("items") or [])
    out = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        doi = clean_text(item.get("DOI")).lower()
        abstract = strip_abstract_label(item.get("abstract"))
        if doi and abstract:
            out[doi] = abstract
    if out:
        log(f"    Crossref 补到 {len(out)} 条摘要")
    return out


def _cap_abstract(value: str) -> tuple[str, bool]:
    value = strip_abstract_label(value)
    if len(value) > MAX_ABSTRACT_CHARS:
        return value[:MAX_ABSTRACT_CHARS].rsplit(" ", 1)[0].rstrip(" ,.;:") + "…", True
    return value, False


def crossref_search_url(genus_latin: str) -> str:
    params = {
        "query.bibliographic": genus_latin,
        "rows": str(PER_GENUS),
        "filter": "type:journal-article",
        "mailto": MAILTO,
    }
    return CROSSREF_API + "?" + urlencode(params)


def normalize_crossref_item(item: dict) -> dict:
    doi = clean_text(item.get("DOI"))
    abstract, truncated = _cap_abstract(item.get("abstract"))
    authors = []
    for author in (item.get("author") or []):
        if not isinstance(author, dict):
            continue
        name = " ".join(part for part in (clean_text(author.get("given")), clean_text(author.get("family"))) if part)
        if name:
            authors.append(name)
    issued = item.get("issued") or {}
    parts = issued.get("date-parts") if isinstance(issued, dict) else None
    year = ""
    date = ""
    if parts and isinstance(parts, list) and parts and isinstance(parts[0], list):
        first = parts[0]
        if first and first[0]:
            year = int(first[0])
            date = "-".join(str(x).zfill(2) for x in first if x is not None)
    venue = clean_text(item.get("container-title"))
    pages = clean_text(item.get("page"))
    return {
        "id": ("https://doi.org/" + doi) if doi else clean_text(item.get("title")),
        "openalex_url": "",
        "doi": doi,
        "doi_url": ("https://doi.org/" + doi) if doi else "",
        "title": clean_text(item.get("title")) or "Untitled",
        "year": year,
        "date": date,
        "authors": authors[:12],
        "venue": venue,
        "type": clean_text(item.get("type")),
        "language": clean_text(item.get("language")),
        "cited_by": int(item.get("is-referenced-by-count") or 0),
        "oa_url": "",
        "volume": clean_text(item.get("volume")),
        "issue": clean_text(item.get("issue")),
        "pages": pages,
        "abstract": abstract,
        "abstract_source": "crossref" if abstract else "",
        "abstract_chars": len(abstract),
        "abstract_truncated": truncated,
        "source": "crossref",
    }


def fetch_genus_crossref(genus: dict, log=print) -> dict:
    ok, data = http_json(crossref_search_url(genus["latin"]), sleep_before=CROSSREF_SLEEP)
    if not ok or not isinstance(data, dict):
        raise RuntimeError("Crossref 请求失败")
    items = ((data.get("message") or {}).get("items") or [])
    papers = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        paper = normalize_crossref_item(item)
        key = paper["doi"].lower() or paper["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        papers.append(paper)
        if len(papers) >= PER_GENUS:
            break
    log(f"    Crossref 回退：{len(papers)} 条")
    return {
        "latin": genus["latin"],
        "zh": genus["zh"],
        "fetched_at": now_iso(),
        "papers": papers,
    }


def fetch_genus(genus: dict, enrich_crossref: bool, log=print) -> dict:
    log(f"  {genus['latin']} ({genus['id']}) …")
    if FORCE_CROSSREF:
        return fetch_genus_crossref(genus, log=log)
    try:
        ok, data = http_json(openalex_url(genus["latin"]), sleep_before=OPENALEX_SLEEP)
        if not ok or not isinstance(data, dict):
            raise RuntimeError("OpenAlex 请求失败")
        works = [w for w in (data.get("results") or []) if isinstance(w, dict)]
        crossref_abstracts = {}
        if enrich_crossref:
            needs_crossref = any(
                not reconstruct_abstract(w.get("abstract_inverted_index")) and clean_text(w.get("doi"))
                for w in works
            )
            if needs_crossref:
                crossref_abstracts = fetch_crossref_abstracts(genus["latin"], log=log)
        papers = []
        seen = set()
        for work in works:
            paper = normalize_openalex_work(work, crossref_abstracts)
            key = paper["id"] or paper["doi"] or paper["title"].lower()
            if key in seen:
                continue
            seen.add(key)
            papers.append(paper)
        return {
            "latin": genus["latin"],
            "zh": genus["zh"],
            "fetched_at": now_iso(),
            "papers": papers[:PER_GENUS],
        }
    except Exception as exc:  # noqa: BLE001 - OpenAlex 429 / 网络失败时回退 Crossref
        log(f"    OpenAlex 不可用（{exc}），改用 Crossref 回退")
        return fetch_genus_crossref(genus, log=log)


# ---------------------------------------------------------------- 生成 / 校验

def build_document(entries: dict, genera: list) -> dict:
    total = with_abstract = with_doi = truncated = 0
    for entry in entries.values():
        for paper in entry.get("papers") or []:
            total += 1
            if paper.get("abstract"):
                with_abstract += 1
            if paper.get("doi"):
                with_doi += 1
            if paper.get("abstract_truncated"):
                truncated += 1
    return {
        "meta": {
            "generated": now_iso(),
            "source": "OpenAlex + Crossref",
            "api": OPENALEX_API,
            "query": 'title_and_abstract.search:"<genus>"',
            "per_genus": PER_GENUS,
            "counts": {
                "genera": len(genera),
                "papers": total,
                "with_abstract": with_abstract,
                "with_doi": with_doi,
                "abstract_truncated": truncated,
            },
            "abstract_policy": (
                "完整摘要缓存；OpenAlex abstract_inverted_index 还原，Crossref JATS 摘要去标签补缺；"
                f"超过 {MAX_ABSTRACT_CHARS} 字符才截断并置 abstract_truncated=true"
            ),
            "license": "OpenAlex data CC0; abstract copyright remains with the original authors/publishers",
            "generated_by": ".github/workflows/build_papers.py",
        },
        "genera": {g["id"]: entries[g["id"]] for g in genera if g["id"] in entries},
    }


def write_outputs(document: dict) -> tuple[int, int]:
    payload = json.dumps(document, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n"
    write_json(DATA_OUT, payload)
    write_json(PUBLIC_OUT, payload)
    return len(payload.encode("utf-8")), len(document.get("genera") or {})


def check_outputs(expected_genera: list) -> int:
    problems = []
    if not DATA_OUT.is_file():
        print(f"error: {DATA_OUT.relative_to(ROOT)} 不存在（运行 --write 生成）")
        return 1
    if not PUBLIC_OUT.is_file():
        print(f"error: {PUBLIC_OUT.relative_to(ROOT)} 不存在（运行 --write 生成）")
        return 1
    data_bytes = DATA_OUT.read_bytes()
    public_bytes = PUBLIC_OUT.read_bytes()
    if data_bytes != public_bytes:
        problems.append("_data/papers.json 与 papers-index.json 字节不一致")
    try:
        document = json.loads(data_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: papers.json 不是合法 JSON：{exc}")
        return 1

    meta = document.get("meta") if isinstance(document, dict) else None
    genera = document.get("genera") if isinstance(document, dict) else None
    if not isinstance(meta, dict) or not isinstance(genera, dict):
        problems.append("顶层必须是 {meta, genera}")

    expected_ids = [g["id"] for g in expected_genera]
    if isinstance(genera, dict):
        missing = [gid for gid in expected_ids if gid not in genera]
        extra = [gid for gid in genera if gid not in set(expected_ids)]
        if missing:
            problems.append(f"缺少属条目 {len(missing)} 个：{missing[:5]}")
        if extra:
            problems.append(f"多出属条目 {len(extra)} 个：{extra[:5]}")

    total = with_abstract = with_doi = truncated = 0
    for gid, entry in (genera or {}).items():
        if not isinstance(entry, dict):
            problems.append(f"{gid}: 条目不是对象")
            continue
        if not entry.get("latin"):
            problems.append(f"{gid}: 缺 latin")
        if not isinstance(entry.get("fetched_at"), str):
            problems.append(f"{gid}: 缺 fetched_at")
        papers = entry.get("papers")
        if not isinstance(papers, list):
            problems.append(f"{gid}: papers 不是数组")
            continue
        if len(papers) > PER_GENUS:
            problems.append(f"{gid}: papers 超过 {PER_GENUS} 条")
        seen = set()
        for idx, paper in enumerate(papers):
            if not isinstance(paper, dict):
                problems.append(f"{gid}[{idx}]: 不是对象")
                continue
            pid = paper.get("id") or paper.get("doi") or paper.get("title")
            if not pid:
                problems.append(f"{gid}[{idx}]: 缺 id/doi/title")
            if pid in seen:
                problems.append(f"{gid}[{idx}]: 重复条目 {pid}")
            seen.add(pid)
            if not paper.get("title"):
                problems.append(f"{gid}[{idx}]: 缺 title")
            abstract = paper.get("abstract", "")
            if not isinstance(abstract, str):
                problems.append(f"{gid}[{idx}]: abstract 不是字符串")
                abstract = ""
            if paper.get("abstract_chars") != len(abstract):
                problems.append(f"{gid}[{idx}]: abstract_chars 与摘要长度不一致")
            if paper.get("doi") and paper.get("doi_url") != ("https://doi.org/" + paper["doi"]):
                problems.append(f"{gid}[{idx}]: doi_url 与 doi 不一致")
            if abstract:
                with_abstract += 1
            if paper.get("doi"):
                with_doi += 1
            if paper.get("abstract_truncated"):
                truncated += 1
            total += 1

    counts = (meta or {}).get("counts") or {}
    expected_counts = {
        "genera": len(expected_genera),
        "papers": total,
        "with_abstract": with_abstract,
        "with_doi": with_doi,
        "abstract_truncated": truncated,
    }
    for key, value in expected_counts.items():
        if counts.get(key) != value:
            problems.append(f"meta.counts.{key}={counts.get(key)}，实际 {value}")

    if problems:
        print(f"papers 缓存校验失败（{len(problems)} 项）：")
        for p in problems[:30]:
            print("  - " + p)
        return 1
    print(
        "papers 缓存 OK：%d 属、%d 条文献、%d 条有摘要（%.1f%%）、%d 条有 DOI、%d 条摘要截断；%.1f KB"
        % (
            len(expected_genera),
            total,
            with_abstract,
            (100.0 * with_abstract / total) if total else 0.0,
            with_doi,
            truncated,
            len(data_bytes) / 1024.0,
        )
    )
    return 0


def parse_fetched_at(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------- 主流程

def main() -> int:
    parser = argparse.ArgumentParser(description="生成 / 校验文献检索器缓存")
    parser.add_argument("--write", action="store_true", help="写入 _data/papers.json 与 papers-index.json")
    parser.add_argument("--check", action="store_true", help="离线校验仓库内缓存")
    parser.add_argument("--refresh", action="store_true", help="显式刷新过期条目（默认 --write 也会刷新过期条目）")
    parser.add_argument("--force", action="store_true", help="全部重新查询")
    parser.add_argument("--stale-days", type=int, default=180, help="过期天数（默认 180）")
    parser.add_argument("--time-budget", type=float, default=0.0, help="网络时间预算（秒，0=不限）")
    parser.add_argument("--genus", default="", help="只更新一个属（调试用）")
    parser.add_argument("--offline", action="store_true", help="只用 _tmp 缓存，不联网")
    parser.add_argument("--no-crossref", action="store_true", help="不向 Crossref 补摘要")
    parser.add_argument("--crossref-only", action="store_true", help="跳过 OpenAlex，只用 Crossref 生成缓存（OpenAlex 当日额度用尽时用）")
    parser.add_argument("--quiet", action="store_true", help="少打印")
    args = parser.parse_args()

    if not args.write and not args.check:
        parser.print_help()
        return 0

    global FORCE_CROSSREF
    FORCE_CROSSREF = args.crossref_only

    genera = load_genera()
    if args.check:
        return check_outputs(genera)

    existing: dict = {}
    if DATA_OUT.is_file():
        try:
            existing_doc = read_json(DATA_OUT)
            existing = (existing_doc.get("genera") or {}) if isinstance(existing_doc, dict) else {}
        except (json.JSONDecodeError, OSError) as exc:
            print(f"warn: 现有 papers.json 不可读（{exc}），从头生成", file=sys.stderr, flush=True)
            existing = {}

    cache: dict = {}
    if CACHE_PATH.is_file():
        try:
            cache = read_json(CACHE_PATH)
            if not isinstance(cache, dict):
                cache = {}
        except (json.JSONDecodeError, OSError):
            cache = {}

    def log(message: str) -> None:
        if not args.quiet:
            print(message, flush=True)

    target_genera = [g for g in genera if (not args.genus or g["id"] == args.genus)]
    if args.genus and not target_genera:
        sys.exit(f"error: 找不到属 {args.genus}")
    started = time.monotonic()
    network_queries = 0
    updated = 0
    skipped = 0
    failed = 0
    budget_exceeded = False

    for index, genus in enumerate(target_genera, 1):
        gid = genus["id"]
        old_entry = existing.get(gid)
        if old_entry and not args.force:
            fetched = parse_fetched_at(old_entry.get("fetched_at", ""))
            stale = (fetched is None) or ((datetime.now(timezone.utc) - fetched) > timedelta(days=args.stale_days))
            if not stale:
                skipped += 1
                continue

        cached = cache.get(gid)
        if cached and not args.force:
            fetched = parse_fetched_at(cached.get("fetched_at", ""))
            stale = (fetched is None) or ((datetime.now(timezone.utc) - fetched) > timedelta(days=args.stale_days))
            if not stale and not args.genus:
                existing[gid] = cached
                skipped += 1
                continue

        if args.offline:
            if cached:
                existing[gid] = cached
                skipped += 1
                continue
            if old_entry:
                existing[gid] = old_entry
                skipped += 1
                continue
            failed += 1
            log(f"  [offline] {genus['latin']} 无缓存，跳过")
            continue

        if args.time_budget and (time.monotonic() - started) > args.time_budget:
            budget_exceeded = True
            if old_entry:
                existing[gid] = old_entry
                skipped += 1
                continue
            log(f"  [budget] {genus['latin']} 跳过（无旧条目）")
            continue

        try:
            entry = fetch_genus(genus, enrich_crossref=not args.no_crossref, log=log)
            existing[gid] = entry
            cache[gid] = entry
            updated += 1
            network_queries += 1
            if updated % 10 == 0:
                write_json(CACHE_PATH, json.dumps(cache, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
        except Exception as exc:  # noqa: BLE001 - 单个属失败不应中断全部
            failed += 1
            print(f"  warn: {genus['latin']} 失败：{exc}", file=sys.stderr, flush=True)
            if old_entry:
                existing[gid] = old_entry
            elif cached:
                existing[gid] = cached

        if index % 20 == 0:
            log(f"  进度 {index}/{len(target_genera)}：更新 {updated}、跳过 {skipped}、失败 {failed}")

    if cache:
        write_json(CACHE_PATH, json.dumps(cache, ensure_ascii=False, separators=(",", ":"), sort_keys=True))

    document = build_document(existing, genera)
    size, count = write_outputs(document)
    print(
        "写入 %s 与 %s：%d 属、%d 条文献；本次更新 %d、跳过 %d、失败 %d、网络查询 %d；%.1f KB"
        % (
            DATA_OUT.relative_to(ROOT),
            PUBLIC_OUT.relative_to(ROOT),
            count,
            document["meta"]["counts"]["papers"],
            updated,
            skipped,
            failed,
            network_queries,
            size / 1024.0,
        ),
        flush=True,
    )
    if budget_exceeded:
        print("提示：达到时间预算，未完成的条目保留旧缓存；下次继续即可。", flush=True)
    if failed:
        print("提示：有失败条目；可重跑 --write（默认只补缺失/过期）或 --force。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
