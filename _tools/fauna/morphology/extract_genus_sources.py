"""Extract genus-level source pointers from Krishna et al. (2013), Treatise on the Isoptera.

Output: _data/genus_sources.json keyed by page URL. Each entry records the original
citation, type species and bibliographic references that Treatise flags as containing
characters / diagnoses / keys. Treatise itself gives no morphological description, so
these are pointers to the literature, never description text.
"""
import json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TREATISE = ROOT / '_unpublished/文库/treatise-on-the-isoptera/_full.txt'
OUT = ROOT / '_data/genus_sources.json'

tax = json.load(open(ROOT / '_data/taxonomy.json', encoding='utf-8'))
genera = tax['genera']
s = TREATISE.read_text(encoding='utf-8', errors='replace')

def clean(x):
    return re.sub(r'\s+', ' ', x).strip()

def entry_end(start):
    tail = s[start:start + 30000]
    # Stop at the next indented genus heading (fossil genera are nested inside the
    # living genus entry), at the species count ("▲ 1 living species, ..."), or at
    # the distribution line, which may be preceded by several private-use glyphs.
    m = re.search(r'(?m)^(?:[ \t]{3,}†?[A-Z][a-z]+[^\n]{0,80}?,\s*\d{4}[a-z]?:'
                  r'|\s*▲|[\uf0fc\uf0fd\uf0fe\s]*Distribution:)', tail)
    if m:
        return start + m.start()
    return min(len(s), start + 30000)

def find_entry(latin):
    pat = re.compile(r'(?m)^[ \t]{0,50}' + re.escape(latin) +
                     r'[ \t]+([A-Z][^\n]{0,70}?),?[ \t]*(\d{4}[a-z]?)(?:[ \t]*:.*)?[ \t]*$')
    best = None
    for m in pat.finditer(s):
        pos = m.start()
        head = s[pos:m.end()].strip()
        end = entry_end(m.end())
        win = s[pos:end]
        if 'Type species:' not in win:
            continue
        lead = len(m.group(0)) - len(m.group(0).lstrip(' \t'))
        score = 0
        if lead >= 8:
            score += 10
        if re.search(r'(?m)^\s*Type species:', win[:1500]):
            score += 3
        if ':' in head:
            score -= 2
        score -= min(5, len(head) // 80)
        if best is None or score > best[0]:
            best = (score, pos, end, head)
    return best

def citation_from(pos, head, latin):
    """Heading plus the following citation line, with wrapped lines joined."""
    cit = head
    if not re.search(r':\s*\d', cit):
        after = s[pos + len(head):pos + 2000]
        m = re.search(r'(?m)^' + re.escape(latin) + r'[^\n]*$', after)
        if m:
            cit = clean(m.group(0))
    idx = s.find(cit, pos)
    if idx < 0 or cit.endswith('.'):
        return cit
    # join up to 6 wrapped lines until a period, but never absorb a reference bullet
    for line in s[idx + len(cit):idx + len(cit) + 1200].splitlines()[1:]:
        line = clean(line)
        if not line or line[0] in '—–' or line.startswith('▲') or line.startswith('Distribution'):
            break
        cit += ' ' + line
        if line.endswith('.'):
            break
    return clean(cit)

def parse_entry(pos, end, head, latin):
    win = s[pos:end]
    cit = citation_from(pos, head, latin)
    tm = re.search(r'(?m)^\s*Type species:\s*(.+?)(?=\n\s*\n|\n\s*—|\n\s*\uf0fe)', win, re.S)
    type_species = clean(tm.group(1)) if tm else ''
    refs = []
    cur = None
    for line in win.splitlines():
        line = line.strip()
        if not line:
            continue
        mm = re.match(r'^[—–-]\s*(.+?)\s*[•·]\s*(.*)$', line)
        if mm:
            cur = {'ref': clean(mm.group(1)), 'note': clean(mm.group(2))}
            refs.append(cur)
        elif cur is not None and not re.match(r'^(▲|\uf0fe|\uf0fd|Distribution:)', line):
            # wrapped continuation of the previous note
            if len(cur['note']) < 400:
                cur['note'] = clean(cur['note'] + ' ' + line)
    keep = []
    for r in refs:
        low = r['note'].lower()
        if ('character' in low or 'diagnos' in low or 'key' in low or
                ('described' in low and any(w in low for w in ('soldier', 'imago', 'worker', 'alate', 'queen', 'king')))):
            keep.append(r)
    return cit, type_species, keep[:8], len(refs)

out = {}
missing = []
for g in genera:
    latin = g['latin']
    b = find_entry(latin)
    url = '/genus/%s/' % g['id']
    if not b:
        missing.append(g['id'])
        out[url] = {'latin': latin, 'zh': g['zh'], 'family': g['family'],
                    'treatise': False, 'citation': '', 'type_species': '',
                    'references': [], 'nrefs': 0}
        continue
    score, pos, end, head = b
    cit, ts, refs, nrefs = parse_entry(pos, end, head, latin)
    out[url] = {'latin': latin, 'zh': g['zh'], 'family': g['family'],
                'treatise': True, 'citation': cit, 'type_species': ts,
                'references': refs, 'nrefs': nrefs}

json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', OUT.name, len(out), 'entries; no Treatise entry:', len(missing))
print('no citation:', sum(1 for v in out.values() if not v['citation']))
print('no type species:', sum(1 for v in out.values() if v['treatise'] and not v['type_species']))
