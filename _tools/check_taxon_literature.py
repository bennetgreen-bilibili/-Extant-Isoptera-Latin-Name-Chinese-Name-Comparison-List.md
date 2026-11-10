#!/usr/bin/env python3
"""校验 _data/taxon_literature.json（或审阅草稿 JSON）的结构与引用完整性。

检查项：
  - 页面 key 必须是真实存在的 /genus/、/family/、/subfamily/、/species/ 页面；
  - 每段有非空 text 和至少一个 src；
  - 每个 src / references[].id 都能在 .sources/index.json 找到；
  - references 覆盖正文用到的全部来源，且不含未用到的来源；
  - 同一页面内没有重复段落；
  - updated 为 YYYY-MM-DD。

用法：
  python _tools/check_taxon_literature.py
  python _tools/check_taxon_literature.py --file _tmp/review/2026-11-12/draft.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LITERATURE = ROOT / "_data" / "taxon_literature.json"
SOURCES = ROOT / ".sources" / "index.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PAGE_RE = re.compile(r"^/(genus|family|subfamily|species)/([a-z0-9-]+)/$")


def load(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def page_path(url):
    m = PAGE_RE.match(url)
    if not m:
        return None
    kind, slug = m.groups()
    if kind == "species":
        return ROOT / "_species" / (slug + ".md")
    return ROOT / kind / (slug + ".md")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", default=str(LITERATURE), help="要校验的 JSON（默认 _data/taxon_literature.json）")
    args = ap.parse_args()
    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path

    try:
        data = load(path)
    except Exception as exc:
        print("无法读取 %s：%s" % (path, exc))
        return 2
    try:
        index = load(SOURCES)
        source_ids = {r.get("id") for r in index.get("sources", []) if r.get("id")}
    except Exception as exc:
        print("无法读取 %s：%s" % (SOURCES, exc))
        return 2

    errors = []
    warnings = []
    pages = 0
    paragraphs = 0
    cited = set()

    if not isinstance(data, dict):
        print("顶层必须是对象")
        return 1

    for url, lit in sorted(data.items()):
        if url == "_meta":
            continue
        pages += 1
        target = page_path(url)
        if target is None:
            errors.append("%s：key 不是合法的分类页面 URL" % url)
            continue
        if not target.is_file():
            errors.append("%s：页面文件不存在（%s）" % (url, target.relative_to(ROOT)))
            continue
        if not isinstance(lit, dict):
            errors.append("%s：值必须是对象" % url)
            continue

        updated = lit.get("updated")
        if updated and not DATE_RE.match(str(updated)):
            errors.append("%s：updated 不是 YYYY-MM-DD" % url)

        sections = lit.get("sections")
        if not isinstance(sections, list) or not sections:
            errors.append("%s：sections 必须是非空数组" % url)
            continue

        page_cited = set()
        seen_text = set()
        for si, sec in enumerate(sections):
            if not isinstance(sec, dict):
                errors.append("%s：sections[%d] 不是对象" % (url, si))
                continue
            heading = (sec.get("heading") or "").strip()
            if not heading:
                warnings.append("%s：sections[%d] 没有 heading" % (url, si))
            paras = sec.get("paragraphs")
            if not isinstance(paras, list) or not paras:
                errors.append("%s：sections[%d].paragraphs 必须是非空数组" % (url, si))
                continue
            for pi, para in enumerate(paras):
                where = "%s sections[%d].paragraphs[%d]" % (url, si, pi)
                if not isinstance(para, dict):
                    errors.append("%s：不是对象" % where)
                    continue
                text = (para.get("text") or "").strip()
                if not text:
                    errors.append("%s：text 为空" % where)
                    continue
                if len(text) < 20:
                    warnings.append("%s：text 很短（%d 字）" % (where, len(text)))
                if text in seen_text:
                    errors.append("%s：页面内重复段落" % where)
                seen_text.add(text)
                src = para.get("src") or []
                if not isinstance(src, list) or not src:
                    errors.append("%s：src 必须是非空数组" % where)
                    continue
                for sid in src:
                    if sid not in source_ids:
                        errors.append("%s：src %s 不在 .sources/index.json" % (where, sid))
                    page_cited.add(sid)
                    cited.add(sid)
                paragraphs += 1

        refs = lit.get("references")
        if not isinstance(refs, list) or not refs:
            errors.append("%s：references 必须是非空数组" % url)
            continue
        ref_ids = set()
        for ri, ref in enumerate(refs):
            where = "%s references[%d]" % (url, ri)
            if not isinstance(ref, dict):
                errors.append("%s：不是对象" % where)
                continue
            rid = ref.get("id")
            if not rid:
                errors.append("%s：缺少 id" % where)
                continue
            if rid in ref_ids:
                errors.append("%s：参考文献 id 重复" % where)
            ref_ids.add(rid)
            if rid not in source_ids:
                errors.append("%s：id %s 不在 .sources/index.json" % (where, rid))
            if not (ref.get("citation") or "").strip():
                errors.append("%s：citation 为空" % where)
            if not (ref.get("url") or ref.get("doi")):
                warnings.append("%s：没有 url/doi（可以接受，但请确认）" % where)
        missing = sorted(page_cited - ref_ids)
        extra = sorted(ref_ids - page_cited)
        if missing:
            errors.append("%s：正文引用了但参考文献未列：%s" % (url, ", ".join(missing)))
        if extra:
            errors.append("%s：参考文献列了但正文未用：%s" % (url, ", ".join(extra)))

    print("页面 %d；段落 %d；引用来源 %d；错误 %d；提示 %d" %
          (pages, paragraphs, len(cited), len(errors), len(warnings)))
    for e in errors:
        print("ERROR " + e)
    for w in warnings:
        print("WARN  " + w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
