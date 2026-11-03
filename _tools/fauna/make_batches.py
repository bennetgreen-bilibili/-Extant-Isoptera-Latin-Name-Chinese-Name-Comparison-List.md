
import json, collections, os
w = json.load(open("_tmp/dz/work.json", encoding="utf-8"))

# merge duplicate pages (same species described twice under different genera)
merged = {}
order = []
for o in w:
    k = o["page"]
    if k not in merged:
        merged[k] = dict(o); order.append(k)
    else:
        m = merged[k]
        for f in ("soldier", "alate", "worker", "nymph", "host", "other"):
            if o[f] and o[f] not in m[f]:
                m[f] = (m[f] + " " + o[f]).strip()
        if o["syn"] and o["syn"] not in m["syn"]:
            m["syn"] = (m["syn"] + " ; " + o["syn"]).strip()
        m["book_alt"] = m.get("book_alt", []) + [f'{o["book_zh"]} {o["book_latin"]}']
        m["book_n_alt"] = m.get("book_n_alt", []) + [o["book_n"]]
data = [merged[k] for k in order]
print("unique pages", len(data))

# taxonomy note per entry
GEN_RENAME = {
 "Tsaitermes": ("蔡白蚁属", "Reticulitermes", "散白蚁属"),
 "Parahypotermes": ("壤白蚁属", "Hypotermes", "地白蚁属"),
 "Mironasutitermes": ("奇象白蚁属", "Nasutitermes", "象白蚁属"),
 "Havilanditermes": ("歧颚白蚁属", "Nasutitermes", "象白蚁属"),
 "Peribulbitermes": ("近瓢白蚁属", "Ahmaditermes", "钝颚白蚁属"),
 "Malaysiocapritermes": ("马扭白蚁属", "Procapritermes", "前扭白蚁属"),
 "Pilotermes": ("棘白蚁属", "Nasopilotermes", "棘象白蚁属"),
 "Sinotermes": ("华白蚁属", "Indotermes", "印白蚁属"),
}
def gen_rename(o):
    bl = (o["book_latin"] or "").split()
    pl = (o["page_latin"] or "").split()
    if not bl or not pl: return ""
    if bl[0] == pl[0]: return ""
    return GEN_RENAME.get(bl[0], (bl[0], pl[0], pl[0]))

os.makedirs("_tmp/dz/batches", exist_ok=True)
B = 30
batches = [data[i:i+B] for i in range(0, len(data), B)]
for i, b in enumerate(batches, 1):
    items = []
    for o in b:
        gr = gen_rename(o)
        note = ""
        if gr:
            note = f'原书属名 {gr[0]} {gr[1]}，本站现名 {gr[2]} {gr[2]} 属（属名变更）'
        if o.get("book_alt"):
            note += ("；原书另有条目：" + "、".join(o["book_alt"])) if note else ("原书另有条目：" + "、".join(o["book_alt"]))
        items.append({
            "book_n": o["book_n"], "page": o["page"],
            "page_latin": o["page_latin"], "page_zh": o["page_zh"],
            "book_zh": o["book_zh"], "book_latin": o["book_latin"],
            "book_genus_zh": o["g_zh"], "book_genus_latin": o["g_latin"],
            "note": note,
            "soldier": o["soldier"], "alate": o["alate"], "worker": o["worker"],
            "nymph": o["nymph"], "syn": o["syn"], "dist": o["dist"],
            "host": o["host"], "other": o["other"],
        })
    json.dump(items, open(f"_tmp/dz/batches/batch_{i:02d}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("batches", len(batches), "sizes", [len(b) for b in batches])
print("avg chars", sum(len(o["soldier"])+len(o["alate"])+len(o["worker"]) for o in data)//len(data))
