import re, json
import vocab
from vocab import SP, GEN, norm, find_terms

lines = open('.tmp/keys/raw.txt', encoding='utf-8').read().split('\n')

CASTE = re.compile(r'^(兵\s*蚁|成\s*虫|有\s*翅\s*成\s*虫|工\s*蚁|大\s*兵\s*蚁|小\s*兵\s*蚁|兵蚁和工蚁|蛹|若虫)\s*[:：]?$')
def clean_line(s):
    s=s.replace('\u3000',' ').replace('\t',' ')
    s=re.sub(r'[.．·…\u2026]{2,}',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

LEADNUM=re.compile(r'(?:^|(?<=[\s。，、）)]))(\d{1,2})\s*[.)．,，]\s*(?=[\u4e00-\u9fa5A-Za-z（(])')
def split_para(text):
    ms=list(LEADNUM.finditer(text))
    if not ms: return [(None,text.strip())] if text.strip() else []
    res=[]
    pre=text[:ms[0].start()].strip()
    if pre: res.append((None,pre))
    for k,m in enumerate(ms):
        end=ms[k+1].start() if k+1<len(ms) else len(text)
        res.append((int(m.group(1)), text[m.end():end].strip()))
    return res

TARGET=re.compile(r'(\d{1,2})\s*[.。]?\s*$')
def tail_target(t):
    m=TARGET.search(t)
    if not m: return None
    n=int(m.group(1))
    if 1<=n<=200 and m.start()>=3: return n
    return None

LATIN_TAIL=re.compile(r'\s*[A-Za-z(（].{0,40}$')
def tail_taxon(t):
    """loose test: does t end with a known species/genus name (allow latin tail)?"""
    t=t.rstrip()
    for _ in range(2):
        t2=re.sub(r'[\s.。,、]*\d{1,2}$','',t)
        t2=LATIN_TAIL.sub('',t2) if re.search(r'[A-Za-z]',t2[-45:]) else t2
        t=t2.rstrip()
    hits=find_terms(t)
    if not hits: return None
    return hits[-1]

def ends_unit(t):
    if tail_target(t) is not None: return 'target'
    if tail_taxon(t): return 'taxon'
    return None

def parse_block(h,e):
    secs=[]; cur={'caste':'','segs':[]}
    for i in range(h+1,e):
        st=lines[i].strip()
        if not st: continue
        if st.startswith('=====CHUNK'): continue
        if re.match(r'^[①-⑩]',st): continue
        if re.match(r'^图\s*\d+',st): continue
        if re.match(r'^仿',st): continue
        if re.search(r'量\s*度\s*[（(]?\s*mm',st): continue
        if CASTE.match(st):
            if cur['segs']: secs.append(cur)
            cur={'caste':CASTE.match(st).group(1).replace(' ',''),'segs':[]}
            continue
        t=clean_line(lines[i])
        if not t: continue
        cur['segs'].extend(split_para(t))
    if cur['segs']: secs.append(cur)

    out=[]
    for s in secs:
        segs=s['segs']; units=[]  # each: [num, [lead_a, lead_b]]
        idx=0; n=len(segs)
        while idx<n:
            num,txt=segs[idx]; idx+=1
            if num is None:
                # orphan continuation before any numbered lead
                if units and len(units[-1][1])<2:
                    units[-1][1][-1]=' '.join([units[-1][1][-1],txt])
                continue
            a=txt; bl=[]
            # gather a's continuations until it ends a unit
            while idx<n and segs[idx][0] is None and ends_unit(a) is None:
                a=' '.join([a,segs[idx][1]]); idx+=1
            # second lead
            b=None
            if idx<n and segs[idx][0] is None:
                b=segs[idx][1]; idx+=1
                while idx<n and segs[idx][0] is None and ends_unit(b) is None:
                    b=' '.join([b,segs[idx][1]]); idx+=1
            units.append([num,[a]+([b] if b else [])])
        out.append({'caste':s['caste'],'units':units})
    return out

def blocks():
    out=[]
    heado=[i for i,l in enumerate(lines) if '检索表' in l and not re.match(r'^(而一个地区性|关于乳白蚁)', l.strip())]
    for h in heado:
        e=len(lines)
        for j in range(h+1,len(lines)):
            if is_stop(lines[j]): e=j;break
        out.append((h,e))
    return out

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

CN_NUM=re.compile(r'^[一二三四五六七八九十]{1,3}\s*、')

if __name__=='__main__':
    import sys
    tot=0; one=0; three=0; opens=0
    for (h,e) in blocks():
        title=lines[h].strip()
        ks=parse_block(h,e)
        for sec in ks:
            for num,leads in sec['units']:
                tot+=1
                if len(leads)==1: one+=1
                if len(leads)>2: three+=1
                for l in leads:
                    if ends_unit(l) is None: opens+=1
        print('%-30s'%title[:30], ' | '.join('%s:%d/%d'%(s['caste'] or '-',len(s['units']),sum(1 for u in s['units'] if len(u[1])==2)) for s in ks))
    print('TOTAL units',tot,'single-lead',one,'multi',three,'open-leads',opens)
