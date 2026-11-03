# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.tmp/keys')
import kp
want=['壤白蚊属','球白蚊属分种','马扭白蚁属','须白蚊属','葫白蚁属','歧颚白蚊属','近瓢白蚊属','夏氏白蚁属']
for (h,e) in kp.blocks():
    t=kp.lines[h].strip()
    if any(w in t for w in want):
        print('#####',t,'lines',h,e)
        for i in range(h,e+1):
            s=kp.lines[i].rstrip()
            if s.strip(): print('%5d %s'%(i,s))
