# -*- coding: utf-8 -*-
"""生成站点图标（favicon）全部尺寸。

设计：品牌深绿圆角方块（#1f4d38，与 _data 里 theme-color 一致）+ 米白侧视白蚁剪影。

产物（全部由本脚本确定性生成，不要手改 PNG/ICO，改样式就改这里再重跑）：
    favicon.ico                          16/32/48 多尺寸（浏览器标签页、Google 默认抓取）
    assets/icons/favicon-48.png          48×48
    assets/icons/favicon-96.png          96×96（Google 搜索结果的「正方形、>48px」要求）
    assets/icons/favicon-144.png         144×144
    assets/icons/favicon-192.png         192×192
    assets/icons/favicon-512.png         512×512
    assets/icons/apple-touch-icon.png    180×180（iOS 主屏，不透明底）
    assets/icons/favicon.svg             矢量版（现代浏览器标签页；Google 搜索不认 SVG）

Google 只接受 BMP/GIF/ICO/PNG/JPEG/PPM/TIFF，且要求图标为正方形、边长大于 48px；
所以 PNG 与 ICO 是必须的，SVG 只是锦上添花。

用法：
    python _tools/make_favicon.py            # 重新生成全部产物
    python _tools/make_favicon.py --check    # 只比对磁盘上的产物是否与脚本输出一致
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "assets" / "icons"

GREEN = (31, 77, 56)        # #1f4d38 —— 与页头 hero 渐变起点同一色
CREAM = (247, 241, 230)     # #f7f1e6 —— 米白剪影，白底/深色标签栏都清晰
RADIUS = 230                # 圆角半径（1024 设计坐标）
TILT = -9                   # 虫体整体上翘角度（Pillow 约定：正数逆时针）
# SVG 的角度约定与 Pillow 相反（y 轴向下，正数在屏幕上是顺时针），所以写进 SVG 时要取反，
# 否则矢量版的虫体是"低头"的，和 PNG 方向正好相反。
SVG_TILT = -TILT
SCALE = 1.12                # 虫体相对设计坐标的放大倍数（小尺寸更醒目）

# 设计坐标（1024×1024）：腹、胸、头三个椭圆
ABDOMEN = (440, 445, 875, 765)
THORAX = (315, 490, 525, 690)
HEAD = (150, 455, 350, 660)
LEGS = (
    ((355, 660), (315, 742)),
    ((420, 672), (412, 760)),
    ((478, 660), (515, 738)),
)
ANTENNAE = (
    ((228, 470), (188, 396), (158, 378)),
    ((262, 462), (236, 384), (214, 366)),
)
LEG_WIDTH = 28
ANTENNA_WIDTH = 26
EYE = (178, 512, 212, 546)   # 眼点：用背景色挖空
PIVOT = (500, 600)           # 旋转中心
BODY_CENTER = (512, 567)     # 缩放中心（剪影大致居中处）

MASTER = 4096                # 主绘尺寸：4× 超采样，缩到 48px 也不会发毛

PNG_SIZES = (48, 96, 144, 192, 512)
ICO_SIZES = (16, 32, 48, 64)
TOUCH_SIZE = 180


def _scale_point(px: float, py: float) -> tuple[float, float]:
    cx, cy = BODY_CENTER
    return cx + (px - cx) * SCALE, cy + (py - cy) * SCALE


def _scaled_box(box):
    x0, y0 = _scale_point(box[0], box[1])
    x1, y1 = _scale_point(box[2], box[3])
    return x0, y0, x1, y1


def build_master() -> Image.Image:
    """1024 设计坐标 → MASTER 像素的 RGBA 主图。"""
    u = MASTER / 1024.0

    def s(v):
        return v * u

    img = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, MASTER - 1, MASTER - 1], radius=s(RADIUS), fill=GREEN + (255,))

    body = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    b = ImageDraw.Draw(body)
    for box in (ABDOMEN, THORAX, HEAD):
        x0, y0, x1, y1 = _scaled_box(box)
        b.ellipse([s(x0), s(y0), s(x1), s(y1)], fill=CREAM + (255,))

    for pts in LEGS:
        b.line([tuple(s(v) for v in _scale_point(x, y)) for x, y in pts],
               fill=CREAM + (255,), width=int(s(LEG_WIDTH * SCALE)), joint="curve")
    for pts in ANTENNAE:
        b.line([tuple(s(v) for v in _scale_point(x, y)) for x, y in pts],
               fill=CREAM + (255,), width=int(s(ANTENNA_WIDTH * SCALE)), joint="curve")

    ex0, ey0, ex1, ey1 = _scaled_box(EYE)
    b.ellipse([s(ex0), s(ey0), s(ex1), s(ey1)], fill=GREEN + (255,))

    px, py = _scale_point(*PIVOT)
    body = body.rotate(TILT, resample=Image.BICUBIC, center=(s(px), s(py)))
    img.alpha_composite(body)
    return img


def build_svg() -> str:
    """与主图同几何参数的矢量版。"""
    def f(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")

    def box(b):
        x0, y0, x1, y1 = _scaled_box(b)
        # 属性值必须带引号：.svg 是按 XML 解析的，裸值会让整份文件解析失败，
        # 浏览器拿到的就是一张坏图（标签页图标变空白）。
        return (f'cx="{(x0 + x1) / 2:.2f}" cy="{(y0 + y1) / 2:.2f}" '
                f'rx="{(x1 - x0) / 2:.2f}" ry="{(y1 - y0) / 2:.2f}"')

    def path(pts):
        (x, y), *rest = [_scale_point(*p) for p in pts]
        d = f"M{f(x)} {f(y)}" + "".join(f" L{f(px)} {f(py)}" for px, py in rest)
        return d

    legs = "\n".join(
        f'    <path d="{path(p)}" stroke-width="{f(LEG_WIDTH * SCALE)}"/>' for p in LEGS)
    ant = "\n".join(
        f'    <path d="{path(p)}" stroke-width="{f(ANTENNA_WIDTH * SCALE)}"/>' for p in ANTENNAE)
    ex0, ey0, ex1, ey1 = _scaled_box(EYE)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="白蚁名录">
  <title>白蚁名录 — 现生等翅下目</title>
  <rect width="1024" height="1024" rx="{RADIUS}" fill="#1f4d38"/>
  <g transform="rotate({SVG_TILT} {f(_scale_point(*PIVOT)[0])} {f(_scale_point(*PIVOT)[1])})"
     fill="#f7f1e6" stroke="#f7f1e6" stroke-linecap="round" stroke-linejoin="round">
    <ellipse {box(ABDOMEN)}/>
    <ellipse {box(THORAX)}/>
    <ellipse {box(HEAD)}/>
{legs}
{ant}
    <ellipse cx="{f((ex0 + ex1) / 2)}" cy="{f((ey0 + ey1) / 2)}" rx="{f((ex1 - ex0) / 2)}" ry="{f((ey1 - ey0) / 2)}" fill="#1f4d38" stroke="none"/>
  </g>
</svg>
"""


