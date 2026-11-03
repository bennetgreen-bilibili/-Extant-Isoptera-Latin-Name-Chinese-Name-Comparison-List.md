import re, json, sys

lines = open('.tmp/keys/raw.txt', encoding='utf-8').read().split('\n')
heads = [i for i,l in enumerate(lines) if '检索表' in l and not re.match(r'^(而一个地区性|关于乳白蚁)', l.strip())]

def clean(s):
    s = s.replace('\u3000',' ')
    s = re.sub(r'[.．。·…\s]{3,}$','',s)          # trailing leader dots
    s = re.sub(r'[.．·…]{2,}',' ',s)
    s = re.sub(r'\s+',' ',s).strip()
    return s

SPECIES_TREAT = re.compile(r'^\d{1,3}\s*[.．、]\s*[\u4e00-\u9fa5]{2,12}\s+[A-Z][a-z]+\s+[a-z]')
def is_stop(l):
    s = l.strip()
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
    out = []
    for h in heads:
        e = len(lines)
        for j in range(h+1, len(lines)):
            if is_stop(lines[j]):
                e = j; break
        out.append((h, e))
    return out

num_re = re.compile(r'^\s*(\d{1,3})\s*[.．、,]?\s*(.*)$')

def parse_block(h, e):
    """return list of sections: {caste, couplets:[{n, a,b}]}"""
    sections = []
    cur = {'caste': '', 'raw': []}
    for i in range(h+1, e):
        s = lines[i].strip()
        if not s: continue
        if s.startswith('①') or s.startswith('(') and len(s) < 4: continue
        if re.match(r'^[①-⑩]', s) and len(s) > 40: continue   # footnotes
        if CASTE.match(s):
            if cur['raw']:
                sections.append(cur)
            cur = {'caste': CASTE.match(s).group(1).replace(' ',''), 'raw': []}
            continue
        cur['raw'].append(s)
    if cur['raw']: sections.append(cur)
    return sections

def is_target(line):
    s = line.strip()
    if re.search(r'(?<![\d.mm])[\s]?\d{1,2}\s*$', s) and not re.search(r'\d\s*(mm|节|根|个|枚|次|倍|%|°)\s*$', s):
        return True
    return False

def tokenize(raw):
    """group physical lines into leads"""
    leads = []
    buf = ''
    for s in raw:
        s2 = clean(s)
        if not s2: continue
        if re.match(r'^……+$', s2) or re.match(r'^[.．…\s]+$', s2): continue
        m = num_re.match(s2)
        if m and not re.match(r'^\d', m.group(2)[:1]) and re.search(r'[\u4e00-\u9fa5]', m.group(2)[:4]):
            # numbered lead start
            if buf: leads.append(buf)
            buf = s2
        else:
            if buf and is_target(buf):
                leads.append(buf); buf = s2
            elif buf:
                buf = buf + s2 if re.search(r'[\u4e00-\u9fa5]$', buf) and re.match(r'^[\u4e00-\u9fa5]', s2) else buf + ' ' + s2
            else:
                buf = s2
    if buf: leads.append(buf)
    return leads

if __name__ == '__main__':
    for (h,e) in blocks():
        secs = parse_block(h,e)
        print('='*70)
        print(lines[h].strip(), '| lines %d-%d' % (h,e))
        for sec in secs:
            leads = tokenize(sec['raw'])
            print('  --caste[%s] leads=%d' % (sec['caste'], len(leads)))
