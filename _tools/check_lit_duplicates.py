#!/usr/bin/env python3
"""检查「研究记述」的重复：同一页面内、跨页面、以及草稿与既有数据之间。

背景：2026-11-15-r2 轮出现两类重复——
1) 扫描按「读得最少」排序，某来源此前已写进页面，新一轮又从同一记录重写；
2) 同一项多物种研究被整段抄到多个种页。
`check_taxon_literature.py` 只查同一页面内的逐字重复段落，查不出跨页面近似重复，
也查不出草稿与既有数据之间的重复。本脚本补这一层。

用法：
    python _tools/check_lit_duplicates.py                     # 查 _data/taxon_literature/ 分片
    python _tools/check_lit_duplicates.py --draft path.json   # 草稿 vs 既有数据 + 草稿内部
    python _tools/check_lit_duplicates.py --threshold 0.8 --json

退出码：0 无重复；1 有达到阈值的重复；2 参数／文件错误。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools"))
import shard_io  # noqa: E402

BASELINE = ROOT / "_reports" / "library-reading" / "duplicate-baseline.json"
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def load_baseline() -> set:
    if not BASELINE.exists():
        return set()
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    out = set()
    for item in data.get("pairs", []):
        a, b = item.get("a"), item.get("b")
        if a and b:
            out.add((a, b) if a <= b else (b, a))
    return out


def norm(text: str) -> str:
    text = TAG_RE.sub("", text or "")
    text = WS_RE.sub("", text)
    return text.lower()


def load_pages(path: Path | None = None, data: dict | None = None) -> dict:
    if data is None:
        data = json.loads(path.read_text(encoding="utf-8"))
    pages = {}
    for url, page in data.items():
        if not isinstance(page, dict) or "sections" not in page:
            continue
        paras = []
        for sec in page["sections"]:
            for p in sec.get("paragraphs", []):
                paras.append((sec.get("heading", ""), p))
        pages[url] = paras
    return pages


def iter_paras(pages: dict):
    for url, paras in pages.items():
        for heading, p in paras:
            text = p.get("text", "")
            n = norm(text)
            if len(n) >= 1:
                yield url, heading, text, n, p.get("src", [])


def main() -> int:
    ap = argparse.ArgumentParser(description="查研究记述的重复段落")
    ap.add_argument("--data", default=None,
                    help="既有数据 JSON（默认读 _data/taxon_literature/ 分片）")
    ap.add_argument("--draft", help="草稿 JSON；给了就同时比草稿与既有数据")
    ap.add_argument("--threshold", type=float, default=0.70, help="相似度阈值（默认 0.70）")
    ap.add_argument("--min-chars", type=int, default=40, help="参与比较的最短正文字数（默认 40）")
    ap.add_argument("--limit", type=int, default=40, help="最多打印多少条")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    ap.add_argument("--strict", action="store_true", help="忽略 duplicate-baseline.json（用于清理基线）")
    args = ap.parse_args()

    if args.data:
        data_path = Path(args.data)
        if not data_path.is_absolute():
            data_path = ROOT / data_path
        if not data_path.exists():
            print(f"[dupes] 找不到数据文件：{data_path}", file=sys.stderr)
            return 2
        base = load_pages(data_path)
    else:
        base = load_pages(data=shard_io.load("taxon_literature"))
    base_items = [it for it in iter_paras(base) if len(it[3]) >= args.min_chars]

    draft_items = []
    if args.draft:
        dpath = Path(args.draft)
        if not dpath.is_absolute():
            dpath = ROOT / dpath
        if not dpath.exists():
            print(f"[dupes] 找不到草稿：{dpath}", file=sys.stderr)
            return 2
        draft = load_pages(dpath)
        draft_items = [it for it in iter_paras(draft) if len(it[3]) >= args.min_chars]

    hits = []
    baselined = []
    baseline = set() if args.strict else load_baseline()

    def compare(a, b, kind):
        ratio = SequenceMatcher(None, a[3], b[3]).ratio()
        if ratio >= args.threshold:
            item = {
                "kind": kind,
                "ratio": round(ratio, 3),
                "a_page": a[0], "a_heading": a[1], "a_text": a[2], "a_src": a[4],
                "b_page": b[0], "b_heading": b[1], "b_text": b[2], "b_src": b[4],
            }
            pair = (a[0], b[0]) if a[0] <= b[0] else (b[0], a[0])
            if pair in baseline:
                item["baselined"] = True
                baselined.append(item)
            else:
                hits.append(item)

    # 既有数据内部
    for i in range(len(base_items)):
        for j in range(i + 1, len(base_items)):
            a, b = base_items[i], base_items[j]
            if a[0] == b[0] and a[3] == b[3]:
                compare(a, b, "exact")
                continue
            compare(a, b, "cross-page" if a[0] != b[0] else "same-page")

    # 草稿 vs 既有数据
    if args.draft:
        for a in draft_items:
            for b in base_items:
                if a[3] == b[3] or SequenceMatcher(None, a[3], b[3]).quick_ratio() >= args.threshold:
                    compare(a, b, "draft-vs-data")
        # 草稿内部
        for i in range(len(draft_items)):
            for j in range(i + 1, len(draft_items)):
                a, b = draft_items[i], draft_items[j]
                if a[3] == b[3]:
                    compare(a, b, "draft-exact")
                else:
                    compare(a, b, "draft-internal")

    hits.sort(key=lambda h: -h["ratio"])

    if args.json:
        print(json.dumps({"threshold": args.threshold, "count": len(hits),
                          "baselined": len(baselined), "hits": hits[: args.limit]},
                         ensure_ascii=False, indent=1))
    else:
        print(f"[dupes] 既有段落 {len(base_items)}，草稿段落 {len(draft_items)}，阈值 {args.threshold}")
        for h in hits[: args.limit]:
            print(f"ERROR {h['ratio']:.3f} {h['kind']}")
            print(f"  A {h['a_page']} / {h['a_heading']} / {h['a_src']}")
            print(f"    {h['a_text'][:110]}")
            print(f"  B {h['b_page']} / {h['b_heading']} / {h['b_src']}")
            print(f"    {h['b_text'][:110]}")
        if len(hits) > args.limit:
            print(f"…… 另有 {len(hits) - args.limit} 条")
        if baselined:
            print(f"INFO {len(baselined)} 条在 duplicate-baseline.json 基线内（未判失败；--strict 可复查）")
        print("OK 没有达到阈值的重复段落" if not hits else f"发现 {len(hits)} 条重复/近似重复")

    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