def targets() -> dict[Path, bytes]:
    """所有产物：{路径: 内容}。"""
    master = build_master()
    out: dict[Path, bytes] = {}

    def png(size: int, *, opaque: bool = False) -> bytes:
        im = master.resize((size, size), Image.LANCZOS)
        if opaque:  # apple-touch-icon 不透明，iOS 会自己加圆角
            bg = Image.new("RGB", (size, size), GREEN)
            bg.paste(im, (0, 0), im)
            im = bg
        import io
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    for size in PNG_SIZES:
        out[ICON_DIR / f"favicon-{size}.png"] = png(size)
    out[ICON_DIR / "apple-touch-icon.png"] = png(TOUCH_SIZE, opaque=True)
    svg = build_svg()
    # 良构性自检：SVG 是 XML，标签没闭合 / 属性没引号都会让浏览器整张丢掉，
    # 而 PNG 那条路是好的，所以肉眼看截图不一定发现——在这里挡死。
    ElementTree.fromstring(svg)
    out[ICON_DIR / "favicon.svg"] = svg.encode("utf-8")

    import io
    buf = io.BytesIO()
    master.save(buf, format="ICO", sizes=[(n, n) for n in ICO_SIZES])
    out[ROOT / "favicon.ico"] = buf.getvalue()
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    files = targets()
    bad = []
    for path, data in files.items():
        rel = path.relative_to(ROOT).as_posix()
        if check:
            if not path.exists():
                bad.append(f"缺失 {rel}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
                bad.append(f"不一致 {rel}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"写入 {rel} ({len(data)} bytes)")
    if check:
        if bad:
            print("图标产物与脚本输出不一致：\n  " + "\n  ".join(bad))
            return 1
        print(f"OK：{len(files)} 个图标产物与 _tools/make_favicon.py 的输出一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
