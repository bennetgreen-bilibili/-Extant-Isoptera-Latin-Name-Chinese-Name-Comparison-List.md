#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""世界名录对照（BSF, Blattodea Species File）：把 _species/*.md 的拉丁学名自动匹配到 BSF 的 OTU。

BSF 前台是 TaxonPages（Vite SPA），没有稳定公开 API；但它背后是 TaxonWorks 公共 API，
且 OTU 深链 https://cockroach.speciesfile.org/otus/<id>/overview 是稳定的。
本脚本因此做"半自动"对照：自动匹配 + 人工复核工作表 + 导出站点渲染用的小 JSON。

产物（全部可确定性重跑）：
  _data/bsf_links.json            站点渲染用数据（同时充当断点续跑缓存）
  _tools/bsf对照/工作表.csv        人工复核工作表（UTF-8 BOM，Excel 直接打开）
  _tools/bsf对照/导入模板.csv      导入格式示例（仅首次创建，不覆盖）

用法：
  python .github/workflows/build_bsf_links.py                      # 只统计，不联网、不写文件
  python .github/workflows/build_bsf_links.py --write              # 仅补齐未缓存的名称后写入
  python .github/workflows/build_bsf_links.py --write --limit 100  # 只查 100 个新名称（分批跑）
  python .github/workflows/build_bsf_links.py --write --budget 900 # 最多花 900 秒联网
  python .github/workflows/build_bsf_links.py --write --refresh    # 忽略缓存全部重查（已人工核对的条目保留）
  python .github/workflows/build_bsf_links.py --no-api --write     # 只用缓存重排工作表/JSON，不联网
  python .github/workflows/build_bsf_links.py --import _tools/bsf对照/工作表.csv   # 回收人工复核结果
  python .github/workflows/build_bsf_links.py --check              # 校验仓库内产物一致（不联网，CI 用）

匹配规则（严格，绝不模糊接受）：
  valid     某候选 id == otu_valid_id，且其拉丁名前 N 个词（N = 本站名的词数）与本站名逐词相等
            → 取该 OTU；恰好 1 个不同 OTU 才算通过。
  synonym   某候选的拉丁名前 N 词与本站名相等，但 id != otu_valid_id，且 label 含 " now "
            → 本站名是异名，取 " now " 之后的接受名与 otu_valid_id。
  ambiguous 有同名候选但结论不唯一（多个不同有效 OTU / 同时命中 valid 与 synonym / 只有模糊候选）
            → 只记录候选，不写 otu（不做断言）。
  missing   没有任何候选的拉丁名前 N 词与本站名相等。
  error     HTTP/网络重试后仍失败（下次运行会自动重查）。

礼貌性：全局请求起始间隔 >= 0.5 s（≤2 req/s），最多 4 个在途请求共享这条"发车时刻"队列；
只读 GET，UA 带项目 URL；429/5xx/超时按指数退避重试并尊重 Retry-After；
连续失败 5 次或 token 被拒即干净停止，保留部分结果。已抓到的结果就是缓存，重跑不重取。
全量 3071 条约 27 分钟 / ~3050 次请求，之后增量刷新是秒级。

