#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三语分页检查：zh / en / es 三份页面齐备、各自单语、站内链接带语言前缀。

为什么需要这个脚本
-----------------
2026-11 起，family / subfamily / genus / species 四类页面从「一页内嵌
<span class="fact-en"> + <span class="fact-es"> 的三语并列」拆成三份独立页面：

    /family/termitidae/        zh-CN   family/termitidae.md
    /en/family/termitidae/     en      en/family/termitidae.md
    /es/family/termitidae/     es      es/family/termitidae.md

拆分之后最容易回来的四类回退，人眼很难查（357 个分类单元 + 3157 个物种 × 3 语言
= 一万多个文件）：

1. **漏页**：某个语言少了某个分类单元 / 物种页 → 语言切换器与 hreflang 指向 404；
2. **混语**：生成器里残留 fact-en / fact-es 包裹，或 `EN — …` / `ES — …` 并列段，
   又让同一页出现两种语言；
3. **链接跨语**：en/es 页里的站内链接忘了加 /en、/es 前缀，读者一点就跳回中文；
4. **permalink 不对**：文件放在 en/family/x.md 但 permalink 写 /family/x/，
   两份页面抢同一个地址（Jekyll 后写覆盖先写，静默丢页）。

检查项
------
A. 文件齐备：taxonomy.json 的 13 科 / 18 亚科 / 326 属，以及 _species/ 下每个物种，
   三种语言的文件都存在；
B. front matter：语言标签、permalink 与文件位置一致（zh 无前缀，en/es 有前缀），
   分类页与物种页都不再带 `lang_only: true`；
C. 单语：三个语言的页面正文都不得出现 `fact-en` / `fact-es` / `EN —` / `ES —`；
   en/es 正文不得出现中文字句标点（。；，、！？「」），也不得有 ≥12 连续汉字
   （中文专名通常 ≤9 字，长串基本是把中文正文留在了外文页）；
D. 站内链接：en/es 页里的 {{ site.base_url }}/family/… 一类必须是 /en/family/… 或
   /es/family/…，且不得出现 /en/en/ 双前缀；
E. 译文覆盖率（警告）：_data/translations_en.json / translations_es.json 是否存在，
   以及 _tools/check_translations.py 的合并结果（若已生成）。

用法
----
    python _tools/check_lang_pages.py                 # 全站检查，打印汇总
    python _tools/check_lang_pages.py --ci            # 同上，CI 用（错误即退出 1）
    python _tools/check_lang_pages.py --strict        # 警告也当错误（交付前跑）
    python _tools/check_lang_pages.py --only genus    # 只查某一级（family/subfamily/genus/species）
    python _tools/check_lang_pages.py --quiet         # 只输出问题行

退出码：0 通过；1 有错误（--strict 时含警告）；2 参数错误。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY = os.path.join(ROOT, "_data", "taxonomy.json")
SPECIES_DIR = os.path.join(ROOT, "_species")
TRANS_EN = os.path.join(ROOT, "_data", "translations_en.json")
TRANS_ES = os.path.join(ROOT, "_data", "translations_es.json")

# (语言键, 目录前缀, front matter 里的 lang 值)
LANGS = (("zh", "", "zh-CN"), ("en", "en/", "en"), ("es", "es/", "es"))
RANKS = ("family", "subfamily", "genus")

# 三语并列的残留标记
SPAN_MARKS = ('fact-en', 'fact-es', 'class="fact-', "class='fact-")
EN_DASH = re.compile(r"^\s*EN\s+—", re.M)
ES_DASH = re.compile(r"^\s*ES\s+—", re.M)

# en/es 页里不该出现的中文标点（出现即说明整句中文留在外文页）
ZH_PUNCT = "。；，、！？「」"
ZH_PUNCT_SOFT = "：（）"
CJK_RUN = re.compile(r"[\u4e00-\u9fff]{12,}")

