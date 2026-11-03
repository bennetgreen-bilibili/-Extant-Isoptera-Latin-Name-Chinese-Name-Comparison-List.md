
import re, json
raw = open("_tmp/dz/fauna_raw.txt", encoding="utf-8").read()
OUT = "_tmp/dz"
GEN = re.compile(r"[（(]([一二三四五六七八九十百]+)[）)]\s*([\u4e00-\u9fa5]{1,8}白蚁属)\s*([A-Z][A-Za-z]{3,})")
gens = [{"idx": m.start(), "zh": m.group(2), "latin": m.group(3)} for m in GEN.finditer(raw)]
FAMS = [{"idx": raw.find("草白蚁科"), "zh": "草白蚁科", "latin": "Hodotermitidae"}]
for zh_, la_ in [("木白蚁科","Kalotermitidae"),("鼻白蚁科","Rhinotermitidae"),("白蚁科","Termitidae")]:
    i = raw.find(zh_ + " " + la_)
    if i < 0: i = raw.find(zh_ + la_)
    FAMS.append({"idx": i if i >= 0 else 10**9, "zh": zh_, "latin": la_})
FAMS.sort(key=lambda x: x["idx"])

HEAD = re.compile(r"(?<![\d])(\d{1,3})\s*[\.．]\s*(?=[\u4e00-\u9fa5])")
heads, last = [], 0
for m in HEAD.finditer(raw):
    n = int(m.group(1))
    if n <= last or n > last + 6 or n > 500: continue
    if m.start() > 0 and raw[m.start() - 1] not in "\n":
        continue
    window = raw[m.start():m.start() + 160]
    if not re.match(r"\d{1,3}\s*[\.\uff0e]\s*[\u4e00-\u9fa5]{3,12}\s*[A-Z]", window):
        continue
    if not re.search(r"\b(1[6-9]\d\d)\b", window):
        continue
    nm = re.match(r"\d{1,3}\s*[\.\uff0e]\s*([\u4e00-\u9fa5]{3,12})", window)
    if nm and re.search(r"[科属族目纲亚]", nm.group(1)):
        continue
    heads.append((n, m.start())); last = n

def owner(anchors, i):
    cur = None
    for a in anchors:
        if a["idx"] <= i: cur = a
        else: break
    return cur

def parse_head(text):
    t = re.sub(r"^\s*\d{1,3}\s*[\.．]\s*", "", text.lstrip())
    m = re.match(r"[\u4e00-\u9fa5\s]{2,20}", t)
    zh = re.sub(r"\s+", "", m.group(0)) if m else ""
    rest = t[m.end():] if m else t
    lm = re.search(r"([A-Z][a-z]{2,})\s*[\(（]?\s*[A-Z]?\.?\s*([a-z]{3,})", rest)
    latin = (lm.group(1) + " " + lm.group(2)) if lm else ""
    return zh, latin

CASTES = ["兵蚁", "有翅成虫", "工蚁", "若虫", "幼蚁"]
MARK = re.compile(r"(兵蚁|有翅成虫|工蚁|若虫|幼蚁|分布|寄主|生物学特性|生物学|异名|量度)")
entries = []
for k, (n, start) in enumerate(heads):
    end = heads[k+1][1] if k+1 < len(heads) else min(start+9000, len(raw))
    text = raw[start:end]
    first = text.split("\n", 1)[0].strip()
    zh, latin = parse_head(first if first else text[:120])
    if not zh:
        zh, latin = parse_head(text[:120])
    buckets = {}
    marks = [(m.start(), m.group(1)) for m in MARK.finditer(text)]
    for j, (pos, name) in enumerate(marks):
        stop = marks[j+1][0] if j+1 < len(marks) else len(text)
        buckets.setdefault(name, []).append(text[pos+len(name):stop])
    def join(key, lim=None):
        v = " ".join(buckets.get(key, []))
        v = re.sub(r"\s+", " ", v).strip()
        return v[:lim] if lim else v
    entries.append({"n": n, "idx": start, "text": text, "fam": owner(FAMS, start), "gen": owner(gens, start),
        "raw_head": first, "zh": zh, "latin": latin,
        "soldier": join("兵蚁", 3000), "alate": join("有翅成虫", 3000), "worker": join("工蚁", 2000),
        "nymph": (join("若虫", 1200) + " " + join("幼蚁", 800)).strip(),
        "syn": join("异名", 800), "dist": join("分布", 500), "host": join("寄主", 600),
        "other": (join("生物学", 1500) + " " + join("生物学特性", 800)).strip()})
json.dump(entries, open(OUT + "/corpus.json", "w", encoding="utf-8"), ensure_ascii=False)
bad = [e["n"] for e in entries if not e["latin"]]
print("entries", len(entries), "no-latin", len(bad), bad[:20])
print("sample", [(e["n"], e["zh"], e["latin"], (e["gen"] or {}).get("latin")) for e in entries[:3]])