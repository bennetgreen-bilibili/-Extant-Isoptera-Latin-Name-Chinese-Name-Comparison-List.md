#!/usr/bin/env python3
"""发布面守卫：不该被发布的东西，不该出现在站点上。

背景：Jekyll 只跳过 `_` 与 `.` 开头的文件，站点根目录下的任何东西——构建日志、
抓取脚本误落的产物、未发表的书稿 docx、出版社 PDF——都会被原样复制进 `_site`，
部署后就是公开可下载的 URL。2026-11 这次就漏过：8 个未发表书稿 docx、4.3MB 的
出版社 PDF、构建日志、`undefined/` 目录。`_config.yml` 的 `exclude` 是防线一，
本脚本是防线二，两种用法：

    # 构建后检查产物（pages.yml，在 Jekyll 之后、上传之前）
    python _tools/check_publish_surface.py            # 默认检查 ./_site
    python _tools/check_publish_surface.py path/to/_site

    # 不构建也能查：只看 git 跟踪 + 会被 Jekyll 发布的路径（validate.yml / 本地）
    python _tools/check_publish_surface.py --tracked

`--tracked` 的判定与 Jekyll 一致：第一段路径以 `_` 或 `.` 开头的不发布，
`_config.yml` 里 `exclude` 列出的不发布，其余都会被复制进站点。
_site 不存在时直接通过（本地只跑 check_site.py 很常见），退出码 0。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 任何位置都不该被发布的类型（数据集归档 zip 是刻意的，单独放行 downloads/）
FORBIDDEN_SUFFIXES = {
    ".pdf", ".log", ".doc", ".docx", ".docm", ".xls", ".xlsx",
    ".ppt", ".pptx", ".univer", ".py", ".pyc", ".sqlite", ".db",
}

# 允许出现 zip / pdf 的位置
ALLOWED_DIRS = ("downloads/",)

# 整个目录都不该出现在站点上
FORBIDDEN_DIRS = ("undefined/", "未发布内容/", "_unpublished/", "_tmp/", ".tmp/")


def site_excludes() -> set[str]:
    """读 _config.yml 里 exclude 列出的路径（列表形式的简单 YAML，不必上 YAML 解析器）。"""
    text = (ROOT / "_config.yml").read_text(encoding="utf-8")
    names: set[str] = set()
    in_block = False
    for line in text.splitlines():
        if re.match(r"^exclude:\s*$", line):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^\s+-\s+(.*)$", line)
            if not m:
                break
            value = m.group(1).split("  #")[0].strip().strip('"').strip("'")
            if value:
                names.add(value)
    return names


def problems_for(entries: list[tuple[str, int | None]], label: str) -> list[str]:
    problems: list[str] = []
    for rel_path, size in entries:
        if any(rel_path.startswith(d) for d in FORBIDDEN_DIRS):
            problems.append(f"不该发布的目录里的文件：{rel_path}")
            continue
        if rel_path.startswith(ALLOWED_DIRS):
            continue
        suffix = Path(rel_path).suffix.lower()
        if suffix in FORBIDDEN_SUFFIXES:
            extra = f"（{size:,} 字节）" if size is not None else ""
            problems.append(f"不该发布的 {suffix} 文件：{rel_path}{extra}")
    return problems


def check_site(site: Path) -> int:
    if not site.is_dir():
        print(f"SKIP: {site.name}/ 不存在（未构建），跳过发布面检查")
        return 0
    entries = [(p.relative_to(site).as_posix(), p.stat().st_size)
               for p in sorted(site.rglob("*")) if p.is_file()]
    problems = problems_for(entries, "_site")
    if problems:
        print(f"FAIL: {site.name}/ 里有 {len(problems)} 个不该发布的东西：")
        for line in problems:
            print(f"  - {line}")
        print("修法：从仓库删掉，或在 _config.yml 的 exclude 里加路径，然后重新构建。")
        return 1
    print(f"OK: {site.name}/ 发布面无遗留文件（{len(entries)} 个文件）")
    return 0


def check_tracked() -> int:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode("utf-8")
    tracked = [p for p in out.split("\0") if p]
    excludes = site_excludes()

    def would_publish(path: str) -> bool:
        first = path.split("/")[0]
        if first.startswith("_") or first.startswith("."):
            return False
        for name in excludes:
            if path == name or path.startswith(name.rstrip("/") + "/"):
                return False
        return True

    entries = [(p, None) for p in tracked if would_publish(p)]
    problems = problems_for(entries, "git")
    if problems:
        print(f"FAIL: 这些被 git 跟踪的文件会被 Jekyll 发布进 _site：")
        for line in problems:
            print(f"  - {line}")
        print("修法：git rm 掉，或在 _config.yml 的 exclude 里加路径（只是不发布，文件仍留本地）。")
        return 1
    print(f"OK: 被跟踪的 {len(tracked)} 个文件里，{len(entries)} 个会进站点，无遗留文件")
    return 0


def main(argv: list[str]) -> int:
    if "--tracked" in argv:
        return check_tracked()
    rest = [a for a in argv[1:] if not a.startswith("--")]
    site = Path(rest[0]) if rest else ROOT / "_site"
    if not site.is_absolute():
        site = ROOT / site
    return check_site(site)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