# 站内一级栏目：en/es 页里出现不带语言前缀的写法即为漏前缀
SECTIONS = (
    "family", "subfamily", "genus", "species", "list", "stats", "data",
    "download", "papers", "blog", "guestbook", "changelog", "name-issues", "search",
)

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


class Report:
    def __init__(self, quiet=False, limit=40):
        self.errors = []
        self.warns = []
        self.quiet = quiet
        self.limit = limit
        self.checked = 0

    def err(self, code, path, msg):
        self.errors.append((code, path, msg))

    def warn(self, code, path, msg):
        self.warns.append((code, path, msg))

    def emit(self):
        out = []
        for level, items in (("ERROR", self.errors), ("WARN ", self.warns)):
            for code, path, msg in items[: self.limit]:
                out.append("%s [%s] %s: %s" % (level, code, path, msg))
            if len(items) > self.limit:
                out.append("  … 另有 %d 条 %s 未列出（--limit 调大）" % (len(items) - self.limit, level.strip()))
        return out


def read_page(path):
    """返回 (front matter dict, body)。front matter 用极简解析，避免依赖 PyYAML。"""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = FM_RE.match(text)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        if not line or line[0] in " \t#" or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if v in ("true", "false"):
            fm[k.strip()] = v == "true"
        else:
            fm[k.strip()] = v
    return fm, text[m.end():]


def check_page(rep, rank, slug, lang, dirprefix, want_lang):
    rel = "%s%s/%s.md" % (dirprefix, rank, slug) if rank != "species" else None
    if rank == "species":
        if lang == "zh":
            rel = "_species/%s.md" % slug
        else:
            rel = "%sspecies/%s.md" % (dirprefix, slug)
    path = os.path.join(ROOT, rel)
    want_url = "/%s%s/%s/" % (dirprefix, rank, slug)

    if not os.path.isfile(path):
        rep.err("E001", rel, "缺少页面（应为 %s）" % want_url)
        return
    rep.checked += 1

    fm, body = read_page(path)
    if fm is None:
        rep.err("E002", rel, "没有 front matter")
        return

    got_lang = fm.get("lang")
    if lang == "zh":
        if got_lang not in (None, "", "zh-CN", "zh-cn"):
            rep.err("E003", rel, "zh 页的 lang 应为 zh-CN（现为 %r）" % got_lang)
    elif got_lang != want_lang:
        rep.err("E003", rel, "lang 应为 %r（现为 %r）" % (want_lang, got_lang))

    if fm.get("lang_only") is True:
        rep.err("E004", rel, "拆分后不应再有 lang_only: true（会让语言切换器与 hreflang 消失）")

    if fm.get("single_lang") is not True:
        rep.warn("W001", rel, "建议标注 single_lang: true（说明本页只含一种语言）")

    permalink = fm.get("permalink")
    if permalink != want_url:
        rep.err("E005", rel, "permalink 应为 %s（现为 %r）" % (want_url, permalink))

    if rank == "species" and lang != "zh":
        if fm.get("species_page") is not True:
            rep.err("E006", rel, "en/es 物种页需 species_page: true（default.html 据此加载 PhotoSwipe/Leaflet 并生成 hreflang）")
        if fm.get("layout") != "species":
            rep.err("E007", rel, "layout 应为 species（现为 %r）" % fm.get("layout"))

    # C 单语检查
    for mark in SPAN_MARKS:
        if mark in body:
            rep.err("E010", rel, "正文残留三语标记 %r" % mark)
            break
    if EN_DASH.search(body) or ES_DASH.search(body):
        rep.err("E011", rel, "正文残留 EN —/ES — 并列段")

    if lang != "zh":
        hits = [ch for ch in ZH_PUNCT if ch in body]
        if hits:
            rep.err("E012", rel, "外文页出现中文标点 %s（中文句子未替换）" % "".join(hits))
        soft = [ch for ch in ZH_PUNCT_SOFT if ch in body]
        if soft:
            rep.err("E013", rel, "外文页出现中文括号/冒号 %s" % "".join(soft))
        long_runs = CJK_RUN.findall(body)
        if long_runs:
            rep.err("E014", rel, "外文页出现 %d 处 ≥12 连续汉字（如 %r）" % (len(long_runs), long_runs[0][:14]))

        # D 链接前缀
        for sec in SECTIONS:
            for pat in ("site.base_url }}/%s/" % sec, "site.base_url}}/%s/" % sec,
                        'href="/%s/' % sec, "](/%s/" % sec):
                if pat in body:
                    rep.err("E020", rel, "站内链接缺语言前缀：%s" % pat)
        if ("/%s/%s/" % (dirprefix.strip("/"), dirprefix.strip("/"))) in body:
            rep.err("E021", rel, "出现双语言前缀（如 %s%s/）" % (dirprefix, dirprefix))


