p='.tmp/keys/kp.py'
s=open(p,encoding='utf-8').read()
old="SPEC_TAIL=re.compile(r'([\\u4e00-\\u9fa5]{0,16}?)\\s*([A-Z])\\s*[.．,，]?\\s*(?:[（(]\\s*([A-Za-z0-9]{1,3})\\s*[)）]\\s*)?([a-z](?:\\s?[a-z]){2,24})\\s*[.。]?\\s*$')"
new="SPEC_TAIL=re.compile(r'([\\u4e00-\\u9fa5]{0,16}?)\\s*([A-Z])\\s*[.．,，]?\\s*(?:[（(]\\s*([A-Za-z0-9]{1,3})\\s*[.．]?\\s*[)）]\\s*)?([a-z](?:\\s?[a-z]){2,24})\\s*[.。]?\\s*$')"
assert old in s
s=s.replace(old,new)
open(p,'w',encoding='utf-8').write(s)
