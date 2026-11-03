import re, json
lines=open('.tmp/keys/raw.txt',encoding='utf-8').read().split('\n')
heads=[i for i,l in enumerate(lines) if re.search(r'检索表',l) and not re.search(r'^而一个地区性|^关于乳白蚁',l)]
def is_stop(l, first=False):
    s=l.strip()
    if not s: return False
    if s.startswith('=====CHUNK'): return True
    if '检索表' in s: return True
    if re.match(r'^[（(][一二三四五六七八九十]+[）)]', s): return True
    if re.match(r'^[一二三四五六七八九十]{1,3}\s*、', s): return True
    if re.match(r'^\d{1,3}\s*[.．、]\s*[\u4e00-\u9fa5]{2,12}\s+[A-Z][a-z]', s): return True
    if re.match(r'^图\s*\d+', s): return True
    if re.match(r'^(分布|寄主|生活习性|量度|生物学|经济意义)', s): return True
    if re.match(r'^\d{1,4}$', s): return True
    return False
blocks=[]
for k,h in enumerate(heads):
    end=len(lines)
    for j in range(h+1, len(lines)):
        if is_stop(lines[j]):
            end=j; break
    blocks.append((h,end))
for (h,e) in blocks:
    print(h,e,e-h-1, '|', lines[h].strip()[:40])
    print('   tail:', ' // '.join(x.strip()[:30] for x in lines[e-3:e]))
