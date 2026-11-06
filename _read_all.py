
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
doc = Document("白蚁基础知识-中文稿-修订-v3.docx")
for i,p in enumerate(doc.paragraphs):
    t = p.text.rstrip()
    st = p.style.name if p.style else ""
    # print heading-like or all with index
    mark = ""
    if st.lower().startswith("heading") or (t and len(t) < 60 and not t.endswith("。")):
        mark = "  <== " + st
    print(f"[{i}] {t}{mark}")
