# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.tmp/keys')
import res
for g,q in [('nasutitermes',['communis','orthonasus','mironasutitermes']),('ahmaditermes',['parafulvus','jinghongensis','dinghuensis','peribulbitermes']),('xiaitermes',['yinxianensis','tiantaiensis']),('reticulitermes',['tsaitermes'])]:
    print('##',g)
    for (gg,e),s in res.SP.items():
        if gg==g and any(x in s['latin'] for x in q): print('   ',s['slug'],'|',s['zh'],'|',s['latin'])
# also print all ahmaditermes and xiaitermes for context
for g in ['ahmaditermes','xiaitermes','cucurbitermes','microtermes']:
    print('## all',g)
    for (gg,e),s in sorted(res.SP.items(), key=lambda kv:kv[1]['latin']):
        if gg==g: print('   ',s['slug'],'|',s['zh'],'|',s['latin'])
