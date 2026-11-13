#!/usr/bin/env python3
"""Technical checks only; a URL is not proof of a substantive claim."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'_7eff7e24'))
from evidence import SOURCES
from content import PAGES

PUBLIC_DOLLAR_AMOUNTS = {
    '$10', '$7,000', '$20,000', '$125,000', '$200,000', '$250,000',
    '$500,000', '$1,044,590', '$15,000,000', '$15,480,000',
}
PUBLIC_PERCENTAGES = {
    '0%', '1%', '1.6%', '2%', '3.8%', '4.3%', '5%', '9.1%', '10%',
    '13.7%', '15%', '20%', '25%', '40%',
}

# Generic regression patterns against publishing supplied household attributes.
# The patterns deliberately avoid storing any household values or exact narratives.
CASE_SPECIFIC_PATTERNS = (
    r'\b(?:owner|user)[\s-]+(?:provided|supplied)\b',
    r'\b(?:owner|user)[’\']s\s+(?:tentative\s+)?estimate\b',
    r'\b(?:additional|extra) inherited (?:money|cash|assets?) (?:is|are|was|were) expected\b',
    r'\b(?:two|three|four|five|six|\d+)\s+(?:rented\s+)?units?\b',
    r'\b\d+\s*/\s*\d+\s+(?:expense|cost|allocation)\b',
    r'\bproperty a (?:is|was) described as\b',
    r'\bthe available b space\b',
    r'\b(?:latest|most recent) supplied year\b',
)

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.ids=set(); self.rows=[]; self.row=None; self.cell_index=None
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
        if tag=='tr':
            self.row={'urls':[],'text':'','cells':0,'cell_texts':[],'blank_flags':[]}
            self.cell_index=None
        if self.row is not None:
            if tag=='td':
                self.row['cells']+=1
                self.row['cell_texts'].append('')
                self.row['blank_flags'].append(a.get('aria-label')=='Not verified; intentionally blank')
                self.cell_index=len(self.row['cell_texts'])-1
            if tag=='a' and a.get('href','').startswith('https://'): self.row['urls'].append(a['href'])
        if tag=='td' and a.get('aria-label')=='Not verified; intentionally blank': self.blank+=1
    def handle_endtag(self,tag):
        if tag in {'script','style'}: self.skip-=1
        if tag in {'table','thead','tbody','tr','td','th'}:
            if not self.tags or self.tags[-1]!=tag: self.issues.append('unbalanced '+tag)
            else: self.tags.pop()
        if tag=='td': self.cell_index=None
        if tag=='tr' and self.row is not None:
            if self.row['cells']: self.rows.append(self.row)
            self.row=None; self.cell_index=None
    def handle_data(self,data):
        if not self.skip: self.visible.append(data)
        if self.row is not None:
            self.row['text']+=data
            if self.cell_index is not None: self.row['cell_texts'][self.cell_index]+=data


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
            if not any(x in row['text'] for x in ('Verified','Guidance','Missing')):
                errors.append(path.name+': row missing status')
            for u in row['urls']:
                if u not in official: errors.append(path.name+': unregistered row URL')
        visible=' '.join(doc.visible)
        normalized_visible=' '.join(visible.split()).casefold()
        if any(re.search(pattern,normalized_visible,re.I) for pattern in CASE_SPECIFIC_PATTERNS):
            errors.append(path.name+': case-specific narrative detail')
        if path.name=='property-tax.html' and re.search(r'<tr>\s*<td>[AB]</td>\s*<td>20\d{2}</td>',text):
            errors.append(path.name+': case-specific historical year range')
        # Geographic source URLs are allowed; detect address/identifier formats without
        # embedding any property-specific place names in the checker.
        address_or_id=(
            r'\b(?:APN|SSN)\b|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|'
            r'\b\d{1,6}\s+(?:[A-Z][\w.\'-]*\s+){1,5}'
            r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b'
        )
        if re.search(address_or_id,visible,re.I): errors.append(path.name+': prohibited identifying text')
        without_money=re.sub(r'\$[\d,]+(?:\.\d+)?','',visible)
        without_money=re.sub(r'(?:(?:RTC|Probate Code|Section)\s+)?§{1,2}\s*\d+(?:\.\d+)?(?:\s*[–-]\s*\d+(?:\.\d+)?)?','',without_money)
        without_money=re.sub(r'\b(?:RTC|Probate Code|Section)\s+\d+(?:\.\d+)?','',without_money)
        if re.search(r'\b\d{5}(?:-\d{4})?\b',without_money): errors.append(path.name+': ZIP-like visible number')
        for token in re.findall(r'\$[\d,]+(?:\.\d+)?',visible):
            amount=float(token[1:].replace(',',''))
            if amount%10: errors.append(path.name+': dollar display not rounded: '+token)
            if token not in PUBLIC_DOLLAR_AMOUNTS: errors.append(path.name+': unverified public dollar amount: '+token)
        for token in re.findall(r'(?<![\w.])\d+(?:\.\d+)?%',visible):
            if token not in PUBLIC_PERCENTAGES: errors.append(path.name+': unverified public percentage: '+token)
        blank+=doc.blank
        for u in doc.links:
            if u.startswith(('http:','https:')):
                links+=1
                if u not in official: errors.append(path.name+': external URL outside checked ledger')
                host=urlsplit(u).hostname or ''
                if not (host.endswith('.gov') or host=='docs.github.com'):
                    errors.append(path.name+': source host is not an approved official domain')
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
    projection_path=ROOT/'pages/projections.html'
    projection_years=set()
    if projection_path not in docs:
        errors.append('missing projection register page')
    else:
        for row in docs[projection_path].rows:
            cells=[x.strip() for x in row['cell_texts']]
            if not cells: continue
            match=re.fullmatch(r'(20\d{2})',cells[0])
            if not match: continue
            year=int(match.group(1))
            if year in projection_years: errors.append(f'duplicate projection year {year}')
            projection_years.add(year)
            if len(cells)!=8:
                errors.append(f'projection year {year}: expected six data cells, status and source')
            elif any(cells[i] for i in range(1,6)):
                errors.append(f'projection year {year}: household amount cell is not blank')
            elif not all(row['blank_flags'][i] for i in range(1,6)):
                errors.append(f'projection year {year}: blank household amount lacks explicit missing label')
        if projection_years != set(range(2026,2077)):
            errors.append('projection register must contain blank rows for every year 2026–2076')
    for key,_,_ in PAGES:
        p=ROOT/'index.html' if key=='index' else ROOT/'pages'/f'{key}.html'
        if p not in docs: errors.append('missing required page '+key)
    if (ROOT/'assets/synthetic-projections.csv').exists():
        errors.append('unverified synthetic monetary projections are still published as a CSV')
    config=(ROOT/'_config.yml').read_text()
    for x in ('tools','_7eff7e24','_s8bb142d0','_a3de132b','_0e6635bc','COORDINATION.md','README.md','_1775f697'):
        if f'  - {x}\n' not in config: errors.append('publication exclusion missing '+x)
    if (ROOT/'.nojekyll').exists(): errors.append('.nojekyll bypasses exclusions')
    for path in [ROOT/'tools/build.py',ROOT/'_7eff7e24/content.py']:
        text=path.read_text()
        if any(x in text for x in ('inputs.json','_c07ccf45/','_s09b3ffa0/','from model import')):
            errors.append('private or retired-model dependency '+path.name)
    for path in [ROOT/'assets/app.js',ROOT/'assets/style.css']:
        text=path.read_text()
        if re.search(r'https?://|fetch\(|XMLHttpRequest|@import',text): errors.append('remote asset/data call '+path.name)
    print(f'Checked {len(pages)} HTML files, {total_rows} sourced/statused rows, {links} official links, {blank} blank cells, and the blank 2026–2076 projection register.')
    for error in errors: print('FAIL:',error)
    print(f'{len(errors)} technical failures. These checks do not certify legal or household financial accuracy.')
    return int(bool(errors))

if __name__=='__main__': sys.exit(verify())
