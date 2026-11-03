# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.tmp/keys')
import emit, kp, res
emit.parse_all()
t=[k for k in emit.cache if k.startswith('木白蚊科分属')][0]
secs=emit.cache[t]
for sec in secs:
    for c in sec['couplets']:
        for lead in c['leads']:
            f=kp._find_end(lead,400)
            print('LEAD n=%s'%c['n'], repr(lead[:60]))
            print('   find_end ->', f[0] if f else None, (f[1] if f else None))
            if f and f[0]=='taxon':
                print('   leaf_generic ->', emit.leaf_generic(f[1],'genus',None))
