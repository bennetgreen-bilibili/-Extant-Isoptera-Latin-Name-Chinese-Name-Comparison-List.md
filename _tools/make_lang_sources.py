#!/usr/bin/env python3
"""把仓库切成三份「语言切片」（`_langsrc/zh`、`_langsrc/en`、`_langsrc/es`）。

## 为什么要有这一步

Jekyll 是单线程渲染，本站一次要出 **11,301 页**（3,089 物种 × 中/英/西三语），
CI 里 `Build with Jekyll` 一步实测 1165s（19.4 分钟），占整个部署时长的 90%+。
页数就是乘数，靠改模板只能省几个百分点，真正有效的是把三语摊到三个进程上并行。

## 为什么是镜像（硬链接）而不是复制三份真文件

切片里**只放硬链接**：页面、`_layouts`、`_includes`、`_data` 仍然只有仓库里那一份真文件，
三份切片指向同一份数据（改一处即三处生效，不会出现会各自漂移的副本）。硬链接在同一文件系统内
只是目录项，不占额外空间，13,000 个链接在 CI 上不到一秒。

不用符号链接是因为这站点是在 **Docker 容器**里构建的：容器只挂载仓库根目录到 `/src`，
切片里的绝对链接会指到容器里的不存在路径；相对链接又取决于 Jekyll 是否愿意穿过链接目录
（`safe` 模式下不穿）。硬链接在容器内外都是普通文件，行为与真文件完全一致。

局部裁剪过的样站（只有几百页）同样跑得动，`--check` 的下限可用 `--min-zh/--min-lang` 调低。

## 切片内容

* `zh`：`_config.yml`、共享模板/数据目录、`_posts`、`_species` 与根目录下所有
  非 `_`/`.` 开头的条目（`photos/`、`genus/`、`family/`、`subfamily/`、
  `basics/`、`data/`、`dataset/`、根页面与根静态文件）——即**除 `en/`、`es/` 之外的一切**。
* `en`：`_config.yml`、共享模板/数据目录、`en/`。
* `es`：`_config.yml`、共享模板/数据目录、`es/`。

`en`/`es` 切片刻意不带 `dataset/` 与根页面：那些是 zh 切片出的，合并时由
`_tools/merge_lang_sites.py` 统一并进去，三份输出因此**基本互不重叠**；
重叠的部分都来自共享条目，合并脚本按「共享产物」处理：

1. 各自生成的 `sitemap.xml`（取并集）；
2. `_posts` 的渲染结果（`blog.md` 用 `site.posts` 列文章，三份切片都要有 `_posts` 才能列出文章）；
3. `downloads/` 的静态复制（`download.md` 用 `site.static_files` 列下载文件，同理）；
4. `assets/` 的静态复制与 `robots.txt`（三份都带，保证三份产物形状一致）。

同路径内容一致就只留一份；内容不一致说明切片泄漏，合并直接判失败。

`_config.yml` 的 `exclude` 列表对切片同样生效（`未发布内容/`、`nul` 等仍被挡掉），
所以这里不需要重复一份排除表 —— 切片靠「不在切片里」来排除，不靠改配置。

## 用法

    python _tools/make_lang_sources.py            # 生成/刷新 _langsrc/
    python _tools/make_lang_sources.py --check    # 只体检：切片存在、互不重叠、覆盖完整
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_langsrc"

# 三种语言切片共用：站点配置 + 模板/数据/样式/插件目录 + 两处「页面会全站枚举」的东西。
# `_posts` 与 `downloads/` 必须三份都带：`blog.md`/`en/blog.md`/`es/blog.md` 用 `site.posts`、
# `download.md`/`en/download.md`/`es/download.md` 用 `site.static_files | where contains '/downloads/'`，
# 少了哪一份，这几页就会在本语言的切片里被渲染成空列表。三份各渲染一遍的结果相同，
# 合并阶段按字节比对后只留一份（`_posts` 只有两篇、`downloads/` 约 2MB，代价可以忽略）。
SHARED = (
    "_config.yml", "_layouts", "_includes", "_data", "_sass", "_plugins",
    "_posts", "downloads",
    # `assets/` 是纯静态资源（没有 front matter，不会被渲染）：三份切片都带，
    # 各容器各自原样复制一遍，合并时按字节去重。看起来多复制了两次 15MB，
    # 但换来「三份产物形状一致」——某份切片缺了它，发布面上就会少掉样式/图标/geo 数据，
    # 而且 Pages 镜像里的 github-pages 工具链有时会自己补一个 assets/css/style.css，
    # 补齐后三份内容一致，合并脚本不必为这种差异开特例。
    "assets",
    # `robots.txt` 仓库里有一份真文件；只给 zh 的话，en/es 切片会被 jekyll-sitemap
    # 自动生成一份内容不同的 robots.txt（追加了 Sitemap 行），合并时就撞「重复渲染」。
    "robots.txt",
)

# 每种语言切片额外挂的目录（zh 另外还要挂根目录下所有非 _/. 开头的条目，见 main()）
LANG_DIRS = {"zh": (), "en": ("en",), "es": ("es",)}

# 只有中文切片需要的集合/根目录（en/es 页面不引用它们：模板里 site.species 出现 0 次）
ZH_ONLY = ("_species",)

# 三份切片共用的顶层条目：比对「有没有互相重叠」时要跳过它们（共用不等于重叠）
_SHARED_TOP = set(SHARED)


def _hardlink_or_copy(src: str, dst: str) -> str:
    """`shutil.copytree` 的 copy_function：优先硬链接，跨卷/无权限时退回复制。"""
    try:
        os.link(src, dst)
        return dst
    except OSError:
        return shutil.copy2(src, dst)


def _mirror(src: Path, dst: Path) -> str:
    """把 src 镜像到 dst：目录建真目录，文件用硬链接（失败则复制）。"""
    if dst.is_symlink() or dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst, copy_function=_hardlink_or_copy)
        return "dir"
    _hardlink_or_copy(str(src), str(dst))
    return "file"


def _config_excludes() -> set[str]:
    """读 `_config.yml` 的 exclude 列表（站里被排除的根条目不必链进切片）。

    只认 `exclude:` 下面那串 `  - "名字"` 的简单列表——本站的 exclude 一直是这个形状，
    写成多行流式或锚点时会读不到，但那种情况极少数见，宁可少链几个也不会链错。
    """
    text = (REPO / "_config.yml").read_text(encoding="utf-8")
    names: set[str] = set()
    in_block = False
    for line in text.splitlines():
        if line.startswith("exclude:"):
            in_block = True
            continue
        if in_block:
            if line.startswith(("  - ", "- ")):
                value = line.split("- ", 1)[1].split("#", 1)[0].strip().strip('"').strip("'")
                if value:
                    names.add(value)
            elif line.strip() and not line.startswith((" ", "\t")):
                in_block = False
    return names


def _root_entries_for_zh() -> list[str]:
    """根目录里归中文切片的东西：所有非 `_`/`.` 开头的条目（文件与目录都算）。"""
    excluded = _config_excludes()
    names = []
    for entry in sorted(os.listdir(REPO)):
        if entry.startswith(("_", ".")):
            continue
        if entry in ("en", "es"):
            continue
        if entry in excluded:  # _config.yml 已排除的发布面卫生条目，无需链入
            continue
        if entry in SHARED:  # 共用条目已经单独链过，不要重复
            continue
        names.append(entry)
    return names


def build() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    total = 0
    for lang in ("zh", "en", "es"):
        slice_dir = OUT / lang
        slice_dir.mkdir(parents=True, exist_ok=True)
        wanted = list(SHARED) + list(LANG_DIRS[lang])
        if lang == "zh":
            wanted += list(ZH_ONLY) + _root_entries_for_zh()
        missing = []
        for name in wanted:
            src = REPO / name
            if not src.exists():
                missing.append(name)  # _sass/_plugins 之类本仓库没有的目录，跳过即可
                continue
            _mirror(src, slice_dir / name)
            total += 1
        print(f"  {lang:2s}: {len(wanted) - len(missing):3d} 个条目"
              f"{'（缺: ' + ', '.join(missing) + '）' if missing else ''}")
    print(f"切片完成：{OUT}（{total} 个条目）")
    return 0


def check(min_zh: int = 1000, min_lang: int = 3000) -> int:
    problems: list[str] = []
    if not OUT.exists():
        print(f"::error::切片目录不存在：{OUT}（先运行 python _tools/make_lang_sources.py）", file=sys.stderr)
        return 1

    pages: dict[str, set[str]] = {}
    for lang in ("zh", "en", "es"):
        slice_dir = OUT / lang
        if not slice_dir.is_dir():
            problems.append(f"缺切片目录 {slice_dir}")
            continue
        if not (slice_dir / "_config.yml").exists():
            problems.append(f"{lang} 切片缺 _config.yml")
        if not (slice_dir / "_layouts").exists():
            problems.append(f"{lang} 切片缺 _layouts")
        if not (slice_dir / "_includes").exists():
            problems.append(f"{lang} 切片缺 _includes")
        if not (slice_dir / "_data").exists():
            problems.append(f"{lang} 切片缺 _data")
        found = set()
        for path in slice_dir.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(slice_dir).as_posix()
            top = rel.split("/", 1)[0]
            if top in _SHARED_TOP:  # 三份切片共用的配置/模板/数据/帖子/下载区，不算页面重叠
                continue
            found.add(rel)
        pages[lang] = found

    # 互不重叠：同一个页面不能出现在两份切片里（否则合并时会被判成冲突）
    for a, b in (("zh", "en"), ("zh", "es"), ("en", "es")):
        if a in pages and b in pages:
            overlap = pages[a] & pages[b]
            if overlap:
                sample = ", ".join(sorted(overlap)[:5])
                problems.append(f"{a} 与 {b} 切片有 {len(overlap)} 个重叠文件，例如 {sample}")

    # 语言目录归属：zh 不许有 en/ es/；en/es 切片不许有自己的语言目录之外的东西
    if "zh" in pages:
        leaked = sorted(p for p in pages["zh"] if p.startswith(("en/", "es/")))
        if leaked:
            problems.append(f"zh 切片混进了 {len(leaked)} 个 en/es 页面，例如 {leaked[0]}")
    for lang in ("en", "es"):
        if lang not in pages:
            continue
        foreign = sorted(p for p in pages[lang] if not p.startswith(lang + "/"))
        if foreign:
            problems.append(f"{lang} 切片混进了 {len(foreign)} 个非 {lang}/ 文件，例如 {foreign[0]}")
        other = "es" if lang == "en" else "en"
        leaked = sorted(p for p in pages[lang] if p.startswith(other + "/"))
        if leaked:
            problems.append(f"{lang} 切片混进了 {len(leaked)} 个 {other} 页面，例如 {leaked[0]}")

    # 中文切片的量级体检：物种页与根页面都在，且没有把 en/es 目录整个漏掉
    if "zh" in pages:
        n_species = sum(1 for p in pages["zh"] if p.startswith("_species/") and p.endswith(".md"))
        if n_species < min_zh:
            problems.append(f"zh 切片只有 {n_species} 个 _species 页面，明显不对（应在 {min_zh} 以上）")
        if not any(p == "index.md" for p in pages["zh"]):
            problems.append("zh 切片缺根页面 index.md")
    for lang in ("en", "es"):
        if lang in pages:
            n = sum(1 for p in pages[lang] if p.startswith(lang + "/") and p.endswith(".md"))
            if n < min_lang:
                problems.append(f"{lang} 切片只有 {n} 个 {lang}/ 页面（应在 {min_lang} 以上）")

    if problems:
        for p in problems:
            print(f"::error::{p}", file=sys.stderr)
        return 1
    counts = ", ".join(f"{k}={len(v)}" for k, v in sorted(pages.items()))
    print(f"切片体检通过：{counts}（不含模板/数据目录）")
    return 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 - 老 Python / 非标准流时保持原样
            pass
    ap = argparse.ArgumentParser(description="生成/校验三语言构建切片（_langsrc/）")
    ap.add_argument("--check", action="store_true", help="只校验切片，不重建")
    ap.add_argument("--min-zh", type=int, default=1000,
                    help="zh 切片 _species 页面数的下限（在裁剪过的小样站点上调试时可调小）")
    ap.add_argument("--min-lang", type=int, default=3000,
                    help="en/es 切片各语言页面数的下限（同上）")
    args = ap.parse_args()
    if args.check:
        return check(min_zh=args.min_zh, min_lang=args.min_lang)
    print("生成语言切片：")
    return build()


if __name__ == "__main__":
    raise SystemExit(main())
