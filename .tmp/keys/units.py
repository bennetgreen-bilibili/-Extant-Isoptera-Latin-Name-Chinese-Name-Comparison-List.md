import re, json

lines = open('.tmp/keys/raw.txt', encoding='utf-8').read().split('\n')
heads = [i for i,l in enumerate(lines) if '检索表' in l and not re.match(r'^(而一个地区性|关于乳白蚁)', l.strip())]

SPECIES_TREAT = re.compile(r'^\d{1,3}\s*[.．、]\s*[\u4e00-\u9fa5]{2,12}\s+[A-Z][a-z]+\s+[a-z]')
def is_stop(l):
    s=l.strip()
    if not s: return False
    if s.startswith('=====CHUNK'): return True
    if '检索表' in s: return True
    if re.match(r'^[（(][一二三四五六七八九十]+[）)]', s): return True
    if re.match(r'^[一二三四五六七八九十]{1,3}\s*、', s): return True
    if SPECIES_TREAT.match(s): return True
    if re.match(r'^图\s*\d+', s): return True
    if re.match(r'^(分布|寄主|生活习性|量度|生物学|经济意义|分类讨论)', s): return True
    if re.match(r'^\d{1,4}$', s): return True
    if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+.*,\s*(19|20)\d\d', s): return True
    return False

CASTE = re.compile(r'^(兵\s*蚁|有\s*翅\s*成\s*虫|工\s*蚁|大\s*兵\s*蚁|小\s*兵\s*蚁|兵蚁和工蚁|蛹|若虫)\s*[:：]?$')

def blocks():
    out=[]
    for h in heads:
        e=len(lines)
        for j in range(h+1,len(lines)):
            if is_stop(lines[j]): e=j;break
        out.append((h,e))
    return out

def clean_line(s):
    s=s.replace('\u3000',' ').replace('\t',' ')
    s=re.sub(r'[.．·…·\u2026]{2,}\s*',' ',s)   # leader dots
    s=re.sub(r'\s*…+\s*',' ',s)
    return s

LEADNUM = re.compile(r'(?<![\d.])[\s。，、）)]*(\d{1,2})\s*[.)．]\s*(?=[\u4e00-\u9fa5A-Za-z（(])')

def split_units(text):
    """split a merged paragraph into lead units"""
    parts=[]
    last=0
    for m in LEADNUM.finditer(text):
        parts.append((m.start(), m.end(), m.group(1)))
    return parts

def parse_block(h,e):
    sections=[]
    cur={'caste':'','text':''}
    for i in range(h+1,e):
        s=lines[i]
        st=s.strip()
        if not st: continue
        if re.match(r'^[①-⑩]',st): continue
        if re.match(r'^图\s*\d+',st): continue
        if '仿' in st and re.search(r'\d\s*[.．]',st) and ('头' in st[:6] or '兵' in st[:4]): continue
        if '\t' in s or re.search(r'量\s*度\s*\(?\s*mm',st): continue
        if CASTE.match(st):
            if cur['text'].strip(): sections.append(cur)
            cur={'caste':CASTE.match(st).group(1).replace(' ',''),'text':''}
            continue
        cur['text'] += clean_line(s)+'\n'
    if cur['text'].strip(): sections.append(cur)
    return sections

if __name__=='__main__':
    for (h,e) in blocks():
        secs=parse_block(h,e)
        tot=sum(len(split_units(s['text'])) for s in secs)
        print(lines[h].strip()[:36].ljust(36), 'lines %4d-%4d'%(h,e), 'units',tot, [ (s['caste'], len(split_units(s['text']))) for s in secs])
