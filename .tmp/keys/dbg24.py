import sys
sys.path.insert(0,'.tmp/keys')
import kp
for i,(h,e) in enumerate(kp.blocks()):
    print('%02d  %-42s %d-%d' % (i, kp.lines[h].strip(), h, e))
