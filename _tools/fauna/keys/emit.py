# -*- coding: utf-8 -*-
"""Emit _data/fauna_keys.json: dichotomous keys for this site.

Sources
-------
- Species- and genus-level keys: 《中国动物志·昆虫纲 第十七卷 等翅目》
  (黄复生等, 2000), mechanically cleaned and pruned to taxa with a site page.
- Order-level key (/list/): Hellemans et al. (2024) Supplementary Note 2,
  "Key to extant families and subfamilies of Isoptera" (translated).
- Termitidae subfamily key: Hellemans et al. (2024) Supplementary Note 3,
  revised from Krishna et al. (2013).

Hand-written couplets live in keys_orders.py (ORDER_OVR / NEOTERMES_OVR);
SITE placement: species keys belong to the genus page, genus keys to the
family/subfamily page."""
import re, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kp
from kp import _find_end
import res

GEN=res.GEN; LAT2G=res.LAT2G; ZH2G=res.ZH2G; SP=res.SP; SUB=res.SUB
SLUG={s['slug']:s for s in SP.values()}
FAM_LAT={f['latin'].lower():f['id'] for f in res.tax['families']}
FAM_ZH={f['zh']:f['id'] for f in res.tax['families']}

MAPPING_LAT={'tsaitermes':'reticulitermes','havilanditermes':'nasutitermes',
  'mironasutitermes':'nasutitermes','peribulbitermes':'ahmaditermes',
  'parahypotermes':'hypotermes','sinotermes':'indotermes',
  'malaysiocapritermes':'procapritermes'}

# idx, kind, page, keygenus(site genus id), book zh, book latin
SPEC=[
 (0,'family','/list/',None,'等翅目','Isoptera'),
 (1,'genus','/family/kalotermitidae/',None,'木白蚁科','Kalotermitidae'),
 (2,'species','/family/kalotermitidae/','glyptotermes','树白蚁属','Glyptotermes'),
 (3,'species','/genus/neotermes/','neotermes','新白蚁属','Neotermes'),
 (4,'genus','/family/rhinotermitidae/',None,'鼻白蚁科','Rhinotermitidae'),
 (6,'species','/family/rhinotermitidae/','schedorhinotermes','长鼻白蚁属','Schedorhinotermes'),
 (7,'species','/family/heterotermitidae/','coptotermes','乳白蚁属','Coptotermes'),
 (8,'species','/family/heterotermitidae/','coptotermes','乳白蚁属','Coptotermes'),
 (9,'species','/family/heterotermitidae/','reticulitermes','平额散白蚁亚属','Reticulitermes (Planifrontotermes)'),
 (10,'species','/family/heterotermitidae/','reticulitermes','突额散白蚁亚属','Reticulitermes (Frontotermes)'),
 (11,'species','/family/heterotermitidae/','reticulitermes','散白蚁亚属','Reticulitermes s. str.'),
 (12,'species','/family/heterotermitidae/','reticulitermes','蔡白蚁属','Tsaitermes'),
 (13,'species','/family/stylotermitidae/','stylotermes','杆白蚁属','Stylotermes'),
 (14,'genus','/family/termitidae/',None,'白蚁科','Termitidae'),
 (15,'species','/subfamily/macrotermitinae/','hypotermes','地白蚁属','Hypotermes'),
 (16,'species','/subfamily/macrotermitinae/','hypotermes','壤白蚁属','Parahypotermes'),
 (17,'species','/subfamily/macrotermitinae/','macrotermes','大白蚁属','Macrotermes'),
 (18,'species','/subfamily/apicotermitinae/','euhamitermes','亮白蚁属','Euhamitermes'),
 (19,'species','/subfamily/apicotermitinae/','indotermes','印白蚁属','Indotermes'),
 (20,'species','/subfamily/apicotermitinae/','indotermes','华白蚁属','Sinotermes'),
 (21,'species','/subfamily/amitermitinae/','globitermes','球白蚁属','Globitermes'),
 (22,'species','/subfamily/macrotermitinae/','microtermes','小白蚁属','Microtermes'),
 (23,'species','/subfamily/macrotermitinae/','ancistrotermes','钩白蚁属','Ancistrotermes'),
 (24,'species','/subfamily/mirocapritermitinae/','mirocapritermes','瘤白蚁属','Mirocapritermes'),
 (25,'species','/subfamily/mirocapritermitinae/','procapritermes','马扭白蚁属','Malaysiocapritermes'),
 (26,'species','/subfamily/mirocapritermitinae/','sinocapritermes','华扭白蚁属','Sinocapritermes'),
 (27,'species','/subfamily/mirocapritermitinae/','pericapritermes','近扭白蚁属','Pericapritermes'),
 (28,'species','/subfamily/mirocapritermitinae/','pseudocapritermes','钩扭白蚁属','Pseudocapritermes'),
 (29,'species','/subfamily/nasutitermitinae/','hospitalitermes','须白蚁属','Hospitalitermes'),
 (30,'species','/subfamily/nasutitermitinae/','cucurbitermes','葫白蚁属','Cucurbitermes'),
 (31,'species','/subfamily/nasutitermitinae/','nasutitermes','歧颚白蚁属','Havilanditermes'),
 (32,'species','/subfamily/nasutitermitinae/','ahmaditermes','近瓢白蚁属','Peribulbitermes'),
 (34,'species','/subfamily/nasutitermitinae/','nasutitermes','象白蚁属','Nasutitermes'),
 (35,'species','/subfamily/nasutitermitinae/','sinonasutitermes','华象白蚁属','Sinonasutitermes'),
 (36,'species','/subfamily/nasutitermitinae/','nasutitermes','奇象白蚁属','Mironasutitermes'),
 (37,'species','/subfamily/nasutitermitinae/','ahmaditermes','钝颚白蚁属','Ahmaditermes'),
]

