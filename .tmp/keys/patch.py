import sys,re; sys.path.insert(0,'.tmp/keys')
p='.tmp/keys/k3.py'
s=open(p,encoding='utf-8').read()
old = s[s.index("LATIN_TAIL="):s.index("def ends_unit")]
new = '''LAT_OK=re.compile(r'[\\sA-Za-z0-9.\\uff0e,\\u3001()\\uff08\\uff09\\u00b7\\u2014\\-\\u00b0\\u2032\\u2033]{0,40}$')
def tail_taxon(t):
    t=t.rstrip()
    hits=find_terms(t)
    for hit in reversed(hits):
        suf=t[hit[1]:]
        if len(suf)<=40 and not re.search(r'[\\u4e00-\\u9fa5]', suf) and LAT_OK.match(suf):
            return hit
    return None

'''
s = s.replace(old, new)
open(p,'w',encoding='utf-8').write(s)
