p='.tmp/keys/kp.py'
s=open(p,encoding='utf-8').read()
s=s.replace("\\\\s*([A-Za-z])\\\\s*[.．,，]?\\\\s*(?:[（(〔\\\\[]","\\\\s*([A-Z])\\\\s*[.．,，]?\\\\s*(?:[（(〔\\\\[]")
open(p,'w',encoding='utf-8').write(s)