TITLEHINT={0:'等翅目科的检索表',1:'木白蚊科分属',2:'树白蚁属的分种',4:'鼻白蚁科分属',
 6:'长鼻白蚁属',7:'乳白蚁属分种',8:'乳白蚊属分种',9:'平额散白蚁亚属',10:'突额散白蚁亚属',
 11:'散白蚁亚属',12:'蔡白蚁属',13:'杆白蚁属',14:'分属 检索表',15:'地白蚁属',
 16:'77□□壤白蚊属',17:'大白蚁属',18:'亮白蚁属',19:'印白蚁属',20:'华白蚁',21:'球白蚊属',
 22:'小白蚁属',23:'钩白蚁属',24:'瘤白蚊属',25:'马扭白蚁属',26:'华扭白蚁属',
 27:'近扭白蚁属',28:'钩扭白蚊属',29:'须白蚊属',30:'葫白蚁属',31:'歧颚白蚊属',
 32:'近瓢白蚊属',34:'象白蚊属',35:'华象白蚁属',36:'奇象白蚁属',37:'钝颚白蚁属'}

# hand-written couplets for keys whose printed layout defeated the line parser
from keys_orders import (ORDER_OVR, NEOTERMES_OVR, NEONOTE, FAMNOTE, ORDSRC, SFSRC,
                         BOOKSRC, HELSHORT, BOOKSHORT, KALO_WORLD, KALOSRC,
                         KRISHNASHORT, KALONOTE)

OVR={
 16:('壤白蚁属',[('兵蚁',[
   (1,[('体长大于4.00 mm','to:2'),('体长小于4.00 mm','to:3')]),
   (2,[('体长4.42—5.05(4.63) mm，头长至颚基1.23—1.26(1.25) mm，左上颚长0.65—0.68(0.68) mm，头最宽1.06—1.10(1.08) mm，前胸背板宽0.77—0.81(0.80) mm','sp:hypotermes-manyunensis'),
       ('体长4.11—4.61 mm，头长至颚基1.17—1.24 mm，头最宽0.96—1.06 mm，前胸背板宽0.68—0.77 mm','sp:hypotermes-sumatrensis')]),
   (3,[('体长3.66—4.36(4.05) mm，头长至颚基1.10—1.26(1.18) mm，左上颚长0.61—0.65(0.64) mm，头最宽0.97—1.03(1.01) mm，前胸背板宽0.71—0.77(0.74) mm','sp:hypotermes-yingjiangensis'),
       ('体长3.28—3.54(3.41) mm，头长至颚基1.03—1.13(1.06) mm，左上颚长0.58—0.61(0.60) mm，头最宽0.87—0.94(0.90) mm，前胸背板宽0.65—0.71(0.67) mm','sp:hypotermes-ruiliensis')]),
 ])]),
 21:('球白蚁属',[('兵蚁',[
   (1,[('头宽大于1.00 mm','to:2'),('头宽0.90—0.99(0.95) mm，头长至颚基0.90—0.99(0.95) mm，左上颚长0.77—0.85(0.81) mm，前胸背板宽0.69—0.74(0.71) mm','sp:globitermes-minor')]),
   (2,[('头长至颚基大于1.00 mm','to:3'),('头长至颚基0.90—1.03(0.98) mm，头宽0.97—1.13(1.07) mm，左上颚长0.94—0.97(0.96) mm，前胸背板宽0.71—0.77(0.74) mm','sp:globitermes-menglaensis')]),
   (3,[('前胸背板宽大于0.80 mm','to:4'),('前胸背板宽0.71—0.77(0.74) mm，头长至上颚端1.71—1.87(1.81) mm，头宽1.06—1.16(1.10) mm，左上颚长0.90—1.00(0.95) mm','sp:globitermes-mengpengensis')]),
   (4,[('头宽1.11—1.21 mm，头长至上颚端1.82—2.00 mm，头长至颚基1.22—1.25 mm，前胸背板宽0.83—0.86 mm','sp:globitermes-sulphureus'),
       ('头宽1.04—1.12(1.09) mm，头长至上颚端1.72—1.91(1.80) mm，头长至颚基1.07—1.11(1.10) mm，左上颚长0.87—0.95(0.91) mm，前胸背板宽0.77—0.87(0.83) mm','sp:globitermes-brachycerastes')]),
 ])]),
 25:('马扭白蚁属',[('兵蚁',[
   (1,[('上颚较细长，长1.54—1.70 mm，后颏腰较粗，腰宽0.25—0.31 mm，头部两侧圆弧','sp:procapritermes-huananensis'),
       ('上颚略短，长1.39—1.52 mm，后颏腰细，腰宽0.23 mm，头部两侧平行','sp:procapritermes-zhangfengensis')]),
 ])]),
 29:('须白蚁属',[('兵蚁',[
   (1,[('头宽大于1.30(1.32—1.44) mm，头长连象鼻1.92—2.04 mm，头长不连鼻1.368—1.512 mm，前胸背板宽0.72—0.79 mm','sp:hospitalitermes-majusculus'),
       ('头宽小于1.30 mm','to:2')]),
   (2,[('前胸背板宽大于0.65 mm','to:3'),
       ('前胸背板宽小于0.65(0.58—0.62) mm，头长连象鼻1.61—1.76 mm，头长不连鼻1.20—1.25 mm，头宽1.00—1.12 mm','sp:hospitalitermes-luzonensis')]),
   (3,[('头长连象鼻最大值大于1.90(1.75—1.92) mm，头长不连鼻1.25—1.32 mm，头宽1.13—1.20 mm，前胸背板宽0.67—0.69 mm','sp:hospitalitermes-jinghongensis'),
       ('头长连象鼻最大值小于1.90(1.67—1.87) mm，头长不连鼻1.25—1.40 mm，头宽1.06—1.24 mm，前胸背板宽0.67—0.70 mm','sp:hospitalitermes-damenglongensis')]),
 ])]),
 30:('葫白蚁属',[('兵蚁',[
   (1,[('兵蚁单态，头长连象鼻1.81—1.98(1.89) mm，头长不连鼻1.08—1.16(1.12) mm，头最宽1.10—1.19(1.15) mm，前胸背板长0.22—0.25(0.23) mm，前胸背板宽0.57—0.59(0.58) mm','sp:cucurbitermes-yingdeensis'),
       ('大、小兵蚁二态，大兵蚁头长连象鼻2.23—2.35(2.30) mm，头长不连鼻1.40—1.46(1.43) mm，头最宽1.43—1.54(1.48) mm，前胸背板长0.31—0.35(0.33) mm，前胸背板宽0.74—0.83(0.80) mm','sp:cucurbitermes-sinensis')]),
 ])]),
 31:('歧颚白蚁属',[('大兵蚁',[
   (1,[('头长连象鼻2.36—2.50(2.42) mm，头长不连鼻1.27—1.36(1.31) mm，头最宽1.37—1.43(1.40) mm，前胸背板长0.21—0.23(0.22) mm，前胸背板宽0.54—0.58(0.56) mm','sp:nasutitermes-communis'),
       ('头长连象鼻2.19—2.33 mm，头长不连鼻1.17—1.22 mm，头最宽1.22—1.31 mm，前胸背板长0.19—0.19 mm，前胸背板宽0.53—0.53 mm','sp:nasutitermes-orthonasus')]),
 ])]),
 32:('近瓢白蚁属',[('兵蚁',[
   (1,[('头最宽大于0.90 mm','to:2'),
       ('头最宽小于0.90 mm，0.72—0.86 mm，头长连象鼻1.33—1.53 mm，头长不连鼻0.89—1.03 mm，前胸背板宽0.42—0.47 mm','sp:ahmaditermes-parafulvus')]),
   (2,[('前胸背板宽大于0.50 mm，0.50—0.53(0.51) mm，头长连象鼻1.84—1.95(1.87) mm，头长不连鼻1.08—1.18(1.13) mm，头最宽0.98—1.13(1.06) mm','sp:ahmaditermes-jinghongensis'),
       ('前胸背板宽小于0.50 mm，0.48—0.50(0.49) mm，头长连象鼻1.71—1.80(1.77) mm，头长不连鼻1.04—1.08(1.07) mm，头最宽0.96—1.03(0.99) mm','sp:ahmaditermes-dinghuensis')]),
 ])]),
}

