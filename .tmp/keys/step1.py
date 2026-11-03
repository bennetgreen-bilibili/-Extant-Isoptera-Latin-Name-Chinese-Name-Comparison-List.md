import re, json, sys
sys.path.insert(0,'.tmp/keys')
import kp
from kp import _find_end

tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
genus_rec={g['id']:g for g in tax['genera']}
LAT2G={g['latin'].lower():g['id'] for g in tax['genera']}
ZH2G={g['zh']:g['id'] for g in tax['genera']}
SP={}; SPZH={}
for gid,lst in sbg.items():
    if gid=='_meta': continue
    for sp in lst:
        epi=re.sub(r'[^a-z]','',sp['latin'].split()[-1].lower())
        SP[(gid,epi)]=sp
        SPZH.setdefault(re.sub(r'\s','',sp['zh']).replace('蚊','蚁'),[]).append((gid,sp))

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

def fuzzy_epi(gid,epi):
    best=None;bd=3
    for (g,e),sp in SP.items():
        if g!=gid: continue
        d=lev(epi,e)
        if d<bd: bd=d;best=sp
    return best if bd<=2 else None

def zbyname(zh):
    z=re.sub(r'\s','',zh).replace('蚊','蚁')
    return SPZH.get(z)

KEYGENUS={
 '木白蚊科分属检索表':'@kalotermitidae','鼻白蚁科分属检索表':'@rhinotermitidae','分属 检索表 兵   蚁':'@termitidae',
 '等翅目科的检索表 兵   蚁':'@isoptera',
 '树白蚁属的分种检索表':('glyptotermes',),'新白蚊属分种检索表':('neotermes',),
 '原鼻白蚁属分种检索表 兵    蚁':('prorhinotermes',),'长鼻白蚁属分种检索表':('schedorhinotermes',),
 '乳白蚁属分种检索表':('coptotermes',),'乳白蚊属分种检索表':('coptotermes',),
 '平额散白蚁亚属分种检索表':('reticulitermes',),'突额散白蚁亚属分种检索表':('reticulitermes',),
 '散白蚁亚属分种检索表Ret iculitermess, str.':('reticulitermes',),'蔡白蚁属分种检索表 兵    蚁':('xiaitermes',),
 '杆白蚁属分种检索表':('stylotermes',),'地白蚁属分种检索表':('hypotermes',),
 '77□□壤白蚊属分种检索表 兵    蚁':('parahypotermes',),'大白蚁属分种检索表':('macrotermes',),
 '亮白蚁属分种检索表':('euhamitermes',),'印白蚁属分种检索表 兵   蚁':('indotermes',),
 '华白蚁羁分种检索表':('sinotermes',),'球白蚊属分种检索表':('globitermes',),
 '小白蚁属分种检索表':('microtermes',),'钩白蚁属分种检索表':('ancistrotermes',),
 '瘤白蚊属分种检索表 兵    蚁':('mirocapritermes',),'马扭白蚁属分种检索表 兵    蚁':('malaysiocapritermes',),
 '华扭白蚁属分种检索表':('sinocapritermes',),'近扭白蚁属分种检索表':('pericapritermes',),
 '钩扭白蚊属分种检索表':('pseudocapritermes',),'须白蚊属分种检索表 兵   蚁':('hospitalitermes',),
 '葫白蚁属分种检索表':('cucurbitermes',),'歧颚白蚊属分种检索表 大  兵  蚁':('ahmaditermes',),
 '近瓢白蚊属分种检索表':('peribulbitermes',),'夏氏白蚁属分种检索表':('xiaitermes',),
 '象白蚊属分种检索表':('nasutitermes',),'华象白蚁属分种检索表':('sinonasutitermes',),
 '奇象白蚁属分种检索表':('mironasutitermes',),'钝颚白蚁属分种检索表 兵    蚁':('ahmaditermes',),
}

def interpret(lead, kg):
    f=_find_end(lead, 200)
    if not f: return None
    kind,pay,end=f
    if kind=='target': return ('goto', pay['next'])
    # taxon
    gid=None
    if pay.get('genus_raw'):
        g=pay['genus_raw']
        if len(g)==1: gid=kg
        else: gid=LAT2G.get(g.lower())
        epi=pay['epi']
        if gid and (gid,epi) in SP: return ('leaf', gid, SP[(gid,epi)])
        if gid:
            s=fuzzy_epi(gid,epi)
            if s: return ('leaf', gid, s)
    if pay.get('zh'):
        c=zbyname(pay['zh'])
        if c:
            c.sort(key=lambda x: 0 if x[0]==kg else 1)
            return ('leaf', c[0][0], c[0][1])
    return ('unresolved', pay)

if __name__=='__main__':
    for (h,e) in kp.blocks():
        title=kp.lines[h].strip()
        kg=KEYGENUS.get(title)
        if kg and isinstance(kg,tuple): kg=kg[0]
        if kg and kg.startswith('@'): kg=None
        for sec in kp.parse_block(h,e):
            cs=sec['couplets']
            kinds=[]
            for c in cs:
                for l in c['leads']:
                    r=interpret(l,kg)
                    kinds.append(r[0] if r else 'none')
            from collections import Counter
            print('%-30s %-6s %s' % (title[:30], sec['caste'], dict(Counter(kinds))))
