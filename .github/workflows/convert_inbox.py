#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, os, re, sys, datetime, subprocess
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

NL = chr(10)
BS = chr(92)

def slugify(s):
    s = (s or '').strip()
    s = ''.join(ch if (ch.isalnum() or ch in '-_') else '-' for ch in s)
    s = re.sub('-+', '-', s)
    return s.strip('-') or 'post'

def git_date(path):
    try:
        out = subprocess.check_output(['git', 'log', '-1', '--format=%cs', '--', path], text=True).strip()
        return out or None
    except Exception:
        return None

def file_date(name, path):
    m = re.match(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})[-_.]', name)
    if m:
        return m.group(1) + '-' + m.group(2) + '-' + m.group(3)
    g = git_date(path)
    if g:
        return g
    return datetime.date.today().strftime('%Y-%m-%d')

def strip_date(name):
    return re.sub(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}[-_.]', '', name)

def inline_md(p):
    out = []
    for r in p.runs:
        t = r.text
        if not t:
            continue
        if r.bold and r.italic:
            t = '***' + t + '***'
        elif r.bold:
            t = '**' + t + '**'
        elif r.italic:
            t = '*' + t + '*'
        out.append(t)
    return ''.join(out)

def heading_level(p):
    name = p.style.name or ''
    sid = (p.style.style_id or '').lower()
    if sid.startswith('heading') or 'heading' in name.lower() or '标题' in name:
        digits = ''.join(c for c in name if c.isdigit())
        return (int(digits) + 1) if digits else 2
    if name.lower() == 'title' or name == '标题':
        return 2
    return None

def is_list(p):
    pPr = p._p.pPr
    if pPr is not None and pPr.numPr is not None:
        return True
    nm = (p.style.name or '').lower()
    return 'list' in nm or '列表' in (p.style.name or '')

def table_to_md(tbl):
    rows = []
    for row in tbl.rows:
        seen = set()
        cells = []
        for cell in row.cells:
            key = id(cell._tc)
            if key in seen:
                continue
            seen.add(key)
            cells.append(' '.join(cell.text.splitlines()).replace('|', BS + '|').strip())
        rows.append(cells)
    if not rows:
        return ''
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    lines = ['| ' + ' | '.join(rows[0]) + ' |', '| ' + ' | '.join(['---'] * ncol) + ' |']
    for r in rows[1:]:
        lines.append('| ' + ' | '.join(r) + ' |')
    return NL.join(lines)

def iter_blocks(doc):
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield Table(child, doc)

def collapse(lines):
    clean = []
    prev = False
    for ln in lines:
        b = (ln.strip() == '')
        if b and prev:
            continue
        clean.append(ln)
        prev = b
    while clean and clean[0].strip() == '':
        clean.pop(0)
    while clean and clean[-1].strip() == '':
        clean.pop()
    return clean

def docx_convert(path):
    doc = Document(path)
    title = None
    excerpt = ''
    body = []
    for b in iter_blocks(doc):
        if isinstance(b, Paragraph):
            txt = b.text.strip()
            if not txt:
                continue
            lvl = heading_level(b)
            if lvl is not None:
                if title is None:
                    title = txt
                    continue
                body.append('#' * lvl + ' ' + txt)
            elif is_list(b):
                body.append('- ' + inline_md(b).strip())
            else:
                md = inline_md(b).strip()
                if not excerpt:
                    excerpt = txt
                body.append(md)
        elif isinstance(b, Table):
            md = table_to_md(b)
            if md:
                body.append('')
                body.append(md)
                body.append('')
    return title, NL.join(collapse(body)), ' '.join(excerpt.split())

def txt_convert(text):
    lines = text.splitlines()
    title = None
    paras = []
    cur = []
    for l in lines:
        s = l.rstrip()
        if s.strip() == '':
            if cur:
                paras.append(' '.join(x.strip() for x in cur))
                cur = []
            continue
        if title is None:
            title = s.strip()
            continue
        cur.append(s)
    if cur:
        paras.append(' '.join(x.strip() for x in cur))
    body = (NL + NL).join(paras)
    return title, body, paras[0] if paras else ''

def md_excerpt(body):
    for ln in body.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s[0] in '#|->' or s.startswith('- '):
            continue
        s = re.sub(r'[#*_>]', '', s)
        s = s.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
        if s.strip():
            return s.strip()
    return ''

def md_convert(text):
    title = None
    fm_date = None
    body = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2].strip()
            for ln in fm.splitlines():
                s = ln.strip()
                if s.startswith('title:'):
                    title = s[6:].strip().strip('"').strip("'")
                elif s.startswith('date:'):
                    fm_date = s[5:].strip().strip('"').strip("'")
    if title is None:
        m = re.search(r'^#[ ]+(.+)$', body, re.M)
        if m:
            title = m.group(1).strip()
            lines = body.splitlines()
            removed = False
            kept = []
            for l in lines:
                ls = l.strip()
                if not removed and ls.startswith('#') and not ls.startswith('##') and ls[1:].strip() == title:
                    removed = True
                    continue
                kept.append(l)
            body = NL.join(kept).strip()
    if title is None:
        for l in body.splitlines():
            if l.strip():
                title = l.strip()
                break
    return title, fm_date, body

def write_post(title, date_str, slug, body, excerpt, outdir, lang, author):
    safe_title = ' '.join(title.splitlines()).replace('"', "'")
    safe_excerpt = ' '.join(excerpt.split()).replace('"', "'")
    if len(safe_excerpt) > 160:
        safe_excerpt = safe_excerpt[:160].rstrip() + '…'
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, date_str + '-' + slug + '.md')
    fm = ['---',
          'layout: post',
          'title: "' + safe_title + '"',
          'date: ' + date_str + ' 00:00:00 +0800',
          'lang: ' + lang,
          'author: ' + author,
          'excerpt: "' + safe_excerpt + '"',
          '---']
    content = NL.join(fm) + NL + NL + body.rstrip() + NL
    with open(out, 'w', encoding='utf-8') as f:
        f.write(content)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inbox', default='_inbox')
    ap.add_argument('--outdir', default='_posts')
    ap.add_argument('--lang', default='zh-CN')
    ap.add_argument('--author', default='班奈特格林')
    args = ap.parse_args()

    if not os.path.isdir(args.inbox):
        print('no inbox dir: ' + args.inbox)
        return

    files = sorted(f for f in os.listdir(args.inbox) if not f.startswith('.') and not f.startswith('_'))
    converted = 0
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in ('.docx', '.txt', '.md', '.markdown'):
            continue
        p = os.path.join(args.inbox, f)
        name = os.path.basename(f)
        date_str = file_date(name, p)
        slug = slugify(strip_date(os.path.splitext(name)[0]))
        try:
            if ext == '.docx':
                title, body, excerpt = docx_convert(p)
                if title is None:
                    title = slug
            elif ext in ('.md', '.markdown'):
                with open(p, 'r', encoding='utf-8') as fh:
                    text = fh.read()
                title, fm_date, body = md_convert(text)
                if fm_date:
                    date_str = fm_date
                if title is None:
                    title = slug
                excerpt = md_excerpt(body)
            else:
                with open(p, 'r', encoding='utf-8') as fh:
                    text = fh.read()
                title, body, excerpt = txt_convert(text)
                if title is None:
                    title = slug
            out = write_post(title, date_str, slug, body, excerpt, args.outdir, args.lang, args.author)
            print('OK  ' + f + '  ->  ' + out)
            converted += 1
        except Exception as e:
            print('ERR ' + f + ' : ' + str(e))
    print('converted ' + str(converted) + ' file(s)')

if __name__ == '__main__':
    main()
