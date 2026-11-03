p='.tmp/keys/kp.py'
s=open(p,encoding='utf-8').read()
i=s.index("SPEC_TAIL=")
j=s.index("LAT_OK=")
new = """SPEC_TAIL=re.compile(r'([\\\\u4e00-\\\\u9fa5]{0,16}?)\\\\s*([A-Za-z])\\\\s*[.．,，]?\\\\s*(?:[（(〔\\\\[]\\\\s*([A-Za-z0-9]{1,3})\\\\s*[.．]?\\\\s*[)）〕\\\\]}]\\\\s*)?([a-zà-ÿł](?:\\\\s?[a-zà-ÿł]){2,24})\\\\s*[.。]?\\\\s*$')
"""
s = s[:i] + new + s[j:]
open(p,'w',encoding='utf-8').write(s)