OVR[0]=ORDER_OVR
OVR[3]=NEOTERMES_OVR

DROPNAME={'hospitalitermes-luzonensis':('吕宋须白蚁','Hospitalitermes luzonensis'),
          'microtermes-mengzhuangensis':('曼庄小白蚁','Microtermes mengzhuangensis')}

SKIP={
      5:'原文该检索表的种对与终端被拆分到相邻页面并夹入书眉噪音，无法可靠复原',
      33:'原表以黟县夏氏白蚁与天台夏氏白蚁二分，后者本站未列为独立种，剔除后仅剩 1 个终点，故不列检索表'}

SKIPPAGE={
          5:('/genus/prorhinotermes/','原鼻白蚁属 Prorhinotermes'),
          33:('/genus/xiaitermes/','夏氏白蚁属 Xiaitermes')}

DROPOVR={'ahmaditermes jinghongensis':('景洪近瓢白蚁','Peribulbitermes jinghongensis'),
         'ahmaditermesjinghongensis':('景洪近瓢白蚁','Peribulbitermes jinghongensis')}

TYPO={'guizhouersis':'guizhouensis','yaxianensi':'yaxianensis','changtaiemsis':'changtaiensis',
      'jangtsekingensis':'jangtsekiangensis','anadalei':'annandalei','cochearus':'cochlearus',
      'formosarus':'formosanus','guizhouersisi':'guizhouensis'}

HEAD_NOISE=re.compile(r'\s*\d{3}\s*[.．]\s*[\u4e00-\u9fa5]{2,12}\s*[A-Z][a-z]{2,}')
MARKS=re.compile(r'[①②③④⑤⑥⑦⑧⑨⑩]')
NAME_TAIL=re.compile(r'[\u4e00-\u9fa5]{1,10}(?:白蚁|白蟻|白蚊|白蛟|白蛇)(?:亚属)?(?:属|科|腐|嵩|羁|羈|漏|蟻)?\s*$')
LAT_TAIL3=re.compile(r'(?<=[\u4e00-\u9fa5])\s*[A-Z]\s*$')
LATTERM=re.compile(r'[A-Za-z]\s*[.．]\s*(?:[(（〔\[][^)）〕\]｝}]{0,30}[)）〕\]｝}]\s*)?[a-zà-ÿł]{2,}(?:\s+[a-zà-ÿł]{1,})?')
LATFULL=re.compile(r'[A-Z][a-zà-ÿł]{3,}\s+[a-zà-ÿł]{2,}')
LAT_RUN=re.compile(r"[A-Z][a-zà-ÿ]{2,}(?:\s+[a-zà-ÿ]+)*")
LAT_TAIL2=re.compile(r"[A-Z]\s*[.．]\s*[a-zà-ÿ]{1,}(?:\s+[a-zà-ÿ]{1,})?\s*[.。]?\s*$")

OCR=[('上频','上颚'),('上颗','上颚'),('上嚬','上颚'),('后须','后颏'),('前须','前颏'),
     ('岗孔','囟孔'),('囱','囟'),('凹人','凹入'),('乳白蚊','乳白蚁'),('白蚊','白蚁'),
     ('白蛟','白蚁'),('白蛇','白蚁'),('钝频','钝颚'),('后频','后颏'),('前频','前颏'),
     ('前缘有无深凹陷','前缘无深凹陷'),('频基','颏基')]

