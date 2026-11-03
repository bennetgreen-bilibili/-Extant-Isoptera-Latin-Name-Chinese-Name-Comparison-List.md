# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.tmp/keys')
import emit
emit.parse_all()
for i in [0,1,4,7,8,10,11,12,13,14,17,22,27,28,35,36,37]:
    sp=[s for s in emit.SPEC if s[0]==i][0]
    a=emit.analyze(sp)
    if not a: print(i,'NO-TITLE'); continue
    for rep in a['reps']:
        if not rep['unres'] and not rep['dead'] and not rep['hoist']: continue
        print('=== %02d %s [%s]'%(i,a['title'][:34],rep['caste']))
        for u in rep['unres'][:14]: print('   U',u)
        for d in rep['dead'][:6]: print('   D',d)
        for h in rep['hoist'][:4]: print('   H',h)
