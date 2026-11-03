import re, json

lines = open('.tmp/keys/raw.txt', encoding='utf-8').read().split('\n')
sbg = json.load(open('_data/species_by_genus.json', encoding='utf-8'))
GENUS = {}
for g, lst in sbg.items():
    if g=='_meta': continue
    for sp in lst:
        lat = sp['latin'].split()[0]
        GENUS[re.sub(r'[^a-z]','',lat.lower())] = lat

def lev(a,b):
    if a==b: return 0
    if abs(len(a)-len(b))>3: return 9
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]

def genus_match(word):
    w=re.sub(r'[^a-z]','',word.lower())
    if w in GENUS: return GENUS[w]
    best=None;bd=3
    for k,v in GENUS.items():
        if abs(len(k)-len(w))>3: continue
        d=lev(k,w)
        if d<bd: bd=d;best=v
    return best if bd<=2 else None

heado = [i for i,l in enumerate(lines) if '检索表' in l and not re.match(r'^(而一个地区性|关于乳白蚁)', l.strip())]
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
def blocks():
    out=[]
    for h in heado:
        e=len(lines)
        for j in range(h+1,len(lines)):
            if is_stop(lines[j]): e=j;break
        out.append((h,e))
    return out

CASTE = re.compile(r'^(兵\s*蚁|成\s*虫|有\s*翅\s*成\s*虫|工\s*蚁|大\s*兵\s*蚁|小\s*兵\s*蚁|兵蚁和工蚁|蛹|若虫)\s*[:：]?$')
def clean_line(s):
    s=s.replace('\u3000',' ').replace('\t',' ')
    s=re.sub(r'[.．·…\u2026]{2,}',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

LEADNUM=re.compile(r'(?:^|(?<=[\s。，、）)]))(\d{1,2})\s*[.)．]\s*(?=[\u4e00-\u9fa5A-Za-z（(])')
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

TAXTAIL=re.compile(r'\s*([\u4e00-\u9fa5]{0,16})\s*([A-Z][A-Za-z]{0,15})\s*[.,、]?\s*([a-z]{2,}(?:\s+[a-z]{2,})?)?\s*[.。]?\s*$')

def terminal_of(t):
    m=TAXTAIL.search(t)
    if not m: return None
    zh = (m.group(1) or '').strip()
    g = m.group(2) or ''
    e = (m.group(3) or '').replace(' ','')
    if not g: return None
    if re.search(r'[（(][^)）]*'+re.escape(g)+r'[^)）]*[)）]\s*$', t): return None
    cand = genus_match(g)
    if cand is None and not (len(g)==1 and e): return None
    return {'zh':zh, 'genus_raw':g, 'genus':cand or g, 'epi_raw':e,
            'prefix':t[:m.start()].strip(), 'latin':(g+(' '+e if e else ''))}

NUMTAIL=re.compile(r'(\d{1,2})\s*[.。]?\s*$')
def target_of(t, maxn):
    m=NUMTAIL.search(t)
    if not m: return None
    n=int(m.group(1))
    if n<1 or n>maxn: return None
    if m.start()<1: return None
    return {'next':n,'prefix':t[:m.start()].strip()}

def classify(t, maxn):
    term=terminal_of(t)
    if term: return ('taxon', term)
    tg=target_of(t,maxn)
    if tg: return ('target', tg)
    return ('open', {'text':t})

def parse_key(h,e):
    secs=[]; cur={'caste':'','units':[]}
    for i in range(h+1,e):
        st=lines[i].strip()
        if not st: continue
        if re.match(r'^[①-⑩]',st): continue
        if re.match(r'^图\s*\d+',st): continue
        if '仿' in st: continue
        if re.search(r'量\s*度\s*[（(]?\s*mm',st): continue
        if CASTE.match(st):
            if cur['units']: secs.append(cur)
            cur={'caste':CASTE.match(st).group(1).replace(' ',''),'units':[]}
            continue
        t=clean_line(lines[i])
        if not t: continue
        for num,txt in split_para(t):
            if num is not None:
                cur['units'].append([num,txt])
            else:
                if not cur['units']:
                    cur['units'].append([None,txt])
                else:
                    prev=cur['units'][-1][1]
                    if terminal_of(prev) or (target_of(prev, 999) and NUMTAIL.search(prev).start()>0):
                        cur['units'].append([None,txt])
                    else:
                        cur['units'][-1][1]=(prev+' '+txt).strip()
    if cur['units']: secs.append(cur)
    out=[]
    for s in secs:
        couplets=[]
        for num,txt in s['units']:
            if num is not None:
                if couplets and couplets[-1]['n']==num and len(couplets[-1]['leads'])==1:
                    couplets[-1]['leads'].append(txt)
                else:
                    couplets.append({'n':num,'leads':[txt]})
            else:
                if couplets and len(couplets[-1]['leads'])==1:
                    couplets[-1]['leads'].append(txt)
                elif couplets:
                    couplets[-1]['leads'][-1]+=' '+txt
                else:
                    couplets.append({'n':1,'leads':[txt]})
        out.append({'caste':s['caste'],'couplets':couplets})
    return out