def clean(s):
    s=res.clean_text(s)
    s=re.sub(r'[…⋯]+',' ',s)
    s=re.sub(r'\.{2,}',' ',s)
    s=re.sub(r'·{2,}',' ',s)
    for a,b in OCR: s=s.replace(a,b)
    s=re.sub(r'(?<=[\u4e00-\u9fa5])([A-Z][a-zà-ÿ]{2,})',r' \1',s)
    s=re.sub(r'([A-Z][a-zà-ÿ]{2,})(?=[\u4e00-\u9fa5])',r'\1 ',s)
    s=re.sub(r'[，,、；;]\s*$','',s)
    s=re.sub(r'(?<=\d)\s*一\s*(?=\d)','—',s)
    s=re.sub(r'\s{2,}',' ',s)
    return s.strip()

def _cut_suffix(s, z):
    """remove the trailing occurrence of z (ignoring spaces inside s)"""
    s2=s.rstrip()
    compact=s2.replace(' ','')
    if not compact.endswith(z): return None
    need=len(z); i=len(s2); cnt=0
    while i>0 and cnt<need:
        i-=1
        if s2[i].strip(): cnt+=1
    return s2[:i]

def _cut_chars(s, n):
    s2=s.rstrip(); i=len(s2); cnt=0
    while i>0 and cnt<n:
        i-=1
        if s2[i].strip(): cnt+=1
    return s2[:i]

def strip_terminal(t, names, kind='species'):
    s=t.rstrip()
    for a,b in OCR: s=s.replace(a,b)
    for _ in range(3):
        s=res.TAIL_LAT.sub('',s)
        s=LAT_TAIL2.sub('',s)
        s=LAT_TAIL3.sub('',s)
        s=re.sub(r'[\s.．,，、·…—\-]+$','',s)
    s=drop_latin_tail(s)
    done=False
    for nm in names:
        z=re.sub(r'\s','',nm or '')
        if len(z)<2: continue
        got=_cut_suffix(s,z)
        if got is not None: s=got; done=True; break
    if not done:
        m=NAME_TAIL.search(s)
        if m: s=s[:m.start()]; done=True
    if not done and kind in ('genus','family'):
        comp=s.rstrip().replace(' ',''); best=0
        for nm in names:
            z=re.sub(r'\s','',nm or '')
            if len(z)<2: continue
            for k in range(min(len(z),10),0,-1):
                if comp.endswith(z[:k]):
                    best=max(best,k); break
        if best: s=_cut_chars(s,best)
    if kind in ('genus','family'):
        s=re.sub(r'[\u4e00-\u9fa5]{0,3}(?:属|科|腐|嵩|羁|羈|漏)\s*$','',s)
    s=re.sub(r'[\s.．,·…—]+$','',s)
    s=re.sub(r'[，,、；;]\s*$','',s)
    return s.strip()

def drop_latin_tail(s):
    idx=max((i for i,c in enumerate(s) if '\u4e00'<=c<='\u9fa5'), default=-1)
    if idx<0: return s
    tail=s[idx+1:]
    if not re.search(r'[A-Za-z]',tail): return s
    if re.fullmatch(r'\s*(mm|cm|m|μm|um|in|%)\s*[.。]?\s*',tail): return s
    if len(tail)>45: return s
    return s[:idx+1]
def split_merged(raw):
    """split a physical unit that swallowed the next lead at each embedded latin terminal"""
    raw=re.sub(r'[\u2080-\u2089]','',raw)
    out=[]; start=0
    for rx in (LATTERM, LATFULL):
        for m in rx.finditer(raw):
            pre=raw[max(0,m.start()-14):m.start()]
            if not pre: continue
            if not re.search(r'[\u4e00-\u9fa5]\s*$',pre): continue
            if not re.search(r'[\u4e00-\u9fa5]', raw[m.end():m.end()+6]): continue
            if m.end()<=start: continue
            out.append(raw[start:m.end()]); start=m.end()
    out.append(raw[start:])
    segs=[x if i==0 else re.sub(r'^[\s\d、,，.]+','',x) for i,x in enumerate(out)]
    return [x for x in segs if x.strip()]
def res_genus(pay, kg):
    g=(pay.get('genus_raw') or '').strip()
    epi=(pay.get('epi') or '').strip()
    if len(g)>1 and re.search(r'\s', g): g=re.sub(r'\s+','',g)
    if len(g)==1 and epi: g=g+epi
    if len(g)>1:
        gl=g.lower()
        if gl in LAT2G: return GEN[LAT2G[gl]]
        if gl in MAPPING_LAT: return GEN[MAPPING_LAT[gl]]
        for k,v in LAT2G.items():
            if res.lev(k,gl)<=1: return GEN[v]
        for k,v in MAPPING_LAT.items():
            if res.lev(k,gl)<=1: return GEN[v]
    zh=pay.get('zh')
    if zh:
        z=re.sub(r'\s','',zh).replace('蚊','蚁')
        for suf in ('属','腐','嵩','羁','羈','漏','嵩属'):
            if z.endswith(suf) and (z[:-1]+'属') in ZH2G: return GEN[ZH2G[z[:-1]+'属']]
        if z in ZH2G: return GEN[ZH2G[z]]
    return None

def leaf_species(pay, kg):
    g=(pay.get('genus_raw') or '').strip(); epi=(pay.get('epi') or '').strip()
    if len(g)>1 and re.search(r'\s', g): g=re.sub(r'\s+','',g)
    if len(g)>1 and g.lower() in MAPPING_LAT:
        sp=res.res_species({'genus_raw':GEN[MAPPING_LAT[g.lower()]]['latin'],'epi':epi,'zh':pay.get('zh')}, MAPPING_LAT[g.lower()])
        if sp: return {'kind':'species','zh':sp['zh'],'latin':sp['latin'],'url':sp['url']}
    sp=res.res_species({'genus_raw':g,'epi':epi,'zh':pay.get('zh')}, kg)
    if sp: return {'kind':'species','zh':sp['zh'],'latin':sp['latin'],'url':sp['url']}
    return None

