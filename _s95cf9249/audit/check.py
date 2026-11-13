"""Independent audit checks (arena-95cf9249, 2026-11-13).
Written separately from tools/verify.py on purpose: an independent implementation.
Checks the PUBLISHED tree only (index.html, pages/*.html, assets/synthetic-projections.csv).
Outputs a plain-text report; exit code is nonzero only on unexpected internal errors.
"""
import re, sys, html
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]
OUT = []
def p(*a): OUT.append(' '.join(str(x) for x in a))

class Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_tbody = 0; self.in_tr = 0; self.in_td = 0; self.in_th = 0; self.in_body_row = False
        self.rows = []; self.cur = None; self.ncols_th = None
        self.in_head = False; self.col_th = 0
        self.src_links = 0; self.badges = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'thead': self.in_head = True; self.col_th = 0
        elif tag == 'tbody': self.in_tbody += 1
        elif tag == 'tr':
            self.in_tr += 1
            if self.in_tbody: self.cur = {'cells': 0, 'src': 0, 'badge': None}; self.in_body_row = True
        elif tag in ('td','th'):
            if tag == 'th':
                if self.in_head and self.in_tr: self.col_th += 1
            else:
                self.in_td += 1
                if self.in_tbody and self.cur is not None: self.cur['cells'] += 1
        elif tag == 'a':
            if self.in_tbody and self.in_td and 'source' in (a.get('class') or ''):
                if self.cur is not None: self.cur['src'] += 1
                self.src_links += 1
        elif tag == 'span':
            if self.in_tbody and 'badge' in (a.get('class') or ''):
                self.badges += 1
                if self.cur is not None: self.cur['badge'] = (a.get('class') or '').replace('badge','').strip()
    def handle_endtag(self, tag):
        if tag == 'thead': self.in_head = False
        elif tag == 'tbody': self.in_tbody -= 1
        elif tag == 'tr':
            self.in_tr -= 1
            if getattr(self, 'in_body_row', False):
                self.rows.append(self.cur); self.cur = None; self.in_body_row = False
        elif tag == 'td':
            self.in_td -= 1

MONEY = re.compile(r'\$\s?([0-9][0-9,]*)(?:\.[0-9]+)?')
PRIV = {
    'ZIP 95014': r'95014', 'ZIP 94122': r'94122',
    'city Cupertino': r'(?i)cupertino', 'neighbourhood Sunset': r'(?i)\bsunset\b',
    'city San Francisco': r'(?i)san francisco', 'email': r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
    'phone': r'\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b', 'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
    'APN wording': r'(?i)\b(?:APN|parcel (?:no|number|#))\b',
}
ALLOWED_PRIV_CONTEXT = ('san francisco',)  # allowed only inside official source link titles

files = sorted([ROOT/'index.html', *sorted((ROOT/'pages').glob('*.html'))])
tot_rows = tot_src = tot_badges = 0
non10 = []
priv_hits = []
col_mismatch = []
status_counts = {}
for f in files:
    t = f.read_text(encoding='utf-8')
    parser = Rows(); parser.feed(t)
    tot_rows += len(parser.rows); tot_src += parser.src_links; tot_badges += parser.badges
    for i, r in enumerate(parser.rows):
        if r['badge'] is not None:
            status_counts[r['badge']] = status_counts.get(r['badge'], 0) + 1
        if r['src'] == 0:
            col_mismatch.append(f'{f.name} row{i+1}: no source link')
    # dollar rounding on visible text
    txt = re.sub(r'<[^>]+>', ' ', t)
    for m in MONEY.finditer(txt):
        v = int(m.group(1).replace(',', ''))
        if v >= 1000 and v % 10 != 0:
            non10.append(f'{f.name}: ${v:,}')
    # privacy patterns on visible text (lowercased)
    low = txt.lower()
    for label, pat in PRIV.items():
        for m in re.finditer(pat, txt):
            ctx = txt[max(0, m.start()-60):m.end()+60].lower()
            if label == 'city San Francisco' and ('class="source"' in txt[max(0,m.start()-200):m.end()+200] or 'rent board' in ctx or 'sfpuc' in ctx or 'sf.gov' in ctx):
                kind = 'in official-source title'
            else:
                kind = 'VISIBLE TEXT'
            priv_hits.append(f'{f.name}: {label} [{kind}]: ...{txt[max(0,m.start()-40):m.end()+40]}...')

p('=== Independent audit checks (arena-95cf9249) ===')
p(f'Published HTML files checked: {len(files)}')
p(f'Table body rows: {tot_rows}; source links in rows: {tot_src}; status badges: {tot_badges}')
p(f'Rows missing a source link: {len([c for c in col_mismatch])}')
for c in col_mismatch[:10]: p('  ', c)
p(f'Visible dollar amounts >= $1,000 NOT a multiple of $10: {len(non10)}')
for x in non10[:10]: p('  ', x)
p('Status label counts:', ', '.join(f'{k}={v}' for k, v in sorted(status_counts.items())))
p(f'Privacy-pattern hits: {len(priv_hits)}')
for x in priv_hits[:20]: p('  ', x)

csv = ROOT/'assets/synthetic-projections.csv'
n = 0
for line in csv.read_text().splitlines()[1:]:
    for m in MONEY.finditer(line):
        v = int(m.group(1).replace(',', ''))
        if v >= 1000 and v % 10 != 0: n += 1
p(f'CSV rows scanned; non-$10-multiple amounts >= $1,000 in CSV: {n}')
open(Path(__file__).with_name('check-output.txt'), 'w').write('\n'.join(OUT) + '\n')
print('\n'.join(OUT))
