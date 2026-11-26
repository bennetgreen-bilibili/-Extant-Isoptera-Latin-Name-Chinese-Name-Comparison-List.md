#!/usr/bin/env python3
"""生成 sitemap-core.xml：分类核心页（13 个科 + 18 个亚科 + 326 个属，三语）的小型 sitemap。

用途：站点有 11,000+ 个 URL，整份 sitemap.xml 一次性提交给 Search Console 时，
新域名拿不到那么多抓取配额。这里单独产一份只含分类层级页的核心 sitemap，
先提交它、等这批页稳定收录后再提交整份 sitemap.xml。

故意不写 <priority> / <changefreq>：Google 已明确忽略这两个字段，写了只会让人误以为
「调高 priority 就会优先抓取」。真正决定先抓哪些页的是站内链接与页面本身的质量信号。

用法：
  python .github/workflows/build_sitemap_core.py          # 生成/更新 sitemap-core.xml
  python .github/workflows/build_sitemap_core.py --check   # 只校验与仓库内文件一致
  python .github/workflows/build_sitemap_core.py --out <路径>

收录范围：三种语言的首页、/list/ 名录索引，以及 /family/ /subfamily/ /genus/ 三种聚合页
（每页的 permalink 从 front matter 读，语言前缀以 permalink 为准）。
不收录物种页——那是第二阶段。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "_config.yml"
DEFAULT_OUT = ROOT / "sitemap-core.xml"

# 分类聚合页的源文件目录（相对仓库根）；en/ es/ 对应三份语言切片里的同名目录
TAXONOMY_DIRS = ("family", "subfamily", "genus")
LANG_DIRS = ("", "en/", "es/")

# 三语首页与名录索引：这些页面不用遍历 front matter，路径固定
HUB_URLS = ("/", "/en/", "/es/", "/list/", "/en/list/", "/es/list/")

LOC_RE = re.compile(r"^\s*loc:\s*(.+?)\s*$", re.MULTILINE)


def read_site_url() -> str:
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"^url:\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        sys.exit(f"error: 无法从 {CONFIG.name} 读取 url")
    return m.group(1).strip().strip("'\"")


def read_global_lastmod() -> str:
    """_config.yml defaults 里全站统一的 last_modified_at（没有就退回今天不写 lastmod）。"""
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"last_modified_at:\s*(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else ""


def front_matter(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return ""


def permalink_of(path: Path) -> str | None:
    m = re.search(r"^permalink:\s*(.+?)\s*$", front_matter(path), re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip("'\"")


def lastmod_of(path: Path, fallback: str) -> str:
    m = re.search(r"^last_modified_at:\s*(\d{4}-\d{2}-\d{2})", front_matter(path), re.MULTILINE)
    return m.group(1) if m else fallback


def discover_taxonomy() -> list[tuple[str, str]]:
    """返回 [(permalink, lastmod)]：按 zh → en → es、科 → 亚科 → 属的顺序，URL 内再字典序。"""
    fallback = read_global_lastmod()
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for prefix in LANG_DIRS:
        for kind in TAXONOMY_DIRS:
            directory = ROOT / prefix / kind
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob("*.md")):
                url = permalink_of(path)
                if not url:
                    sys.exit(f"error: {path.relative_to(ROOT).as_posix()} 缺少 permalink，无法确定核心页 URL")
                if not url.startswith("/"):
                    url = "/" + url
                if url in seen:
                    sys.exit(f"error: 核心页 URL 重复: {url!r}")
                seen.add(url)
                found.append((url, lastmod_of(path, fallback)))
    return found


def build_urls() -> list[tuple[str, str]]:
    fallback = read_global_lastmod()
    entries = [(url, fallback) for url in HUB_URLS] + discover_taxonomy()
    site_url = read_site_url().rstrip("/")
    out: list[tuple[str, str]] = []
    for url, lastmod in entries:
        full = site_url + url
        if any(ch.isspace() for ch in full):
            sys.exit(f"error: 生成的 URL 非法: {full!r}")
        out.append((full, lastmod))
    return out


def render(entries: list[tuple[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, lastmod in entries:
        if lastmod:
            lines.append(f"  <url>\n    <loc>{escape(url)}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </url>")
        else:
            lines.append(f"  <url>\n    <loc>{escape(url)}</loc>\n  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 sitemap-core.xml（分类核心页优先 sitemap）")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"输出路径（默认 {DEFAULT_OUT.name}）")
    parser.add_argument("--check", action="store_true", help="只校验仓库内文件是否与生成结果一致")
    args = parser.parse_args()

    entries = build_urls()
    content = render(entries)
    out = args.out if args.out.is_absolute() else ROOT / args.out

    # 防御性校验：至少覆盖科 + 属三语（(13+18+326)×3 = 1071，加 6 个枢纽页）
    if len(entries) < 1000:
        sys.exit(f"error: 核心页只有 {len(entries)} 条，明显少于预期（分类聚合页没生成全？）")
    locs = LOC_RE.findall(content)
    if len(set(locs)) != len(locs):
        sys.exit("error: 生成的 <loc> 有重复")

    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current != content:
            print(f"error: {out.name} 已过期，请重新运行本脚本", file=sys.stderr)
            return 1
        print(f"ok: {out.name} 与生成结果一致（{len(entries)} 个 URL）")
        return 0

    out.write_text(content, encoding="utf-8", newline="\n")
    print(f"已写入 {out.relative_to(ROOT).as_posix()}：{len(entries)} 个核心页 URL（三语 首页 + 名录索引 + 科/亚科/属聚合页）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