def leaf_generic(pay, kind, kg):
    if kind=='genus':
        g=res_genus(pay, kg)
        if g: return {'kind':'genus','zh':g['zh'],'latin':g['latin'],'url':'/genus/%s/'%g['id']}
        return None
    if kind=='family':
        g=(pay.get('genus_raw') or ''); gl=g.lower(); fid=None
        if gl in FAM_LAT: fid=FAM_LAT[gl]
        if not fid:
            for k,v in FAM_LAT.items():
                if len(gl)>5 and res.lev(k,gl)<=2: fid=v; break
        if not fid:
            zh=pay.get('zh') or ''
            z=re.sub(r'\s','',zh).replace('蚊','蚁')
            if z.endswith('科') and z in FAM_ZH: fid=FAM_ZH[z]
            if not fid and z.endswith('腐') and (z[:-1]+'科') in FAM_ZH: fid=FAM_ZH[z[:-1]+'科']
        if not fid: return None
        f=res.FAM[fid]
        return {'kind':'family','zh':f['zh'],'latin':f['latin'],'url':'/family/%s/'%fid}
    return None

def fix_dropped(items, base=None):
    out=[]; seen=set()
    for d in items:
        zh=re.sub(r'\s+','',d.get('zh') or '').replace('蚊','蚁')
        for _p in ('节','形','个','宽','长','头','深','体'):
            if zh.startswith(_p) and zh.endswith('白蚁') and len(zh)>=5:
                zh=zh[1:]; break
        lat=(d.get('latin') or '').strip()
        ov=(DROPOVR.get(lat.lower()) or DROPOVR.get(re.sub(r'\s+','',lat.lower()))
            or DROPOVR.get(zh.lower()))
        if ov:
            zh,lat=ov
        else:
            if zh and not re.search(r'[\u4e00-\u9fa5]', zh):
                lat=lat or zh; zh=''
            if lat and base:
                m=re.match(r'^([A-Z])[.．]\s*(.+)$', lat) or re.match(r'^([A-Z])\s+(.+)$', lat)
                if m: lat=base+' '+m.group(2)
                elif not re.match(r'^[A-Z][a-zà-ÿ]', lat): lat=base+' '+lat
            lat=re.sub(r'\s+',' ',lat).strip()
        if lat:
            parts=lat.split(' '); epi=parts[-1].lower()
            if epi in TYPO: parts[-1]=TYPO[epi]; lat=' '.join(parts)
        key=(zh,lat)
        if not (zh or lat) or key in seen: continue
        seen.add(key); out.append({'zh':zh,'latin':lat})
    return out

def map_note(spec):
    idx,kind,page,kg,bzh,blat=spec
    if not kg: return None
    site=GEN.get(kg)
    if not site: return None
    base=re.split(r'[\s(]', blat)[0]
    if base.lower()!=site['latin'].lower():
        return ('原书把这一群放在 %s（%s）名下，本站现归入 %s（%s）；表中各种按本站的现行归属链接。'
                % (bzh, blat, site['zh'], site['latin']))
    zb=re.sub(r'(亚属|属)$','',bzh)
    if '亚属' not in bzh and zb+'属'!=site['zh']:
        return '原书中文名作 %s，本站作 %s（拉丁名相同）。' % (bzh, site['zh'])
    return None

def title_of(spec, ovr_title=None):
    kind,bzh=spec[1],spec[4]
    if kind=='family': return '等翅目科的检索表'
    sp=' ' if re.search(r'[A-Za-z]$', bzh) else ''
    if kind=='genus': return bzh+sp+'分属检索表'
    b=ovr_title or bzh
    return b+(' ' if re.search(r'[A-Za-z]$', b) else '')+'分种检索表'

cache={}
def parse_all():
    if cache: return cache
    for (h,e) in kp.blocks():
        cache[kp.lines[h].strip()]=kp.parse_block(h,e)
    return cache

def named_leaf(tgt):
    if not tgt: return None
    if tgt.startswith('sp:'):
        s=SLUG.get(tgt[3:])
        return {'kind':'species','zh':s['zh'],'latin':s['latin'],'url':s['url']} if s else None
    if tgt.startswith('gen:'):
        parts=tgt.split('+')
        out=[]
        for part in parts:
            gid=part[4:]
            note=''
            if '|' in gid:
                gid,note=gid.split('|',1)
            g=GEN.get(gid)
            if not g: return None
            lf={'kind':'genus','zh':g['zh'],'latin':g['latin'],'url':'/genus/%s/'%g['id']}
            if note: lf['note']=note
            out.append(lf)
        leaf=out[0]
        if len(out)>1: leaf['also']=out[1:]
        return leaf
    if tgt.startswith('fos:'):
        lat=tgt[4:]
        return {'kind':'fossil','latin':lat}
    if tgt.startswith('fam:'):
        f=res.FAM.get(tgt[4:])
        if not f: return None
        lat=f['latin']
        if lat.isupper(): lat=lat.capitalize()
        return {'kind':'family','zh':f['zh'],'latin':lat,'url':'/family/%s/'%f['id']}
    if tgt.startswith('sub:'):
        s=SUB.get(tgt[4:])
        return {'kind':'subfamily','zh':s['zh'],'latin':s['latin'],'url':'/subfamily/%s/'%s['id']} if s else None
    return None

def flatten(root, spec):
    flat=[]; ctr=[0]
    def walk(node, depth):
        if 'leaf' in node: return
        ctr[0]+=1; node['num']=ctr[0]
        flat.append((node,depth))
        for l in node['leads']:
            if 'child' in l: walk(l['child'], depth+1)
    walk(root,0)
    out=[]
    for node,depth in flat:
        ls=[]
        for l in node['leads']:
            o={'t':l['text']}
            if 'leaf' in l: o['leaf']=l['leaf']
            else: o['to']=l['child']['num']
            ls.append(o)
        out.append({'n':node['num'],'d':depth,'leads':ls})
    return out

