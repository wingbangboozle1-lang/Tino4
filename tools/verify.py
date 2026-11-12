#!/usr/bin/env python3
"""Static checks: structure, local links, official-source links and monetary rounding.
These tests do not verify source content, re-identification risk, history or deployment."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
class Check(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.path=path; self.links=[]; self.rows=[]; self.row=None; self.inbody=False; self.inhead=False; self.columns=0; self.headcount=0; self.cellcount=0; self.text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a':
            link=a.get('href',''); self.links.append(link)
            if self.row is not None and urlparse(link).scheme=='https': self.row.append(link)
        if tag=='thead': self.inhead=True; self.headcount=0
        if tag=='tbody': self.inbody=True
        if tag=='tr' and self.inbody: self.row=[]; self.cellcount=0
        if tag=='th' and self.inhead: self.headcount+=1
        if tag=='td' and self.row is not None: self.cellcount+=1
    def handle_endtag(self,tag):
        if tag=='thead': self.inhead=False; self.columns=self.headcount
        if tag=='tbody': self.inbody=False
        if tag=='tr' and self.row is not None: self.rows.append((self.row,self.cellcount,self.columns)); self.row=None
    def handle_data(self,data): self.text.append(data)
errors=[]; total=0
files=[ROOT/'index.html',*sorted((ROOT/'pages').glob('*.html'))]
for p in files:
    c=Check(p); c.feed(p.read_text(encoding='utf8'))
    for links,cells,cols in c.rows:
        total+=1
        if not links: errors.append(f'{p}: missing source')
        if cells!=cols: errors.append(f'{p}: {cells} cells vs {cols} headings')
    for link in c.links:
        u=urlparse(link)
        if u.scheme:
            host=u.hostname or ''
            if u.scheme!='https' or not (host.endswith('.gov') or host.endswith('.ca.gov') or host=='docs.github.com'): errors.append(f'{p}: not an official HTTPS source: {link}')
        elif link and not link.startswith('#'):
            target=(p.parent / unquote(u.path)).resolve()
            if not target.is_file() or not target.is_relative_to(ROOT): errors.append(f'{p}: broken local link {link}')
    text=' '.join(c.text)
    for match in re.finditer(r'\$([\d,]+)(?![\d,.])',text):
        if int(match.group(1).replace(',',''))%10: errors.append(f'{p}: unrounded dollar amount')
    # Guard public HTML against common identifiers and owner-supplied exact detail.
    if re.search(r'\b(?:95014|94122)\b|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|\b\d{3}-\d{2}-\d{4}\b', text, re.I):
        errors.append(f'{p}: potential private identifier')
    if c.rows and 'Status</th>' not in p.read_text(encoding='utf8'):
        errors.append(f'{p}: table lacks verification status column')
    if not c.rows and p.name not in {'decisions.html','costs.html','properties.html','flagged.html'}: errors.append(f'{p}: no sourced table')
if not (ROOT/'_config.yml').exists() or (ROOT/'.nojekyll').exists(): errors.append('Jekyll exclusions not enabled')
config=(ROOT/'_config.yml').read_text()
for x in ['tools','COORDINATION.md','README.md']:
    if f'  - {x}' not in config: errors.append(f'missing exclusion: {x}')
for dir in ['archive-v2','internal','docs','data']:
    if (ROOT/dir).exists(): errors.append(f'old public tree remains: {dir}')
print(f'{len(files)} pages, {total} table rows; {len(errors)} structural failures')
for e in errors: print(e)
sys.exit(bool(errors))
