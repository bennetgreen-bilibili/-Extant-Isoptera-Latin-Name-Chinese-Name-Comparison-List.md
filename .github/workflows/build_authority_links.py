#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立 _data/authority_links.json：GBIF Backbone + Catalogue of Life (ChecklistBank) + Wikidata 外链与一致性核对。

用途
  为站点 3071 个物种/亚种页面提供「其他数据库」外链与「本站名 vs 外部接受名」一致性提示。
  只读取外部库的公开 API，**不改动本站任何分类数据**；差异只作为提示展示。

用法
  python .github/workflows/build_authority_links.py                 # 只统计，不写文件
  python .github/workflows/build_authority_links.py --write         # 增量抓取并写入 _data/authority_links.json + downloads CSV
  python .github/workflows/build_authority_links.py --refresh       # 重新抓取缺失/出错条目（默认行为）
  python .github/workflows/build_authority_links.py --refresh-all   # 全部重新抓取
  python .github/workflows/build_authority_links.py --limit 50      # 只抓 50 个（调试）
  python .github/workflows/build_authority_links.py --budget 600    # 最多花 600 秒，剩余条目留给下次
  python .github/workflows/build_authority_links.py --check         # 校验已提交 JSON 的完整性与一致性
  python .github/workflows/build_authority_links.py --report        # 打印覆盖统计

数据源（均为免费、无需 API key）
  GBIF Backbone Taxonomy   https://api.gbif.org/v1/species/match
  Catalogue of Life        https://api.checklistbank.org/dataset/<alias>/match/nameusage
  Wikidata                 https://query.wikidata.org/sparql （P225 taxon name）

说明
  - 结果缓存进 _data/authority_links.json，重复运行自动增量（--refresh-all 才全量重抓）。
  - 输出确定性：条目按拉丁名排序、JSON 缩进 1，--check 可校验。
  - 礼貌抓取：全局限速、指数退避重试、失败留空不阻断。
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
DATA_DIR = ROOT / "_data"
OUT_PATH = DATA_DIR / "authority_links.json"
CSV_PATH = ROOT / "downloads" / "isoptera-authority-crossref.csv"

GBIF_MATCH = "https://api.gbif.org/v1/species/match"
GBIF_SPECIES = "https://api.gbif.org/v1/species/{key}"
COL_DATASET = "3LR"          # Catalogue of Life 年度发布别名；换版可 --col-dataset 或改这里
COL_MATCH = "https://api.checklistbank.org/dataset/{ds}/match/nameusage"
COL_META = "https://api.checklistbank.org/dataset/{ds}"
WD_SPARQL = "https://query.wikidata.org/sparql"

UA = ("isoptera-checklist-site-build/1.0 "
      "(+https://github.com/bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md)")

RATE_PER_SEC = 6.0          # 全局请求上限
WORKERS = 8
TIMEOUT = 60
RETRIES = 4

FLAG_ZH = {
    "gbif_missing": "GBIF 未收录",
    "gbif_synonym": "GBIF 视为异名",
    "gbif_doubtful": "GBIF 存疑",
    "gbif_fuzzy": "GBIF 仅模糊匹配",
    "gbif_higherrank": "GBIF 仅匹配到上级阶元",
    "gbif_rank_mismatch": "GBIF 阶元不一致",
    "col_missing": "COL 未收录",
    "col_synonym": "COL 视为异名",
    "col_ambiguous": "COL 匹配不确定",
    "col_rank_mismatch": "COL 阶元不一致",
    "col_higherrank": "COL 仅匹配到上级阶元",
}


# ------------------------------------------------------------------ 工具

class RateLimiter:
    """全局令牌桶：所有线程共享，避免并发时把对方挤爆。"""

    def __init__(self, rate: float) -> None:
        self._interval = 1.0 / rate
        self._lock = threading.Lock()
        self._next = time.monotonic()

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._next - now
            self._next = max(now, self._next) + self._interval
        if wait > 0:
            time.sleep(wait)


LIMITER = RateLimiter(RATE_PER_SEC)


