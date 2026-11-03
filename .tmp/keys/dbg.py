# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0,'.tmp/keys')
import emit
emit.parse_all()
for i in [16,21,25,29,30,31,32,33]:
    a=emit.analyze([s for s in emit.SPEC if s[0]==i][0])
    if not a: print(i,'NO-TITLE'); continue
    for rep in a['reps']:
        print('=== %02d %s caste=%s couplets=%s'%(i,a['title'],rep['caste'],rep.get('couplets')))
        for e in rep.get('flat',[]):
            for l in e['leads']:
                print('  %2d d%d %s | %s'%(e['n'],e['d'],l['t'][:70], (l.get('leaf') or {}).get('latin') or ('->%s'%l.get('to'))))
        for u in rep['unres']: print('   UNRES',u)
        for d in rep['dead']: print('   DEAD',d)
