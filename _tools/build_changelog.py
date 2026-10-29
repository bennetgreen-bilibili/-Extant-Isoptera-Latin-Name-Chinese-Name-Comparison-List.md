#!/usr/bin/env python3
"""从 dataset/CHANGELOG.md 生成「版本记录」数据与 Atom feed。

  _data/changelog.json   版本记录页（/changelog/ 三语）用
  changelog.atom         静态 Atom feed（root，部署后可在阅读器订阅）

版本号就是名录发布日期（YYYY.MM.DD），因此条目顺序 = 日期倒序 = 文件顺序。
输出确定性（不含生成时间戳），可用 --check 校验。

用法：
  python _tools/build_changelog.py           # 只统计
  python _tools/build_changelog.py --write   # 写入两个产物
  python _tools/build_changelog.py --check   # 校验产物是否最新
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dataset" / "CHANGELOG.md"
CONFIG = ROOT / "_config.yml"
DATA_OUT = ROOT / "_data" / "changelog.json"
ATOM_OUT = ROOT / "changelog.atom"

VERSION_RE = re.compile(r"^##\s+(\d{4}\.\d{2}\.\d{2})\s*[—-]+\s*(.+?)\s*$")
BULLET_RE = re.compile(r"^(\s*)[-*]\s+(.+?)\s*$")
CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def inline_html(text: str) -> str:
    """把 CHANGELOG 条目里的行内 Markdown 转成最小 HTML（page 里直接输出，无需 markdown 渲染）。"""
    s = escape(text)
    s = CODE_RE.sub(lambda m: "<code>" + m.group(1) + "</code>", s)
    s = LINK_RE.sub(lambda m: '<a href="' + m.group(2) + '">' + m.group(1) + "</a>", s)
    s = BOLD_RE.sub(lambda m: "<strong>" + m.group(1) + "</strong>", s)
    return s


def site_url() -> str:
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"^base_url:\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        sys.exit("error: 无法从 _config.yml 读取 base_url")
    return m.group(1).strip().strip("'\"").rstrip("/")


def parse_changelog() -> dict:
    versions = []
    current = None
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        m = VERSION_RE.match(line)
        if m:
            date, title = m.group(1), m.group(2)
            current = {"version": date, "date": date.replace(".", "-"), "title": title, "items": []}
            versions.append(current)
            continue
        b = BULLET_RE.match(line)
        if b and current is not None:
            depth = 1 if len(b.group(1)) >= 2 else 0
            text = b.group(2)
            current["items"].append({"depth": depth, "text": text, "html": inline_html(text)})
    if not versions:
        sys.exit("error: " + SOURCE.name + " 里没有解析到版本标题（## YYYY.MM.DD — 标题）")
    return {
        "meta": {"source": "dataset/CHANGELOG.md", "versions": len(versions)},
        "versions": versions,
    }


def atom(payload: dict) -> str:
    base = site_url()
    updated = payload["versions"][0]["date"] + "T00:00:00Z"
    parts = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="zh-CN">',
        "  <title>现存等翅下目（白蚁）拉丁学名—中文正名对照名录 · 版本记录</title>",
        "  <subtitle>Extant Isoptera (Termites) checklist — release changelog</subtitle>",
        "  <id>" + escape(base + "/changelog/") + "</id>",
        '  <link rel="self" type="application/atom+xml" href="' + escape(base + "/changelog.atom") + '"/>',
        '  <link rel="alternate" type="text/html" href="' + escape(base + "/changelog/") + '"/>',
        "  <updated>" + updated + "</updated>",
        "  <author><name>班奈特格林 (Bennet Green)</name><uri>" + escape(base + "/") + "</uri></author>",
    ]
    for v in payload["versions"]:
        entry_id = base + "/changelog/" + v["version"].replace(".", "-") + "/"
        summary = "".join(escape(i["text"]) + "\n" for i in v["items"] if i["depth"] == 0)
        parts += [
            "  <entry>",
            "    <title>" + escape(v["version"] + " — " + v["title"]) + "</title>",
            "    <id>" + escape(entry_id) + "</id>",
            '    <link rel="alternate" type="text/html" href="' + escape(base + "/changelog/#v" + v["version"].replace(".", "-")) + '"/>',
            "    <updated>" + v["date"] + "T00:00:00Z</updated>",
            "    <published>" + v["date"] + "T00:00:00Z</published>",
            '    <content type="text">' + escape(summary) + "</content>",
            "  </entry>",
        ]
    parts.append("</feed>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="生成版本记录数据与 Atom feed")
    parser.add_argument("--write", action="store_true", help="写入 _data/changelog.json 与 changelog.atom")
    parser.add_argument("--check", action="store_true", help="校验产物是否最新")
    args = parser.parse_args()

    if not SOURCE.is_file():
        sys.exit("error: 找不到 " + str(SOURCE.relative_to(ROOT)))
    payload = parse_changelog()
    js = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    xml = atom(payload)

    print("版本 %d 个：%s；条目 %d 条" % (
        payload["meta"]["versions"],
        " / ".join(v["version"] for v in payload["versions"]),
        sum(len(v["items"]) for v in payload["versions"])))

    if args.check:
        problems = []
        if not DATA_OUT.is_file() or DATA_OUT.read_text(encoding="utf-8") != js:
            problems.append("_data/changelog.json")
        if not ATOM_OUT.is_file() or ATOM_OUT.read_text(encoding="utf-8") != xml:
            problems.append("changelog.atom")
        if problems:
            print("error: 以下产物已过期，请运行 --write：" + "、".join(problems), file=sys.stderr)
            return 1
        print("校验通过：_data/changelog.json 与 changelog.atom 均为最新")
        return 0

    if args.write:
        DATA_OUT.write_text(js, encoding="utf-8", newline="\n")
        ATOM_OUT.write_text(xml, encoding="utf-8", newline="\n")
        print("已写入 _data/changelog.json、changelog.atom")
    else:
        print("未写入（加 --write 写入文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
