
import os, re, json, sys
from docx import Document

BASE = r"E:\TENXUN\Tencent Files\3230435183\[www.19cr.com]中国动物志.昆虫纲.第十七卷.等翅目 (2)"
OUT = "_tmp/dz"
os.makedirs(OUT, exist_ok=True)

files = [f for f in os.listdir(BASE) if f.lower().endswith(".docx")]
def key(f):
    m = re.search(r"_(\d+)-(\d+)\.docx$", f)
    return int(m.group(1)) if m else 9999
files.sort(key=key)
print("docx chunks:", len(files))

if not os.path.exists(OUT + "/fauna_raw.txt"):
    chunks = []
    for f in files:
        d = Document(os.path.join(BASE, f))
        chunks.append("\n".join(p.text for p in d.paragraphs))
    raw = "\n".join(chunks)
    open(OUT + "/fauna_raw.txt", "w", encoding="utf-8").write(raw)
    print("raw chars", len(raw))
else:
    raw = open(OUT + "/fauna_raw.txt", encoding="utf-8").read()
    print("reused raw chars", len(raw))
