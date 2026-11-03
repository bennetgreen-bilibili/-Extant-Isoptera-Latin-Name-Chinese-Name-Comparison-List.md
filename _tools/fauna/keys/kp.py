import re, json, os
import vocab
from vocab import find_terms, SP, GEN

RAW_PATH = os.environ.get('FZ_KEYS_RAW', '.tmp/keys/raw.txt')
lines = open(RAW_PATH, encoding='utf-8').read().split('\n')

CASTE = re.compile(r'^(兵\s*蚁|成\s*虫|有\s*翅\s*成\s*虫|工\s*蚁|大\s*兵\s*蚁|小\s*兵\s*蚁|兵蚁和工蚁|蛹|若虫)\s*[:：]?$')
def clean_line(s):
    s=s.replace('\u3000',' ').replace('\t',' ')
    s=re.sub(r'[‘’]',"'",s)
    s=re.sub(r'[.．·…\u2026]{2,}',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

def squash(t):
    return re.sub(r'(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])','',t)

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

TARGET=re.compile(r'(\d{1,2})\s*([.。]?)\s*$')
def _target_end(t, maxn):
    m=TARGET.search(t)
    if not m: return None
    st=m.start()
    if st>0 and (t[st-1] in '.．,，' or t[st-1].isdigit()): return None
    if st<3: return None
    n=int(m.group(1))
    if not (1<=n<=maxn): return None
    return ('target', {'next':n,'prefix':t[:st].rstrip()}, m.end())

SPEC_TAIL=re.compile("([\u4e00-\u9fa5]{0,16}?)\\s*([A-Z])\\s*[.,\uff0e\uff0c]?\\s*(?:[(\uff08\u3014\\[]\\s*([A-Za-z0-9]{1,5}(?:\\s*[.\uff0e]\\s*[A-Za-z]{0,8})?)\\s*[)\uff09\u3015\\]}]\\s*)?([a-z\u00e0-\u00ff\u0142](?:\\s?[a-z\u00e0-\u00ff\u0142]){1,24})\\s*[.\u3002]?\\s*$")
LAT_OK=re.compile("^(?=[^\\u4e00-\\u9fa5]*$)[\\sA-Za-z0-9.\\uff0e,\\u3001()\\uff08\\uff09\\u00b7\\u2014\\-\\u00b0']{0,40}$")

def _latin_tail(t):
    m=SPEC_TAIL.search(t)
    if not m: return None
    return {'zh':(m.group(1) or '').strip(),'genus_raw':m.group(2),'subgen':m.group(3),
            'epi':re.sub(r'\s+','',m.group(4)),'end':m.end()}

def _find_end(t, maxn=200):
    t=t.rstrip()
    r=_target_end(t,maxn)
    m=_latin_tail(t)
    best=None
    if m: best=('taxon', m, m['end'])
    tn=squash(t)
    if tn!=t:
        m2=_latin_tail(tn)
        if m2 and (best is None or m2['end']>best[2]):
            m2['end']=len(t)
            best=('taxon', m2, len(t))
    for src in ([t,tn] if tn!=t else [t]):
        for hit in reversed(find_terms(src)):
            suf=src[hit[1]:]
            if len(suf)<=40 and LAT_OK.match(suf):
                if best is None or hit[1]>best[2]:
                    best=('taxon', {'zh':hit[3],'kind':hit[2],'payload':hit[4]}, hit[1])
                break
    if best: return best
    return r

def ends_unit(t, maxn=200):
    return _find_end(t,maxn)

def parse_block(h,e):
    secs=[]; cur={'caste':'','units':[]}; acc=None
    def push(num,txt):
        cur['units'].append([num,txt])
    for i in range(h+1,e):
        st=lines[i].strip()
        if not st: continue
        if st.startswith('=====CHUNK'): continue
        if re.match(r'^[①-⑩]',st): continue
        if re.match(r'^图\s*\d+',st): continue
        if re.match(r'^仿',st): continue
        if re.search(r'量\s*度\s*[（(]?\s*mm',st): continue
        if CASTE.match(st):
            if acc: push(acc[0],acc[1]); acc=None
            if cur['units']: secs.append(cur)
            cur={'caste':CASTE.match(st).group(1).replace(' ',''),'units':[]}
            continue
        for num,txt in split_para(clean_line(lines[i])):
            if acc is None:
                acc=[num,txt]
            elif num is not None:
                push(acc[0],acc[1].strip()); acc=[num,txt]
            else:
                acc[1]=(acc[1]+' '+txt).strip()
            while acc:
                f=_find_end(acc[1],200)
                if not f: break
                kind,pay,end=f
                head=acc[1][:end].strip()
                rest=acc[1][end:].strip()
                push(acc[0],head)
                acc=[None,rest] if rest else None
    if acc: push(acc[0],acc[1].strip())
    if cur['units']: secs.append(cur)

    out=[]
    for s in secs:
        couplets=[]
        for num,txt in s['units']:
            if num is not None:
                couplets.append({'n':num,'leads':[txt]})
            else:
                if couplets and len(couplets[-1]['leads'])==1: couplets[-1]['leads'].append(txt)
                elif couplets: couplets[-1]['leads'][-1]+=' '+txt
                else: couplets.append({'n':1,'leads':[txt]})
        out.append({'caste':s['caste'],'couplets':couplets})
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

def blocks():
    out=[]
    heado=[i for i,l in enumerate(lines) if '检索表' in l and not re.match(r'^(而一个地区性|关于乳白蚁)', l.strip())]
    for h in heado:
        e=len(lines)
        for j in range(h+1,len(lines)):
            if is_stop(lines[j]): e=j;break
        out.append((h,e))
    return out

if __name__=='__main__':
    tot=0; bad=0; opens=0
    for (h,e) in blocks():
        title=lines[h].strip()
        ks=parse_block(h,e)
        for sec in ks:
            cs=sec['couplets']
            maxn=max([c['n'] for c in cs],default=0)
            for c in cs:
                tot+=1
                if len(c['leads'])!=2: bad+=1
                for l in c['leads']:
                    if _find_end(l,maxn) is None: opens+=1
        print('%-26s'%title[:26], ' | '.join('%s:c%d/two%d'%(s['caste'] or '-',len(s['couplets']),sum(1 for c in s['couplets'] if len(c['leads'])==2)) for s in ks))
    print('TOTAL couplets',tot,'not-two',bad,'open-leads',opens)