def fetch_json(url: str, params: dict | None = None, *, post: bytes | None = None,
               headers: dict | None = None, timeout: int = TIMEOUT,
               retries: int = RETRIES) -> dict | list | None:
    """带重试与限速的 JSON 抓取；失败返回 None（调用方记为未取到，不中断）。"""
    if params:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{urllib.parse.urlencode(params)}"
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    data = post
    if data is not None:
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    for attempt in range(retries):
        LIMITER.acquire()
        req = urllib.request.Request(url, data=data, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code in (408, 425, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(1.5 ** attempt)
                continue
            return None
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError):
            if attempt < retries - 1:
                time.sleep(1.5 ** attempt)
                continue
            return None
    return None


# ------------------------------------------------------------------ 读取名录

def parse_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
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


def collect_taxa() -> list[dict]:
    rows = []
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        latin = (fm.get("latin") or "").strip()
        if not latin:
            sys.exit(f"error: {path.name} 缺少 latin 字段")
        rows.append({
            "latin": latin,
            "zh": fm.get("zh", ""),
            "rank": fm.get("rank", "species"),
            "genus_latin": fm.get("genus_latin", ""),
            "genus_id": fm.get("genus_id", ""),
            "family_latin": fm.get("family_latin", ""),
            "family_zh": fm.get("family_zh", ""),
            "family_id": fm.get("family_id", ""),
            "author_year": fm.get("author_year", ""),
            "slug": path.stem,
        })
    if not rows:
        sys.exit("error: _species/ 下没有找到物种页")
    seen = set()
    for row in rows:
        if row["latin"] in seen:
            print(f"warn: 重复学名 {row['latin']}", file=sys.stderr)
        seen.add(row["latin"])
    return rows


# ------------------------------------------------------------------ GBIF

def gbif_lookup(name: str) -> dict:
    """单个学名在 GBIF Backbone 的匹配结果。"""
    empty = {"key": None, "status": None, "match": "NONE", "confidence": 0,
             "rank": None, "name": None, "accepted": None,
             "accepted_key": None, "higherrank": False}
    match = fetch_json(GBIF_MATCH, {"name": name, "kingdom": "Animalia"})
    if not isinstance(match, dict) or not match.get("usageKey"):
        return empty
    match_type = match.get("matchType") or "NONE"
    status = match.get("status")
    rank = match.get("rank")
    key = match.get("usageKey")
    # 只有真正落到种/亚种、且匹配质量足够时才给外链，避免把属级/模糊结果当成本种
    usable = (
        match_type in ("EXACT", "FUZZY")
        and rank in ("SPECIES", "SUBSPECIES")
        and (match_type == "EXACT" or int(match.get("confidence") or 0) >= 95)
    )
    item = {
        "key": int(key) if usable else None,
        "status": status,
        "match": match_type,
        "confidence": int(match.get("confidence") or 0),
        "rank": rank,
        "name": match.get("scientificName"),
        "accepted": None,
        # 异名时 GBIF 只在这里给出真正的接受名 usageKey（勿用 usageKey 自己顶替）
        "accepted_key": int(match["acceptedUsageKey"]) if match.get("acceptedUsageKey") else None,
        "higherrank": match_type == "HIGHERRANK",
        "raw_key": int(key),
    }
    return item


def gbif_accepted_detail(key: int) -> dict | None:
    detail = fetch_json(GBIF_SPECIES.format(key=key))
    if not isinstance(detail, dict):
        return None
    return {
        "key": int(detail.get("key") or key),
        "name": detail.get("scientificName"),
        "status": detail.get("status"),
        "rank": detail.get("rank"),
    }


# ------------------------------------------------------------------ Catalogue of Life

def col_lookup(name: str, dataset: str) -> dict:
    empty = {"id": None, "status": None, "label": None, "name": None, "type": "none", "accepted": None}
    data = fetch_json(COL_MATCH.format(ds=dataset), {"q": name})
    if not isinstance(data, dict):
        return empty
    usage = data.get("usage")
    if not isinstance(usage, dict) or not usage.get("id"):
        return {"id": None, "status": None, "label": None, "name": None,
                "type": data.get("type") or "none", "accepted": None}
    status = usage.get("status")
    accepted = None
    classification = usage.get("classification") or []
    if status == "synonym" and classification:
        top = classification[0]
        if isinstance(top, dict) and top.get("status") == "accepted":
            accepted = {"id": top.get("id"), "label": top.get("label"), "name": top.get("name")}
    return {
        "id": usage.get("id"),
        "status": status,
        "label": usage.get("label"),
        "name": usage.get("name"),
        "type": data.get("type") or "",
        "rank": usage.get("rank"),
        "accepted": accepted,
    }


def col_meta(dataset: str) -> dict:
    data = fetch_json(COL_META.format(ds=dataset))
    if not isinstance(data, dict):
        return {"dataset": dataset}
    return {
        "dataset": dataset,
        "key": data.get("key"),
        "title": data.get("title"),
        "doi": data.get("doi"),
        "issued": data.get("issued") or data.get("created"),
        "version": data.get("version"),
        "license": data.get("license"),
        "url": f"https://www.checklistbank.org/dataset/{dataset}",
    }


# ------------------------------------------------------------------ Wikidata

def wikidata_lookup(names: list[str], batch_size: int = 120) -> dict[str, str]:
    """按 P225（分类单元学名）批量查 Wikidata QID。一次 SPARQL 查一批，失败则二分重试。"""
    result: dict[str, str] = {}
    batches = [names[i:i + batch_size] for i in range(0, len(names), batch_size)]
    for batch in batches:
        _sparql_batch(batch, result)
        time.sleep(0.3)
    return result


def _sparql_batch(names: list[str], out: dict[str, str]) -> None:
    values = " ".join('"%s"' % n.replace('"', '\\"') for n in names)
    query = (
        "SELECT ?name ?item WHERE { VALUES ?name { " + values + " } "
        "?item wdt:P225 ?name . }"
    )
    body = urllib.parse.urlencode({"query": query, "format": "json"}).encode("utf-8")
    data = fetch_json(WD_SPARQL, post=body, headers={"Accept": "application/sparql-results+json"},
                      timeout=120, retries=3)
    if isinstance(data, dict):
        for binding in data.get("results", {}).get("bindings", []):
            name = binding.get("name", {}).get("value")
            item = binding.get("item", {}).get("value", "")
            qid = item.rsplit("/", 1)[-1]
            if name and re.fullmatch(r"Q\d+", qid) and name not in out:
                out[name] = qid
        return
    if len(names) <= 1:
        return
    mid = len(names) // 2
    _sparql_batch(names[:mid], out)
    _sparql_batch(names[mid:], out)


# ------------------------------------------------------------------ 一致性标记

def _binomial(name: str, words: int) -> str:
    return " ".join((name or "").split()[:words]).lower()


def normalize_gbif(gbif: dict, latin: str, want_rank: str) -> dict:
    """把 GBIF 的原始匹配整理成「能否作为本种外链」的语义。

    三类要特别处理（否则会给用户错误的「异名」结论）：
    1) matchType=HIGHERRANK：只匹配到属/科，绝不能当成本种，也不叫异名；
    2) SYNONYM 但接受名的双名与本站名相同：只是命名人/组合写法不同，按接受名处理；
    3) SYNONYM 但接受名只到属级：同样不给异名结论。
    """
    status = (gbif.get("status") or "").upper()
    accepted = gbif.get("accepted")
    match_type = (gbif.get("match") or "").upper()
    if match_type == "HIGHERRANK":
        gbif["key"] = None
        gbif["accepted"] = None
        gbif["higherrank"] = True
        return gbif
    if status == "SYNONYM":
        if not isinstance(accepted, dict) or not accepted.get("key"):
            # 拿不到接受名就不下结论：不给链接、不标异名
            gbif["key"] = None
            gbif["accepted"] = None
            gbif["notes"] = "GBIF 记为异名但接受名未取到"
            return gbif
        acc_rank = (accepted.get("rank") or "").upper()
        if acc_rank and acc_rank not in ("SPECIES", "SUBSPECIES"):
            gbif["key"] = None
            gbif["accepted"] = None
            gbif["higherrank"] = True
            return gbif
        words = len(latin.split())
        if _binomial(accepted.get("name") or "", words) == latin.lower():
            # 同一双名，仅命名人/组合不同：当作接受名，避免误报「本站名是异名」
            gbif["key"] = accepted.get("key")
            gbif["status"] = "ACCEPTED"
            gbif["name"] = accepted.get("name")
            gbif["accepted"] = None
    return gbif


def normalize_col(col: dict, want_rank: str) -> dict:
    """COL 的 higherrank / 阶元不一致结果不能当成本种外链。"""
    col_type = (col.get("type") or "").lower()
    col_rank = (col.get("rank") or "").upper()
    if col_type == "higherrank" or (col_rank and col_rank != want_rank):
        col["id"] = None
        col["accepted"] = None
        col["higherrank"] = True
    return col


def compute_flags(entry: dict, latin: str, rank: str) -> list[str]:
    flags: list[str] = []
    gbif = entry.get("gbif") or {}
    col = entry.get("col") or {}
    want_rank = "SUBSPECIES" if rank == "subspecies" else "SPECIES"

    if gbif.get("higherrank"):
        flags.append("gbif_higherrank")
    elif not gbif.get("key") and gbif.get("match") in (None, "NONE"):
        flags.append("gbif_missing")
    else:
        status = (gbif.get("status") or "").upper()
        if status == "SYNONYM":
            flags.append("gbif_synonym")
        elif status == "DOUBTFUL":
            flags.append("gbif_doubtful")
        if (gbif.get("match") or "").upper() == "FUZZY":
            flags.append("gbif_fuzzy")
        if gbif.get("rank") and gbif.get("rank") != want_rank:
            flags.append("gbif_rank_mismatch")

    if col.get("higherrank"):
        flags.append("col_higherrank")
    elif not col.get("id"):
        flags.append("col_missing")
    else:
        if str(col.get("status") or "").lower() == "synonym":
            flags.append("col_synonym")
        if (col.get("type") or "").lower() not in ("exact", "variant", ""):
            flags.append("col_ambiguous")
        col_rank = (col.get("rank") or "").upper()
        if col_rank and col_rank != want_rank:
            flags.append("col_rank_mismatch")
    return flags


def consistency_zh(flags: list[str]) -> str:
    if not flags:
        return "一致"
    return "；".join(FLAG_ZH[f] for f in flags if f in FLAG_ZH)


# ------------------------------------------------------------------ 主流程

def load_existing() -> dict:
    if not OUT_PATH.exists():
        return {}
    try:
        data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(f"warn: {OUT_PATH} 无法解析，按空缓存处理", file=sys.stderr)
        return {}
    return data.get("taxa") or {}


def needs_fetch(existing: dict, name: str, mode: str, stale_days: int) -> bool:
    entry = existing.get(name)
    if not entry:
        return True
    if mode == "all":
        return True
    if mode == "stale":
        fetched = entry.get("_d")
        if not fetched:
            return True
        try:
            age = (datetime.now(timezone.utc).date() - datetime.fromisoformat(fetched).date()).days
        except ValueError:
            return True
        return age >= stale_days
    # mode == "missing"：已有 gbif 与 col 结果就不重抓（wikidata 单独补）
    return not (entry.get("gbif") and entry.get("col"))


def build_entries(taxa: list[dict], existing: dict, args: argparse.Namespace) -> dict:
    mode = "all" if args.refresh_all else ("stale" if args.refresh else "missing")
    today = datetime.now(timezone.utc).date().isoformat()
    todo = [t for t in taxa if needs_fetch(existing, t["latin"], mode, args.stale_days)]
    if args.limit:
        todo = todo[: args.limit]
    total = len(todo)
    print(f"待抓取 {total} / {len(taxa)} 个学名（模式 {mode}）", file=sys.stderr)

    new_entries: dict[str, dict] = {}
    started = time.monotonic()
    stopped = False

    def work(taxon: dict) -> tuple[str, dict]:
        if args.budget and time.monotonic() - started > args.budget:
            return taxon["latin"], {}
        gbif = gbif_lookup(taxon["latin"])
        col = col_lookup(taxon["latin"], args.col_dataset)
        return taxon["latin"], {"gbif": gbif, "col": col, "_d": today}

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(work, t): t for t in todo}
        for future in as_completed(futures):
            name, entry = future.result()
            if not entry:
                stopped = True
                continue
            new_entries[name] = entry
            done += 1
            if done % 200 == 0:
                elapsed = time.monotonic() - started
                print(f"  {done}/{total}  已用 {elapsed:.0f}s", file=sys.stderr)
            if args.budget and time.monotonic() - started > args.budget:
                stopped = True
                for fut in futures:
                    fut.cancel()

    if stopped:
        print("warn: 达到 --budget 时间上限，剩余条目下次继续（缓存已保留）", file=sys.stderr)

    # 第二遍：异名的接受名详情
    if not args.no_accepted_details:
        pending = [
            (name, entry["gbif"]["accepted_key"]) for name, entry in new_entries.items()
            if entry.get("gbif") and (entry["gbif"].get("status") or "").upper() == "SYNONYM"
            and entry["gbif"].get("accepted_key") and not entry["gbif"].get("accepted")
        ]
        if pending:
            print(f"补抓 {len(pending)} 条 GBIF 接受名详情", file=sys.stderr)

            def accepted_work(item: tuple[str, int]) -> tuple[str, dict | None]:
                return item[0], gbif_accepted_detail(item[1])

            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(accepted_work, p): p for p in pending}
                for future in as_completed(futures):
                    name, detail = future.result()
                    if detail and name in new_entries:
                        new_entries[name]["gbif"]["accepted"] = detail

    merged = dict(existing)
    merged.update(new_entries)

    # Wikidata：只补缺
    if not args.no_wikidata:
        need_wd = [t["latin"] for t in taxa
                   if t["latin"] in merged and not merged[t["latin"]].get("wd")]
        if args.limit:
            need_wd = need_wd[: max(args.limit, 200)]
        if need_wd:
            print(f"Wikidata 批量查询 {len(need_wd)} 个学名", file=sys.stderr)
            found = wikidata_lookup(need_wd)
            for name, qid in found.items():
                if name in merged:
                    merged[name]["wd"] = qid
            print(f"  Wikidata 命中 {len(found)} / {len(need_wd)}", file=sys.stderr)

    # 整理字段与标记
    by_name = {t["latin"]: t for t in taxa}
    cleaned: dict[str, dict] = {}
    for name, entry in merged.items():
        taxon = by_name.get(name)
        if not taxon:
            continue
        want_rank = "SUBSPECIES" if taxon["rank"] == "subspecies" else "SPECIES"
        gbif = dict(entry.get("gbif") or {})
        col = dict(entry.get("col") or {})
        gbif = normalize_gbif(gbif, name, want_rank)
        col = normalize_col(col, want_rank)
        wd = entry.get("wd")
        clean_gbif = {
            "key": gbif.get("key"),
            "status": gbif.get("status"),
            "match": gbif.get("match"),
            "confidence": gbif.get("confidence"),
            "rank": gbif.get("rank"),
            "name": gbif.get("name"),
            "accepted": gbif.get("accepted"),
        }
        if gbif.get("higherrank"):
            clean_gbif["higherrank"] = True
        if gbif.get("notes"):
            clean_gbif["notes"] = gbif["notes"]
        clean_col = {
            "id": col.get("id"),
            "status": col.get("status"),
            "label": col.get("label"),
            "type": col.get("type"),
            "rank": col.get("rank"),
            "accepted": col.get("accepted"),
        }
        if col.get("higherrank"):
            clean_col["higherrank"] = True
        clean = {"gbif": clean_gbif, "col": clean_col}
        if wd:
            clean["wd"] = wd
        clean["flags"] = compute_flags(clean, name, taxon["rank"])
        if entry.get("_d"):
            clean["_d"] = entry["_d"]
        cleaned[name] = clean
    return cleaned


