from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.rows=[]; self.row=None; self.header=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('a','link','script'):
            value=attrs.get('href') or attrs.get('src')
            if value: self.links.append(value)
            if tag=='a' and self.row is not None and value: self.row.append(value)
        if tag=='tr': self.row=[]; self.header=False
        if tag=='th' and self.row is not None: self.header=True
    def handle_endtag(self,tag):
        if tag=='tr' and self.row is not None:
            if not self.header: self.rows.append(self.row)
            self.row=None
errors=[]
for file in sorted(Path('.').glob('*.html')):
    parser=Parser(); parser.feed(file.read_text())
    for link in parser.links:
        u=urlsplit(link)
        if not u.scheme and not u.netloc and u.path and not (file.parent/unquote(u.path)).exists(): errors.append(f'{file}: missing {link}')
    for n,row in enumerate(parser.rows,1):
        if not any(urlsplit(u).scheme=='https' and (urlsplit(u).hostname or '').endswith(('.gov','.ca.gov')) for u in row): errors.append(f'{file}: data row {n} lacks official source')
if errors: print('\n'.join(errors)); raise SystemExit(1)
print('All local links resolve; every table data row links to an official .gov source.')
