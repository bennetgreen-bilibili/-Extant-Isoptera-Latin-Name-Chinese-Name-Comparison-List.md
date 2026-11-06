
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
doc = Document("白蚁基础知识-中文稿-修订-v3.docx")
paras = doc.paragraphs
print("total paragraphs:", len(paras))
keys = ["鼻白蚁","原鼻","寡脉","沙白蚁","异白蚁","乳白蚁","散白蚁","Prorhinotermes","Termitogeton","Rhinotermitidae","Heterotermitidae","Psammotermitidae","Termitogetonidae","Stylotermitidae","Serritermitidae","木白蚁科","草白蚁科","白蚁科"]
for i,p in enumerate(paras):
    t = p.text.strip()
    if not t: continue
    hit = [k for k in keys if k in t]
    if hit:
        print(f"[{i}] {{{','.join(hit)}}}: {t}")
        print()
