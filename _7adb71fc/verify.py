"""Technical verification of the published site.

This checks structure, source coverage, rounding, privacy tokens and links. It
does not certify that a sentence is entailed by its source, and it is not legal
or financial advice.
"""
import csv
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7eff7e24'))
sys.path.insert(0, str(ROOT / '_7adb71fc'))

from evidence import SOURCES
from sitebuild import PAGES, REDIRECTS

# Words that would identify a place, a person or a parcel. Checked as visible
# text only, so that official source URLs on .gov domains remain linkable.
# Geographic names of the two jurisdictions would identify the properties even
# without an address, so they are blocked as visible text. Official source URLs
# on .gov domains are allowed to contain them, because a link is not a claim
# about where these homes are.
PROHIBITED = re.compile(
    r'\b(?:cupertino|san\s+francisco\s+metro|outer\s+sunset|sunnyvale|95014|94122|'
    r'santa\s+clara\s+county|san\s+jose\s+metro|\bAPN\b|assessor\s+parcel\s+number|'
    r'social\s+security\s+number|SSN)\b', re.I)
# Document identifiers that are citations, not geography or identity.
# Official document identifiers appear as citations, not as geography or
# identity. Each pattern is anchored on the issuing series so a bare five-digit
# number in prose is still caught.
CITATION = re.compile(
    r'(?:\b(?:Probate Code|Civil Code|Revenue and Taxation Code|Election Code|'
    r'LTA|Letter to Assessors|IR|Rev\.\s*Proc\.|Prop\.|Proposition|RTC|Probate|'
    r'Prob\.|Civ\.|Form|Publication|Topic|Section|File\s*No\.)\s*[\d./\-]+)|'
    r'(?:\bprop\.?\s*(?:13|19|42|58|193)\b)|'
    r'(?:\bsection\s+2\.1\b)|'
    r'(?:\b\d{4}/\d{3}\b)|(?:\b\d{3}/\d{3}\b)|(?:\b20\d{2}-(?:19|20)\d{2}\b)', re.I)
# Any five-digit number that is not inside a dollar figure and not a statute year.
ZIPLIKE = re.compile(r'(?<![\d$,.])\d{5}(?![\d,])')


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.rows, self.row = [], set(), [], None
        self.visible, self.stack, self.issues = [], [], []
        self.noindex = False
        self.blank = 0
        self.skip = 0
        self.selects = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {'script', 'style'}:
            self.skip += 1
        if tag in {'table', 'thead', 'tbody', 'tr', 'td', 'th'}:
            self.stack.append(tag)
        if 'id' in a:
            if a['id'] in self.ids:
                self.issues.append('duplicate id ' + a['id'])
            self.ids.add(a['id'])
        for attr in ('href', 'src'):
            if attr in a:
                self.links.append(a[attr])
        if tag == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content', ''):
            self.noindex = True
        if tag == 'select' and 'review-choice' in a.get('class', ''):
            self.selects += 1
        if tag == 'tr':
            self.row = {'urls': [], 'text': '', 'cells': 0}
        if self.row is not None:
            if tag == 'td':
                self.row['cells'] += 1
            if tag == 'a' and a.get('href', '').startswith('https://'):
                self.row['urls'].append(a['href'])
        if tag == 'td' and a.get('aria-label') == 'Not verified; intentionally blank':
            self.blank += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.skip -= 1
        if tag in {'table', 'thead', 'tbody', 'tr', 'td', 'th'}:
            if not self.stack or self.stack[-1] != tag:
                self.issues.append('unbalanced ' + tag)
            else:
                self.stack.pop()
        if tag == 'tr' and self.row is not None:
            if self.row['cells']:
                self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if not self.skip:
            self.visible.append(data)
        if self.row is not None:
            self.row['text'] += data


