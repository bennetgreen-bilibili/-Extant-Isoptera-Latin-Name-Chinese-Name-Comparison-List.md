#!/usr/bin/env python3
"""全文原文爬取 + 归档（仅合法 OA）。

在「文献检索器」缓存 _data/papers.json 的基础上，对其中标记为开放获取（oa_url 非空）、
且尚未归档进 _unpublished/文库 的论文，按被引数从高到低抓取**合法 OA 全文**
（Unpaywall / OpenAlex / Europe PMC），下载 PDF 或 JATS XML，再用
python _tools/sources.py library-add 入库（_unpublished/文库 + .sources/）。

只走合法 OA 通道，不绕过付费墙；HTML 落地页一律不下。政策见 _tools/文献检索器说明.md §3
与 AGENTS.md §1.4 / §1.6。详细文档见 _tools/原文归档工作流说明.md。

用法：
  python _tools/fetch_fulltext.py --check                        # 离线校验 + 计划（只读）
  python _tools/fetch_fulltext.py --discover 20                  # 从 papers.json 生成候选队列（不下载）
  python _tools/fetch_fulltext.py --dry-run --discover 20 --limit 2   # 只解析 OA 链接，不下载/不入库
  python _tools/fetch_fulltext.py --write --discover 20 --limit 10 --time-budget 600

环境变量：
  UNPAYWALL_EMAIL   必填（Unpaywall 礼貌邮箱；缺省则跳过 Unpaywall）
  OPENALEX_API_KEY  可选（OpenAlex 自己的额度）
  OPENALEX_MAILTO   可选（OpenAlex 礼貌邮箱）
  CROSSREF_MAILTO   可选（备用联系邮箱）

退出码：0 完成（含「部分条目无 OA / 失败」这类可重试情形）；2 用法 / 配置错误。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# 强制 UTF-8 输出，避免 Windows 控制台/管道编码导致中文乱码；Linux CI 上无害。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DEFAULT = "."
QUEUE_DEFAULT = "_tmp/fulltext-queue.json"
CACHE_DEFAULT = "_tmp/fulltext-cache.json"
TMP_DIR_DEFAULT = "_tmp/fulltext"
MANIFEST_REL = "_unpublished/文库/manifest.json"
INDEX_REL = ".sources/index.json"
PAPERS_REL = "_data/papers.json"
SOURCES_PY = "_tools/sources.py"

OCR_MIN_CHARS = 500
OCR_MAX_PAGES = 60
OCR_TESSDATA_REL = "_tmp/tessdata"
TESSERACT_CANDIDATES = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
)
OCR_LANG_MAP = {
    "en": "eng", "eng": "eng", "english": "eng",
    "es": "spa", "spa": "spa", "spanish": "spa",
    "zh": "chi_sim", "zh-cn": "chi_sim", "zh_cn": "chi_sim",
    "zh-hans": "chi_sim", "cn": "chi_sim", "chi": "chi_sim", "chinese": "chi_sim",
}

DOWNLOAD_TIMEOUT = 60
POLITE_DELAY = 0.2
MAX_TRIES = 2
# 仅存摘要、全文仍可重试的标记（区别于已拿到全文的「已归档」）
RETRYABLE_STATUSES = ("abstract-no-oa", "abstract-download-failed")


class Budget:
    """网络时间预算：limit<=0 表示不限时。"""

    def __init__(self, seconds: int):
        self.limit = seconds or 0
        self.start = time.monotonic()

    def used(self) -> float:
        return time.monotonic() - self.start

    def ok(self) -> bool:
        return self.limit <= 0 or self.used() < self.limit


def _norm_doi(doi: str) -> str:
    d = (doi or "").strip().lower()
    for pre in ("https://doi.org/", "http://doi.org/",
                "https://dx.doi.org/", "http://dx.doi.org/", "doi:"):
        if d.startswith(pre):
            d = d[len(pre):]
    return d


def _doi_slug(doi: str, title) -> str:
    """文库子目录名：优先用 DOI（唯一），避免标题截断/同名导致两篇论文落到同一目录互相覆盖。"""
    d = _norm_doi(doi)
    return d if d else (str(title or "paper"))


def _to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _entry_fulltext_status(rec: dict) -> str:
    """从一条 manifest/索引记录里读出 fulltext_status（manifest 在 meta 里，索引在顶层）。"""
    return str((rec.get("meta") or {}).get("fulltext_status")
               or rec.get("fulltext_status") or "").strip()


def _doi_keys(rec: dict) -> list:
    """从一条 manifest/索引记录里取出规范化 DOI（0-1 个）。"""
    key = rec.get("canonical_key") or ""
    if key.startswith("doi:"):
        return [key[4:].lower()]
    doi = rec.get("doi") or (rec.get("meta") or {}).get("doi")
    if doi:
        return [_norm_doi(doi)]
    return []


def _archived_dois(root: Path) -> set:
    """返回「已有全文或来源记录、不应再重试」的 DOI 集合。

    摘要存档（fulltext_status 为 abstract-*）不算已归档：会重试，但优先级靠后。
    """
    seen = set()
    for rel in (MANIFEST_REL, INDEX_REL):
        data = _load_json(root / rel)
        if not data:
            continue
        records = data.get("books") if rel == MANIFEST_REL else data.get("sources")
        for rec in records or []:
            if _entry_fulltext_status(rec) in RETRYABLE_STATUSES:
                continue
            for k in _doi_keys(rec):
                seen.add(k)
    return seen


def _retryable_dois(root: Path) -> set:
    """返回「已存摘要、全文仍待重试」的 DOI 集合（无 OA 或下载失败）。"""
    retry = set()
    for rel in (MANIFEST_REL, INDEX_REL):
        data = _load_json(root / rel)
        if not data:
            continue
        records = data.get("books") if rel == MANIFEST_REL else data.get("sources")
        for rec in records or []:
            if _entry_fulltext_status(rec) in RETRYABLE_STATUSES:
                for k in _doi_keys(rec):
                    retry.add(k)
    return retry


def _load_papers(root: Path) -> list:
    data = _load_json(root / PAPERS_REL)
    if not data:
        return []
    out = []
    for genus in (data.get("genera") or {}).values():
        for p in genus.get("papers") or []:
            if not p.get("doi"):
                continue
            out.append({
                "doi": p["doi"],
                "title": p.get("title") or "",
                "year": _to_int(p.get("year")),
                "authors": p.get("authors") or [],
                "venue": p.get("venue") or "",
                "type": p.get("type") or "",
                "language": p.get("language") or "",
                "cited_by": p.get("cited_by") or 0,
                "oa_url": p.get("oa_url") or "",
                "abstract": p.get("abstract") or "",
                "abstract_source": p.get("abstract_source") or "",
            })
    return out


def _discover_candidates(root: Path, limit: int) -> list:
    archived = _archived_dois(root)
    retryable = _retryable_dois(root)
    seen = set()
    cands = []
    for p in _load_papers(root):
        if not (p.get("oa_url") or (p.get("abstract") or "").strip()):
            continue
        key = _norm_doi(p["doi"])
        if key in archived or key in seen:
            continue
        seen.add(key)
        cands.append(p)
    # 未试过的论文优先；仅存摘要待重试的往后排
    cands.sort(key=lambda x: (1 if _norm_doi(x.get("doi") or "") in retryable else 0,
                               -(x.get("cited_by") or 0), -(x.get("year") or 0)))
    return cands[:limit]


def _merge_queue(root: Path, queue_path: Path, cands: list) -> list:
    existing = _load_json(queue_path)
    if not isinstance(existing, list):
        existing = []
    by_doi = {}
    for it in existing:
        if isinstance(it, dict) and it.get("doi"):
            by_doi[_norm_doi(it["doi"])] = it
    for p in cands:
        by_doi[_norm_doi(p["doi"])] = p
    merged = list(by_doi.values())
    retryable = _retryable_dois(root)
    # 未试过的论文优先；仅存摘要待重试的往后排
    merged.sort(key=lambda x: (1 if _norm_doi(x.get("doi") or "") in retryable else 0,
                                -(x.get("cited_by") or 0), -(x.get("year") or 0)))
    _save_json(queue_path, merged)
    return merged


def _http_get(url: str, mailto: str, accept=None, timeout: int = DOWNLOAD_TIMEOUT):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; termite-checklist-fulltext/1.0; mailto:" + mailto + ")",
        "Accept": accept or "*/*",
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(1, MAX_TRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                hdrs = {k: v for k, v in resp.headers.items()}
                return resp.status, body, resp.geturl(), hdrs
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403, 404, 410, 429, 451):
                try:
                    return e.code, e.read(), url, dict(e.headers)
                except Exception:
                    return e.code, b"", url, {}
            time.sleep(1.5 * attempt)
        except Exception:
            time.sleep(1.5 * attempt)
    return None, b"", url, {}


def _unpaywall(doi: str, mailto: str):
    url = "https://api.unpaywall.org/v2/" + urllib.parse.quote(doi) + "?email=" + urllib.parse.quote(mailto)
    st, body, _, _ = _http_get(url, mailto)
    if st != 200:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


def _openalex(doi: str, mailto: str, api_key: str):
    params = {"mailto": mailto}
    if api_key:
        params["api_key"] = api_key
    url = ("https://api.openalex.org/works/doi:" + urllib.parse.quote(_norm_doi(doi))
           + "?" + urllib.parse.urlencode(params))
    st, body, _, _ = _http_get(url, mailto)
    if st != 200:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


def _europepmc(doi: str, mailto: str):
    query = 'DOI:"' + doi + '"'
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urllib.parse.urlencode({"query": query, "format": "json", "resultType": "core"}))
    st, body, _, _ = _http_get(url, mailto)
    if st != 200:
        return None
    try:
        data = json.loads(body.decode("utf-8"))
        hits = (data.get("resultList") or {}).get("result") or []
    except Exception:
        return None
    if not hits:
        return None
    hit = hits[0]
    pmcid = hit.get("pmcid")
    if not pmcid:
        return None
    # isOpenAccess 字段在老文献上不可靠（PMC 全文常标 N），不据此判断；
    # 以 fullTextXML 端点能否返回正文为准（该端点只服务 OA 全文，非 OA 会 404）。
    authors = []
    for a in (hit.get("authorList") or {}).get("author") or []:
        nm = a.get("fullName") if isinstance(a, dict) else None
        if nm:
            authors.append(nm)
    jinfo = hit.get("journalInfo") or {}
    venue = ""
    if isinstance(jinfo, dict):
        venue = (jinfo.get("journal") or {}).get("title") or ""
    return {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/" + pmcid + "/fullTextXML",
        "kind": "xml",
        "source": "europepmc",
        "title": hit.get("title") or "",
        "year": _to_int(hit.get("pubYear")),
        "authors": authors,
        "venue": venue,
        "license": hit.get("license"),
    }


def resolve(doi: str, item: dict, mailto: str, api_key: str, budget: Budget):
    """返回可下载的 OA 全文（PDF 或 JATS XML），查不到合法 OA 全文返回 None。"""
    d = _norm_doi(doi)
    meta = {
        "doi": doi,
        "title": item.get("title") or "",
        "year": _to_int(item.get("year")),
        "authors": [a for a in (item.get("authors") or []) if a],
        "venue": item.get("venue") or "",
        "publisher": item.get("publisher") or "",
        "type": item.get("type") or "",
        "language": item.get("language") or "",
        "license": item.get("license"),
        "genre": None,
        "landing": item.get("oa_url") or ("https://doi.org/" + d),
        "source": None,
        "kind": None,
        "url": None,
    }
    # 1. 队列里显式给的 URL
    if item.get("url"):
        meta["url"] = item["url"]
        meta["kind"] = "xml" if _looks_xml(item["url"]) else "pdf"
        meta["source"] = "queue"
        return meta
    # 2. Unpaywall
    pdf_url = None
    pdf_source = None
    unp = _unpaywall(doi, mailto) if mailto else None
    if unp and unp.get("is_oa"):
        best = unp.get("best_oa_location") or {}
        if best.get("url_for_pdf"):
            pdf_url = best["url_for_pdf"]
            pdf_source = "unpaywall"
        meta["title"] = meta["title"] or (unp.get("title") or "")
        meta["year"] = meta["year"] or _to_int(unp.get("year"))
        meta["genre"] = unp.get("genre")
        meta["publisher"] = meta["publisher"] or (unp.get("publisher") or "")
        meta["venue"] = meta["venue"] or (unp.get("journal_name") or "")
        meta["license"] = meta["license"] or best.get("license")
        if not meta["authors"] and unp.get("z_authors"):
            meta["authors"] = [" ".join(x for x in (a.get("given"), a.get("family")) if x)
                               for a in unp["z_authors"]]
        if best.get("url_for_landing_page"):
            meta["landing"] = best["url_for_landing_page"]
    # 3. OpenAlex
    oa = _openalex(doi, mailto, api_key)
    if oa:
        meta["title"] = meta["title"] or (oa.get("title") or "")
        meta["year"] = meta["year"] or _to_int(oa.get("publication_year"))
        meta["type"] = meta["type"] or (oa.get("type") or "")
        meta["language"] = meta["language"] or (oa.get("language") or "")
        if not meta["authors"] and oa.get("authorships"):
            meta["authors"] = [a.get("author", {}).get("display_name") or ""
                               for a in oa["authorships"]
                               if (a.get("author") or {}).get("display_name")]
        src = (oa.get("primary_location") or {}).get("source") or {}
        meta["venue"] = meta["venue"] or (src.get("display_name") or "")
        meta["publisher"] = meta["publisher"] or (src.get("host_organization_name") or "")
        bol = oa.get("best_oa_location") or {}
        if bol.get("pdf_url") and not pdf_url:
            pdf_url = bol["pdf_url"]
            pdf_source = "openalex"
        if not pdf_url:
            for loc in oa.get("locations") or []:
                if loc.get("pdf_url"):
                    pdf_url = loc["pdf_url"]
                    pdf_source = "openalex"
                    break
        if not meta["license"]:
            for loc in [bol] + list(oa.get("locations") or []):
                if loc.get("license"):
                    meta["license"] = loc["license"]
                    break
        oa_url = (oa.get("open_access") or {}).get("oa_url")
        if oa_url:
            meta["landing"] = oa_url
    # 4. Europe PMC（JATS 更干净，优先于出版社 PDF）
    pmc = _europepmc(doi, mailto)
    if pmc:
        meta["title"] = meta["title"] or pmc.get("title") or ""
        meta["year"] = meta["year"] or pmc.get("year")
        meta["venue"] = meta["venue"] or pmc.get("venue") or ""
        meta["license"] = meta["license"] or pmc.get("license")
        if not meta["authors"]:
            meta["authors"] = pmc.get("authors") or []
        meta["url"] = pmc["url"]
        meta["kind"] = "xml"
        meta["source"] = "europepmc"
        return meta
    if pdf_url:
        meta["url"] = pdf_url
        meta["kind"] = "pdf"
        meta["source"] = pdf_source or "openalex"
        return meta
    return None


def _looks_xml(u: str) -> bool:
    return u.lower().endswith(".xml") or "fulltextxml" in u.lower()


def _ext_from(url: str, ctype: str, hint: str) -> str:
    c = (ctype or "").lower()
    if "pdf" in c:
        return ".pdf"
    if "xml" in c:
        return ".xml"
    p = urllib.parse.urlparse(url).path.lower()
    if p.endswith(".pdf"):
        return ".pdf"
    if p.endswith(".xml"):
        return ".xml"
    return ".xml" if hint == "xml" else ".pdf"


def _download(url: str, kind: str, mailto: str, dest: Path):
    accept = "application/pdf,application/xml,text/xml,*/*"
    st, body, final_url, headers = _http_get(url, mailto, accept=accept)
    if st != 200 or not body:
        return None, final_url, ""
    ctype = headers.get("Content-Type") or headers.get("content-type") or ""
    if kind == "pdf" and "html" in ctype.lower():
        return None, final_url, ctype
    ext = _ext_from(final_url, ctype, kind)
    path = dest / ("fulltext" + ext)
    path.write_bytes(body)
    return path, final_url, ctype


def _reliability(meta: dict) -> str:
    t = (meta.get("type") or "").lower()
    g = (meta.get("genre") or "").lower()
    u = (meta.get("url") or "").lower()
    preprint_hint = any(s in u for s in ("arxiv.org", "biorxiv.org", "medrxiv.org", "chemrxiv",
                                         "researchsquare.com", "preprints.org", "ssrn.com",
                                         "osf.io/preprints"))
    if t == "preprint" or g == "preprint" or preprint_hint:
        return "unverified"
    if t == "book-chapter":
        return "reference"
    if t in ("article", "review") or g in ("journal-article", "article"):
        return "peer_reviewed"
    return "unverified"


def _notes(meta: dict) -> str:
    src = meta.get("source") or "oa"
    kind = str(meta.get("kind") or "").upper()
    return ("OA 全文自动归档（" + src + " " + kind + "）；全文只存本地文库供检索，"
            "不发布、不对外分发。标题/作者/年份取自开放元数据，引用以出版方原文为准。")


def _find_tesseract(cmd_hint=None):
    if cmd_hint:
        p = Path(cmd_hint).expanduser()
        if p.is_file():
            return str(p)
    found = shutil.which("tesseract")
    if found:
        return found
    for cand in TESSERACT_CANDIDATES:
        if Path(cand).is_file():
            return cand
    env = os.environ.get("TESSERACT_CMD")
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return str(p)
    return None


def _resolve_tessdata(root, explicit):
    if explicit:
        return explicit
    td = root / OCR_TESSDATA_REL
    if td.is_dir() and any(td.glob("*.traineddata")):
        return str(td)
    return None


def _ocr_lang(language, override):
    if override:
        return override
    return OCR_LANG_MAP.get((language or "").strip().lower(), "eng")


def _probe_pdf_text(pdf_path, max_pages=10):
    try:
        import fitz  # noqa: F401
    except ImportError:
        return -1
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return -1
    total = 0
    try:
        for page in doc:
            total += len((page.get_text("text") or "").strip())
            if page.number + 1 >= max_pages:
                break
    finally:
        doc.close()
    return total


def _ocr_pdf(pdf_path, tess_cmd, tessdata, lang, out_txt, max_pages):
    try:
        import fitz
    except ImportError:
        return 1, "pymupdf 不可用，无法渲染 PDF 页"
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        return 1, "无法打开 PDF：" + str(e)
    parts = []
    try:
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            png = out_txt.parent / ("ocr-page-%03d.png" % (i + 1))
            try:
                pix = page.get_pixmap(dpi=300)
                pix.save(str(png))
                cmd = [tess_cmd, str(png), "stdout", "-l", lang]
                if tessdata:
                    cmd += ["--tessdata-dir", tessdata]
                r = subprocess.run(cmd, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=240)
                if r.returncode != 0:
                    return 1, "tesseract 失败（第 " + str(i + 1) + " 页）：" + (r.stderr or "").strip()[:160]
                parts.append(r.stdout or "")
            finally:
                try:
                    png.unlink()
                except OSError:
                    pass
    finally:
        doc.close()
    text = "\n\n".join(parts).strip()
    if len(text) < 50:
        return 1, "OCR 结果过短（" + str(len(text)) + " 字），可能不是可读扫描件"
    out_txt.write_text(text, encoding="utf-8", newline="\n")
    return 0, str(len(text))


def _ingest(root: Path, tmpfile: Path, meta: dict, text_path=None, ocr_note=None):
    doi = meta.get("doi") or ""
    cmd = [sys.executable, str(root / SOURCES_PY), "--root", str(root), "library-add",
           "--file", str(tmpfile),
           "--title", (meta.get("title") or doi).strip(),
           "--slug", _doi_slug(doi, meta.get("title")),
           "--doi", doi,
           "--kind", "paper",
           "--reliability", _reliability(meta),
           "--url", meta.get("landing") or ("https://doi.org/" + _norm_doi(doi)),
           "--notes", ocr_note or _notes(meta)]
    if text_path:
        cmd += ["--text", str(text_path)]
    if meta.get("year"):
        cmd += ["--year", str(meta["year"])]
    if meta.get("authors"):
        cmd += ["--authors", "; ".join(str(a) for a in meta["authors"] if str(a).strip())]
    pub = meta.get("publisher") or meta.get("venue") or ""
    if pub:
        cmd += ["--publisher", pub]
    if meta.get("language"):
        cmd += ["--lang", meta["language"]]
    if meta.get("license"):
        cmd += ["--license", meta["license"]]
    try:
        r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)
    return r.returncode, r.stdout or "", r.stderr or ""


def _ingest_abstract(root: Path, item: dict, tmp_dir: Path, fulltext_status: str = "abstract-no-oa"):
    """无 OA 全文 / 下载失败时，把完整摘要作为「摘要全文」存进文库（不截断），.sources/ 记元数据。

    摘要全文进 _unpublished/文库/<slug>/full.txt（gitignored），账本 .sources/ 只留元数据 +
    短摘录，符合 AGENTS.md §1.6 红线（单处 ≤400 字、累计 ≤2000 字）。
    fulltext_status 标记「仅摘要、全文待重试」，让以后还能重试找全文。
    """
    abstract = " ".join((item.get("abstract") or "").split())
    if not abstract:
        return 1, "", "无摘要"
    src = (item.get("abstract_source") or "unknown").strip()
    doi = (item.get("doi") or "").strip()
    stem = (_norm_doi(doi) or (item.get("title") or "abstract")).replace("/", "_").replace(":", "_")[:80]
    txt = tmp_dir / (stem + "-abstract.txt")
    txt.write_text(abstract, encoding="utf-8", newline="\n")
    reason = "下载失败" if fulltext_status == "abstract-download-failed" else "无 OA 全文"
    notes = (reason + "，仅存完整摘要（" + str(len(abstract)) + " 字，abstract_source=" + src
             + "）。摘要全文存于本地文库供检索，不发布、不对外分发；引用以出版方原文为准。")
    cmd = [sys.executable, str(root / SOURCES_PY), "--root", str(root), "library-add",
           "--file", str(txt),
           "--title", (item.get("title") or doi or "摘要").strip(),
           "--slug", _doi_slug(doi, item.get("title")),
           "--kind", "paper",
           "--reliability", _reliability({"type": item.get("type") or "",
                                          "url": item.get("oa_url") or ""}),
           "--fulltext-status", fulltext_status,
           "--notes", notes]
    if doi:
        cmd += ["--doi", doi]
    if item.get("year"):
        cmd += ["--year", str(item["year"])]
    if item.get("authors"):
        cmd += ["--authors", "; ".join(str(a) for a in item["authors"] if str(a).strip())]
    pub = (item.get("venue") or "").strip()
    if pub:
        cmd += ["--publisher", pub]
    if item.get("language"):
        cmd += ["--lang", item["language"]]
    try:
        r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)
    try:
        txt.unlink()
    except OSError:
        pass
    return r.returncode, r.stdout or "", r.stderr or ""


def run_check(root: Path, args) -> int:
    archived = _archived_dois(root)
    papers = _load_papers(root)
    oa_entries = [p for p in papers if p.get("oa_url")]
    seen = set()
    unarchived = []
    for p in papers:
        if not p.get("oa_url"):
            continue
        key = _norm_doi(p["doi"])
        if key in archived or key in seen:
            continue
        seen.add(key)
        unarchived.append(p)
    unarchived.sort(key=lambda x: (-(x.get("cited_by") or 0), -(x.get("year") or 0)))
    print("[fulltext] 已归档 DOI（文库 + 账本）：" + str(len(archived)))
    print("[fulltext] papers.json 带 OA 标记的条目：" + str(len(oa_entries))
          + "；去重后未归档：" + str(len(unarchived)))
    qp = root / args.queue
    if qp.exists():
        q = _load_json(qp)
        if q is None:
            print("[fulltext] 队列 " + args.queue + " 解析失败", file=sys.stderr)
            return 2
        q = q if isinstance(q, list) else []
        q_un = [it for it in q if isinstance(it, dict) and it.get("doi")
                and _norm_doi(it["doi"]) not in archived]
        print("[fulltext] 队列 " + args.queue + "：" + str(len(q)) + " 条，其中未归档 " + str(len(q_un)) + " 条")
    else:
        print("[fulltext] 队列 " + args.queue + " 不存在（用 --discover N 生成）")
    n = args.discover or 10
    for i, p in enumerate(unarchived[:n]):
        t = (p.get("title") or "").strip()
        print("[fulltext]   候选 {:>3}. {:<60s} doi:{} cited:{}".format(
            i + 1, t[:60], p.get("doi"), p.get("cited_by") or 0))
    return 0


def run_discover(root: Path, args) -> int:
    cands = _discover_candidates(root, args.discover or 20)
    merged = _merge_queue(root, root / args.queue, cands)
    print("[fulltext] 已写入队列 " + args.queue + "：共 " + str(len(merged)) + " 条（本次新增候选 " + str(len(cands)) + "）")
    for i, p in enumerate(cands):
        t = (p.get("title") or "").strip()
        print("[fulltext]   候选 {:>3}. {:<60s} doi:{} cited:{}".format(
            i + 1, t[:60], p.get("doi"), p.get("cited_by") or 0))
    return 0


def run_write(root: Path, args) -> int:
    mailto = (os.environ.get("UNPAYWALL_EMAIL") or os.environ.get("OPENALEX_MAILTO")
              or os.environ.get("CROSSREF_MAILTO") or "").strip()
    api_key = (os.environ.get("OPENALEX_API_KEY") or "").strip()
    if not mailto:
        print("[fulltext] 提示：未设 UNPAYWALL_EMAIL / OPENALEX_MAILTO，将跳过 Unpaywall"
              "（Europe PMC / OpenAlex 仍可用）", file=sys.stderr)
    if args.discover:
        _merge_queue(root, root / args.queue, _discover_candidates(root, args.discover))
    queue = _load_json(root / args.queue)
    if not isinstance(queue, list) or not queue:
        print("[fulltext] 队列为空：先 --discover N 生成候选", file=sys.stderr)
        return 2
    archived = _archived_dois(root)
    retryable = _retryable_dois(root)
    cache = _load_json(root / args.cache)
    if not isinstance(cache, dict):
        cache = {}
    budget = Budget(args.time_budget)
    tmp_dir = root / args.tmp
    tmp_dir.mkdir(parents=True, exist_ok=True)
    processed = archived_ok = abstract_ok = skipped = recent = no_oa = errors = scanned = 0
    for it in queue:
        if not isinstance(it, dict) or not it.get("doi"):
            continue
        doi = it["doi"]
        key = _norm_doi(doi)
        if key in archived:
            skipped += 1
            continue
        prev = cache.get(key)
        if not args.force and isinstance(prev, dict) and prev.get("status") not in ("ok", "resolved"):
            age = time.time() - (prev.get("attempted_at") or 0)
            if args.stale_days and age < args.stale_days * 86400:
                recent += 1
                continue
        if args.limit and processed >= args.limit:
            break
        if not budget.ok():
            print("[fulltext] 时间预算用尽，停止")
            break
        processed += 1
        print("[fulltext] [" + str(processed) + "] doi:" + doi)
        meta = resolve(doi, it, mailto, api_key, budget)
        if not meta or not meta.get("url"):
            if key in retryable:
                skipped += 1
                print("[fulltext]   仍无 OA 全文，保留既有摘要（标记可重试）")
                continue
            if not (it.get("abstract") or "").strip():
                no_oa += 1
                cache[key] = {"status": "no-fulltext", "attempted_at": time.time(),
                              "error": "无 OA 全文且无摘要"}
                print("[fulltext]   跳过：无 OA 全文且无摘要")
                continue
            if args.dry_run:
                abstract_ok += 1
                print("[fulltext]   [dry-run] 无 OA 全文，将存摘要（"
                      + str((it.get("abstract_source") or "?")) + "）")
                continue
            rc2, out2, err2 = _ingest_abstract(root, it, tmp_dir, fulltext_status="abstract-no-oa")
            if rc2 == 0:
                abstract_ok += 1
                archived.add(key)
                cache[key] = {"status": "abstract-archived", "attempted_at": time.time(),
                              "source": it.get("abstract_source") or "abstract"}
                print("[fulltext]   无 OA 全文，已存摘要（" + str((it.get("abstract_source") or "?")) + "）")
            else:
                no_oa += 1
                cache[key] = {"status": "no-fulltext", "attempted_at": time.time(),
                              "error": ("摘要归档失败：" + ((err2 or out2) or "").strip()[:200])}
                print("[fulltext]   摘要归档失败：" + ((err2 or out2) or "").strip()[:160])
            continue
        if args.dry_run:
            archived_ok += 1
            cache[key] = {"status": "resolved", "source": meta.get("source"),
                          "kind": meta.get("kind"), "url": meta.get("url"),
                          "attempted_at": time.time()}
            print("[fulltext]   [dry-run] " + str(meta.get("source")) + " " + str(meta.get("kind")).upper()
                  + ": " + str(meta.get("url")))
            print("[fulltext]   [dry-run] " + str((meta.get("title") or "")[:90]))
            continue
        tmpfile, final_url, ctype = _download(meta["url"], meta.get("kind"), mailto, tmp_dir)
        if tmpfile is None:
            if key in retryable:
                errors += 1
                cache[key] = {"status": "error", "attempted_at": time.time(), "url": meta.get("url"),
                              "error": "下载仍失败（保留既有摘要，标记可重试）"}
                print("[fulltext]   下载仍失败，保留既有摘要（标记可重试）")
                continue
            if not (it.get("abstract") or "").strip():
                errors += 1
                cache[key] = {"status": "error", "attempted_at": time.time(), "url": meta.get("url"),
                              "error": "下载失败（content-type=" + ctype + "）"}
                print("[fulltext]   下载失败：" + str(meta.get("url")))
                continue
            rc2, out2, err2 = _ingest_abstract(root, it, tmp_dir, fulltext_status="abstract-download-failed")
            if rc2 == 0:
                abstract_ok += 1
                archived.add(key)
                cache[key] = {"status": "abstract-archived", "attempted_at": time.time(),
                              "url": meta.get("url"),
                              "source": it.get("abstract_source") or "abstract",
                              "retry": "download-failed"}
                print("[fulltext]   下载失败，已存摘要（标记 OA 待重试）")
            else:
                errors += 1
                cache[key] = {"status": "error", "attempted_at": time.time(), "url": meta.get("url"),
                              "error": ("下载失败且摘要归档失败：" + ((err2 or out2) or "").strip()[:200])}
                print("[fulltext]   下载失败且摘要归档失败：" + ((err2 or out2) or "").strip()[:160])
            continue
        text_path = None
        ocr_note = None
        if meta.get("kind") == "pdf":
            probed = _probe_pdf_text(tmpfile)
            if 0 <= probed < OCR_MIN_CHARS:
                tess = _find_tesseract(args.tesseract_cmd)
                if not tess:
                    scanned += 1
                    cache[key] = {"status": "scanned-needs-ocr", "attempted_at": time.time(),
                                  "url": meta.get("url"),
                                  "error": "扫描件（文字层 " + str(probed) + " 字），无 tesseract"}
                    print("[fulltext]   扫描件（文字层 " + str(probed) + " 字），无 tesseract，跳过")
                    try:
                        tmpfile.unlink()
                    except OSError:
                        pass
                    continue
                lang = _ocr_lang(meta.get("language") or "", args.ocr_langs)
                td = _resolve_tessdata(root, args.tessdata_dir)
                ocr_txt = tmp_dir / (tmpfile.stem + "-ocr.txt")
                rc_ocr, info = _ocr_pdf(tmpfile, tess, td, lang, ocr_txt, args.ocr_max_pages)
                if rc_ocr != 0:
                    errors += 1
                    cache[key] = {"status": "scanned-ocr-failed", "attempted_at": time.time(),
                                  "url": meta.get("url"), "error": info[:300]}
                    print("[fulltext]   扫描件 OCR 失败：" + info[:160])
                    try:
                        tmpfile.unlink()
                    except OSError:
                        pass
                    continue
                text_path = ocr_txt
                ocr_note = ("扫描件（无文字层），经 tesseract OCR（语言 " + lang + "）转为文本入库，"
                            "未经人工校对，引用前须核对出版方原文。全文只存本地文库，不发布、不对外分发。")
                print("[fulltext]   扫描件，已 OCR（" + lang + "，全文 " + info + " 字）")
        rc, out, err = _ingest(root, tmpfile, meta, text_path=text_path, ocr_note=ocr_note)
        if rc == 0:
            archived_ok += 1
            archived.add(key)
            cache[key] = {"status": "ok", "source": meta.get("source"), "kind": meta.get("kind"),
                          "url": meta.get("url"), "attempted_at": time.time()}
            print("[fulltext]   已归档（" + str(meta.get("source")) + " " + str(meta.get("kind")).upper() + "）")
            try:
                tmpfile.unlink()
            except OSError:
                pass
        else:
            errors += 1
            cache[key] = {"status": "error", "attempted_at": time.time(), "url": meta.get("url"),
                          "error": ((err or out) or "library-add 失败").strip()[:300]}
            print("[fulltext]   library-add 失败：" + ((err or out) or "").strip()[:200])
        time.sleep(POLITE_DELAY)
    _save_json(root / args.cache, cache)
    print("[fulltext] 完成：处理 " + str(processed) + "，归档全文 " + str(archived_ok)
          + "，存档摘要 " + str(abstract_ok)
          + "，扫描件跳过 " + str(scanned)
          + "，跳过已归档 " + str(skipped) + "，近期已试 " + str(recent)
          + "，无 OA 且无摘要 " + str(no_oa) + "，出错 " + str(errors))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="OA 全文爬取 + 归档（见 _tools/原文归档工作流说明.md）")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--queue", default=QUEUE_DEFAULT)
    ap.add_argument("--cache", default=CACHE_DEFAULT)
    ap.add_argument("--tmp", default=TMP_DIR_DEFAULT)
    ap.add_argument("--discover", type=int, metavar="N", default=None,
                    help="从 papers.json 挑选被引最高的 N 条未归档 OA 论文进队列")
    ap.add_argument("--limit", type=int, default=0, help="单次最多处理几条（0=不限）")
    ap.add_argument("--time-budget", type=int, default=300, help="网络时间预算（秒；0=不限）")
    ap.add_argument("--stale-days", type=int, default=30, help="失败条目多少天内不重试")
    ap.add_argument("--force", action="store_true", help="忽略失败缓存，全部重试")
    ap.add_argument("--dry-run", action="store_true", help="只解析 OA 链接，不下载、不入库")
    ap.add_argument("--tesseract-cmd", default=None, help="tesseract 可执行文件路径（缺省自动探测）")
    ap.add_argument("--tessdata-dir", default=None, help="语言数据目录（缺省自动探测 _tmp/tessdata 或系统默认）")
    ap.add_argument("--ocr-langs", default=None, help="扫描件 OCR 语言（缺省按论文 language 自动映射）")
    ap.add_argument("--ocr-max-pages", type=int, default=OCR_MAX_PAGES, help="扫描件最多 OCR 页数")
    ap.add_argument("--check", action="store_true", help="离线校验 + 计划（只读）")
    ap.add_argument("--write", action="store_true", help="执行爬取 + 归档")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if args.check:
        return run_check(root, args)
    if args.write or args.dry_run:
        return run_write(root, args)
    if args.discover:
        return run_discover(root, args)
    build_parser().print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
