#!/usr/bin/env python3
"""分布图产物闸门（离线·只读）：assets/geo/**/*.geojson 与索引一一对应，且 JSON 合法。

索引分两处，缺一不可：

  _data/occurrence_summary.json  -> families / genera / species
                                    （.github/workflows/build_occurrence_geojson.py 从 GBIF 抓来的
                                     科/属/种 1° 网格地图）
  _data/subfamily_maps.json      -> subfamilies
                                    （.github/workflows/build_taxonomy_pages.py 把本亚科各属的
                                     网格地图按坐标合并而成；GBIF 没有亚科层级，所以单独一份索引）

两个方向都必须成立，任一失败即退出码 1：

  · 索引引用、磁盘没有 -> 线上地图 404（missing）
  · 磁盘存在、索引没有 -> 生成器留下没人引用的残件（orphan）

本文件是这条不变量的**唯一实现**：_tools/check_site.py 的 check_geo() 与
.github/workflows/pages.yml 的「Verify external data caches」步骤都调用它。
以前那段校验内联在 pages.yml 里，只认 occurrence_summary.json；加上亚科地图后
（assets/geo/subfamily/ 15 个文件 + _data/subfamily_maps.json）内联版把它们全算成
孤儿，部署因此假红。以后再加一层目录（比如族/亚族），只改这里即可。

用法：
  python _tools/check_geo.py            # 失败时打印逐条明细
  python _tools/check_geo.py --quiet    # 只打印计数
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
OCCURRENCE = "_data/occurrence_summary.json"
SUBFAMILY_MAPS = "_data/subfamily_maps.json"
GEO_DIR = "assets/geo"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))


def listed_files(root: Path = ROOT) -> tuple[set, list]:
    """索引引用的 GeoJSON 相对路径（POSIX 形式）；第二个返回值是索引本身的问题。"""
    listed: set = set()
    problems: list = []

    occurrence = root / OCCURRENCE
    if not occurrence.is_file():
        problems.append(OCCURRENCE + " 不存在（运行 build_occurrence_geojson.py --write）")
    else:
        try:
            summary = _load(occurrence)
        except Exception as exc:  # JSON 坏了也要说清楚是哪个文件
            problems.append("%s JSON 不可解析：%s" % (OCCURRENCE, str(exc)[:120]))
            summary = None
        if summary is not None:
            for item in summary.get("families") or []:
                listed.add(item["file"])
            for item in summary.get("genera") or []:
                listed.add(item["file"])
            for item in (summary.get("species") or {}).values():
                listed.add(item["file"])

    subfamily_maps = root / SUBFAMILY_MAPS
    if subfamily_maps.is_file():
        try:
            for item in _load(subfamily_maps).get("subfamilies") or []:
                listed.add(item["file"])
        except Exception as exc:
            problems.append("%s JSON 不可解析：%s" % (SUBFAMILY_MAPS, str(exc)[:120]))
    else:
        # 亚科索引缺失本身不算错（老分支没有这一层），但磁盘上若有亚科地图就成了孤儿，
        # 会在下面 missing/orphan 里如实报出来。
        pass

    return {Path(p).as_posix() for p in listed}, problems


def collect(root: Path = ROOT) -> dict:
    """返回一条完整体检结果，供本脚本的 CLI 与 check_site.py 共用。"""
    listed, problems = listed_files(root)
    geo_dir = root / GEO_DIR
    disk = {p.relative_to(root).as_posix() for p in geo_dir.rglob("*.geojson")} if geo_dir.is_dir() else set()

    invalid = []
    for rel in sorted(disk):
        try:
            _load(root / rel)
        except Exception as exc:
            invalid.append((rel, str(exc)[:100]))

    return {
        "listed": listed,
        "disk": disk,
        "problems": problems,
        "missing": sorted(listed - disk),
        "orphan": sorted(disk - listed),
        "invalid": invalid,
    }


def _emit(where: str, msg: str) -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("::error file=%s::%s" % (where, msg))
    print("  [ERROR] %s: %s" % (where, msg))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="分布图产物与索引一一对应（离线校验）")
    parser.add_argument("--quiet", action="store_true", help="只打印计数与错误")
    args = parser.parse_args(argv)

    report = collect(ROOT)
    failed = bool(report["problems"] or report["missing"] or report["orphan"] or report["invalid"])

    if not args.quiet or failed:
        print("分布图产物：索引 %d 条 / 磁盘 %d 个" % (len(report["listed"]), len(report["disk"])))

    for problem in report["problems"]:
        _emit("_data", problem)

    if report["missing"]:
        _emit("assets/geo", "%d 个索引引用但磁盘缺失的 GeoJSON（线上地图会 404）" % len(report["missing"]))
        for rel in report["missing"]:
            print("    - " + rel)

    if report["orphan"]:
        _emit("assets/geo", "%d 个磁盘存在但索引未引用的 GeoJSON（孤儿产物）" % len(report["orphan"]))
        for rel in report["orphan"]:
            print("    + " + rel)

    if report["invalid"]:
        for rel, msg in report["invalid"]:
            _emit(rel, "GeoJSON 解析失败：" + msg)

    if failed:
        return 1

    if not args.quiet:
        print("geo artefacts OK：%d 个文件全部被索引引用，JSON 合法" % len(report["disk"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