def verify(verbose=True):
    errors = []
    docs = {}
    official = {v[1] for v in SOURCES.values()}
    pages = [ROOT / 'index.html', *sorted((ROOT / 'pages').glob('*.html'))]
    total_rows = links = blank = 0
    for path in pages:
        text = path.read_text()
        d = Doc()
        d.feed(text)
        d.close()
        docs[path] = d
        errors += [f'{path.name}: {x}' for x in d.issues]
        if d.stack:
            errors.append(path.name + ': unclosed table tags')
        if not d.noindex:
            errors.append(path.name + ': missing noindex')
        for row in d.rows:
            total_rows += 1
            if not row['urls']:
                errors.append(path.name + ': row without an official link')
            if not any(s in row['text'] for s in ('Verified', 'Owner', 'Projection', 'Assumption', 'Missing', 'Guidance')):
                errors.append(path.name + ': row without a status')
            for u in row['urls']:
                if u not in official:
                    errors.append(path.name + ': row link outside the ledger: ' + u[:70])
        visible = ' '.join(d.visible)
        if PROHIBITED.search(visible):
            errors.append(path.name + ': prohibited identifying text: ' + PROHIBITED.search(visible).group(0))
        stripped = re.sub(r'\$[\d,]+(?:\.\d+)?', '', visible)
        stripped = CITATION.sub('', stripped)
        stripped = re.sub(r'\b(?:19|20)\d{2}\b', '', stripped)
        stripped = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '', stripped)
        m = ZIPLIKE.search(stripped)
        if m:
            errors.append(path.name + ': five-digit number outside a dollar figure: ' + m.group(0))
        # A dollar cell must be rounded. Two exemptions are deliberate and are
        # flagged by their own wording: a statutory amount quoted verbatim, and a
        # per-$500 tax rate that cannot be expressed in tens.
        exact_context = re.compile(
            r'exact|statutory|verbatim|per \$500|per \$1,000|\$0\.55|\$1\.10|published amount', re.I)
        # The source ledger quotes official passages word for word. An exact figure
        # there is a quotation, not a published finding about these properties.
        quotes_ledger = path.name == 'sources.html'
        for match in re.finditer(r'\$([\d,]+(?:\.\d+)?)', visible):
            token = match.group(1)
            if float(token.replace(',', '')) % 10:
                window = visible[max(0, match.start() - 140):match.end() + 140]
                if exact_context.search(window) or quotes_ledger:
                    continue
                errors.append(path.name + ': dollar amount not rounded to $10: ' + token)
        blank += d.blank
        for u in d.links:
            if u.startswith(('http:', 'https:')):
                links += 1
                if u not in official:
                    errors.append(path.name + ': external URL outside the ledger: ' + u[:70])
                host = urlsplit(u).hostname or ''
                if not host.endswith('.gov'):
                    errors.append(path.name + ': source is not on a .gov domain: ' + host)
    # internal links and anchors
    for path, d in docs.items():
        for u in d.links:
            parts = urlsplit(u)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if not target.is_file():
                errors.append(path.name + ': broken internal link ' + u)
            elif parts.fragment and target in docs and parts.fragment not in docs[target].ids:
                errors.append(path.name + ': missing anchor ' + u)
    expected = len(PAGES) + len(REDIRECTS)
    if len(pages) != expected:
        errors.append(f'expected {expected} html files, found {len(pages)}')
    if blank < 20:
        errors.append('missing blank-cell registers, found ' + str(blank))
    # CSV
    with (ROOT / 'assets/case-projections.csv').open() as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 51 * 4:
        errors.append('CSV row count ' + str(len(rows)))
    for row in rows:
        if row['property'] not in {'A', 'B'}:
            errors.append('CSV property label')
        for key, value in row.items():
            if key in {'property', 'transfer_year', 'year', 'assumption_note'}:
                continue
            if int(value) % 10:
                errors.append('CSV value not rounded: ' + value)
    if len({r['year'] for r in rows}) != 51:
        errors.append('CSV horizon')
    # publication exclusions and build hygiene
    config = (ROOT / '_config.yml').read_text()
    for x in ('tools', '_7eff7e24', '_7adb71fc', '_s8bb142d0', '_a3de132b', '_1775f697',
              'COORDINATION.md', 'README.md'):
        if f'  - {x}\n' not in config:
            errors.append('publication exclusion missing: ' + x)
    if (ROOT / '.nojekyll').exists():
        errors.append('.nojekyll would bypass the exclusions')
    for path in [ROOT / 'assets/app.js', ROOT / 'assets/style.css']:
        if re.search(r'https?://|fetch\(|XMLHttpRequest|@import', path.read_text()):
            errors.append('remote call in ' + path.name)
    # a hard privacy gate: the raw owner figures and the geography must never be
    # published in any form a search engine could match.
    raw_source = re.compile(
        r'\b95014\b|\b94122\b|cupertino|outer sunset|\bsunset district\b', re.I)
    # Exact owner values must not appear at all. The rent figure is checked
    # against the annual total, because a monthly rent can legitimately collide
    # with an unrelated projection (an insurance line, for example).
    raw_exact = re.compile(
        r'\b550,?537\b|\b114,?248\b|\b7,?207\b|\b2,?439\b|\b7,?150\s*(?:per month|/mo|a month|monthly)', re.I)
    for path in pages:
        text = path.read_text()
        for pattern, why in ((raw_source, 'geography'), (raw_exact, 'unrounded owner figure')):
            hit = pattern.search(text)
            if hit:
                errors.append(path.name + ': ' + why + ' published: ' + hit.group(0))
    if verbose:
        print(f'Checked {len(pages)} HTML files, {total_rows} sourced/statused rows, '
              f'{links} official link instances, {blank} blank cells, {len(rows)} CSV rows.')
        for e in errors:
            print('FAIL:', e)
        print(f'{len(errors)} technical failures. These checks are not legal or financial verification.')
    return errors


if __name__ == '__main__':
    sys.exit(1 if verify() else 0)
