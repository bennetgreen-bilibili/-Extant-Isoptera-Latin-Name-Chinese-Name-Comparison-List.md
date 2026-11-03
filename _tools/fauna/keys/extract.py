import zipfile, os, re, sys
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SRC=os.environ.get('FZ_KEYS_DOCX', r'E:/TENXUN/Tencent Files/3230435183/[www.19cr.com]中国动物志.昆虫纲.第十七卷.等翅目 (2)')
OUT=os.environ.get('FZ_KEYS_RAW', '.tmp/keys/raw.txt')
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
out=[]
names=[f for f in os.listdir(SRC) if f.endswith('.docx')]
names.sort(key=lambda n:int(re.search(r'_(\d+)-(\d+)\.docx',n).group(1)))
for name in names:
    p=os.path.join(SRC,name)
    with zipfile.ZipFile(p) as z:
        xml=z.read('word/document.xml')
    root=etree.fromstring(xml)
    body=root.find(W+'body')
    lines=[]
    def text_of(el):
        return ''.join(t.text or '' for t in el.iter(W+'t'))
    def walk(node):
        for ch in node:
            tag=ch.tag
            if tag==W+'p':
                lines.append(text_of(ch).strip())
            elif tag==W+'tbl':
                for tr in ch.iter(W+'tr'):
                    cells=[text_of(tc).strip() for tc in tr.findall(W+'tc')]
                    lines.append('\t'.join(cells))
            elif tag==W+'sdt':
                cont=ch.find(W+'sdtContent')
                if cont is not None: walk(cont)
            elif tag==W+'sdtContent':
                walk(ch)
            elif tag in (W+'bookmarkStart',W+'bookmarkEnd'):
                pass
            elif len(ch):
                walk(ch)
    walk(body)
    out.append('=====CHUNK:%s=====' % name)
    out.extend(lines)
open(OUT,'w',encoding='utf-8').write('\n'.join(out))
print('lines',len(out),'chars',sum(len(x) for x in out))