def count_leaves(couplets):
    return sum(1 for c in couplets for l in c['leads'] if 'leaf' in l)

def key_from_ovr(spec, caste, couplets, dropped):
    nodes={n:leads for n,leads in couplets}
    def build(n, path):
        if n not in nodes or n in path: return None
        path=path|{n}
        leads=[]
        for txt,tgt in nodes[n]:
            if tgt and tgt.startswith('to:'):
                ch=build(int(tgt[3:]), path)
                if ch is None: continue
                leads.append({'text':clean(txt),'child':ch})
            else:
                lf=named_leaf(tgt)
                if lf is None:
                    slug=tgt[3:] if tgt and tgt.startswith('sp:') else ''
                    zh,lat=DROPNAME.get(slug,(slug.replace('-',' '),''))
                    dropped.append({'zh':zh,'latin':lat})
                    continue
                leads.append({'text':clean(txt),'leaf':lf})
        if not leads: return None
        if len(leads)==1 and 'child' in leads[0]: return leads[0]['child']
        return {'n':n,'leads':leads}
    root=build(1,set())
    if root is None: return None
    return flatten(root, spec)

def analyze(spec):
    idx,kind,page,kg,bzh,blat=spec
    if kind=='species' and kg: page='/genus/%s/'%kg
    keys=[]; omitted=[]
    ttl=title_of(spec, OVR[idx][0] if idx in OVR else None)
    if idx in OVR:
        for caste,cps in OVR[idx][1]:
            dropped=[]
            cs=key_from_ovr(spec, caste, cps, dropped)
            if not cs: continue
            nl=count_leaves(cs)
            if nl<2:
                omitted.append({'title':ttl+'（'+caste+'）','reason':'剔除本站未收录的种后仅剩 %d 个终点，故不列检索表'%nl})
                continue
            kk={'title':ttl,'caste':caste,'couplets':cs,'dropped':dropped,'n_leaves':nl}
            if idx==0:
                kk['note']=FAMNOTE; kk['source']=ORDSRC; kk['src_short']=HELSHORT
            if idx==3: kk['note']=NEONOTE
            keys.append(kk)
    else:
        parse_all()
        hit=[t for t in cache if t.startswith(TITLEHINT[idx])]
        if not hit: return None
        for sec in cache[hit[0]]:
            nodes={}
            for c in sec['couplets']:
                nodes.setdefault(c['n'],[]).extend(c['leads'])
            dropped=[]
            def parts_of(raw):
                if kind in ('genus','family') and MARKS.search(raw):
                    p=[x for x in MARKS.split(raw) if len(x.strip())>6]
                    if len(p)>1: return p
                return [raw]
            def leaf_of_lead(t):
                t=re.sub(r'[\u2080-\u2089]','',t).replace('ł','l')
                m=HEAD_NOISE.search(t)
                if m: t=t[:m.start()]
                f=_find_end(t,400)
                if not f: return None
                if f[0]=='target':
                    return ('to', f[1]['next'], clean(f[1]['prefix']))
                pay=f[1]
                g=(pay.get('genus_raw') or '').strip(); epi=(pay.get('epi') or '').strip()
                if len(g)==1 and epi and g.isupper() and kind in ('genus','family'):
                    pay=dict(pay); pay['genus_raw']=g+epi; pay['epi']=''
                lf=None
                if kind=='species': lf=leaf_species(pay,kg)
                elif kind in ('genus','family'): lf=leaf_generic(pay,kind,kg)
                nm=(pay.get('zh') or '').strip()
                if lf is None:
                    lat=(g+(' '+epi if epi else '')).strip()
                    if len(nm)>=3 or lat:
                        if len(nm)<3: nm=''
                        dropped.append({'zh':nm,'latin':lat})
                    return None
                body=strip_terminal(t,[lf['zh']],kind)
                return ('leaf', lf, clean(body))
            def build(n, path):
                if n not in nodes or n in path: return None
                p=path|{n}
                leads=[]
                for raw in nodes[n]:
                    for part in parts_of(raw):
                        for seg in split_merged(part):
                            r=leaf_of_lead(seg.strip())
                            if not r: continue
                            if r[0]=='to':
                                ch=build(r[1], p)
                                if ch is None: continue
                                leads.append({'text':r[2],'child':ch})
                            else:
                                leads.append({'text':r[2],'leaf':r[1]})
                if not leads: return None
                if len(leads)==1 and 'child' in leads[0]: return leads[0]['child']
                return {'n':n,'leads':leads}
            root=build(1,set())
            if root is None: continue
            out=flatten(root, spec)
            nl=count_leaves(out)
            if nl<2:
                omitted.append({'title':ttl+'（'+(sec['caste'] or '兵蚁')+'）',
                                'reason':'剔除本站未收录的种后仅剩 %d 个终点'%nl})
                continue
            keys.append({'title':ttl,'caste':sec['caste'] or '兵蚁','couplets':out,
                         'dropped':dropped,'n_leaves':nl})
    return {'idx':idx,'page':page,'kind':kind,'title':ttl,'book_zh':bzh,'book_lat':blat,
            'site_genus':kg,'keys':keys,'omitted':omitted}

