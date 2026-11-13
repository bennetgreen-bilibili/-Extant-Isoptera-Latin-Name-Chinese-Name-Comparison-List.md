#!/usr/bin/env python3
"""把 assets/ 下前端资源的内容指纹写进 _data/build.json。

模板里的缓存戳（`assets/custom.css?v=…`）过去用 `site.time`，导致**每次部署所有
CSS/JS 的 URL 都变**，浏览器与 CDN 缓存全部失效，哪怕这次只改了一篇物种页正文。
本脚本改为按文件内容取 sha256 前缀：内容不变 → 版本号不变 → 缓存继续命中；
只有真正改了某个文件，那个文件的 URL 才变。

用法：
    python _tools/stamp_assets.py            # 写入 _data/build.json
    python _tools/stamp_assets.py --check    # 只校验（CI 用），过期则 exit 1

输出是确定性的（键按文件名排序、不含时间戳）：同样的 assets 内容永远得到同一个
_data/build.json，因此 validate.yml 里「重跑 regen_all.sh 后 git diff 应为空」
这条闸门对它同样成立。
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets"
OUT = ROOT / "_data" / "build.json"
LAYOUT_DIR = ROOT / "_layouts"
INCLUDE_DIR = ROOT / "_includes"

# 只给模板里以 ?v= 引用、会直接改动的顶层资源做指纹；vendor/ 下的第三方库
# 升级时会连文件名/目录一起换，不需要（也不应该）参与这个哈希。
SUFFIXES = {".css", ".js"}
HASH_LEN = 10


def asset_files() -> list[Path]:
    return sorted(
        p
        for p in ASSET_DIR.iterdir()
        if p.is_file() and p.suffix in SUFFIXES and not p.name.startswith(".")
    )


def fingerprint(path: Path) -> str:
    """按文件内容取指纹，行尾统一成 LF 后再哈希。

    为什么归一化：本仓库的 .gitattributes 不固定行尾，Windows 检出会把部分文件写成
    CRLF（assets/phylogeny.css、phylogeny.js 就是），Linux 上的 CI 则是 LF。若直接
    哈希工作区字节，同一份提交在本地与 CI 会得出不同指纹，_data/build.json 就会在
    validate.yml 的「生成产物过期」检查里反复红。归一化后两端一致。
    """
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:HASH_LEN]


def build_payload() -> dict:
    assets = {p.name: fingerprint(p) for p in asset_files()}
    return {
        "_comment": "由 _tools/stamp_assets.py 生成，请勿手改；内容指纹随 assets/*.css|js 变化。",
        "assets": assets,
    }


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


AV_REF = re.compile(r"AV\['([^']+)'\]")
LEGACY = re.compile(r"site\.time\s*\|\s*date:\s*'%s'")


def template_refs() -> tuple[dict[str, list[str]], list[str]]:
    """模板里引用了哪些资源指纹，以及有没有人把 site.time 那段写回来了。"""
    refs: dict[str, list[str]] = {}
    legacy: list[str] = []
    for path in sorted(list(LAYOUT_DIR.rglob("*.html")) + list(INCLUDE_DIR.rglob("*.html"))):
        text = path.read_text(encoding="utf-8")
        try:
            rel_path = path.relative_to(ROOT).as_posix()
        except ValueError:
            rel_path = path.as_posix()
        for name in AV_REF.findall(text):
            refs.setdefault(name, []).append(rel_path)
        if LEGACY.search(text):
            legacy.append(rel_path)
    return refs, legacy


def main(argv: list[str]) -> int:
    check = "--check" in argv
    build = build_payload()
    assets = build["assets"]
    text = render(build)
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    rc = 0

    # 引用一致性：模板里 AV['x'] 的每个 x 都得真有指纹，拼错的名字会悄悄退化成
    # 数据集版本号（缓存失效但不报错），所以在写盘前就红掉。
    refs, legacy = template_refs()
    unknown = {n: files for n, files in refs.items() if n not in assets}
    if unknown:
        print("FAIL: 模板引用了 assets/ 里不存在的资源指纹：")
        for name, files in sorted(unknown.items()):
            print(f"  - {name}（{', '.join(sorted(set(files)))}）")
        rc = 1
    if legacy:
        print(f"FAIL: 这些模板又用回了部署时间做缓存戳：{', '.join(legacy)}")
        rc = 1
    if rc:
        return rc

    if check:
        if current == text:
            print(f"OK: {OUT.relative_to(ROOT)} 与 assets 内容一致（模板引用 {len(refs)} 个资源）")
            return 0
        print(f"STALE: {OUT.relative_to(ROOT)} 与 assets 内容不一致，请运行 python _tools/stamp_assets.py")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if current == text:
        print(f"OK: {OUT.relative_to(ROOT)} 无需改动（{len(assets)} 个资源指纹，模板引用 {len(refs)} 个）")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"WROTE: {OUT.relative_to(ROOT)}（{len(assets)} 个资源指纹，模板引用 {len(refs)} 个）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
