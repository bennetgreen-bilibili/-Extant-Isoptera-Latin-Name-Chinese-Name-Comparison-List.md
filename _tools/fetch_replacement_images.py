#!/usr/bin/env python3
"""下载替代插图到 assets/images/（仅在确认许可后使用）。

用法：python _tools/fetch_replacement_images.py
依赖：仅标准库。下载后请检查文件大小，并在对应名录页补回 figcaption
（图注模板见 _tools/图片版权核查与处理清单.md）。
"""
import urllib.request
import urllib.error
from pathlib import Path

# 目标文件名 -> iNaturalist 照片 ID（许可见清单文档，均为 CC BY / CC BY-NC）
IMAGES = {
    "cubitermitinae.jpg": 669541219,       # Thoracotermes sp. / Philippe Hornus / CC BY 4.0
    "cylindrotermitinae.jpg": 599650673,   # Cylindrotermes sp. / portioid / CC BY 4.0
    "neocapritermitinae.jpg": 698854667,   # Neocapritermes taracua / sernat / CC BY-NC 4.0
    "sphaerotermitinae-1.jpg": 658071787,  # Sphaerotermes sp. / Philippe Hornus / CC BY 4.0
    "sphaerotermitinae-2.jpg": 658072317,  # Sphaerotermes sp. / Philippe Hornus / CC BY 4.0
    "syntermitinae.jpg": 457765944,        # Rhynchotermes perarmatus / Ben Costamagna / CC BY 4.0
}

OUT = Path(__file__).resolve().parent.parent / "assets" / "images"
BASE = "https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/{size}.{ext}"


def fetch(pid, dest):
    for ext in ("jpeg", "jpg", "png"):
        for size in ("original", "large"):
            url = BASE.format(pid=pid, size=size, ext=ext)
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    data = resp.read()
                if data[:2] == b"\xff\xd8" or data[:8] == b"\x89PNG\r\n\x1a\n":
                    dest.write_bytes(data)
                    return url, len(data)
            except urllib.error.HTTPError:
                continue
            except urllib.error.URLError as exc:
                raise SystemExit(f"网络错误：{exc}")
    return None, 0


def main():
    for name, pid in IMAGES.items():
        dest = OUT / name
        url, size = fetch(pid, dest)
        if url:
            print(f"OK   {name:28s} {size/1024:7.1f} KB  <- {url}")
        else:
            print(f"FAIL {name:28s} 未找到原图，请到 https://www.inaturalist.org/photos/{pid} 手动下载")


if __name__ == "__main__":
    main()