# --- Termitidae subfamily index, translated from the phylogenetic supplement ---
SUBFAM=[
 (1,[('工蚁肠道：无混合段；中肠发达（长度与直径均显著），背观可原位透见；中肠与后肠连接处具 4 叶（部分种不明显）；无马氏管结或假马氏管结','to:2'),
     ('工蚁肠道：混合段有或无；胃与结肠（P3—P4）连接处无明显向后刚毛；具马氏管结或假马氏管结','to:3')]),
 (2,[('成虫/工蚁：上唇具深色硬化横带；左上颚第三缘齿（LMt3）前缘长度不及后缘的 2 倍','sub:macrotermitinae'),
     ('成虫/工蚁：上唇无深色硬化横带；LMt3 前缘长度为后缘的 2 倍或更多；工蚁肠道 P3—P4 连接处有明显的向后刚毛','sub:sphaerotermitinae')]),
 (3,[('工蚁肠道：P3b 背方突出部形成 2 个环，自中部离开盘曲；具假马氏管结；无混合段；肠瓣（P2）无刺','sub:foraminitermitinae'),
     ('工蚁肠道：P3b 背方突出部直立向后或形成单一环，沿中肠边缘离开盘曲；具马氏管结；混合段有或无；肠瓣（P2）有刺或无刺','to:4')]),
 (4,[('工蚁肠道：砂囊无柱状带（退化型）；无混合段；回肠（P1）圆筒形，沿腹部左侧作延长的 S 形走行；肠瓣（P2）由 6 个光滑的长垫组成，每垫端部具 1 刺','sub:engelitermitinae'),
     ('工蚁肠道：砂囊具柱状带（普通型）或不具（退化型）；混合段有或无；P1 形状多变；肠瓣（P2）形态多变','to:5')]),
 (5,[('成虫/工蚁：左上颚第三缘齿（LMt3）与愈合的第一、第二缘齿（LMt1+2）之间无明显缺刻或凹陷；成虫囟呈裂缝状、卵形或圆形；工蚁肠道混合段（若存在）位于中肠弧盘曲之外','to:6'),
     ('成虫/工蚁：LMt3 与 LMt1+2 之间具明显缺刻或凹陷；成虫囟非裂缝状，不明显或呈卵形、圆形；工蚁肠道混合段（若存在）位于中肠弧盘曲之内','sub:apicotermitinae')]),
 (6,[('工蚁肠道：胃（P3）具盲突或盲囊（兵蚁与成虫亦有）','to:7'),
     ('工蚁肠道：胃（P3）无盲突或盲囊','to:8')]),
 (7,[('工蚁肠道：砂囊无柱状带（退化型）；盲囊位于腹面；P1 膨大；肠瓣装置由 6 个长垫与 6 个较小的中间垫组成，装置较弱；通常具马氏管小结（埃塞俄比亚区分布）','sub:cubitermitinae'),
     ('工蚁肠道：砂囊具柱状带（普通型）；右侧观盲囊见于 P3 突出部；P1 管状；肠瓣装置由 6 个垫组成，无中间垫（新热带区分布）','sub:crepititermitinae')]),
 (8,[('工蚁肠道：双重混合段有或无；兵蚁（总存在）：囟孔位于额突顶端或象鼻末端','to:9'),
     ('工蚁肠道：无双重混合段；兵蚁（罕见缺失）：囟位于头前部或额突基部（具额突者）','to:10')]),
 (9,[('工蚁肠道：双重混合段有或无；回肠（P1）扩张。兵蚁：囟宽，上颚具功能（新热带区分布）','sub:syntermitinae'),
     ('工蚁肠道：无双重混合段；回肠（P1）管状。兵蚁：囟狭窄，上颚退化（世界性分布）','sub:nasutitermitinae')]),
 (10,[('工蚁肠道：P1 管状而长，在 P5 腹面形成一环；P1 于腹部右侧插入 P3。工蚁上颚：臼齿区总具脊','to:11'),
      ('工蚁肠道：P1 形状多变（管状或膨大），无腹面环；P1 于 P3 的插入位置多变；肠瓣位于腹部右侧或左侧。工蚁上颚：臼齿区具脊或不具脊','to:12')]),
 (11,[('成虫/工蚁：右上颚第一缘齿（RMt1）基部无副齿，第二缘齿（RMt2）不如下述。兵蚁：存在。工蚁肠道：P1 于 P3 背方插入（埃塞俄比亚区与新热带区）','sub:cylindrotermitinae'),
      ('成虫/工蚁：RMt1 基部具副齿，RMt2 发达，前缘成角、后缘弯曲。兵蚁：缺。工蚁肠道：P1 于 P3 腹后部插入（东洋区分布）','sub:protohamitermitinae')]),
 (12,[('工蚁肠道：通常具马氏管小结，位于中肠弧内侧、马氏管插入处。兵蚁：额突发达或极度退化','sub:termitinae'),
      ('工蚁肠道：无马氏管小结（有时具壶腹）。兵蚁：形态多变','to:13')]),
 (13,[('工蚁肠道：P1（肠瓣位置）于腹部左侧插入 P3','to:14'),
      ('工蚁肠道：P1（肠瓣位置）于腹部右侧插入 P3','to:15')]),
 (14,[('工蚁肠道：无混合段。兵蚁上颚：不作弹击','sub:forficulitermitinae'),
      ('工蚁肠道：具混合段','to:16')]),
 (15,[('工蚁/兵蚁肠道：P1 膨大或管状。兵蚁上颚：咬碎、穿刺、切割或对称弹击（仅新热带区的属具对称弹击的上颚）；兵蚁头梨形，无额突（裸白蚁属 Eremotermes、齿刺白蚁属 Dentispicotermes 除外），上唇圆形或端部微尖','sub:amitermitinae'),
      ('工蚁/兵蚁肠道：P1 始终膨大。兵蚁：上颚对称弹击，头具显著额瘤或额突；上唇分叉','sub:promirotermitinae')]),
 (16,[('工蚁肠道：混合段与回肠（P1）连接处收缩并向腹面折曲，与向前的顶点成锐角。成虫/工蚁：RMt2 向前，后缘延长；臼齿区具脊','to:17'),
      ('工蚁肠道：混合段与回肠（P1）连接处成弓形。兵蚁：不对称弹击。成虫/工蚁：RMt2 两缘近等长，后缘微凹；臼齿区光滑或脊极退化（澳大利亚区、非洲热带区、古北区（中日）、巴布亚区）','sub:mirocapritermitinae')]),
 (17,[('兵蚁上颚：穿刺（Onkotermes，新热带区）或切割（小锯白蚁属 Microcerotermes，澳大利亚区、巴布亚区、东洋区、埃塞俄比亚区与新热带区）','sub:microcerotermitinae'),
      ('兵蚁上颚：不对称或近对称弹击（新热带区分布）','sub:neocapritermitinae')]),
]

