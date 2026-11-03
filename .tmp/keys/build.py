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

CASTE = re.compile(r'^(兵\s*蚁|成\s*虫|有\s*翅\s*成\s*虫|工\s*蚁|大\s*兵\s*蚁|小\s*兵\s*蚁|兵蚁和工蚁|蛹|若虫)\s*[:：]?$')

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
    s=re.sub(r'[.．·…\u2026]{2,}',' ',s)
    s=re.sub(r'(?<=[\u4e00-\u9fa5])\s*[.．·…\u2026]\s*(?=[\u4e00-\u9fa5])',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

LEADNUM = re.compile(r'(?:^|(?<=[\s。，、）)]))(\d{1,2})\s*[.)．]\s*(?=[\u4e00-\u9fa5A-Za-z（(])')

def split_para(text):
    ms=list(LEADNUM.finditer(text))
    res=[]
    if not ms:
        return [(None, text.strip())] if text.strip() else []
    pre=text[:ms[0].start()].strip()
    if pre: res.append((None, pre))
    for k,m in enumerate(ms):
        end=ms[k+1].start() if k+1<len(ms) else len(text)
        res.append((int(m.group(1)), text[m.end():end].strip()))
    return res

NUMTAIL=re.compile(r'(\d{1,2})\s*$')
def ends_with_target(t, maxn=99):
    m=NUMTAIL.search(t)
    return bool(m) and m.start()>=1 and int(m.group(1))<=maxn

def parse_block(h,e):
    sections=[]; cur={'caste':'','units':[]}
    for i in range(h+1,e):
        st=lines[i].strip()
        if not st: continue
        if re.match(r'^[①-⑩]',st): continue
        if re.match(r'^图\s*\d+',st): continue
        if '仿' in st: continue
        if re.search(r'量\s*度\s*[（(]?\s*mm',st): continue
        if CASTE.match(st):
            if cur['units']: sections.append(cur)
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
                elif ends_with_target(cur['units'][-1][1]):
                    cur['units'].append([None,txt])
                else:
                    cur['units'][-1][1]=(cur['units'][-1][1]+' '+txt).strip()
    if cur['units']: sections.append(cur)
    return sections

def assemble(units):
    couplets=[]
    for num,txt in units:
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
    return couplets

if __name__=='__main__':
    import sys
    want=[int(x) for x in sys.argv[1:]] if len(sys.argv)>1 else []
    for (h,e) in blocks():
        if want and h not in want: continue
        print('#'*70); print(lines[h].strip(),'|',h,e)
        for s in parse_block(h,e):
            cs=assemble(s['units'])
            print(' CASTE',s['caste'],'couplets',len(cs),'single',[c['n'] for c in cs if len(c['leads'])!=2])
            for c in cs:
                print('  %2d'%c['n'])
                for k,l in enumerate(c['leads']):
                    print('     %s %s'%('ab'[k], l[:110]))
