
import json, glob, os, re

def _fix_latin(t):
    return re.sub(r"\b([A-Z][a-z]{3,}) ([a-z]{2,6})\b", lambda m: m.group(1) + m.group(2), t)

batches = {}
for f in glob.glob("_tmp/dz/batches/batch_*.json"):
    for it in json.load(open(f, encoding="utf-8")):
        batches[it["page"]] = it

items = {}
for f in sorted(glob.glob("_tmp/dz/out/batch_*.json")):
    for it in json.load(open(f, encoding="utf-8")):
        p = it.get("page")
        if p in batches: items[p] = it
for f in sorted(glob.glob("_tmp/dz/out_clean/batch_*.json")):
    for it in json.load(open(f, encoding="utf-8")):
        p = it.get("page")
        if p in batches: items[p] = it   # out_clean 优先
print("collected", len(items), "of", len(batches))

out = {}
for page, it in items.items():
    src = batches[page]
    note = (it.get("taxonomy_note") or "").strip()
    if "扫描" in note: note = ""
    rec = {
        "book_ref": ("（原书第 %s 号条目）" % src["book_n"]) if src.get("book_n") else "",
        "book_n": src.get("book_n"),
        "book_name": _fix_latin((src.get("book_zh","") + " " + src.get("book_latin","")).strip()),
        "soldier": (it.get("soldier") or "").strip(),
        "alate": (it.get("alate") or "").strip(),
        "worker": (it.get("worker") or "").strip(),
        "nymph": (it.get("nymph") or "").strip(),
        "biology": (it.get("biology") or "").strip(),
        "distribution": (it.get("distribution") or "").strip(),
        "taxonomy_note": note,
        "en": (it.get("en") or "").strip(),
    }
    if not any(rec[k] for k in ("soldier","alate","worker","nymph","biology","distribution")): continue
    out[page] = rec
json.dump(out, open("_data/fauna_species.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
miss = [p for p in batches if p not in out]
print("entries", len(out), "bytes", os.path.getsize("_data/fauna_species.json"), "| pages without fauna", len(miss))
