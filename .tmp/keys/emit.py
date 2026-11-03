# -*- coding: utf-8 -*-
"""Emit _data/fauna_keys.json: dichotomous keys from 《中国动物志·等翅目》,
pruned to the species that still have a page on this site and renumbered."""
import re, json, sys
sys.path.insert(0,'.tmp/keys')
import kp
from kp import _find_end
import res

GEN=res.GEN; LAT2G=res.LAT2G; ZH2G=res.ZH2G; SP=res.SP
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
# (duplicated / missing lead numbers, or a second lead sharing one paragraph)
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

SKIP={3:'原文该检索表被 OCR 黏连成整段（种对无编号、终端丢失），无法可靠复原',
      5:'原文该检索表的种对与终端被拆分到相邻页面并夹入书眉噪音，无法可靠复原',
      33:'原书仅 2 种，其中天台夏氏白蚁 X. tiantaiensis 本站未收录，剔除后仅存 1 种，不成检索表'}

HEAD_NOISE=re.compile(r'\s*\d{3}\s*[.．]\s*[\u4e00-\u9fa5]{2,12}\s*[A-Z][a-z]{2,}')

def res_genus(pay, kg):
    g=(pay.get('genus_raw') or '').strip()
    epi=(pay.get('epi') or '').strip()
    if len(g)==1 and epi: g=g+epi
    if len(g)>1:
        gl=g.lower()
        if gl in LAT2G: return GEN[LAT2G[gl]]
        if gl in MAPPING_LAT: return GEN[MAPPING_LAT[gl]]
        for k,v in LAT2G.items():
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
    if len(g)>1 and g.lower() in MAPPING_LAT:
        sp=res.res_species({'genus_raw':GEN[MAPPING_LAT[g.lower()]]['latin'],'epi':epi,'zh':pay.get('zh')}, MAPPING_LAT[g.lower()])
        if sp: return {'zh':sp['zh'],'latin':sp['latin'],'url':sp['url']}
    sp=res.res_species({'genus_raw':g,'epi':epi,'zh':pay.get('zh')}, kg)
    if sp: return {'zh':sp['zh'],'latin':sp['latin'],'url':sp['url']}
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

def title_of(spec, ovr_title=None):
    kind,kg,bzh,blat=spec[1],spec[3],spec[4],spec[5]
    if kind=='family': return '等翅目科的检索表'
    if kind=='genus': return bzh+'分属检索表'
    base=ovr_title or bzh
    return base+'分种检索表'

cache={}
def parse_all():
    if cache: return cache
    for (h,e) in kp.blocks():
        cache[kp.lines[h].strip()]=kp.parse_block(h,e)
    return cache

def key_from_couplets(spec, caste, couplets, dropped):
    """couplets: [(n,[(text,target)])] -> rendered list with dfs numbering"""
    nodes={n:leads for n,leads in couplets}
    kg=spec[3]; kind=spec[1]
    def leaf_of(tgt):
        if tgt is None: return None
        if tgt.startswith('sp:'):
            s=SLUG.get(tgt[3:])
            return {'zh':s['zh'],'latin':s['latin'],'url':s['url']} if s else None
        if tgt.startswith('gen:'):
            g=GEN.get(tgt[4:])
            return {'kind':'genus','zh':g['zh'],'latin':g['latin'],'url':'/genus/%s/'%g['id']} if g else None
        return None
    def build(n, path):
        if n not in nodes: return None
        if n in path: return None
        path=path|{n}
        leads=[]
        for txt,tgt in nodes[n]:
            if tgt and tgt.startswith('to:'):
                ch=build(int(tgt[3:]), path)
                if ch is None: continue
                leads.append({'text':txt,'child':ch})
            else:
                lf=leaf_of(tgt)
                if lf is None:
                    dropped.append(txt)
                    continue
                leads.append({'text':txt,'leaf':lf})
        if not leads: return None
        if len(leads)==1 and 'child' in leads[0]: return leads[0]['child']
        return {'n':n,'leads':leads}
    root=build(1,set())
    if root is None: return None
    flat=[]; ctr=[0]
    def emit(node,depth):
        if 'leaf' in node: return
        ctr[0]+=1; node['num']=ctr[0]
        flat.append((node, depth))
        for l in node['leads']:
            if 'child' in l: emit(l['child'], depth+1)
    emit(root,0)
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