def build_meta(taxa: list[dict], entries: dict, args: argparse.Namespace) -> dict:
    """统计以 flags 为准（而不是原始 status），避免把 HIGHERRANK 的属级结果算成本种异名。"""
    total = len(taxa)
    counts = {
        "total": total,
        "gbif_linked": 0,
        "gbif_accepted": 0,
        "gbif_synonym": 0,
        "gbif_missing": 0,
        "gbif_fuzzy": 0,
        "gbif_doubtful": 0,
        "gbif_higherrank": 0,
        "col_linked": 0,
        "col_accepted": 0,
        "col_synonym": 0,
        "col_missing": 0,
        "col_higherrank": 0,
        "wikidata": 0,
        "consistent": 0,
        "flagged": 0,
    }
    flag_counts: dict[str, int] = {}
    for taxon in taxa:
        entry = entries.get(taxon["latin"])
        if not entry:
            continue
        flags = set(entry.get("flags") or [])
        gbif, col = entry.get("gbif") or {}, entry.get("col") or {}
        if gbif.get("key"):
            counts["gbif_linked"] += 1
        if "gbif_higherrank" in flags:
            counts["gbif_higherrank"] += 1
        elif "gbif_synonym" in flags:
            counts["gbif_synonym"] += 1
        elif "gbif_missing" in flags:
            counts["gbif_missing"] += 1
        else:
            counts["gbif_accepted"] += 1
        if "gbif_fuzzy" in flags:
            counts["gbif_fuzzy"] += 1
        if "gbif_doubtful" in flags:
            counts["gbif_doubtful"] += 1
        if col.get("id"):
            counts["col_linked"] += 1
        if "col_higherrank" in flags:
            counts["col_higherrank"] += 1
        elif "col_synonym" in flags:
            counts["col_synonym"] += 1
        elif "col_missing" in flags:
            counts["col_missing"] += 1
        else:
            counts["col_accepted"] += 1
        if entry.get("wd"):
            counts["wikidata"] += 1
        if flags:
            counts["flagged"] += 1
            for flag in flags:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
        else:
            counts["consistent"] += 1
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {
            "gbif": {
                "name": "GBIF Backbone Taxonomy",
                "api": "https://api.gbif.org/v1/species/match",
                "url": "https://www.gbif.org/",
                "license": "CC BY 4.0（GBIF Backbone 元数据；使用须署名）",
            },
            "col": col_meta(args.col_dataset),
            "wikidata": {
                "name": "Wikidata",
                "endpoint": WD_SPARQL,
                "property": "P225 (taxon name)",
                "url": "https://www.wikidata.org/",
                "license": "CC0 1.0",
            },
        },
        "policy": {
            "scope": "只做外链与一致性提示，不改动本站任何分类数据",
            "link_rule": "GBIF 仅当 matchType=EXACT（或 FUZZY 且 confidence≥95）且阶元为 SPECIES/SUBSPECIES 时给外链；HIGHERRANK 与同名异名组合不给异名结论",
            "flag_meanings": FLAG_ZH,
        },
        "counts": counts,
        "flag_counts": dict(sorted(flag_counts.items())),
    }


