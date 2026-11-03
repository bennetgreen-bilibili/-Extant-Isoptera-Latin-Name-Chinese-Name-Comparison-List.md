
import json, collections
w = json.load(open(".tmp/dz/work.json", encoding="utf-8"))
c = collections.Counter(o["page_url"] for o in w)
dups = [k for k,v in c.items() if v>1]
for k in dups:
    for o in w:
        if o["page_url"]==k:
            print(k, "| book_n", o["book_n"], "| via", o["via"], "| book", o["book_zh"], o["book_latin"], "| page", o["page_latin"], o["page_zh"])
    print("---")
