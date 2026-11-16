#!/usr/bin/env python3
"""把三份语言构建产物（`_site-zh` / `_site-en` / `_site-es`）合并成一份 `_site`。

配合 `_tools/make_lang_sources.py` 使用：三份切片互不重叠地渲染各自的页面，
这里只做三件事：

1. **并集**：按 zh → en → es 顺序把文件并进 `_site`；同名文件先比对内容，
   完全一致就只留一份，不一致说明切片漏了东西（同一页面被两份切片各渲染了一遍），
   直接判失败并列出差异，避免「两份内容悄悄互相覆盖」。
2. **合并 sitemap.xml**：每份切片只生成本语言那一部分 URL，这里取三份的并集
   （按 `<loc>` 去重、按 URL 排序，输出确定），其余 XML 原样不动。
3. **体检**：每份切片的页面数量级、语言目录归属（zh 里不许出现 `en/`、`es/`），
   合并后总页数是否与预期相符 —— 任何一条不满足都当失败处理，
   而不是把半套站点发上线。

`_posts`、`downloads/` 与 `assets/` 是三份切片共用的源（`blog.md` 用 `site.posts`、
`download.md` 用 `site.static_files`、模板用 `assets/` 下的样式与图标），所以每份产物里
都会出现它们的输出（外加 `robots.txt`）；这些路径按「共享产物」放行，内容不同才算冲突。

用法：python _tools/merge_lang_sites.py [--sites _site-zh _site-en _site-es] [--dest _site]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 切片的产物边界：zh 不许出现 en/ es/；en 只许有 en/；es 只许有 es/。
# 这两条一旦破了，说明切片没把别的语言挡住（白渲染几千页）或整份语言漏构建，
# 而合并这一步是唯一能在发布前发现它的地方。
ZH_FORBIDDEN = ("en/", "es/")
ONLY_PREFIX = {"en": "en/", "es": "es/"}
# jekyll-sitemap 在没有 robots.txt 时会自己生成一份（内容只取决于 site.url），
# 于是三份切片都会各产一份同名文件；内容一致就只留一份，不算切片泄漏。
SHARED_ROOT = {"robots.txt"}

# `_posts` 与 `downloads/` 是三份切片共用的源（见 make_lang_sources.py 的 SHARED），
# 于是每份产物里都会出现它们的输出：`downloads/**` 静态复制、每篇 post 的 permalink。
# 这些路径出现在任何一份切片里都正常，不属于「泄漏」，内容不同才是问题（交给冲突检查）。
SHARED_PREFIXES = ("downloads/", "assets/")
POST_PERMALINK = re.compile(r"^permalink:\s*['\"]?([^'\"\s#]+)", re.M)
POST_FILE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.(?:md|markdown|html)$")


def _is_shared_output(rel: str, shared_posts: frozenset[str]) -> bool:
    """该产物路径是「三份切片都会产出」的共享源输出吗？

    比对用全小写：Windows 上 Jekyll 会把顶层 `downloads/` 输出成 `Downloads/`
    （大小写由文件系统/Host 决定，Linux 上仍是 `downloads/`），两种写法都不该判成泄漏。
    语言目录（`en/`、`es/`）仍按原样严格比对——那里的大小写变了才是真问题。
    """
    low = rel.lower()
    return (
        low in SHARED_ROOT
        or low in shared_posts
        or low.startswith(SHARED_PREFIXES)
    )


def _shared_outputs() -> frozenset[str]:
    """共享源在三份切片里各自产出的路径（`_posts` 的输出路径）。

    `downloads/` 按前缀放行，这里只算 post。permalink 是站内既有写法
    （`_posts/*.md` 都显式写了），没有时按 Jekyll 默认 `/:year/:month/:day/:title.html` 兜底。
    """
    exact: set[str] = set()
    posts_dir = REPO / "_posts"
    if not posts_dir.is_dir():
        return frozenset()
    for path in sorted(posts_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".markdown", ".html"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        front = text.split("---", 2)[1] if text.startswith("---") else ""
        m = POST_PERMALINK.search(front)
        if m:
            url = m.group(1).strip("/")
            exact.add(url if url.endswith(".html") else f"{url}/index.html")
            continue
        fm = POST_FILE.match(path.name)
        if fm:
            year, month, day, slug = fm.groups()[:4]
            exact.add(f"{year}/{month}/{day}/{slug}.html")
    return frozenset(p.lower() for p in exact)

URL_BLOCK = re.compile(r"<url>.*?</url>", re.DOTALL)
LOC = re.compile(r"<loc>(.*?)</loc>", re.DOTALL)
SITEMAP_HEAD = re.compile(r"<urlset[^>]*>", re.DOTALL)


def _walk(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


def _merge_sitemaps(slices: list[tuple[str, Path]], dest: Path) -> tuple[int, str]:
    """取三份 sitemap.xml 的并集，写回 dest。返回 (URL 数, 说明)。"""
    head = None
    seen: dict[str, str] = {}
    sources = 0
    for lang, site in slices:
        path = site / "sitemap.xml"
        if not path.exists():
            continue
        sources += 1
        text = path.read_text(encoding="utf-8")
        if head is None:
            m = SITEMAP_HEAD.search(text)
            head = m.group(0) if m else '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        for block in URL_BLOCK.findall(text):
            m = LOC.search(block)
            if not m:
                continue
            loc = m.group(1).strip()
            seen.setdefault(loc, block.strip())
    if head is None:
        return 0, "三份切片都没有 sitemap.xml（jekyll-sitemap 插件没跑起来？）"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', head]
    for loc in sorted(seen):
        lines.append(seen[loc])
    lines.append("</urlset>")
    (dest / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(seen), f"合并 {sources} 份 sitemap.xml → {len(seen)} 条 URL"


def main() -> int:
    ap = argparse.ArgumentParser(description="合并三语言构建产物")
    ap.add_argument("--sites", nargs="+", default=["_site-zh", "_site-en", "_site-es"],
                    help="三份切片产物目录（顺序即优先级）")
    ap.add_argument("--dest", default="_site", help="合并后的站点目录")
    ap.add_argument("--min-pages", type=int, default=10500,
                    help="合并后 index.html 总数的合格下限（本机小样本调试时可调小）")
    ap.add_argument("--min-urls", type=int, default=10500,
                    help="合并后 sitemap.xml URL 数的合格下限（本机小样本调试时可调小）")
    ap.add_argument("--min-lang-pages", type=int, default=2000,
                    help="每一份切片各自的 index.html 下限（防某一语言整份漏构建；小样本调试时可调小）")
    args = ap.parse_args()

    slices: list[tuple[str, Path]] = []
    for name in args.sites:
        path = REPO / name
        if not path.is_dir():
            print(f"::error::切片产物不存在：{path}", file=sys.stderr)
            return 1
        lang = name.rsplit("-", 1)[-1]
        slices.append((lang, path))

    dest = REPO / args.dest
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    problems: list[str] = []
    conflicts: list[str] = []
    counts: dict[str, int] = {}
    slice_html: dict[str, int] = {}
    written: set[str] = set()
    html_total = 0
    shared_posts = _shared_outputs()

    for lang, site in slices:
        files = _walk(site)
        counts[lang] = len(files)
        html_pages = sum(1 for p in files if p.name == "index.html")
        slice_html[lang] = html_pages
        if html_pages < args.min_lang_pages:
            problems.append(
                f"{lang} 切片只产出 {html_pages} 个 index.html（下限 {args.min_lang_pages}）"
                f"——这一份构建是空的或被截断了"
            )
        for path in files:
            rel = path.relative_to(site).as_posix()
            if rel == "sitemap.xml":
                continue  # 三份都在这里，单独合并
            # 语言目录归属体检：zh 里不该出现 en/ es/；en/es 切片只该有自己的语言目录
            top = rel.split("/", 1)[0] + "/" if "/" in rel else rel
            shared_output = _is_shared_output(rel, shared_posts)
            if not shared_output:
                if lang == "zh":
                    if top in ZH_FORBIDDEN:
                        problems.append(f"zh 切片产物里出现了 {top} 路径（{rel}），切片漏了东西")
                elif top != ONLY_PREFIX[lang]:
                    problems.append(
                        f"{lang} 切片产物里出现了不属于它的路径（{rel}），切片漏了东西"
                        f"——本语言目录之外，只有 `assets/`、`downloads/`、`_posts` 的 permalink 页"
                        f"和 `robots.txt` 是常见共享产物；新增的共享目录要同时写进"
                        f"`make_lang_sources.py` 的 SHARED 与这里的 SHARED_PREFIXES"
                    )
            target = dest / rel
            if rel in written:
                try:
                    same = target.read_bytes() == path.read_bytes()
                except OSError:
                    same = False
                if not same:
                    conflicts.append(f"{rel}（来自 {lang}，与已有版本内容不同）")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            written.add(rel)
            if rel.endswith("index.html"):
                html_total += 1

    n_urls, note = _merge_sitemaps(slices, dest)
    print(f"  {note}")
    for lang, _ in slices:
        print(f"  {lang}: {counts.get(lang, 0)} 个文件，其中 {slice_html.get(lang, 0)} 个 index.html")
    print(f"  合并结果：{len(written)} 个文件（其中 {html_total} 个 index.html）")

    if html_total < args.min_pages:
        problems.append(
            f"合并后只有 {html_total} 个 index.html（下限 {args.min_pages}，预期 11,300 上下）——有语言整份缺失？"
        )
    if n_urls < args.min_urls:
        problems.append(f"sitemap.xml 只有 {n_urls} 条 URL（下限 {args.min_urls}，预期 11,300 上下）")
    if conflicts:
        problems.append(
            f"{len(conflicts)} 个文件被两份切片重复渲染且内容不同（切片该排除没排除，"
            f"或模板依赖了本语言切片里不存在的页面/数据）；前几条：" + "；".join(conflicts[:5])
        )

    if problems:
        for p in problems:
            print(f"::error::{p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
