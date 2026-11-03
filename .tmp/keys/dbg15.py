import re, json, sys
sys.path.insert(0,'.tmp/keys')
import kp
tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
from collections import defaultdict
EPI=defaultdict(list)
for gid,lst in sbg.items():
    if gid=='_meta': continue
    for sp in lst:
        epi=re.sub(r'[^a-z]','',sp['latin'].split()[-1].lower())
        EPI[epi].append((gid,sp))
targets={'蔡白蚁属分种检索表 兵    蚁','华白蚁羁分种检索表','77□□壤白蚊属分种检索表 兵    蚁','马扭白蚁属分种检索表 兵    蚁','歧颚白蚊属分种检索表 大  兵  蚁','近瓢白蚊属分种检索表','奇象白蚁属分种检索表'}
for (h,e) in kp.blocks():
    t=kp.lines[h].strip()
    if t not in targets: continue
    print('==',t)
    for sec in kp.parse_block(h,e):
        for c in sec['couplets']:
            for l in c['leads']:
                f=kp._find_end(l,200)
                if f and f[0]=='taxon':
                    pay=f[1]; epi=pay.get('epi') or ''
                    print('   ',repr(l[:70]),'| zh=',pay.get('zh'),'| g=',pay.get('genus_raw'),'| epi=',epi)
                    if epi in EPI: print('        EPI-HIT',[(g,s['zh'],s['latin']) for g,s in EPI[epi]][:4])
            # noop
