import sys
sys.path.insert(0,'.tmp/keys')
import kp
lines=kp.lines
want=['葫白蚁属分种检索表','夏氏白蚁属分种检索表','马扭白蚁属分种检索表 兵    蚁','瘤白蚊属分种检索表 兵    蚁','印白蚁属分种检索表 兵   蚁','歧颚白蚊属分种检索表 大  兵  蚁','近瓢白蚊属分种检索表','华白蚁羁分种检索表','77□□壤白蚊属分种检索表 兵    蚁','球白蚊属分种检索表']
for (h,e) in kp.blocks():
    t=lines[h].strip()
    if t in want:
        print('=====',t,'lines',h,e)
        for i in range(h,min(e+1,h+40)):
            print(i, lines[i][:200])