def analyze(spec):
    idx,kind,page,kg,bzh,blat=spec
    dropped=[]
    keys=[]
    if idx in OVR:
        _,caste_blocks=OVR[idx]
        ttl=title_of(spec, OVR[idx][0])
        for caste,cps in caste_blocks:
            cs=key_from_couplets(spec,caste,cps,dropped)
            if cs:
                keys.append({'title':ttl,'caste':caste,'couplets':cs,'dropped':[]})
    else:
        parse_all()
        hit=[t for t in cache if t.startswith(TITLEHINT[idx])]
        if not hit: return None
        ttl=title_of(spec)
        for sec in cache[hit[0]]:
            nodes={}
            for c in sec['couplets']:
                nodes.setdefault(c['n'],[]).extend(c['leads'])
            def build(n, path):
                if n not in nodes: return None
                if n in path: return None
                path=path|{n}
                leads=[]
                for raw in nodes[n]:
                    t=raw.strip()
                    m=HEAD_NOISE.search(t)
                    if m: t=t[:m.start()]
                    f=_find_end(t,400)
                    if not f: continue
                    if f[0]=='target':
                        ch=build(f[1]['next'], path)
                        if ch is None: continue
                        leads.append({'text':res.clean_text(f[1]['prefix']),'child':ch})
                        continue
                    pay=f[1]
                    g=(pay.get('genus_raw') or '').strip(); epi=(pay.get('epi') or '').strip()
                    if len(g)==1 and epi and g.isupper() and kind=='genus':
                        pay=dict(pay); pay['genus_raw']=g+epi; pay['epi']=''
                    body=res.clean_text(res.strip_taxon(t,pay))
                    lf=None
                    if kind=='species': lf=leaf_species(pay,kg)
                    elif kind in ('genus','family'): lf=leaf_generic(pay,kind,kg)
                    if lf is None:
                        nm=(pay.get('zh') or '').strip()
                        lat=(g+(' '+epi if epi else '')).strip()
                        if nm and nm not in ('属','科'): dropped.append((nm+' '+lat).strip())
                        continue
                    leads.append({'text':body,'leaf':lf})
                if not leads: return None
                if len(leads)==1 and 'child' in leads[0]: return leads[0]['child']
                return {'n':n,'leads':leads}
            root=build(1,set())
            if root is None: continue
            flat=[]; ctr=[0]
            def emit(node,depth):
                if 'leaf' in node: return
                ctr[0]+=1; node['num']=ctr[0]
                flat.append((node,depth))
                for l in node['leads']:
                    if 'child' in l: emit(l['child'],depth+1)
            emit(root,0)
            out=[]
            for node,depth in flat:
                ls=[]
                for l in node['leads']:
                    o={'t':l['text']}
                    if 'leaf' in l: o['leaf']=l['leaf']
                    else: o['to']=l['child']['num']
                    ls.append(o)
                out.append({'n':node['num'],'d':depth,'leads':ls})
            keys.append({'title':ttl,'caste':sec['caste'] or '兵蚁','couplets':out,'dropped':[]})
    # aggregate dropped per key later; simple: attach all to first key
    return {'idx':idx,'page':page,'kind':kind,'title':title_of(spec, OVR[idx][0] if idx in OVR else None),
            'book_zh':bzh,'book_lat':blat,'site_genus':kg,'keys':keys,'dropped':dropped}

if __name__=='__main__':
    pages={}
    report=[]
    for spec in SPEC:
        a=analyze(spec)
        if a is None:
            report.append((spec[0],spec[4],'NO-TITLE',0,0,0,[]))
            continue
        for k in a['keys']:
            nleaf=sum(1 for c in k['couplets'] for l in c['leads'] if 'leaf' in l)
            report.append((spec[0], a['title'], k['caste'], len(k['couplets']), nleaf, len(a['dropped']), []))
        if not a['keys']:
            report.append((spec[0], a['title'], '-', 0, 0, len(a['dropped']), []))
        entry=pages.setdefault(a['page'],{'keys':[]})
        for k in a['keys']:
            if not k['couplets']: continue
            entry['keys'].append({
              'title':k['title'],'caste':k['caste'],
              'site_genus':('/genus/%s/'%a['site_genus']) if a['site_genus'] else None,
              'book_genus':'%s %s'%(a['book_zh'],a['book_lat']),
              'couplets':k['couplets'],'dropped':a['dropped']})
    for pg,v in pages.items():
        v['keys']=[k for k in v['keys'] if len(k['couplets'])>0]
        v['n_keys']=len(v['keys'])
        v['n_couplets']=sum(len(k['couplets']) for k in v['keys'])
        v['n_leaves']=sum(1 for k in v['keys'] for c in k['couplets'] for l in c['leads'] if 'leaf' in l)
    json.dump(pages, open('_data/fauna_keys.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in report:
        print('%02d %-24s %-6s c=%-3d l=%-3d drop=%d'%(r[0],r[1][:24],r[2],r[3],r[4],r[5]))
    print('pages',len(pages),'keys',sum(v['n_keys'] for v in pages.values()),
          'couplets',sum(v['n_couplets'] for v in pages.values()),
          'leaves',sum(v['n_leaves'] for v in pages.values()))
    print('skipped',SKIP)
