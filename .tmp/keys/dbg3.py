# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0,'.tmp/keys')
import res
for g in ['hypotermes','globitermes','procapritermes','hospitalitermes','cucurbitermes','nasutitermes','ahmaditermes','xiaitermes','microtermes','reticulitermes']:
    sps=res.SP
    lst=sorted([s for (gg,e),s in sps.items() if gg==g], key=lambda s:s['latin'])
    print('##',g,len(lst))
    for s in lst: print('   ',s['slug'],'|',s['zh'],'|',s['latin'])
