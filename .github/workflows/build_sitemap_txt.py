#!/usr/bin/env python3
"""生成 sitemap.txt：纯文本格式的站点地图（每行一个绝对 URL，无注释、无 XML 标签）。

Google / Bing 支持的 sitemap.txt 格式就是「每行一个 URL」的 UTF-8 纯文本：
  https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

站点本身已有 jekyll-sitemap 插件在构建时生成的 sitemap.xml；本脚本生成的
sitemap.txt 是同一批页面（页面 + 文章 + 物种页）的纯文本版本，放在仓库根目录，
构建时由 Jekyll 作为静态文件复制到 _site/sitemap.txt。

用法：
  python .github/workflows/build_sitemap_txt.py          # 生成/更新 sitemap.txt
  python .github/workflows/build_sitemap_txt.py --check  # 只校验是否与仓库内文件一致
  python .github/workflows/build_sitemap_txt.py --out <路径>

收录范围（与 sitemap.xml 一致，均为 Jekyll 实际渲染出的 HTML 页面）：
  1. 根目录与子目录中带 front matter 的 Markdown 页面（permalink，缺省按 Jekyll 规则推导）
  2. _posts 下的文章（permalink，缺省用 _config.yml defaults 里的 /blog/:year/:month/:day/:slug/）
  3. _species 集合的全部物种页（permalink /species/:name/）
不收录静态资源（assets/、data/、downloads/、search-index.json 等），与 jekyll-sitemap 行为一致。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "_config.yml"
DEFAULT_OUT = ROOT / "sitemap.txt"

# 中文核心页面在前，英文页随后；其余页面按路径排序追加
CORE_ORDER = ["/", "/list/", "/stats/", "/data/", "/download/", "/blog/", "/guestbook/"]

# 这些目录里不会有「页面」（下划线前缀由 Jekyll 自身排除，其余为静态资源/数据目录）
SKIP_DIRS = {".git", ".github", "_site", "assets", "data", "downloads", "_inbox", "_tmp", "_tools"}


def read_site_urls() -> tuple[str, str]:
    """从 _config.yml 读取 url 与 baseurl（不依赖 PyYAML，CI 无需额外安装）。"""
    text = CONFIG.read_text(encoding="utf-8")

    def grab(key: str) -> str:
        m = re.search(rf"^\s*{key}:\s*(.+?)\s*$", text, re.MULTILINE)
        if not m:
            sys.exit(f"error: 无法从 {CONFIG.name} 读取 {key}")
        return m.group(1).strip().strip("'\"")

    return grab("url").rstrip("/"), grab("baseurl").rstrip("/")


def front_matter(path: Path) -> str | None:
    """返回 front matter 文本；没有 front matter 的文件不是 Jekyll 页面（返回 None）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    text = text.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return None


def get_permalink(path: Path) -> str | None:
    fm = front_matter(path)
    if fm is None:
        return None
    m = re.search(r"^permalink:\s*(.+?)\s*$", fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip("'\"")


def page_url(path: Path) -> str:
    """页面 URL：优先 front matter 的 permalink，否则按 Jekyll 页面规则推导。"""
    permalink = get_permalink(path)
    if permalink:
        return permalink if permalink.startswith("/") else "/" + permalink
    rel = path.relative_to(ROOT).as_posix()
    if rel.endswith("/index.md"):
        return "/" + rel[: -len("index.md")]
    return "/" + rel[: -len(".md")] + ".html"


def discover_pages() -> list[str]:
    urls = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") or part.startswith("_") for part in rel.parts[:-1]):
            continue
        if rel.parts[0] in SKIP_DIRS:
            continue
        if path.name.startswith("_") or front_matter(path) is None:
            continue
        urls.append(page_url(path))
    return urls


def discover_posts() -> list[str]:
    posts = ROOT / "_posts"
    if not posts.is_dir():
        return []
    found = []
    for path in sorted(posts.glob("*.md")):
        permalink = get_permalink(path)
        if permalink:
            found.append(permalink if permalink.startswith("/") else "/" + permalink)
            continue
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", path.stem)
        if not m:
            sys.exit(f"error: 文章文件名不符合 Jekyll 约定，无法推导 URL: {path.name}")
        year, month, day, slug = m.groups()
        found.append(f"/blog/{year}/{month}/{day}/{slug}/")
    return found


def discover_species() -> list[str]:
    species = ROOT / "_species"
    if not species.is_dir():
        return []
    urls = []
    for path in species.glob("*.md"):
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        urls.append(f"/species/{name}/")
    return urls


def build_sitemap() -> list[str]:
    site_url, baseurl = read_site_urls()
    root = site_url + baseurl  # 与 _config.yml 的 base_url 一致（无尾斜杠）

    pages = discover_pages()
    page_set = set(pages)
    ordered: list[str] = []
    for core in CORE_ORDER:
        if core in page_set:
            ordered.append(core)
            page_set.discard(core)
    ordered += sorted(page_set)
    # 英文页与中文页同构，紧跟中文页之后；其余页面已在上面按路径排序

    en_pages = [u for u in ordered if u.startswith("/en/")]
    zh_pages = [u for u in ordered if u not in en_pages]

    paths = zh_pages + en_pages
    posts = discover_posts()
    species = sorted(discover_species(), key=str.casefold)
    paths += posts + species

    urls = [root + p for p in paths]

    # 防御性校验：格式、重复、前缀
    seen: set[str] = set()
    for url in urls:
        if not url.startswith(root + "/") or any(ch.isspace() for ch in url):
            sys.exit(f"error: 生成的 URL 非法: {url!r}")
        if url in seen:
            sys.exit(f"error: 生成的 URL 重复: {url!r}")
        seen.add(url)
    return urls


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 sitemap.txt（纯文本站点地图）")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"输出路径（默认 {DEFAULT_OUT.name}）")
    parser.add_argument("--check", action="store_true", help="只校验仓库内文件是否与生成结果一致")
    args = parser.parse_args()

    urls = build_sitemap()
    content = "\n".join(urls) + "\n"
    out = args.out if args.out.is_absolute() else ROOT / args.out

    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current != content:
            print(f"error: {out.name} 已过期，请重新运行本脚本", file=sys.stderr)
            return 1
        print(f"ok: {out.name} 与生成结果一致（{len(urls)} 个 URL）")
        return 0

    out.write_text(content, encoding="utf-8", newline="\n")
    print(f"已写入 {out.relative_to(ROOT).as_posix()}：{len(urls)} 个 URL（页面 {len(discover_pages())}，文章 {len(discover_posts())}，物种页 {len(discover_species())}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