def write_outputs(taxa: list[dict], entries: dict, args: argparse.Namespace) -> None:
    payload = {"meta": build_meta(taxa, entries, args), "taxa": dict(sorted(entries.items()))}
    text = json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"写入 {OUT_PATH.relative_to(ROOT)}  ({len(text) / 1024:.0f} KB, {len(entries)} 条)", file=sys.stderr)
    write_csv(taxa, entries)


def write_csv(taxa: list[dict], entries: dict) -> None:
    """一致性核对表：供人工复核与下载，不影响站点数据。"""
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow([
        "latinName", "chineseName", "rank", "familyLatin", "familyChinese",
        "gbifKey", "gbifStatus", "gbifMatch", "gbifConfidence", "gbifScientificName",
        "gbifAcceptedKey", "gbifAcceptedName",
        "colID", "colStatus", "colLabel", "colAcceptedLabel",
        "wikidata", "consistency", "flags", "gbifURL", "colURL", "wikidataURL",
    ])
    for taxon in sorted(taxa, key=lambda t: t["latin"]):
        entry = entries.get(taxon["latin"]) or {}
        gbif = entry.get("gbif") or {}
        col = entry.get("col") or {}
        wd = entry.get("wd") or ""
        accepted = gbif.get("accepted") or {}
        col_accepted = col.get("accepted") or {}
        writer.writerow([
            taxon["latin"], taxon["zh"], taxon["rank"], taxon["family_latin"], taxon["family_zh"],
            gbif.get("key") or "", (gbif.get("status") or ""), (gbif.get("match") or ""),
            gbif.get("confidence") if gbif.get("confidence") is not None else "",
            gbif.get("name") or "",
            accepted.get("key") or "", accepted.get("name") or "",
            col.get("id") or "", col.get("status") or "", col.get("label") or "",
            col_accepted.get("label") or "",
            wd, consistency_zh(entry.get("flags") or []), " ".join(entry.get("flags") or []),
            (f"https://www.gbif.org/species/{gbif['key']}" if gbif.get("key") else ""),
            (f"https://www.checklistbank.org/dataset/{COL_DATASET}/taxon/{col['id']}" if col.get("id") else ""),
            (f"https://www.wikidata.org/wiki/{wd}" if wd else ""),
        ])
    CSV_PATH.write_bytes(("\ufeff" + buf.getvalue()).encode("utf-8"))
    print(f"写入 {CSV_PATH.relative_to(ROOT)}", file=sys.stderr)


