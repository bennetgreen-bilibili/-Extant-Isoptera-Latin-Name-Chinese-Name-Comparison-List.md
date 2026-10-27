#!/usr/bin/env python3
"""批量下载候选插图到 _tmp/review/（仅用于审阅；_tmp/ 已被 .gitignore 忽略）。

用法：python _tools/fetch_review_batch.py
下载完成后告诉我，我再逐张看、挑出有兵蚁的图。
"""
import urllib.request, urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_tmp" / "review"
BASE = "https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/{size}.{ext}"

# (图位, iNaturalist 照片 ID, 许可, 物种/类群, 作者)
CANDS = [
    ("P2", 742344685, "cc-by-nc", "Cubitermes", "Gwili Gibbon, some rights reserved (CC BY-NC)"),
    ("P2", 659093404, "cc-by-nc", "Cubitermes", "bright_coffie, some rights reserved (CC BY-NC)"),
    ("P2", 659093891, "cc-by-nc", "Cubitermes", "bright_coffie, some rights reserved (CC BY-NC)"),
    ("P2", 447232669, "cc-by-nc-sa", "Cubitermes", "Rob Palmer, some rights reserved (CC BY-NC-SA)"),
    ("P2", 447232679, "cc-by-nc-sa", "Cubitermes", "Rob Palmer, some rights reserved (CC BY-NC-SA)"),
    ("P2", 447232685, "cc-by-nc-sa", "Cubitermes", "Rob Palmer, some rights reserved (CC BY-NC-SA)"),
    ("P2", 418580804, "cc-by-nc", "Cubitermitinae", "Tomáš Hovorka, some rights reserved (CC BY-NC)"),
    ("P2", 669541219, "cc-by", "Thoracotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P2", 662955759, "cc-by", "Thoracotermes", "avocat, some rights reserved (CC BY)"),
    ("P2", 641349059, "cc-by", "Thoracotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P2", 641349305, "cc-by", "Thoracotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P2", 641295512, "cc-by", "Thoracotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P3", 599650673, "cc-by", "Cylindrotermes", "portioid, some rights reserved (CC BY)"),
    ("P3", 621575432, "cc-by-nc", "Cephalotermes", "Angus Davison, some rights reserved (CC BY-NC)"),
    ("P6", 754177707, "cc-by-nc", "Neocapritermes", "Frederic Griesbaum, some rights reserved (CC BY-NC)"),
    ("P6", 752940600, "cc-by-nc-nd", "Neocapritermes", "Norbert VERNEAU, some rights reserved (CC BY-NC-ND)"),
    ("P6", 752940574, "cc-by-nc-nd", "Neocapritermes", "Norbert VERNEAU, some rights reserved (CC BY-NC-ND)"),
    ("P6", 752940604, "cc-by-nc-nd", "Neocapritermes", "Norbert VERNEAU, some rights reserved (CC BY-NC-ND)"),
    ("P6", 742509825, "cc-by-nc", "Neocapritermitinae", "manu_bio26, some rights reserved (CC BY-NC)"),
    ("P6", 737197540, "cc-by-nc", "Cupim peteleco", "Léa Maria Steffen S. Fernandes, some rights reserved (CC BY-NC)"),
    ("P6", 677331577, "cc-by-sa", "Cupim Peteleco", "Luciano Silveira, some rights reserved (CC BY-SA)"),
    ("P6", 677331587, "cc-by-sa", "Cupim Peteleco", "Luciano Silveira, some rights reserved (CC BY-SA)"),
    ("P6", 677331599, "cc-by-sa", "Cupim Peteleco", "Luciano Silveira, some rights reserved (CC BY-SA)"),
    ("P6", 670263560, "cc-by-nc", "Neocapritermes talpa", "mandarijn77, some rights reserved (CC BY-NC)"),
    ("P8", 658071787, "cc-by", "Sphaerotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P8", 658072317, "cc-by", "Sphaerotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P8", 658072333, "cc-by", "Sphaerotermes", "Philippe Hornus, some rights reserved (CC BY)"),
    ("P10", 748583893, "cc-by-nc", "Rhynchotermes", "Sylvain Morin, some rights reserved (CC BY-NC)"),
    ("P10", 748583878, "cc-by-nc", "Rhynchotermes", "Sylvain Morin, some rights reserved (CC BY-NC)"),
    ("P10", 748000309, "cc-by-nc", "Rhynchotermes", "seth_msp, some rights reserved (CC BY-NC)"),
    ("P10", 725068917, "cc-by-nc", "Rhynchotermes", "aeon2012, some rights reserved (CC BY-NC)"),
    ("P10", 725068916, "cc-by-nc", "Rhynchotermes", "aeon2012, some rights reserved (CC BY-NC)"),
    ("P10", 725068920, "cc-by-nc", "Rhynchotermes", "aeon2012, some rights reserved (CC BY-NC)"),
    ("P10", 725068918, "cc-by-nc", "Rhynchotermes", "aeon2012, some rights reserved (CC BY-NC)"),
    ("P10", 618531010, "cc-by-nc", "Rhynchotermes perarmatus", "river_monster, some rights reserved (CC BY-NC)"),
    ("P10", 618531002, "cc-by-nc", "Rhynchotermes perarmatus", "river_monster, some rights reserved (CC BY-NC)"),
    ("P10", 618475924, "cc-by-nc", "Rhynchotermes", "Julián Maya, some rights reserved (CC BY-NC)"),
    ("P10", 618478590, "cc-by-nc", "Rhynchotermes", "Julián Maya, some rights reserved (CC BY-NC)"),
    ("P10", 620243251, "cc-by-nc", "Rhynchotermes", "Julián Maya, some rights reserved (CC BY-NC)"),
    ("P1", None, "cc-by", "Glossotermes（BOLD 标本）", "BOLD/GBIF"),
]

BOLD = "https://caos.boldsystems.org/api/objects/caos-cloud.linode-us-east.17_171.91557efe-5862-4ff9-88a0-a4d5011a68a1.jpg?subunit=1024.jpg"


def download(pid):
    for ext in ("jpeg", "jpg", "png"):
        for size in ("original", "large"):
            url = BASE.format(pid=pid, size=size, ext=ext)
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    data = r.read()
                if data[:2] == b"\xff\xd8" or data[:8] == b"\x89PNG\r\n\x1a\n":
                    return data, url
            except urllib.error.HTTPError:
                continue
            except urllib.error.URLError as e:
                raise SystemExit(f"网络错误：{e}")
    return None, None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    seen = set()
    for pos, pid, lic, name, author in CANDS:
        if pid is None:
            dest = OUT / f"{pos}__BOLD_glossotermes.jpg"
            try:
                req = urllib.request.Request(BOLD, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    dest.write_bytes(r.read())
                print(f"OK   {dest.name}")
                ok += 1
            except Exception as e:
                print(f"FAIL {dest.name}: {e}")
            continue
        key = (pos, pid)
        if key in seen:
            continue
        seen.add(key)
        data, url = download(pid)
        if data:
            dest = OUT / f"{pos}__{pid}.jpg"
            dest.write_bytes(data)
            print(f"OK   {dest.name:28s} {len(data)/1024:7.1f} KB  {lic:12s} {author[:28]}")
            ok += 1
        else:
            print(f"FAIL {pos}__{pid}.jpg  请手动打开 https://www.inaturalist.org/photos/{pid}")
    print(f"\n完成：{ok} 张 -> {OUT}")


if __name__ == "__main__":
    main()