def load_units(only):
    with open(TAXONOMY, encoding="utf-8") as fh:
        data = json.load(fh)
    units = []
    if only in (None, "family"):
        units += [("family", f["id"]) for f in data.get("families", [])]
    if only in (None, "subfamily"):
        units += [("subfamily", s["id"]) for s in data.get("subfamilies", [])]
    if only in (None, "genus"):
        units += [("genus", g["id"]) for g in data.get("genera", [])]
    if only in (None, "species"):
        for name in sorted(os.listdir(SPECIES_DIR)):
            if name.endswith(".md"):
                units.append(("species", name[:-3]))
    return units


def coverage(rep):
    if not (os.path.isfile(TRANS_EN) and os.path.isfile(TRANS_ES)):
        rep.warn("W010", "_data/translations_*.json", "译文文件尚未生成（en/es 页会缺小节）")
        return
    for p in (TRANS_EN, TRANS_ES):
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            rep.err("E030", os.path.relpath(p, ROOT).replace("\\", "/"), "JSON 解析失败：%s" % exc)
            continue
        keys = {k: len(v) if isinstance(v, (list, dict)) else 1 for k, v in d.items() if k != "meta"}
        rep.info_trans = getattr(rep, "info_trans", {})
        rep.info_trans[os.path.basename(p)] = keys


def main(argv=None):
    ap = argparse.ArgumentParser(description="三语分页检查（zh / en / es）")
    ap.add_argument("--ci", action="store_true", help="CI 模式：有错误即退出 1")
    ap.add_argument("--strict", action="store_true", help="警告也当错误（交付前跑）")
    ap.add_argument("--only", choices=RANKS + ("species",), help="只检查某一级")
    ap.add_argument("--quiet", action="store_true", help="只输出问题行")
    ap.add_argument("--limit", type=int, default=40, help="每类问题最多打印几条（默认 40）")
    args = ap.parse_args(argv)

    if not os.path.isfile(TAXONOMY):
        print("找不到 %s —— 先跑 _tools/regen_all.sh" % TAXONOMY, file=sys.stderr)
        return 2

    rep = Report(quiet=args.quiet, limit=args.limit)
    units = load_units(args.only)
    for rank, slug in units:
        for lang, prefix, want in LANGS:
            check_page(rep, rank, slug, lang, prefix, want)
    coverage(rep)

    if not args.quiet:
        print("检查页面：%d 个文件（%d 个分类单元/物种 × 3 语言）" % (rep.checked, len(units)))
        for name, keys in getattr(rep, "info_trans", {}).items():
            total = sum(v for k, v in keys.items() if k != "meta")
            print("  %s：%s" % (name, ", ".join("%s=%d" % (k, v) for k, v in sorted(keys.items())) + "（合计 %d 条）" % total))

    lines = rep.emit()
    if lines:
        print("\n".join(lines))
    print("错误 %d 条，警告 %d 条" % (len(rep.errors), len(rep.warns)))

    bad = bool(rep.errors) or (args.strict and bool(rep.warns))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