def run_check(taxa: list[dict]) -> int:
    if not OUT_PATH.exists():
        print(f"error: 缺少 {OUT_PATH}", file=sys.stderr)
        return 1
    try:
        payload = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: {OUT_PATH.name} 不是合法 JSON：{exc}", file=sys.stderr)
        return 1
    entries = payload.get("taxa") or {}
    names = [t["latin"] for t in taxa]
    name_set = set(names)
    missing = [n for n in names if n not in entries]
    extra = [n for n in entries if n not in name_set]
    bad = 0
    for name, entry in entries.items():
        gbif = entry.get("gbif") or {}
        col = entry.get("col") or {}
        if not isinstance(gbif, dict) or not isinstance(col, dict):
            print(f"error: {name} 结构不合法", file=sys.stderr)
            bad += 1
            continue
        if gbif.get("key") and not re.fullmatch(r"\d+", str(gbif["key"])):
            print(f"error: {name} GBIF key 非数字", file=sys.stderr)
            bad += 1
        if col.get("id") and not re.fullmatch(r"[A-Za-z0-9]{3,10}", str(col["id"])):
            print(f"error: {name} COL id 异常：{col['id']}", file=sys.stderr)
            bad += 1
    print(f"校验：{len(entries)} 条，缺 {len(missing)}，多 {len(extra)}，结构错误 {bad}")
    if missing:
        print("  缺失示例：" + ", ".join(missing[:8]))
    meta = payload.get("meta") or {}
    print("  统计：" + json.dumps(meta.get("counts") or {}, ensure_ascii=False))
    ok = not missing and not extra and not bad
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


