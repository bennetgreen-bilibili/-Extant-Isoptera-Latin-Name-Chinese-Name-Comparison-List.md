# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.tmp/keys')
import res
for g in ['coptotermes','pericapritermes','macrotermes','hospitalitermes','sinonasutitermes','pseudocapritermes','reticulitermes']:
    print('##',g)
    for (gg,e),s in sorted(res.SP.items(), key=lambda kv:kv[1]['latin']):
        if gg==g: print('   ',s['slug'],'|',s['zh'],'|',s['latin'])