作者：本仓库构建脚本；仅使用 Python 标准库（Python 3.12+）。
"""

from __future__ import annotations

import argparse
import csv
import html as htmllib
import io
import json
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
DATA_PATH = ROOT / "_data" / "bsf_links.json"
TOOLS_DIR = ROOT / "_tools" / "bsf对照"
WORKSHEET_PATH = TOOLS_DIR / "工作表.csv"
TEMPLATE_PATH = TOOLS_DIR / "导入模板.csv"

# TaxonWorks 公共 API（token 是 BSF 自己前端 JS 里公开的那个，属只读公共项目 48）
API_BASE = "https://sfg.taxonworks.org/api/v1"
PROJECT_TOKEN = "rABfQ7Q0gtV8m-Nb-BvajQ"
# 站点前台（OTU 深链）
SITE_BASE = "https://cockroach.speciesfile.org"

SOURCE_NAME = "Blattodea Species File (cockroach.speciesfile.org)"
CITATION = "Blattodea Working Group. Blattodea Species File Online. https://cockroach.speciesfile.org"
REVIEW_NOTE = "semi-automatic; see _tools/bsf对照/操作说明.md"
GENERATED_BY = ".github/workflows/build_bsf_links.py"

UA = (
    "isoptera-checklist-bsf/1.0 "
    "(+https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md)"
)

MIN_INTERVAL = 0.5          # 秒 —— 全局请求起始间隔，即 ≤2 req/s
CONCURRENCY = 4             # 在途请求上限（延迟约 1.9 s，4 个在途刚好跑满 2 req/s）
CHUNK = 30                  # 每批提交量：批末检查是否需要收手
MAX_RETRIES = 4             # 429/5xx/超时
MAX_CONSECUTIVE_FAILS = 5   # 连续失败这么多次就收手
HTTP_TIMEOUT = 30

STATUSES = ("valid", "synonym", "ambiguous", "missing", "error")
MATCHED = ("valid", "synonym")

CSV_FIELDS = [
    "latin",
    "zh",
    "family_latin",
    "family_zh",
    "bsf_status",
    "bsf_label",
    "bsf_valid_label",
    "bsf_otu",
    "bsf_url",
    "auto_rule",
    "check_status",
    "notes",
    "reviewer",
]

CHECK_PENDING = "待核对"
CHECK_DONE = "已核对"
CHECK_FILL = "待补录"

ENTRY_FIELDS = (
    "status",
    "otu",
    "label",
    "valid_otu",
    "valid_label",
    "url",
    "match",
    "verified",
    "notes",
)

FM_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
LOWER_WORD = re.compile(r"^[a-z][a-z-]*$")


# --------------------------------------------------------------------------- #
# 输出
# --------------------------------------------------------------------------- #
def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass


def log(msg: str = "") -> None:
    print(msg, flush=True)


def rel(path: Path) -> str:
    """仓库内路径显示为相对路径，仓库外（测试/临时）原样返回。"""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- #
# 读取 _species 的 front matter（与 build_dataset.py 一样就地简单解析）
# --------------------------------------------------------------------------- #
def parse_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = FM_LINE.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
            raw = raw[1:-1].replace('\\"', '"')
        data[key] = raw
    return data


def load_species() -> list[dict]:
    records = []
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        latin = (fm.get("latin") or "").strip()
        if not latin:
            continue
        records.append(
            {
                "latin": latin,
                "zh": (fm.get("zh") or "").strip(),
                "family_latin": (fm.get("family_latin") or "").strip(),
                "family_zh": (fm.get("family_zh") or "").strip(),
                "rank": (fm.get("rank") or "").strip(),
                "slug": path.stem,
            }
        )
    return records


# --------------------------------------------------------------------------- #
# 名称归一与标签解析
# --------------------------------------------------------------------------- #
def name_words(latin: str) -> tuple[str, ...]:
    return tuple(w.casefold() for w in latin.split())


def label_head(label: str) -> str:
    """'Genus sp. Author, 1900 now Genus other Author, 1901' -> 'Genus sp. Author, 1900'"""
    head, sep, _ = label.partition(" now ")
    return head.strip() if sep else label.strip()


def label_accepted(label: str) -> str:
    """'... now Genus other Author, 1901' -> 'Genus other Author, 1901'（无 now 则空串）"""
    parts = label.rsplit(" now ", 1)
    if len(parts) == 2:
        return parts[1].strip()
    return ""


def _drop_subgenus(tokens: list[str]) -> list[str]:
    """去掉位于第 2 个位置的亚属括号，如 Coptotermes (Polycrinitermes) changtaiensis。

    只处理 index == 1 的括号词（属名之后的亚属写法）；作者的括号出现在更后面，不受影响。
    """
    if len(tokens) >= 2 and tokens[1].startswith("(") and not tokens[1].endswith(","):
        return [tokens[0]] + tokens[2:]
    return tokens


def _is_trinomen_tail(token: str) -> bool:
    return bool(LOWER_WORD.match(token))


def label_matches_name(label: str, words: tuple[str, ...]) -> tuple[bool, bool]:
    """返回 (是否逐词命中, 是否发生过亚属剥离)。只比较标签 'now' 之前的前半段。"""
    head = label_head(label)
    if not head:
        return False, False
    tokens = head.split()
    stripped = _drop_subgenus(tokens)
    used_strip = len(stripped) != len(tokens)
    if len(stripped) < len(words):
        return False, used_strip
    if tuple(t.casefold() for t in stripped[: len(words)]) != words:
        return False, used_strip
    # 本站是 2 词（种），BSF 标签却是三名法（第 3 词是小写种加词）→ 那是亚种 OTU，不认领
    if len(words) == 2 and len(stripped) >= 3 and _is_trinomen_tail(stripped[2]):
        return False, used_strip
    return True, used_strip


def otu_url(otu) -> str | None:
    if otu is None:
        return None
    return "%s/otus/%d/overview" % (SITE_BASE, otu)


# --------------------------------------------------------------------------- #
# 分类
# --------------------------------------------------------------------------- #
def classify(latin: str, candidates: list[dict]) -> dict:
    """把 autocomplete 的候选列表压成 9 字段条目（不含 verified）。"""
    words = name_words(latin)
    seen: set[tuple[int | None, str]] = set()
    pool: list[dict] = []
    for cand in candidates:
        try:
            oid = int(cand["id"])
        except (KeyError, TypeError, ValueError):
            continue
        vid = cand.get("otu_valid_id")
        try:
            vid = int(vid) if vid is not None else None
        except (TypeError, ValueError):
            vid = None
        label = str(cand.get("label") or "").strip()
        key = (oid, label)
        if key in seen:
            continue
        seen.add(key)
        pool.append({"id": oid, "valid_id": vid, "label": label})

    exact: list[dict] = []
    fuzzy: list[dict] = []
    for cand in pool:
        ok, stripped = label_matches_name(cand["label"], words)
        if ok:
            cand["subgenus"] = stripped
            exact.append(cand)
        else:
            fuzzy.append(cand)

    valid_hits: dict[int, dict] = {}
    synonym_hits: dict[int, dict] = {}
    for cand in exact:
        has_now = " now " in cand["label"]
        if cand["valid_id"] is not None and cand["id"] == cand["valid_id"] and not has_now:
            valid_hits.setdefault(cand["id"], cand)
        elif cand["valid_id"] is not None and cand["id"] != cand["valid_id"] and has_now:
            accepted = label_accepted(cand["label"])
            if accepted:
                synonym_hits.setdefault(cand["valid_id"], cand)

    notes: list[str] = []
    if any(c.get("subgenus") for c in exact):
        notes.append("BSF 标签含亚属括号")

    def entry(status, otu=None, label="", valid_otu=None, valid_label=None, match=None, extra=""):
        bits = list(notes)
        if extra:
            bits.append(extra)
        return {
            "status": status,
            "otu": otu,
            "label": label,
            "valid_otu": valid_otu,
            "valid_label": valid_label,
            "url": otu_url(otu),
            "match": match,
            "notes": "；".join(bits),
        }

    if len(valid_hits) == 1 and not synonym_hits:
        cand = next(iter(valid_hits.values()))
        return entry("valid", cand["id"], cand["label"], cand["id"], None, "exact")

    if len(synonym_hits) == 1 and not valid_hits:
        cand = next(iter(synonym_hits.values()))
        return entry(
            "synonym",
            cand["valid_id"],
            cand["label"],
            cand["valid_id"],
            label_accepted(cand["label"]),
            "exact",
        )

    if len(valid_hits) > 1 or len(synonym_hits) > 1 or (valid_hits and synonym_hits):
        parts = []
        for cand in list(valid_hits.values()) + list(synonym_hits.values()):
            parts.append("OTU %d %s" % (cand["id"], cand["label"]))
        return entry(
            "ambiguous",
            None,
            "",
            None,
            None,
            None,
            "候选：" + "；".join(parts),
        )

    if exact or fuzzy:
        parts = []
        for cand in (exact + fuzzy)[:4]:
            parts.append("OTU %d %s" % (cand["id"], cand["label"]))
        extra = "仅模糊候选：" + "；".join(parts) if parts else "仅模糊候选"
        return entry("ambiguous", None, "", None, None, None, extra)

    return entry("missing", None, "", None, None, None)


def error_entry(message: str) -> dict:
    return {
        "status": "error",
        "otu": None,
        "label": "",
        "valid_otu": None,
        "valid_label": None,
        "url": None,
        "match": None,
        "verified": False,
        "notes": message[:200],
    }


# --------------------------------------------------------------------------- #
# HTTP 客户端（限速 + 退避 + 预算）
# --------------------------------------------------------------------------- #
class ApiAbort(Exception):
    """整轮收手（token 被拒 / 被限流 / 手动中断）。"""


class ApiError(Exception):
    """单个名称硬失败（重试后仍 5xx/超时/4xx）：只标 error，不拖垮整轮。"""


class BudgetExceeded(Exception):
    pass


class ApiClient:
    """全局速率限制器：所有线程共享一条"请求发车时刻"队列，保证请求起始间隔 >= min_interval。

    线程只负责等待 I/O 延迟，因此同时最多 CONCURRENCY 个请求在途，而总速率仍 <= 2 req/s。
    """

    def __init__(self, budget: float | None = None, min_interval: float = MIN_INTERVAL, verbose: bool = True):
        self.min_interval = min_interval
        self.budget = budget
        self.verbose = verbose
        self.started = time.monotonic()
        self._lock = threading.Lock()
        self._next_slot = 0.0
        self.calls = 0
        self.fail_streak = 0
        self.aborted: str | None = None

    def elapsed(self) -> float:
        return time.monotonic() - self.started

    def remaining(self) -> float | None:
        if self.budget is None:
            return None
        return self.budget - self.elapsed()

    def _check_budget(self) -> None:
        rem = self.remaining()
        if rem is not None and rem <= 0:
            raise BudgetExceeded("budget %ds exhausted" % int(self.budget or 0))

    def _throttle(self) -> None:
        """占一个发车名额：全局串行化发车时刻，绝不并发冲刺。"""
        with self._lock:
            slot = max(time.monotonic(), self._next_slot)
            self._next_slot = slot + self.min_interval
        wait = slot - time.monotonic()
        if wait > 0:
            time.sleep(wait)

    def _count_call(self) -> None:
        with self._lock:
            self.calls += 1

    def _note_success(self) -> None:
        with self._lock:
            self.fail_streak = 0

    def _note_failure(self) -> None:
        with self._lock:
            self.fail_streak += 1

    def _sleep(self, seconds: float) -> None:
        rem = self.remaining()
        if rem is not None:
            seconds = min(seconds, max(rem, 0))
        if seconds > 0:
            time.sleep(seconds)

    def _open(self, url: str):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        return urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)

    def get_json(self, path: str):
        url = API_BASE + path + ("&" if "?" in path else "?") + "project_token=" + PROJECT_TOKEN
        attempt = 0
        while True:
            self._check_budget()
            self._throttle()
            try:
                with self._open(url) as resp:
                    raw = resp.read()
                self._count_call()
                self._note_success()
                return json.loads(raw.decode("utf-8"))
            except urllib.error.HTTPError as exc:
                self._count_call()
                code = exc.code
                if code in (401, 403):
                    self.aborted = "API 拒绝了 token（HTTP %d）" % code
                    raise ApiAbort(self.aborted)
                if code == 404:
                    self._note_success()
                    return []
                if code == 429 or 500 <= code < 600:
                    attempt += 1
                    self._note_failure()
                    if attempt > MAX_RETRIES:
                        # 429 = 明确的限流信号 → 整轮停下；5xx = 可能只是单次抖动 → 只标这一条
                        if code == 429:
                            raise ApiAbort("HTTP 429 重试 %d 次仍被限流，先停下" % MAX_RETRIES)
                        raise ApiError("HTTP %d 重试 %d 次仍失败" % (code, MAX_RETRIES))
                    delay = min(2 ** attempt, 16) + random.random()
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    if retry_after and retry_after.isdigit():
                        delay = max(delay, int(retry_after))
                    if self.verbose:
                        log("    · HTTP %d，%.1fs 后重试（%d/%d）" % (code, delay, attempt, MAX_RETRIES))
                    self._sleep(delay)
                    continue
                raise ApiError(
                    "HTTP %d：%s" % (code, exc.read()[:120].decode("utf-8", "replace"))
                )
            except BudgetExceeded:
                raise
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
                self._count_call()
                attempt += 1
                self._note_failure()
                if attempt > MAX_RETRIES:
                    raise ApiError("网络/解析失败 %d 次：%s" % (MAX_RETRIES, str(exc)[:120]))
                delay = min(2 ** attempt, 16) + random.random()
                if self.verbose:
                    log("    · 网络异常，%.1fs 后重试（%d/%d）" % (delay, attempt, MAX_RETRIES))
                self._sleep(delay)

    def autocomplete(self, latin: str) -> list[dict]:
        data = self.get_json("/otus/autocomplete?term=" + urllib.parse.quote(latin))
        return data if isinstance(data, list) else []


def strip_html(raw: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = htmllib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def spot_check(entries: dict, count: int, seed: int) -> dict:
    """随机抽 count 个已匹配 OTU，抓 overview 页面，确认页面里出现期望的拉丁名。

    期望字符串：valid 用本站名本身；synonym 用 BSF 的接受名标签（深链指向接受名那条 OTU）。
    """
    matched = sorted(
        (latin for latin, e in entries.items() if e["status"] in MATCHED and e.get("otu")),
    )
    if not matched or count <= 0:
        return {"checked": 0, "passed": 0, "sample": [], "note": "无可抽查的已匹配 OTU"}
    rng = random.Random(seed)
    picked = rng.sample(matched, min(count, len(matched)))
    sample = []
    passed = 0
    for latin in picked:
        entry = entries[latin]
        otu = int(entry["otu"])
        key = latin
        if entry["status"] == "synonym" and entry.get("valid_label"):
            key = entry["valid_label"]
        url = otu_url(otu) or ""
        row = {"latin": latin, "status": entry["status"], "otu": otu, "url": url, "ok": False}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", "replace")
                status = resp.status
            text = strip_html(raw)
            row["http"] = status
            row["ok"] = key.casefold() in text.casefold()
            if not row["ok"]:
                row["note"] = "页面未出现 %r" % key
        except Exception as exc:  # 抽查失败不应让整次运行失败
            row["note"] = str(exc)[:160]
        if row["ok"]:
            passed += 1
        sample.append(row)
        time.sleep(MIN_INTERVAL)
    return {"checked": len(sample), "passed": passed, "sample": sample}


# --------------------------------------------------------------------------- #
# 文档组装
# --------------------------------------------------------------------------- #
def build_document(
    species: list[dict],
    entries: dict,
    spot: dict | None,
    generated: str,
    calls: int,
    aborted: str | None,
) -> dict:
    counts = {key: 0 for key in STATUSES}
    for entry in entries.values():
        status = entry.get("status")
        if status in counts:
            counts[status] += 1
    total = len(species)
    classified = sum(counts.values())
    meta = {
        "generated": generated,
        "source": SOURCE_NAME,
        "api": API_BASE,
        "citation": CITATION,
        "fetched": classified,
        "counts": {
            "total": total,
            "valid": counts["valid"],
            "synonym": counts["synonym"],
            "ambiguous": counts["ambiguous"],
            "missing": counts["missing"],
            "error": counts["error"],
        },
        "pending": total - classified,
        "spot_check": spot
        or {"checked": 0, "passed": 0, "sample": [], "note": "本次未运行抽查（--no-api）"},
        "review": REVIEW_NOTE,
        "generated_by": GENERATED_BY,
        "rate_limit": "global <=2 req/s (max 4 in flight), exponential backoff on 429/5xx, resumable cache",
        "api_calls": calls,
        "aborted": aborted,
    }
    # 只输出 9 个约定字段，输入里混进来的临时键（如 reviewer）不会进 JSON
    name_map = {}
    for key in sorted(entries):
        item = {field: entries[key].get(field) for field in ENTRY_FIELDS}
        item["verified"] = bool(item.get("verified"))
        name_map[key] = item
    return {"meta": meta, "name_map": name_map}


def sanitize_entry(raw: dict, latin: str) -> dict | None:
    """读入既有 JSON 时校验条目，坏条目丢弃（下次重查）。"""
    if not isinstance(raw, dict):
        return None
    status = raw.get("status")
    if status not in STATUSES:
        return None
    out = {}
    for field in ENTRY_FIELDS:
        out[field] = raw.get(field)
    out["status"] = status
    for field in ("otu", "valid_otu"):
        value = out.get(field)
        if value is None:
            continue
        try:
            out[field] = int(value)
        except (TypeError, ValueError):
            out[field] = None
    out["verified"] = bool(out.get("verified"))
    out["label"] = out.get("label") or ""
    out["valid_label"] = out.get("valid_label") or None
    out["notes"] = out.get("notes") or ""
    out["match"] = out.get("match") or None
    if out["otu"]:
        out["url"] = otu_url(out["otu"])
    else:
        out["otu"] = None
        out["url"] = None
    if out["status"] not in MATCHED:
        out["otu"] = None
        out["url"] = None
    return out


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log("！无法解析已有 %s（%s），按空缓存继续" % (path.name, exc))
        return {}
    name_map = doc.get("name_map")
    if not isinstance(name_map, dict):
        return {}
    out = {}
    for latin, raw in name_map.items():
        entry = sanitize_entry(raw, latin)
        if entry is not None:
            out[str(latin)] = entry
    return out


def write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------- #
# 工作表
# --------------------------------------------------------------------------- #
CHECK_DEFAULT = {
    "valid": CHECK_PENDING,
    "synonym": CHECK_PENDING,
    "ambiguous": CHECK_PENDING,
    "missing": CHECK_FILL,
    "error": CHECK_PENDING,
}


def read_worksheet(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                latin = (row.get("latin") or "").strip()
                if latin:
                    out[latin] = {key: (row.get(key) or "") for key in CSV_FIELDS}
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        log("！无法读取既有工作表（%s），按空表继续" % exc)
        return {}
    return out


def worksheet_rows(
    species: list[dict],
    entries: dict,
    previous: dict[str, dict],
    reviewers: dict[str, str] | None = None,
) -> list[dict]:
    reviewers = reviewers or {}
    rows = []
    for sp in sorted(species, key=lambda s: (s["family_latin"], s["family_latin"], s["latin"])):
        latin = sp["latin"]
        entry = entries.get(latin)
        prev = previous.get(latin, {})
        if entry is None:
            rows.append(
                {
                    "latin": latin,
                    "zh": sp["zh"],
                    "family_latin": sp["family_latin"],
                    "family_zh": sp["family_zh"],
                    "bsf_status": "",
                    "bsf_label": "",
                    "bsf_valid_label": "",
                    "bsf_otu": "",
                    "bsf_url": "",
                    "auto_rule": "not-fetched",
                    "check_status": prev.get("check_status") or CHECK_PENDING,
                    "notes": prev.get("notes", ""),
                    "reviewer": reviewers.get(latin, prev.get("reviewer", "")),
                }
            )
            continue
        status = entry["status"]
        otu = entry.get("otu")
        default_check = CHECK_DEFAULT.get(status, CHECK_PENDING)
        check = prev.get("check_status") or default_check
        notes = prev.get("notes") or entry.get("notes", "")
        otu_text = str(otu) if otu else ""
        url = entry.get("url") or ""
        # 待补录行允许人工填过 otu/url
        if check == CHECK_FILL and prev.get("bsf_otu"):
            otu_text = prev["bsf_otu"].strip()
            url = prev.get("bsf_url", "").strip() or (
                otu_url(int(otu_text)) if otu_text.isdigit() else ""
            )
        rows.append(
            {
                "latin": latin,
                "zh": sp["zh"],
                "family_latin": sp["family_latin"],
                "family_zh": sp["family_zh"],
                "bsf_status": status,
                "bsf_label": entry.get("label") or "",
                "bsf_valid_label": entry.get("valid_label") or "",
                "bsf_otu": otu_text,
                "bsf_url": url,
                "auto_rule": entry.get("match") or "",
                "check_status": check,
                "notes": notes,
                "reviewer": reviewers.get(latin, prev.get("reviewer", "")),
            }
        )
    return rows


def write_worksheet(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in CSV_FIELDS})
    # utf-8-sig：Excel 打开中文不乱码
    path.write_text(buf.getvalue(), encoding="utf-8-sig", newline="")


def template_rows() -> list[dict]:
    return [
        {
            "latin": "Coptotermes formosanus",
            "zh": "台湾乳白蚁",
            "family_latin": "HETEROTERMITIDAE",
            "family_zh": "异白蚁科",
            "bsf_status": "valid",
            "bsf_label": "Coptotermes formosanus Shiraki, 1909",
            "bsf_valid_label": "",
            "bsf_otu": "83152",
            "bsf_url": otu_url(83152),
            "auto_rule": "exact",
            "check_status": CHECK_DONE,
            "notes": "示例行：已核对 → JSON verified=true",
            "reviewer": "示例复核人",
        },
        {
            "latin": "Mastotermes darwiniensis",
            "zh": "达尔文澳白蚁",
            "family_latin": "MASTOTERMITIDAE",
            "family_zh": "澳白蚁科",
            "bsf_status": "valid",
            "bsf_label": "Mastotermes darwiniensis Froggatt, 1897",
            "bsf_valid_label": "",
            "bsf_otu": "",
            "bsf_url": "",
            "auto_rule": "manual",
            "check_status": CHECK_FILL,
            "notes": "示例行：待补录 —— 人工填 bsf_otu（或整段 bsf_url）后再改成 已核对",
            "reviewer": "",
        },
    ]


def write_template(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in template_rows():
        writer.writerow(row)
    path.write_text(buf.getvalue(), encoding="utf-8-sig", newline="")


# --------------------------------------------------------------------------- #
# 导入人工复核结果
# --------------------------------------------------------------------------- #
def import_csv(path: Path, entries: dict, species: list[dict]) -> dict:
    known = {sp["latin"] for sp in species}
    unknown: list[str] = []
    changes: list[str] = []
    reviewers: dict[str, str] = {}
    verified_count = 0
    filled = 0
    merged = 0
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        missing_cols = [c for c in ("latin", "check_status") if c not in (reader.fieldnames or [])]
        if missing_cols:
            raise SystemExit("导入失败：%s 缺少列 %s" % (path.name, ", ".join(missing_cols)))
        for row in reader:
            latin = (row.get("latin") or "").strip()
            if not latin:
                continue
            if latin not in known:
                unknown.append(latin)
                continue
            merged += 1
            entry = entries.get(latin)
            if entry is None:
                entry = {
                    "status": "missing",
                    "otu": None,
                    "label": "",
                    "valid_otu": None,
                    "valid_label": None,
                    "url": None,
                    "match": None,
                    "verified": False,
                    "notes": "",
                }
            status = (row.get("check_status") or "").strip()
            notes = (row.get("notes") or "").strip()
            reviewer = (row.get("reviewer") or "").strip()
            otu_raw = (row.get("bsf_otu") or "").strip()
            url_raw = (row.get("bsf_url") or "").strip()
            label = (row.get("bsf_label") or "").strip()
            valid_label = (row.get("bsf_valid_label") or "").strip()
            status_col = (row.get("bsf_status") or "").strip()
            manual_otu = int(otu_raw) if otu_raw.isdigit() else None
            if manual_otu is None and url_raw:
                m = re.search(r"/otus/(\d+)", url_raw)
                if m:
                    manual_otu = int(m.group(1))

            if entry is None:
                # 这一行既没抓过、也没有人工结论：不要凭空造一条 "missing"
                if not manual_otu:
                    continue
                entry = {
                    "status": "missing",
                    "otu": None,
                    "label": "",
                    "valid_otu": None,
                    "valid_label": None,
                    "url": None,
                    "match": None,
                    "verified": False,
                    "notes": "",
                }

            prev_otu = entry.get("otu")
            if manual_otu and manual_otu != prev_otu:
                if prev_otu:
                    changes.append("%s：ID 变更 %s → %s（人工）" % (latin, prev_otu, manual_otu))
                else:
                    changes.append("%s：人工补录 OTU %s" % (latin, manual_otu))
                entry["otu"] = manual_otu
                entry["url"] = otu_url(manual_otu)
                entry["match"] = "manual"
                if label:
                    entry["label"] = label
                if valid_label:
                    entry["valid_label"] = valid_label
                if status_col in MATCHED:
                    entry["status"] = status_col
                elif entry["status"] not in MATCHED:
                    entry["status"] = "synonym" if valid_label else "valid"
                if entry["status"] == "valid":
                    entry["valid_otu"] = manual_otu
                    entry["valid_label"] = None
                elif entry["status"] == "synonym":
                    entry["valid_otu"] = manual_otu

            if status == CHECK_DONE:
                if entry.get("otu"):
                    entry["verified"] = True
                    verified_count += 1
                    if not manual_otu:
                        changes.append(
                            "%s：工作表 bsf_otu 为空，沿用 JSON 中已抓到的 OTU %s"
                            % (latin, entry["otu"])
                        )
                else:
                    entry["verified"] = False
                    changes.append("%s：标为已核对但没有 OTU，未采信（仍为 %s）" % (latin, entry["status"]))
            elif status == CHECK_FILL:
                entry["verified"] = False
                if manual_otu:
                    filled += 1
            if notes and notes != entry.get("notes"):
                entry["notes"] = notes
            if reviewer:
                # 复核人只写工作表（JSON 形状固定为 9 个字段），用 reviewers 映射带回去
                reviewers[latin] = reviewer
            entry["verified"] = bool(entry.get("verified"))
            if entry.get("otu"):
                entry["url"] = otu_url(entry["otu"])
            else:
                entry["url"] = None
            entries[latin] = entry
    return {
        "merged": merged,
        "unknown": unknown,
        "changes": changes,
        "verified": verified_count,
        "filled": filled,
        "reviewers": reviewers,
    }


# --------------------------------------------------------------------------- #
# 校验
# --------------------------------------------------------------------------- #
def check_repo() -> int:
    species = load_species()
    problems: list[str] = []
    if not DATA_PATH.exists():
        log("✗ %s 不存在" % rel(DATA_PATH))
        return 1
    try:
        doc = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log("✗ %s 不是合法 JSON：%s" % (rel(DATA_PATH), exc))
        return 1
    if not isinstance(doc, dict) or "meta" not in doc or "name_map" not in doc:
        log("✗ JSON 顶层必须含 meta 与 name_map")
        return 1
    meta = doc["meta"]
    name_map = doc["name_map"]
    known = {sp["latin"] for sp in species}
    for latin, raw in name_map.items():
        if latin not in known:
            problems.append("name_map 含 _species 中不存在的名称：%s" % latin)
        entry = sanitize_entry(raw, latin)
        if entry is None:
            problems.append("%s：条目结构不合法" % latin)
            continue
        extra = set(raw) - set(ENTRY_FIELDS)
        if extra:
            problems.append("%s：多余字段 %s" % (latin, sorted(extra)))
        if entry["status"] in MATCHED and not entry["otu"]:
            problems.append("%s：状态 %s 却无 otu" % (latin, entry["status"]))
        if entry["status"] not in MATCHED and entry["otu"]:
            problems.append("%s：状态 %s 却带 otu" % (latin, entry["status"]))
        if entry["url"] and entry["otu"] and entry["url"] != otu_url(entry["otu"]):
            problems.append("%s：url 与 otu 不一致" % latin)
        if entry["status"] == "synonym" and not entry["valid_label"]:
            problems.append("%s：synonym 缺 valid_label" % latin)
    counts = {key: 0 for key in STATUSES}
    for raw in name_map.values():
        status = raw.get("status")
        if status in counts:
            counts[status] += 1
    expected = {
        "total": len(species),
        "valid": counts["valid"],
        "synonym": counts["synonym"],
        "ambiguous": counts["ambiguous"],
        "missing": counts["missing"],
        "error": counts["error"],
    }
    got = meta.get("counts") or {}
    if got != expected:
        problems.append("meta.counts 与 name_map 不符：期望 %s，实际 %s" % (expected, got))
    if meta.get("fetched") != sum(counts.values()):
        problems.append("meta.fetched 与 name_map 不符")
    pending = len(species) - sum(counts.values())
    if meta.get("pending") != pending:
        problems.append("meta.pending 应为 %d" % pending)
    for key in ("source", "api", "citation", "review", "generated"):
        if not meta.get(key):
            problems.append("meta 缺 %s" % key)
    spot = meta.get("spot_check") or {}
    if spot.get("checked", 0) < spot.get("passed", 0):
        problems.append("spot_check.passed 大于 checked")

    if WORKSHEET_PATH.exists():
        previous = read_worksheet(WORKSHEET_PATH)
        expected_rows = worksheet_rows(species, name_map, previous)
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in expected_rows:
            writer.writerow({key: row.get(key, "") for key in CSV_FIELDS})
        current = WORKSHEET_PATH.read_text(encoding="utf-8-sig", newline="")
        if current.lstrip("\ufeff") != buf.getvalue():
            problems.append(
                "工作表与 JSON 不同步（改了 CSV 请先 --import；改了 JSON 请 --write 重排）"
            )
    else:
        problems.append("缺少 %s" % rel(WORKSHEET_PATH))

    log("== BSF 对照校验 ==")
    log("名称 %d 条；已分类 %d，未抓取 %d" % (len(species), sum(counts.values()), pending))
    for key in STATUSES:
        log("  %-9s %d" % (key, counts[key]))
    if problems:
        for line in problems[:40]:
            log("✗ " + line)
        if len(problems) > 40:
            log("… 另有 %d 条问题" % (len(problems) - 40))
        return 1
    log("✓ 产物一致")
    return 0


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(
        description="把 _species 的拉丁学名对照到 Blattodea Species File（半自动，可断点续跑）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--write", action="store_true", help="写入 _data/bsf_links.json 与工作表")
    parser.add_argument("--check", action="store_true", help="只校验仓库内产物是否一致（不联网）")
    parser.add_argument("--refresh", action="store_true", help="忽略缓存重新查询（已人工核对的条目保留）")
    parser.add_argument("--limit", type=int, default=0, help="本次最多新增查询 N 个名称（0 = 不限）")
    parser.add_argument("--budget", type=float, default=None, help="本次联网时间预算（秒）")
    parser.add_argument("--no-api", action="store_true", help="完全不联网，只用已有缓存重排产物")
    parser.add_argument("--import", dest="import_path", default=None, help="导入人工复核后的工作表 CSV")
    parser.add_argument("--spot-check", type=int, default=20, help="抽查多少个已匹配 OTU（默认 20，0 = 不抽查）")
    parser.add_argument("--seed", type=int, default=20250101, help="抽查抽样随机种子（保证可复现）")
    parser.add_argument("--quiet", action="store_true", help="减少进度输出")
    args = parser.parse_args(argv)

    if args.check:
        return check_repo()

    species = load_species()
    log("== Blattodea Species File 对照 ==")
    log("_species：%d 条名称" % len(species))
    if not species:
        log("✗ 未找到任何物種页，检查工作目录")
        return 1

    entries = {} if args.refresh else load_existing(DATA_PATH)
    if args.refresh:
        log("--refresh：忽略缓存（已人工核对 verified=true 的条目仍保留旧值，除非重新导入）")
        keep = {k: v for k, v in load_existing(DATA_PATH).items() if v.get("verified")}
        entries = keep
        if keep:
            log("  保留 %d 条已核对条目不再重查" % len(keep))
    cached = sum(1 for sp in species if sp["latin"] in entries)
    log("缓存命中：%d / %d" % (cached, len(species)))

    api_notes: list[str] = []
    aborted: str | None = None
    calls = 0
    reviewers: dict[str, str] = {}

    if args.import_path:
        path = Path(args.import_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            log("✗ 找不到导入文件 %s" % path)
            return 1
        report = import_csv(path, entries, species)
        reviewers = report["reviewers"]
        log(
            "导入 %s：合并 %d 行，已核对 %d，补录 %d"
            % (path.name, report["merged"], report["verified"], report["filled"])
        )
        for line in report["changes"]:
            log("  · ID/状态变化：" + line)
        if report["unknown"]:
            log("  ！%d 行 latin 不在 _species 中（已忽略，未写入 JSON）：" % len(report["unknown"]))
            for latin in report["unknown"][:20]:
                log("     - " + latin)
            if len(report["unknown"]) > 20:
                log("     … 另有 %d 行" % (len(report["unknown"]) - 20))
        if not report["changes"] and not report["unknown"]:
            log("  · 无变化")

    todo = [sp["latin"] for sp in species if sp["latin"] not in entries or entries[sp["latin"]]["status"] == "error"]
    if args.limit and args.limit > 0:
        todo = todo[: args.limit]
    if args.no_api:
        todo = []
        log("--no-api：跳过全部网络查询")

    if todo:
        client = ApiClient(budget=args.budget, verbose=not args.quiet)
        log(
            "待查询 %d 个名称（全局 ≤2 req/s，在途 ≤%d%s）"
            % (len(todo), CONCURRENCY, "，预算 %ds" % int(args.budget) if args.budget else "")
        )
        done = 0
        errors = 0

        def lookup(name: str):
            """单个名称的查询：异常就地收成哨兵值，避免丢掉同批已成功的结果。"""
            try:
                return client.autocomplete(name)
            except (BudgetExceeded, ApiAbort, ApiError) as exc:
                return exc

        pool = ThreadPoolExecutor(max_workers=CONCURRENCY)
        try:
            for start in range(0, len(todo), CHUNK):
                chunk = todo[start : start + CHUNK]
                for latin, outcome in zip(chunk, pool.map(lookup, chunk)):
                    if isinstance(outcome, ApiError):
                        entries[latin] = error_entry(str(outcome))
                        errors += 1
                        continue
                    if isinstance(outcome, BudgetExceeded):
                        aborted = "时间预算用尽（%ds）" % int(args.budget or 0)
                        break
                    if isinstance(outcome, ApiAbort):
                        aborted = str(outcome) or "API 请求失败"
                        break
                    entries[latin] = classify(latin, outcome)
                    done += 1
                if not args.quiet:
                    log(
                        "  … %d/%d（HTTP %d 次，已用 %.0fs）"
                        % (done, len(todo), client.calls, client.elapsed())
                    )
                if aborted:
                    break
                if client.fail_streak >= MAX_CONSECUTIVE_FAILS:
                    aborted = "连续 %d 次请求失败，先停下（可能被限流）" % client.fail_streak
                    break
        except KeyboardInterrupt:
            aborted = "被手动中断"
            log("！中断，保留已抓到的结果")
        finally:
            pool.shutdown(wait=True)
        calls = client.calls
        log(
            "本次完成 %d 个查询（其中 %d 个失败标 error），HTTP 调用 %d 次，用时 %.0fs"
            % (done, errors, calls, client.elapsed())
        )
        if aborted:
            api_notes.append(aborted)
            log("！%s —— 已保留部分结果，可用同样的命令续跑" % aborted)
    else:
        log("无需联网：全部名称已有缓存")

    spot = None
    if not args.no_api and args.spot_check > 0:
        log("抽查 %d 个已匹配 OTU 的 overview 页面…" % args.spot_check)
        try:
            spot = spot_check(entries, args.spot_check, args.seed)
            log("抽查：%d/%d 通过" % (spot["passed"], spot["checked"]))
            for row in spot["sample"]:
                if not row["ok"]:
                    log("  ✗ %s  %s  %s" % (row["latin"], row["url"], row.get("note", "")))
        except Exception as exc:  # 抽查是附加信息，不阻塞主流程
            log("！抽查失败：%s" % exc)
            spot = {"checked": 0, "passed": 0, "sample": [], "note": "抽查失败：%s" % str(exc)[:160]}

    doc = build_document(
        species,
        entries,
        spot,
        now_iso(),
        calls,
        "；".join(api_notes) if api_notes else None,
    )
    counts = doc["meta"]["counts"]
    log("")
    log("== 分类统计 ==")
    log("  total     %d" % counts["total"])
    for key in ("valid", "synonym", "ambiguous", "missing", "error"):
        log("  %-9s %d" % (key, counts[key]))
    if doc["meta"]["pending"]:
        log("  pending   %d（尚未抓取）" % doc["meta"]["pending"])

    if args.write or args.import_path:
        previous = read_worksheet(WORKSHEET_PATH)
        write_json(DATA_PATH, doc)
        rows = worksheet_rows(species, entries, previous, reviewers)
        write_worksheet(WORKSHEET_PATH, rows)
        write_template(TEMPLATE_PATH)
        log("")
        log("已写入：")
        log("  %s" % rel(DATA_PATH))
        log("  %s（%d 行）" % (rel(WORKSHEET_PATH), len(rows)))
        log("下一步：人工复核工作表 → --import 回收 → 再 --write/--check")
    else:
        log("")
        log("（只统计，未写文件；加 --write 写入）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
