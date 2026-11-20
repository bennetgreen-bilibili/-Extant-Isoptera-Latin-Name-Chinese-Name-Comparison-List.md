#!/usr/bin/env python3
"""维护仓库根目录的 SITE-INDEX.md：刷新现状快照，并校验「新增的东西有没有登记」。

为什么需要这个脚本
------------------
SITE-INDEX.md 是给下一次改站的 AI 看的入口索引：先读一页，再按表只打开需要的
那几个文件，不必通读 3,000+ 个页面。为了不让入口页本身变成要通读的长文，
细节拆在 `_meta/` 里（`DATA-MAP.md` 数据层、`PIPELINE.md` 生成链与校验、
`DOCS.md` 文档索引），只在需要时打开。

索引一旦和仓库脱节（新增了 `_data/xxx.json` 或 `_data/<数据集>/` 分片目录、
新增了生成脚本、新增了一篇说明文档却没写进去），它就比没有更糟——读者会以为
「表里没有的就是不重要」。

所以这里做两件事：

1. `--write` 重新计算 SITE-INDEX.md 的现状快照（`<!-- AUTO:INDEX:BEGIN -->` 与
   `<!-- AUTO:INDEX:END -->` 之间），内容只有计数，确定性输出，不含时间戳，
   连跑两次结果不变——regen_all.sh 末尾调用它不会制造 diff 噪音。
2. `--check` 逐项核对登记完整性。登记语料 = `SITE-INDEX.md` + `_meta/*.md`：
   - `_data/` 下每个顶层文件、每个 `_data/<数据集>/` 分片目录都要在语料里出现；
   - 每个 `build_*.py`（`_tools/` 与 `.github/workflows/`）都要出现；
   - 每篇 `_tools/*.md`、`_reports/**/*.md` 都要出现；
   - 快照的计数必须与当前仓库一致（含分片目录与分片数）。

用法：
    python _tools/build_ai_index.py --write    # 刷新快照（regen_all.sh 末尾）
    python _tools/build_ai_index.py --check    # 只校验（CI 用），不合规则 exit 1

退出码：0 = 通过；1 = 有缺登记或快照过期；2 = 索引文件本身缺失 / 锚点损坏。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "SITE-INDEX.md"
DETAIL_DIR = ROOT / "_meta"
BEGIN = "<!-- AUTO:INDEX:BEGIN -->"
END = "<!-- AUTO:INDEX:END -->"

# 目录相对路径 -> 每页文件的子目录（用于统计生成页数量）
PAGE_DIRS = {
    "科页": "family",
    "亚科页": "subfamily",
    "属页": "genus",
}


def read_index() -> str:
    if not INDEX.exists():
        raise SystemExit(f"[build_ai_index] 找不到 {INDEX.name}")
    text = INDEX.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        raise SystemExit(f"[build_ai_index] {INDEX.name} 缺少自动区块锚点")
    return text


def corpus_text(index_text: str | None = None) -> str:
    """登记语料：SITE-INDEX.md（入口页）+ `_meta/*.md`（按需打开的细节页）。

    登记检查看的是「有没有写到某一页」，不关心写在哪一页——细节下沉到 `_meta/`
    以后，入口页可以被裁剪而不触发缺登记。
    """
    parts = [read_index() if index_text is None else index_text]
    if DETAIL_DIR.is_dir():
        parts += [p.read_text(encoding="utf-8") for p in sorted(DETAIL_DIR.glob("*.md"))]
    return "\n".join(parts)


def count_pages() -> dict[str, int]:
    out: dict[str, int] = {}
    for label, rel in PAGE_DIRS.items():
        out[label] = len(list((ROOT / rel).glob("*.md")))
    return out


def count_species() -> tuple[int, int]:
    species = subspecies = 0
    for path in (ROOT / "_species").glob("*.md"):
        head = path.read_text(encoding="utf-8", errors="replace")[:4000]
        m = re.search(r"^rank:\s*(\S+)", head, re.M)
        rank = m.group(1) if m else ""
        if rank == "subspecies":
            subspecies += 1
        else:
            species += 1
    return species, subspecies


def taxonomy_counts() -> dict[str, int]:
    data = json.loads((ROOT / "_data" / "taxonomy.json").read_text(encoding="utf-8"))
    return {
        "支系": len(data.get("clades", [])),
        "科": len(data.get("families", [])),
        "亚科": len(data.get("subfamilies", [])),
        "属": len(data.get("genera", [])),
    }


def docs() -> tuple[list[str], list[str]]:
    tools_md = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "_tools").glob("*.md"))
    reports_md = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "_reports").rglob("*.md"))
    return tools_md, reports_md


def scripts() -> list[str]:
    found = list((ROOT / "_tools").glob("build_*.py"))
    found += list((ROOT / ".github" / "workflows").glob("build_*.py"))
    return sorted(p.name for p in found)


def data_files() -> list[str]:
    return sorted(p.name for p in (ROOT / "_data").iterdir() if p.is_file())


def data_dirs() -> list[str]:
    """`_data/<数据集>/` 分片目录（一阶元一档，聚合文件已删除）。"""
    return sorted(p.name for p in (ROOT / "_data").iterdir() if p.is_dir())


def shard_counts() -> tuple[int, int]:
    """返回 (分片目录数, 分片文件总数)；只数 *.json，不解析内容。"""
    dirs = data_dirs()
    total = sum(1 for d in dirs for _ in (ROOT / "_data" / d).rglob("*.json"))
    return len(dirs), total


def snapshot() -> str:
    tax = taxonomy_counts()
    species, subspecies = count_species()
    pages = count_pages()
    tools_md, reports_md = docs()
    n_dirs, n_shards = shard_counts()
    rows = [
        ("支系 / 科 / 亚科 / 属", f"{tax['支系']} / {tax['科']} / {tax['亚科']} / {tax['属']}"),
        ("种 / 亚种 / 记录合计", f"{species} / {subspecies} / {species + subspecies}"),
        ("物种页 `_species/*.md`", str(species + subspecies)),
        ("科页 / 亚科页 / 属页（中文）",
         f"{pages['科页']} / {pages['亚科页']} / {pages['属页']}"),
        ("`_data/` 顶层文件", str(len(data_files()))),
        ("`_data/` 分片目录（数据集 / 分片文件）", f"{n_dirs} / {n_shards}"),
        ("`build_*.py` 脚本（`_tools/` + `.github/workflows/`）", str(len(scripts()))),
        ("说明文档（`_tools/*.md` / `_reports/**/*.md`）", f"{len(tools_md)} / {len(reports_md)}"),
    ]
    lines = ["| 项目 | 数量 |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in rows]
    lines.append("")
    lines.append("> 数字由 `_tools/build_ai_index.py --write` 从 `_data/taxonomy.json`、"
                 "`_species/`、各页面目录与文件系统直接统计，改完数据请重跑 `_tools/regen_all.sh`。")
    return "\n".join(lines)


def apply_snapshot(text: str, body: str) -> str:
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n{body}\n{END}{tail}"


def check() -> int:
    index_text = read_index()
    text = corpus_text(index_text)
    problems: list[str] = []

    missing_data = [f for f in data_files() if f not in text]
    if missing_data:
        problems.append("`_data/` 下这些文件没在索引里出现：" + "、".join(missing_data))

    missing_dirs = [d for d in data_dirs() if d + "/" not in text]
    if missing_dirs:
        problems.append("`_data/` 下这些分片目录没在索引里出现：" + "、".join(missing_dirs))

    missing_scripts = [s for s in scripts() if s not in text]
    if missing_scripts:
        problems.append("这些生成脚本没在索引里出现：" + "、".join(missing_scripts))

    tools_md, reports_md = docs()
    missing_docs = [d for d in tools_md + reports_md if d.split("/")[-1] not in text]
    if missing_docs:
        problems.append("这些文档没在索引里出现：" + "、".join(missing_docs))

    current = index_text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    fresh = snapshot().strip()
    if current != fresh:
        problems.append("现状快照已过期：跑 `python _tools/build_ai_index.py --write`")

    if problems:
        for p in problems:
            print(f"[build_ai_index] {p}")
        print("[build_ai_index] 索引与仓库不一致")
        return 1
    print("[build_ai_index] 索引登记完整、快照最新")
    return 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    if "--write" in argv:
        text = read_index()
        new = apply_snapshot(text, snapshot())
        if new != text:
            INDEX.write_text(new, encoding="utf-8")
            print("[build_ai_index] 已刷新现状快照")
        else:
            print("[build_ai_index] 快照已是最新，未改动")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
