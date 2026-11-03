import sys
sys.path.insert(0,'.tmp/keys')
import kp
lines=kp.lines
want=['77□□壤白蚊属分种检索表 兵    蚁','葫芦'.replace('芦','白')+'蚁属分种检索表','歧颚白蚊属分种检索表 大  兵  蚁','近瓢白蚊属分种检索表','夏氏白蚁属分种检索表','华白蚁羁分种检索表','球白蚊属分种检索表','新白蚊属分种检索表','须白蚊属分种检索表 兵   蚁']
for (h,e) in kp.blocks():
    t=lines[h].strip()
    if t not in want: continue
    print('=====',t)
    for sec in kp.parse_block(h,e):
        print('  --caste',sec['caste'])
        for c in sec['couplets']:
            print('   c%d'%c['n'])
            for l in c['leads']:
                f=kp._find_end(l,200)
                tag = ('->%s'%f[1]['next']) if f and f[0]=='target' else ('LEAF:%s|%s'%(f[1].get('zh'),f[1].get('epi')) if f else 'OPEN')
                print('      [%s] %s' % (tag, l[:110]))