def subfamily_key():
    dropped=[]
    cs=key_from_ovr({'page':'/family/termitidae/'}, '工蚁与兵蚁', SUBFAM, dropped)
    return {'title':'白蚁科亚科检索表','caste':'工蚁与兵蚁','couplets':cs,'dropped':dropped,
            'n_leaves':count_leaves(cs),
            'source':SFSRC, 'src_short':HELSHORT,
            'note':'以工蚁肠道解剖与上颚齿序为主，覆盖现存等翅目全部 18 个亚科，与原书（2000）按兵蚁、有翅成虫形态划分的亚科系统不完全一致；各终点链接到本站对应的亚科页面。',
            'n_subfamilies':18}

def kalotermes_world_keys():
    """木白蚁科世界分属检索表（Krishna et al. 2013），两套：有翅成虫、兵蚁。"""
    keys=[]
    ttl_base=KALO_WORLD[0]
    for caste,cps in KALO_WORLD[1]:
        dropped=[]
        cs=key_from_ovr({'page':'/family/kalotermitidae/'}, caste, cps, dropped)
        if not cs: continue
        keys.append({'title':ttl_base,'caste':caste,'couplets':cs,'dropped':dropped,
                     'n_leaves':count_leaves(cs),'note':KALONOTE,
                     'source':KALOSRC,'src_short':KRISHNASHORT})
    return keys

if __name__=='__main__':
    pages={}
    report=[]
    for spec in SPEC:
        a=analyze(spec)
        if a is None:
            report.append((spec[0],spec[4],'NO-TITLE',0,0,0)); continue
        entry=pages.setdefault(a['page'],{'keys':[],'omitted':[]})
        for k in a['keys']:
            if not k['couplets']: continue
            k['site_genus']=('/genus/%s/'%a['site_genus']) if a['site_genus'] else None
            k['book_genus']='%s %s'%(a['book_zh'],a['book_lat'])
            k.setdefault('source',BOOKSRC)
            k.setdefault('src_short',BOOKSHORT)
            base=re.split(r'[\s(]', a['book_lat'])[0] if a['kind']=='species' else None
            k['dropped']=fix_dropped(k.get('dropped') or [], base)
            if not k.get('note'):
                mn=map_note(spec)
                if mn: k['note']=mn
            entry['keys'].append(k)
        entry['omitted'].extend(a['omitted'])
        for s in SKIP:
            if s==spec[0]:
                entry['omitted'].append({'title':title_of(spec),'reason':SKIP[s]})
        for k in a['keys']:
            report.append((spec[0],a['title'],k['caste'],len(k['couplets']),k['n_leaves'],len(k['dropped'])))
    for s,(pg0,name0) in SKIPPAGE.items():
        e0=pages.setdefault(pg0,{'keys':[],'omitted':[]})
        sp0=' ' if re.search(r'[A-Za-z]$', name0) else ''
        e0['omitted'].append({'title':name0+sp0+'分种检索表','reason':SKIP[s]})
    sf=subfamily_key()
    ent=pages.setdefault('/family/termitidae/',{'keys':[],'omitted':[]})
    ent['keys'].insert(0,sf)
    # 木白蚁科：中国动物志分属表之后，接 Krishna et al. (2013) 世界分属表（有翅成虫、兵蚁）
    kent=pages.setdefault('/family/kalotermitidae/',{'keys':[],'omitted':[]})
    kent['keys'].extend(kalotermes_world_keys())
    # order: subfamily index first, then genus keys
    for pg,v in pages.items():
        v['keys']=[k for k in v['keys'] if k.get('couplets')]
    # 2025-11: 中国动物志（黄复生等, 2000）的检索表已从站点撤下。
    # 该书的表无法据以整理出整套可靠的形态学检索表；只保留 Hellemans et al. (2024)
    # 的目级/白蚁科亚科表与 Krishna et al. (2013) 的木白蚁科世界分属表。
    # 此处的过滤是硬约束：重新运行本脚本也不会把书表写回 _data/fauna_keys.json。
    for pg,v in list(pages.items()):
        v['keys']=[k for k in v['keys'] if BOOKSHORT not in (k.get('src_short') or '')]
        # 现有 omitted 条目都是书表未转述的说明，随书表一并撤下。
        v['omitted']=[]
    for pg,v in pages.items():
        v['n_keys']=len(v['keys'])
        v['n_couplets']=sum(len(k['couplets']) for k in v['keys'])
        v['n_leaves']=sum(k['n_leaves'] for k in v['keys'])
    pages={p:v for p,v in pages.items() if v['n_keys']}
    json.dump(pages, open('_data/fauna_keys.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in report:
        print('%02d %-22s %-8s c=%-3d l=%-3d drop=%d'%(r[0],r[1][:22],r[2],r[3],r[4],r[5]))
    print('pages',len(pages),'keys',sum(v['n_keys'] for v in pages.values()),
          'couplets',sum(v['n_couplets'] for v in pages.values()),
          'leaves',sum(v['n_leaves'] for v in pages.values()))
    for pg,v in pages.items():
        print(pg,'keys',v['n_keys'],'cp',v['n_couplets'],'lf',v['n_leaves'],'omit',len(v['omitted']))
