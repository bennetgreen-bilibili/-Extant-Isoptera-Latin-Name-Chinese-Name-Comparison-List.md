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
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# 强制 UTF-8 输出，避免 Windows 控制台/管道编码导致中文乱码；Linux CI 上无害。
# line_buffering：CI 日志按行落地，时间戳才能反映真实的慢步骤位置。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
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
CANDIDATE_TIMEOUT = 25      # 单个候选 URL 的超时：站点级拦截（403/HTML）通常秒回，等 60s 是浪费
PER_PAPER_SECONDS = 90      # 单篇所有候选合计的耗时上限
POLITE_DELAY = 0.2
MAX_TRIES = 2
MAX_CANDIDATES = 5          # 每篇最多尝试的候选 URL 数（超过就放弃，不再逐站试错）
HOSTS_REL = "_data/fulltext_hosts.json"
HOST_BLOCK_AFTER = 3        # 同一 host 连续硬失败 N 次 → 冷却，不再逐篇撞墙
HOST_COOLDOWN_DAYS = 120
HARD_FAIL_CODES = (400, 401, 403, 404, 405, 410, 451)   # 站点级拒绝/资源失效，重试同一 host 无意义
# 仅存摘要、全文仍可重试的标记（区别于已拿到全文的「已归档」）
#   abstract-no-oa     ：查不到任何 OA 全文候选，或 OA 只给落地页、页面也没自报 PDF 直链
#   abstract-blocked   ：有候选，但全部被站点拦截/资源已下架（换 IP 也多半无效，长冷却）
#   abstract-download-failed：瞬时失败（超时/5xx/返回网页），短冷却
RETRYABLE_STATUSES = ("abstract-no-oa", "abstract-blocked", "abstract-download-failed")
NEXT_TRY_DAYS = {"abstract-blocked": 180, "abstract-download-failed": 21, "abstract-no-oa": 120}


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
        # utf-8-sig：Windows 上手工用 PowerShell/记事本存的 json 常带 BOM
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
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
    # 摘要存档条目即使 manifest 里仍有同名记录，也应可重试：本地 vault 无法解包打标记，
    # 故用「已归档集合 - 重试集合」让 .sources/ 里的 fulltext_status 标记压过 manifest。
    seen -= _retryable_dois(root)
    return seen


def _fulltext_dois(root: Path) -> set:
    """返回「文库里有真全文」的 DOI 集合。

    判据：manifest 条目带 `book`（= 已落进 `_unpublished/文库/` 的目录名），且该条目的
    `meta.fulltext_status` 不是 abstract-*。摘要入库的条目也算有 book，所以要靠状态区分——
    否则人工补下全文后，旧的「abstract-blocked」条目会让这篇永远留在待人工清单里。
    """
    data = _load_json(root / MANIFEST_REL) or {}
    full = set()
    for rec in data.get("books") or []:
        if not rec.get("book"):
            continue
        if _entry_fulltext_status(rec) in RETRYABLE_STATUSES:
            continue
        for k in _doi_keys(rec):
            full.add(k)
    return full


def _retryable_dois(root: Path) -> set:
    """返回「已存摘要、全文仍待重试」的 DOI 集合（无 OA 或下载失败）。

    同一 DOI 只要有一条「真有全文」的文库记录，就不再算待重试：人工补下之后状态必须是
    单向的（下到即可，不会因为旧的 abstract-* 条目又退回重试队列）。
    """
    retry = set()
    full = _fulltext_dois(root)
    for rel in (MANIFEST_REL, INDEX_REL):
        data = _load_json(root / rel)
        if not data:
            continue
        records = data.get("books") if rel == MANIFEST_REL else data.get("sources")
        for rec in records or []:
            if _entry_fulltext_status(rec) in RETRYABLE_STATUSES:
                for k in _doi_keys(rec):
                    retry.add(k)
    return retry - full


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
        "pmcid": pmcid,
        "title": hit.get("title") or "",
        "year": _to_int(hit.get("pubYear")),
        "authors": authors,
        "venue": venue,
        "license": hit.get("license"),
    }


