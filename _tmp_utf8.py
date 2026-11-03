
import sys
files = [l.rstrip("\n") for l in open("_tmp_files.txt", encoding="utf-8", errors="surrogateescape") if l.strip()]
bad = []
skipped_bin = 0
for f in files:
    try:
        data = open(f, "rb").read()
    except Exception as e:
        bad.append((f, "READ " + type(e).__name__)); continue
    if b"\x00" in data[:4096]:
        skipped_bin += 1; continue
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as e:
        bad.append((f, "UTF8 at %d: %s" % (e.start, e.reason)))
print("tracked:", len(files), "| binary skipped:", skipped_bin, "| bad utf8:", len(bad))
for f, e in bad[:30]:
    print("  ", f, "->", e)