def run_report(taxa: list[dict]) -> int:
    if not OUT_PATH.exists():
        print(f"error: 缺少 {OUT_PATH}", file=sys.stderr)
        return 1
    payload = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    meta = payload.get("meta") or {}
    entries = payload.get("taxa") or {}
    print(json.dumps(meta.get("counts") or {}, ensure_ascii=False, indent=1))
    print("flags:", json.dumps(meta.get("flag_counts") or {}, ensure_ascii=False))
    print("sources:", json.dumps(meta.get("sources") or {}, ensure_ascii=False, indent=1)[:1200])
    for name in [t["latin"] for t in taxa[:3]]:
        print(name, json.dumps(entries.get(name), ensure_ascii=False)[:400])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="GBIF / Catalogue of Life / Wikidata 外链与一致性核对")
    parser.add_argument("--write", action="store_true", help="写入 _data/authority_links.json 与 CSV")
    parser.add_argument("--check", action="store_true", help="校验已提交 JSON")
    parser.add_argument("--report", action="store_true", help="打印统计")
    parser.add_argument("--limit", type=int, default=0, help="本次最多抓取多少个学名")
    parser.add_argument("--budget", type=float, default=0, help="本次抓取时间上限（秒）")
    parser.add_argument("--workers", type=int, default=WORKERS)
    parser.add_argument("--refresh", action="store_true", help="重抓过期条目（--stale-days）")
    parser.add_argument("--refresh-all", action="store_true", help="全部重抓")
    parser.add_argument("--stale-days", type=int, default=180, help="--refresh 的过期天数")
    parser.add_argument("--col-dataset", default=COL_DATASET, help="ChecklistBank 数据集别名")
    parser.add_argument("--no-wikidata", action="store_true")
    parser.add_argument("--no-accepted-details", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    taxa = collect_taxa()
    if args.check:
        return run_check(taxa)
    if args.report:
        return run_report(taxa)
    existing = load_existing()
    entries = build_entries(taxa, existing, args)
    if args.write:
        write_outputs(taxa, entries, args)
    else:
        missing = [t["latin"] for t in taxa if t["latin"] not in entries]
        print(f"只统计：{len(entries)} / {len(taxa)} 条已有结果；缺 {len(missing)} 条（加 --write 写入）")
        if missing and not args.quiet:
            print("  示例：" + ", ".join(missing[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