def _host_of(url: str) -> str:
    try:
        return (urllib.parse.urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def _norm_url(u: str) -> str:
    u = (u or "").strip()
    if u.startswith("http://"):
        u = "https://" + u[7:]
    return u.rstrip("/")


def _cand(url: str, kind: str, source: str, host_type: str = "", version: str = "") -> dict:
    return {"url": url.strip(), "kind": kind, "source": source, "host": _host_of(url),
            "host_type": host_type, "version": version}


def _load_hosts(root: Path) -> dict:
    data = _load_json(root / HOSTS_REL)
    return data if isinstance(data, dict) else {}


def _save_hosts(root: Path, hosts: dict) -> None:
    _save_json(root / HOSTS_REL, hosts)


def _host_blocked(hosts: dict, host: str) -> bool:
    st = hosts.get(host) or {}
    until = st.get("blocked_until") or 0
    return bool(until and time.time() < until)


def _note_host_fail(hosts: dict, host: str, reason: str) -> None:
    """记一次站点级硬失败；连续 HOST_BLOCK_AFTER 次 → 冷却 HOST_COOLDOWN_DAYS 天。"""
    if not host:
        return
    st = hosts.get(host) or {}
    st["fails"] = int(st.get("fails") or 0) + 1
    st["last"] = time.time()
    st["last_reason"] = reason[:120]
    if st["fails"] >= HOST_BLOCK_AFTER:
        st["blocked_until"] = time.time() + HOST_COOLDOWN_DAYS * 86400
    hosts[host] = st


def _note_host_ok(hosts: dict, host: str) -> None:
    if not host:
        return
    hosts[host] = {"fails": 0, "blocked_until": 0, "last": time.time(), "last_reason": "ok"}


# 站点迁移：旧域名已失效，同一篇 OA 文章在出版方新域名下仍可直接下载。
# 只做「同一篇文章换个官方域名」，不构造任何未公开的下载地址。
def _derived_candidates(doi: str, cands: list) -> list:
    d = _norm_doi(doi)
    out = []
    for c in list(cands):
        if c["host"].endswith("downloads.hindawi.com") and d.startswith("10.1155/"):
            out.append(_cand("https://onlinelibrary.wiley.com/doi/pdfdirect/" + d, "pdf",
                             "wiley-migrated"))
    return out


_META_PDF_RES = (
    r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',
    r'<link[^>]+type=["\']application/pdf["\'][^>]+href=["\']([^"\']+)',
)


def _pdf_link_from_html(body: bytes, base_url: str):
    """落地页自己声明的「本文 PDF」（citation_pdf_url / alternate pdf）；没有就是没有。"""
    if not body:
        return None
    head = body[:300000].decode("utf-8", "replace")
    for rx in _META_PDF_RES:
        m = re.search(rx, head, re.I)
        if m:
            u = urllib.parse.urljoin(base_url, m.group(1).strip())
            return u if u.lower().startswith("http") else None
    return None


_SOURCE_PRIORITY = {"europepmc": 0, "unpaywall": 1, "europepmc-pdf": 2, "openalex": 3, "s2": 4,
                    "queue": 5, "html-meta": 6, "wiley-migrated": 7, "landing": 8}


def _order_candidates(cands: list, hosts: dict) -> list:
    """排序并去重：XML 优先（JATS 最干净）；冷却中的 host 排最后；仓储副本优先于出版社。"""
    def key(c):
        return (0 if c["kind"] == "xml" else 1,
                1 if _host_blocked(hosts, c["host"]) else 0,
                0 if c["host_type"] == "repository" else 1,
                _SOURCE_PRIORITY.get(c["source"], 9))
    out, seen = [], set()
    for c in sorted(cands, key=key):
        k = _norm_url(c["url"])
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out[:MAX_CANDIDATES]


def _s2_pdf(doi: str, mailto: str):
    """Semantic Scholar 的 openAccessPdf：只在其它源都没候选时补一刀（有速率限制）。"""
    url = ("https://api.semanticscholar.org/graph/v1/paper/DOI:"
           + urllib.parse.quote(_norm_doi(doi), safe="/:;()._-") + "?fields=openAccessPdf")
    st, body, _, _ = _http_get(url, mailto, accept="application/json", timeout=20)
    if st != 200 or not body:
        return None
    try:
        d = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    u = (d.get("openAccessPdf") or {}).get("url")
    return u or None


def _metadata_bundle(doi: str, mailto: str, api_key: str):
    """四路元数据并行取（原先串行要 4 个往返，是最费时间预算的一环）。"""
    with ThreadPoolExecutor(max_workers=4) as ex:
        fu = ex.submit(_unpaywall, doi, mailto) if mailto else None
        fo = ex.submit(_openalex, doi, mailto, api_key)
        fe = ex.submit(_europepmc, doi, mailto)
        fs = ex.submit(_s2_pdf, doi, mailto)
        out = []
        for f in (fu, fo, fe, fs):
            if f is None:
                out.append(None)
                continue
            try:
                out.append(f.result())
            except Exception:
                out.append(None)
    return out[0], out[1], out[2], out[3]


def resolve(doi: str, item: dict, mailto: str, api_key: str, budget: Budget, hosts=None):
    """返回候选 OA 全文清单（PDF / JATS XML，已排序），查不到任何合法 OA 全文返回 None。"""
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
    cands = []
    # 1. 队列里显式给的 URL
    if item.get("url"):
        cands.append(_cand(item["url"], "xml" if _looks_xml(item["url"]) else "pdf", "queue"))
    # 2. 三路元数据（并行）：Unpaywall 全部 oa_locations / OpenAlex 全部 locations / Europe PMC
    unp, oa, pmc, s2 = _metadata_bundle(doi, mailto, api_key)
    if unp and unp.get("is_oa"):
        best = unp.get("best_oa_location") or {}
        for loc in [best] + list(unp.get("oa_locations") or []):
            if isinstance(loc, dict) and loc.get("url_for_pdf"):
                cands.append(_cand(loc["url_for_pdf"], "pdf", "unpaywall",
                                   loc.get("host_type") or "", loc.get("version") or ""))
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
        for loc in [bol] + list(oa.get("locations") or []):
            if isinstance(loc, dict) and loc.get("pdf_url"):
                cands.append(_cand(loc["pdf_url"], "pdf", "openalex"))
        if not meta["license"]:
            for loc in [bol] + list(oa.get("locations") or []):
                if isinstance(loc, dict) and loc.get("license"):
                    meta["license"] = loc["license"]
                    break
        oa_url = (oa.get("open_access") or {}).get("oa_url")
        if oa_url:
            meta["landing"] = oa_url
    # 4. Europe PMC 的 JATS 全文（最干净；非 OA 时该端点 404，失败会自然回退到 PDF 候选）
    if pmc:
        meta["title"] = meta["title"] or pmc.get("title") or ""
        meta["year"] = meta["year"] or pmc.get("year")
        meta["venue"] = meta["venue"] or pmc.get("venue") or ""
        meta["license"] = meta["license"] or pmc.get("license")
        if not meta["authors"]:
            meta["authors"] = pmc.get("authors") or []
        cands.append(_cand(pmc["url"], "xml", "europepmc"))
        # JATS 端点挂掉时，同一篇还有 PMC 自己的 PDF 直链可退
        pmcid = pmc.get("pmcid")
        if pmcid:
            cands.append(_cand("https://europepmc.org/articles/" + pmcid + "/pdf",
                               "pdf", "europepmc-pdf"))
            cands.append(_cand("https://www.ncbi.nlm.nih.gov/pmc/articles/" + pmcid + "/pdf/",
                               "pdf", "europepmc-pdf"))
    # 5. 站点迁移（Hindawi → Wiley）与 Semantic Scholar（补一条，落地页也能靠 citation_pdf_url 救回）
    cands.extend(_derived_candidates(doi, cands))
    if s2:
        cands.append(_cand(s2, "pdf", "s2"))
    if meta.get("landing"):
        # 最后一招：PDF 直链被拦时，回官方落地页读 citation_pdf_url（Springer/PMC 等常见）
        cands.append(_cand(meta["landing"], "landing", "landing"))
    if not cands:
        return None
    meta["candidates"] = _order_candidates(cands, hosts if hosts is not None else {})
    meta["url"] = meta["candidates"][0]["url"]
    meta["kind"] = meta["candidates"][0]["kind"]
    meta["source"] = meta["candidates"][0]["source"]
    return meta


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


def _download(url: str, kind: str, mailto: str, dest: Path, timeout: int = CANDIDATE_TIMEOUT):
    """下载一个候选，返回 (path, final_url, ctype, status, html_pdf_hint)。

    失败时 path=None：status 是 HTTP 码（403/404…），None 表示网络异常/超时；
    html_pdf_hint 非空表示「返回的是网页，但网页自己声明了本文 PDF 地址」，可据此再试一次。
    """
    accept = "application/pdf,application/xml,text/xml,*/*"
    st, body, final_url, headers = _http_get(url, mailto, accept=accept, timeout=timeout)
    ctype = headers.get("Content-Type") or headers.get("content-type") or ""
    if st != 200 or not body:
        return None, final_url, ctype, st, None
    if kind == "landing":
        # 只探路：从官方落地页读「本文 PDF」地址，不落盘
        return None, final_url, ctype, st, _pdf_link_from_html(body, final_url)
    if kind == "pdf" and "html" in ctype.lower():
        return None, final_url, ctype, st, _pdf_link_from_html(body, final_url)
    ext = _ext_from(final_url, ctype, kind)
    path = dest / ("fulltext" + ext)
    path.write_bytes(body)
    return path, final_url, ctype, st, None


def _fetch_paper(meta: dict, mailto: str, dest: Path, hosts: dict, budget: Budget):
    """按候选顺序逐个试，直到拿到一份全文；返回 (path, final_url, ctype, report)。

    report: {"tried": [(url, 结果)], "reason": blocked|transient|html-page|per-paper-timeout,
             "hosts": [本轮硬失败的 host]}
    """
    report = {"tried": [], "reason": "", "hosts": []}
    saw = {"block": False, "html": False, "transient": False, "timeout": False, "no_link": False}
    queue = list(meta.get("candidates") or [])
    attempted = set()
    started = time.monotonic()
    tried = 0
    i = 0
    while i < len(queue):
        c = queue[i]
        i += 1
        if _host_blocked(hosts, c["host"]):
            # 冷却中的站点：连试都不试，省下的预算留给没撞过的站
            report["tried"].append((c["url"], "冷却中，跳过"))
            saw["block"] = True
            continue
        if tried >= MAX_CANDIDATES:
            break
        if _norm_url(c["url"]) in attempted:
            continue          # 落地页回指的地址可能就是刚失败的那条，别重撞
        if not budget.ok() or time.monotonic() - started > PER_PAPER_SECONDS:
            saw["timeout"] = True
            break
        tried += 1
        attempted.add(_norm_url(c["url"]))
        probe = c["kind"] == "landing"      # 落地页只探路，不落盘
        path, final_url, ctype, st, html_pdf = _download(c["url"], c["kind"], mailto, dest)
        if path is not None:
            _note_host_ok(hosts, c["host"])
            report["tried"].append((c["url"], "ok"))
            meta["url"] = c["url"]
            meta["kind"] = c["kind"]
            meta["source"] = c["source"]
            return path, final_url, ctype, report
        if html_pdf:
            report["tried"].append((c["url"], "HTML 页面→找到 PDF 地址"))
            extra = _cand(html_pdf, "pdf", "html-meta")
            if (_norm_url(extra["url"]) not in attempted
                    and all(_norm_url(x["url"]) != _norm_url(extra["url"]) for x in queue)):
                queue.insert(i, extra)   # 落地页声明的 PDF 地址，下一轮就试
            saw["html"] = True
            continue
        if probe:
            # OA 只给了落地页、页面又不自报 PDF 地址：有 OA 但没有可下载直链，
            # 不是「站点拦爬虫」，不该罚这个 host、也不该记成下载失败。
            report["tried"].append((c["url"], "落地页无 PDF 地址（" + str(st) + "）"))
            saw["no_link"] = True
            continue
        if st in HARD_FAIL_CODES:
            report["tried"].append((c["url"], "HTTP " + str(st)))
            _note_host_fail(hosts, c["host"], "HTTP " + str(st))
            report["hosts"].append(c["host"])
            saw["block"] = True
        elif "html" in (ctype or "").lower():
            report["tried"].append((c["url"], "返回网页非 PDF"))
            _note_host_fail(hosts, c["host"], "返回网页非 PDF")
            report["hosts"].append(c["host"])
            saw["html"] = True
        elif st is None:
            report["tried"].append((c["url"], "超时/网络异常"))
            saw["transient"] = True
        else:
            report["tried"].append((c["url"], "HTTP " + str(st) + " 空响应"))
            saw["transient"] = True
    # 分类优先级：被拦 > 网页拦路 > 无 PDF 直链 > 超预算 > 瞬时失败
    # （拦截类要长冷却，不能被先前的瞬时失败掩盖；「无直链」按「无 OA 全文」处理）
    if saw["block"]:
        report["reason"] = "blocked"
    elif saw["html"]:
        report["reason"] = "html-page"
    elif saw["no_link"]:
        report["reason"] = "no-pdf-link"
    elif saw["timeout"]:
        report["reason"] = "per-paper-timeout"
    else:
        report["reason"] = "transient"
    return None, "", "", report


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
    reason = {"abstract-download-failed": "下载失败",
              "abstract-blocked": "OA 站点拦截下载",
              "abstract-no-oa": "仅有 OA 落地页（无 PDF 直链）或未找到 OA 全文"}.get(
                  fulltext_status, "无 OA 全文")
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


# ---------------------------------------------------------------- 待人工获取清单
# 每次 --write 运行后重建：把「自动下载被出版方拦掉」「OA 只有落地页、没有 PDF 直链」
# 的条目累积成一份可照着去取的清单。拿到全文后（本轮下载成功，或本地 library-add 入库）
# 该条会在下一轮自动消失。

MANUAL_REL = "_data/fulltext_manual.json"       # 结构化清单（进仓库；每轮合并）
MANUAL_MD_REL = "_tools/manual_fulltext.md"     # 同一份清单的 Markdown 视图（进仓库）
MANUAL_REASONS = ("blocked", "no-pdf-link")     # 只收「OA 存在但自动下载拿不到」的两类

_HOST_LABELS = {
    "downloads.hindawi.com": "Hindawi（旧域名，已迁移 Wiley）",
    "onlinelibrary.wiley.com": "Wiley",
    "academic.oup.com": "Oxford Academic",
    "link.springer.com": "Springer",
    "www.sciencedirect.com": "ScienceDirect",
    "www.tandfonline.com": "Taylor & Francis",
    "www.biodiversitylibrary.org": "BHL",
    "bioone.org": "BioOne",
    "royalsocietypublishing.org": "Royal Society",
    "www.jstor.org": "JSTOR",
    "journals.flvc.org": "Florida Entomologist（FLVC）",
    "doi.org": "doi.org 解析页",
    "hdl.handle.net": "handle.net 解析页",
}

_MANUAL_HINTS = (
    ("10.5962/", "BHL 条目页（biodiversitylibrary.org/item/…），同一册常在 archive.org 有扫描本"),
    ("10.1206/", "AMNH 数字图书馆 digitallibrary.amnh.org（Novitates 系列多数免费）"),
    ("10.1653/", "Florida Entomologist 存档 journals.flvc.org，或 archive.org 同名卷期"),
    ("10.1155/", "Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org"),
    ("10.1093/", "Oxford Academic，需机构网络；生物医学类可先试 PMC"),
    ("10.1111/", "Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本"),
    ("10.1016/", "Elsevier（ScienceDirect），需机构网络；可试作者主页 / 机构库"),
)


def _manual_hint(doi: str) -> str:
    d = _norm_doi(doi or "")
    for prefix, hint in _MANUAL_HINTS:
        if d.startswith(prefix):
            return hint
    return "出版社站点（需机构网络），或 archive.org / 馆际互借"


def _hosts_label(hosts: list) -> str:
    if not hosts:
        return ""
    return " / ".join(_HOST_LABELS.get(h, h) for h in hosts[:3])


def _load_manual(root: Path) -> dict:
    doc = _load_json(root / MANUAL_REL)
    if isinstance(doc, dict) and isinstance(doc.get("items"), list):
        items = {_norm_doi(it.get("doi") or ""): it for it in doc["items"]
                 if isinstance(it, dict) and it.get("doi")}
        doc["_by_key"] = items
        return doc
    return {"items": [], "updated_at": ""}


def _merge_manual(root: Path, seen: list, archived: set) -> tuple:
    """本轮新判定的条目并入既有清单；已拿到全文的移出。返回 (entries, prev_doc)。"""
    prev = _load_manual(root)
    by_key = dict(prev.get("_by_key") or {})
    now = time.time()
    for e in seen:
        k = _norm_doi(e["doi"])
        old = by_key.get(k) or {}
        e["first_seen"] = old.get("first_seen") or now
        e["attempts"] = int(old.get("attempts") or 0) + 1
        by_key[k] = e
    keep = [e for k, e in by_key.items() if k not in archived]
    keep.sort(key=lambda e: (MANUAL_REASONS.index(e.get("reason"))
                             if e.get("reason") in MANUAL_REASONS else 9,
                             -(e.get("cited_by") or 0), -(e.get("year") or 0), e.get("doi") or ""))
    return keep, prev


def _manual_md(entries: list, stamp: str) -> str:
    blocked = sum(1 for e in entries if e.get("reason") == "blocked")
    linkless = sum(1 for e in entries if e.get("reason") == "no-pdf-link")
    out = ["# 待人工获取清单（自动生成，勿手改）", "",
           "由 `_tools/fetch_fulltext.py` 在每次抓取后重建：收录**自动下载已被出版方拦掉**、",
           "或**OA 只给落地页而没有 PDF 直链**的文献。拿到全文后（下一轮自动下到，或本地",
           "`library-add` 入库）该条会自动从清单里消失，不需要手工删。",
           "查不到任何 OA 全文的条目不在本表（那是「没有合法 OA」，只能走图书馆），",
           "它们的标记在 `.sources` 的 `fulltext_status = abstract-no-oa`。", "",
           "- 更新时间：" + (stamp or "—") + "（清单内容不变时不刷新）",
           "- 共 **" + str(len(entries)) + "** 条：站点拦截 " + str(blocked)
           + " ／ 仅有落地页 " + str(linkless),
           "- 结构化版本：`_data/fulltext_manual.json`（同一次运行写出的同一份数据）", "",
           "| # | 引用 | 年 | 标题 | DOI | 上次撞到的站点 | 建议取法 |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for i, e in enumerate(entries, 1):
        title = " ".join(str(e.get("title") or "").split())
        if len(title) > 95:
            title = title[:94] + "…"
        title = title.replace("|", "\\|")
        doi = e.get("doi") or ""
        out.append("| " + str(i) + " | " + str(e.get("cited_by") or 0) + " | "
                   + str(e.get("year") or "") + " | " + title + " | "
                   + "[" + doi + "](https://doi.org/" + doi + ") | "
                   + _hosts_label(e.get("hosts") or []).replace("|", "\\|") + " | "
                   + _manual_hint(doi).replace("|", "\\|") + " |")
    out += ["", "## 怎么用这张表", "",
            "1. 按「引用」从高到低处理（表已排好序：先站点拦截、后仅有落地页）。",
            "2. 拿到 PDF 后在本地跑 `python _tools/sources.py library-add --file <pdf> --title \"…\" --doi <doi> …`，",
            "   入库即从本站与清单里消失；CI 下一轮也不会再下载。",
            "3. 拿不到就让它留着——拦站点已进 `_data/fulltext_hosts.json` 的 120 天冷却，不会拖慢抓取。",
            "4. 不要手工编辑本文件：下次 `--write` 会用 `_data/fulltext_manual.json` 覆盖它。"]
    return "\n".join(out) + "\n"


def _write_manual(root: Path, entries: list, prev: dict) -> None:
    prev_items = json.dumps(prev.get("items") or [], ensure_ascii=False, sort_keys=True)
    items_txt = json.dumps(entries, ensure_ascii=False, sort_keys=True)
    stamp = prev.get("updated_at") or ""
    if not stamp or items_txt != prev_items:
        stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    doc = {"updated_at": stamp, "count": len(entries),
           "note": "自动生成：待人工获取的 OA 全文。抓取成功或本地 library-add 后自动移除。"
                   "不要手工编辑本文件，改由 _tools/fetch_fulltext.py --write 重建。",
           "items": entries}
    _save_json(root / MANUAL_REL, doc)
    md_path = root / MANUAL_MD_REL
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_manual_md(entries, stamp), encoding="utf-8", newline="\n")


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
    if getattr(args, "manual_only", False):
        # 只重建清单：不联网、不抓取。人工把 PDF 补进文库（sources.py library-add）后用一次，
        # 已解决的条目立刻从清单消失，不必等下一轮抓取。
        entries, prev = _merge_manual(root, [], _archived_dois(root))
        _write_manual(root, entries, prev)
        print("[fulltext] 待人工获取 " + str(len(entries)) + " 条 → " + MANUAL_MD_REL
              + " ／ " + MANUAL_REL)
        return 0
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
    archived0 = set(archived)      # 起跑时已有的全文；收尾合并待人工清单时用它算「已解决」
    fulltext_ok = set()            # 本轮真正下到全文的 DOI（摘要入库不算）
    budget = Budget(args.time_budget)
    hosts = _load_hosts(root)
    tmp_dir = root / args.tmp
    tmp_dir.mkdir(parents=True, exist_ok=True)
    processed = archived_ok = abstract_ok = skipped = recent = no_oa = errors = scanned = 0
    blocked_n = transient_n = linkless_n = 0
    manual_seen = []      # 本轮判定「拿不到 = 需要人工」的条目，收尾时并入待人工获取清单
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
            now = time.time()
            age = now - (prev.get("attempted_at") or 0)
            if (prev.get("next_try") or 0) > now:
                recent += 1   # 站点拦截 / 无 OA：冷却期内不重复撞同一堵墙
                continue
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
        meta = resolve(doi, it, mailto, api_key, budget, hosts)
        if not meta or not (meta.get("candidates") or []):
            if key in retryable:
                skipped += 1
                cool = NEXT_TRY_DAYS.get("abstract-no-oa", 120)
                cache[key] = dict(prev or {}, attempted_at=time.time(),
                                  next_try=time.time() + cool * 86400)
                print("[fulltext]   仍无 OA 全文，保留既有摘要（" + str(cool) + " 天内不再试）")
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
                              "next_try": time.time() + NEXT_TRY_DAYS.get("abstract-no-oa", 120) * 86400,
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
            cands = meta.get("candidates") or []
            print("[fulltext]   [dry-run] " + str(len(cands)) + " 个候选：")
            for c in cands:
                mark = "（站点冷却中）" if _host_blocked(hosts, c["host"]) else ""
                print("[fulltext]     - " + c["source"] + " " + c["kind"].upper() + " "
                      + c["host"] + mark + " " + c["url"][:110])
            print("[fulltext]   [dry-run] " + str((meta.get("title") or "")[:90]))
            continue
        tmpfile, final_url, ctype, report = _fetch_paper(meta, mailto, tmp_dir, hosts, budget)
        if tmpfile is None:
            reason = report.get("reason") or "transient"
            if reason in ("blocked", "html-page"):
                status = "abstract-blocked"
                blocked_n += 1
                what = "站点拦截"
            elif reason == "no-pdf-link":
                status = "abstract-no-oa"
                linkless_n += 1
                what = "仅有落地页、无 PDF 直链"
            else:
                status = "abstract-download-failed"
                transient_n += 1
                what = "瞬时失败"
            days = NEXT_TRY_DAYS.get(status, 60)
            tried_txt = " / ".join((u.split("://")[-1][:70] + "→" + str(r))
                                   for u, r in (report.get("tried") or []))
            if reason in ("blocked", "html-page", "no-pdf-link"):
                # 这两类不是「再等等就好」的失败：出版方按 IP 拦、或 OA 只有落地页。
                # 写进待人工获取清单，人照着取；站点已进冷却，不会再每周重撞。
                manual_seen.append({
                    "doi": doi,
                    "title": (meta.get("title") or it.get("title") or "").strip()[:200],
                    "year": meta.get("year") or it.get("year") or "",
                    "venue": meta.get("venue") or it.get("venue") or "",
                    "publisher": meta.get("publisher") or it.get("publisher") or "",
                    "cited_by": it.get("cited_by") or 0,
                    "landing": meta.get("landing") or ("https://doi.org/" + key),
                    "reason": "blocked" if reason in ("blocked", "html-page") else "no-pdf-link",
                    "hosts": sorted({_host_of(u) for u, _ in (report.get("tried") or []) if _host_of(u)}),
                    "tried": [u for u, _ in (report.get("tried") or [])][:5],
                    "last_result": tried_txt[:300],
                    "last_tried": time.time(),
                })
            if key in retryable:
                errors += 1
                cache[key] = dict(prev or {}, status=status, attempted_at=time.time(),
                                  next_try=time.time() + days * 86400, url=meta.get("url"),
                                  error=what + "（" + reason + "），保留既有摘要")
                print("[fulltext]   " + what + "（" + reason + "，保留既有摘要，" + str(days) + " 天内不再试）")
                print("[fulltext]     试过：" + tried_txt)
                continue
            if not (it.get("abstract") or "").strip():
                errors += 1
                cache[key] = {"status": status, "attempted_at": time.time(),
                              "next_try": time.time() + days * 86400,
                              "url": meta.get("url"), "error": what + "（" + reason + "）"}
                print("[fulltext]   " + what + "（" + reason + "）：" + str(meta.get("url")))
                print("[fulltext]     试过：" + tried_txt)
                continue
            rc2, out2, err2 = _ingest_abstract(root, it, tmp_dir, fulltext_status=status)
            if rc2 == 0:
                abstract_ok += 1
                archived.add(key)
                cache[key] = {"status": "abstract-archived", "attempted_at": time.time(),
                              "next_try": time.time() + days * 86400,
                              "url": meta.get("url"),
                              "source": it.get("abstract_source") or "abstract",
                              "retry": reason}
                print("[fulltext]   " + what + "，已存摘要（" + str(days) + " 天后重试）")
                print("[fulltext]     试过：" + tried_txt)
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
            fulltext_ok.add(key)
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
    _save_hosts(root, hosts)
    _save_json(root / args.cache, cache)
    # 待人工获取清单：每轮 --write 都重建（不只是本轮失败的，历史列表会累积到全部解决为止）
    if not args.dry_run:
        resolved = archived0 | fulltext_ok
        entries, prev = _merge_manual(root, manual_seen, resolved)
        _write_manual(root, entries, prev)
        print("[fulltext] 待人工获取 " + str(len(entries)) + " 条（本轮新增 "
              + str(len(manual_seen)) + "）→ " + MANUAL_MD_REL
              + " ／ " + MANUAL_REL)
    print("[fulltext] 完成：处理 " + str(processed) + "，归档全文 " + str(archived_ok)
          + "，存档摘要 " + str(abstract_ok)
          + "，扫描件跳过 " + str(scanned)
          + "，跳过已归档 " + str(skipped) + "，冷却/近期已试 " + str(recent)
          + "，无 OA 且无摘要 " + str(no_oa) + "，出错 " + str(errors))
    print("[fulltext] 失败分类：站点拦截 " + str(blocked_n) + "（同一站点连续 "
          + str(HOST_BLOCK_AFTER) + " 次硬失败即冷却 " + str(HOST_COOLDOWN_DAYS) + " 天），"
          "无 PDF 直链 " + str(linkless_n) + "（只有落地页，按 "
          + str(NEXT_TRY_DAYS.get("abstract-no-oa")) + " 天重试），"
          "瞬时失败 " + str(transient_n) + "（按 " + str(NEXT_TRY_DAYS.get("abstract-download-failed")) + " 天重试）")
    now = time.time()
    cooling = sorted(((h, s) for h, s in hosts.items() if (s.get("blocked_until") or 0) > now),
                     key=lambda x: -(x[1].get("blocked_until") or 0))
    if cooling:
        print("[fulltext] 冷却中的站点 " + str(len(cooling)) + " 个（到期前不再尝试）：")
        for h, s in cooling[:12]:
            days = int(((s.get("blocked_until") or 0) - now) / 86400) + 1
            print("[fulltext]   - " + h + "  失败 " + str(s.get("fails")) + " 次，还剩 " + str(days) + " 天")
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
    ap.add_argument("--manual-only", action="store_true",
                    help="只重建待人工获取清单（不联网；人工 library-add 后用它刷新）")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if args.check:
        return run_check(root, args)
    if args.manual_only:
        return run_write(root, args)
    if args.write or args.dry_run:
        return run_write(root, args)
    if args.discover:
        return run_discover(root, args)
    build_parser().print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
