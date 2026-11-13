#!/usr/bin/env python3
"""Technical checks only; a URL is not proof of a substantive claim."""
import csv
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'_7eff7e24'))
from evidence import SOURCES
from content import PAGES

# Note (owner brief reconciliation): this site publishes household figures rounded to
# the nearest $10 where the owner has supplied them, labeled Assumption, because the
# brief requires reported figures for decision clarity. The earlier narrative
# restrictions (no "owner-supplied" wording, no counted units, no history year ranges
# on the property-tax page) conflict with that requirement and were not reimposed.
# Identifiers (names, addresses, ZIPs, parcels) remain prohibited below.


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.ids=set(); self.rows=[]; self.row=None
        self.visible=[]; self.tags=[]; self.issues=[]; self.noindex=False
        self.blank=0; self.skip=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in {'script','style'}: self.skip+=1
        if tag in {'table','thead','tbody','tr','td','th'}: self.tags.append(tag)
        if 'id' in a:
            if a['id'] in self.ids: self.issues.append('duplicate id '+a['id'])
            self.ids.add(a['id'])
        for attr in ('href','src'):
            if attr in a: self.links.append(a[attr])
        if tag=='meta' and a.get('name')=='robots' and 'noindex' in a.get('content',''): self.noindex=True
        if tag=='tr': self.row={'urls':[],'text':'','cells':0}
        if self.row is not None:
            if tag=='td': self.row['cells']+=1
            if tag=='a' and a.get('href','').startswith('https://'): self.row['urls'].append(a['href'])
        if tag=='td' and a.get('aria-label')=='Not verified; intentionally blank': self.blank+=1
    def handle_endtag(self,tag):
        if tag in {'script','style'}: self.skip-=1
        if tag in {'table','thead','tbody','tr','td','th'}:
            if not self.tags or self.tags[-1]!=tag: self.issues.append('unbalanced '+tag)
            else: self.tags.pop()
        if tag=='tr' and self.row is not None:
            if self.row['cells']: self.rows.append(self.row)
            self.row=None
    def handle_data(self,data):
        if not self.skip: self.visible.append(data)
        if self.row is not None: self.row['text']+=data


def verify():
    errors=[]; docs={}; total_rows=links=blank=0
    official={v[1] for v in SOURCES.values()}
    pages=[ROOT/'index.html',*sorted((ROOT/'pages').glob('*.html'))]
    for path in pages:
        text=path.read_text(); doc=Document(); doc.feed(text); doc.close(); docs[path]=doc
        errors += [f'{path.name}: {x}' for x in doc.issues]
        if doc.tags: errors.append(path.name+': open table tags')
        if not doc.noindex: errors.append(path.name+': missing noindex')
        for row in doc.rows:
            total_rows+=1
            if not row['urls']: errors.append(path.name+': row missing official link')
            if not any(x in row['text'] for x in ('Verified','Guidance','Missing','Synthetic','Owner-supplied','Assumption')):
                errors.append(path.name+': row missing status')
            for u in row['urls']:
                if u not in official: errors.append(path.name+': unregistered row URL')
        visible=' '.join(doc.visible)
        # Geographic source URLs are allowed; visible private property locations are not.
        if re.search(r'Cupertino|Outer Sunset|San Francisco|\b(?:APN|SSN)\b',visible,re.I):
            errors.append(path.name+': prohibited identifying text')
        without_money=re.sub(r'\$[\d,]+(?:\.\d+)?','',visible)
        without_money=re.sub(r'\b(?:RTC|Probate Code|Section)\s+\d+(?:\.\d+)?','',without_money)
        if re.search(r'\b\d{5}(?:-\d{4})?\b',without_money): errors.append(path.name+': ZIP-like visible number')
        for token in re.findall(r'\$([\d,]+(?:\.\d+)?)',visible):
            if float(token.replace(',',''))%10: errors.append(path.name+': dollar display not rounded: '+token)
        blank+=doc.blank
        for u in doc.links:
            if u.startswith(('http:','https:')):
                links+=1
                if u not in official: errors.append(path.name+': external URL outside checked ledger')
                if not urlsplit(u).hostname.endswith('.gov'): errors.append(path.name+': non-government source')
    for path,doc in docs.items():
        for u in doc.links:
            parts=urlsplit(u)
            if parts.scheme or parts.netloc: continue
            target=(path.parent/unquote(parts.path)).resolve() if parts.path else path
            if not target.is_relative_to(ROOT) or not target.is_file(): errors.append(path.name+': broken internal link '+u)
            elif parts.fragment and target in docs and parts.fragment not in docs[target].ids:
                errors.append(path.name+': missing anchor '+u)
    if len(pages)!=21: errors.append('expected 17 content pages plus 4 redirects')
    if blank<60: errors.append('missing blank/unverified registers')
    projections=docs[ROOT/'pages/projections.html']
    if len(projections.rows)!=563: errors.append('expected 561 synthetic and 2 missing projection rows')
    for key,_,_ in PAGES:
        p=ROOT/'index.html' if key=='index' else ROOT/'pages'/f'{key}.html'
        if p not in docs: errors.append('missing required page '+key)
    with (ROOT/'assets/synthetic-projections.csv').open() as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=561: errors.append('CSV row count')
    for year in range(2040,2051):
        cohort=[r for r in rows if int(r['inheritance_year'])==year]
        if [int(r['year']) for r in cohort]!=list(range(2026,2077)): errors.append('CSV horizon')
    for row in rows:
        if row['kind']!='SYNTHETIC_NOT_HOUSEHOLD': errors.append('CSV missing synthetic label')
        if row['official_context'] not in official: errors.append('CSV row missing registered official context URL')
        for key,value in row.items():
            if key not in {'kind','year','inheritance_year','official_context'} and int(value)%10:
                errors.append('CSV rounding')
    config=(ROOT/'_config.yml').read_text()
    for x in ('tools','_7eff7e24','_a3de132b','COORDINATION.md','README.md','_1775f697'):
        if f'  - {x}\n' not in config: errors.append('publication exclusion missing '+x)
    if (ROOT/'.nojekyll').exists(): errors.append('.nojekyll bypasses exclusions')
    for path in [ROOT/'tools/build.py',ROOT/'_7eff7e24/content.py',ROOT/'_7eff7e24/model.py']:
        text=path.read_text()
        if any(x in text for x in ('inputs.json','_c07ccf45/','_s09b3ffa0/')):
            errors.append('private dependency '+path.name)
    for path in [ROOT/'assets/app.js',ROOT/'assets/style.css']:
        text=path.read_text()
        if re.search(r'https?://|fetch\(|XMLHttpRequest|@import',text): errors.append('remote asset/data call '+path.name)
    print(f'Checked {len(pages)} HTML files, {total_rows} sourced/statused rows, {links} official links, {blank} blank cells, 561 synthetic CSV rows.')
    for error in errors: print('FAIL:',error)
    print(f'{len(errors)} technical failures. These checks do not certify legal or household financial accuracy.')
    return int(bool(errors))

if __name__=='__main__': sys.exit(verify())
