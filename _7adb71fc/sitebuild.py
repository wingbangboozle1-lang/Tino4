"""Assemble the public site. Standard library only. No network at build time."""
import csv
import json
import sys
from pathlib import Path
from html import escape as E

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7eff7e24'))
sys.path.insert(0, str(ROOT / '_7adb71fc'))

import content_part1 as c1
import content_part2 as c2
import content_part3 as c3
from case_model import projection, money as M, rounded
from case_data import P
from evidence import DATE

PAGES = [
    ('index', 'Decision overview', 'Start here', c1.page_overview),
    ('executive-summary', 'Executive summary', 'Decision', c1.page_exec),
    ('decision-analysis', 'Live, rent or sell', 'Decision', c1.page_decision),
    ('questions', 'Questions & missing evidence', 'Decision', c2.page_questions),
    ('suggestions', 'Suggestions for review', 'Decision', c2.page_suggestions),
    ('projections', 'Year-by-year projections', 'The numbers', c1.page_projections),
    ('property-tax', 'Property tax & history', 'The numbers', c2.page_tax),
    ('operating-costs', 'Costs & insurance', 'The numbers', c2.page_cost),
    ('black-swan', 'Black-swan conditions', 'Stress', c1.page_black_swan),
    ('estate-thresholds', 'Estate tax & headroom', 'Tax & process', c3.page_estate),
    ('inheritance-process', 'Inheritance step by step', 'Tax & process', c3.page_process),
    ('law-watchlist', 'Law watchlist', 'Tax & process', c3.page_law),
    ('flagged-for-review', 'Flagged for review', 'Evidence', c3.page_flagged),
    ('sources', 'Official source ledger', 'Evidence', c3.page_sources),
    ('privacy', 'Privacy & rounding', 'Evidence', c3.page_privacy),
]

REDIRECTS = {'costs': 'operating-costs', 'decisions': 'decision-analysis',
             'flagged': 'flagged-for-review', 'open-questions': 'questions',
             'methodology': 'privacy', 'black-swan-scenarios': 'black-swan',
             'inheritance-law': 'law-watchlist'}

HEAD = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Two-property inheritance decision brief. Official sources, rounded figures, stated assumptions and open questions.">
<title>{title} &middot; Two-property decision brief</title>
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script></head>'''


def nav_html(active, prefix):
    out, group = [], None
    for key, title, cat, _ in PAGES:
        if cat != group:
            out.append(f'<div class="nav-group">{E(cat)}</div>')
            group = cat
        url = prefix + 'index.html' if key == 'index' else prefix + f'pages/{key}.html'
        cur = ' aria-current="page"' if key == active else ''
        out.append(f'<a href="{url}"{cur}>{E(title)}</a>')
    return ''.join(out)


def build():
    (ROOT / 'pages').mkdir(exist_ok=True)
    (ROOT / 'assets').mkdir(exist_ok=True)
    manifest = []
    for key, title, cat, fn in PAGES:
        home = key == 'index'
        prefix = '' if home else '../'
        target = ROOT / 'index.html' if home else ROOT / 'pages' / f'{key}.html'
        body = fn()
        heading = '' if home else (
            f'<div class="page-heading"><span class="eyebrow">{E(cat.upper())}</span><h1>{E(title)}</h1>'
            f'<p class="lead">Current law, owner figures, stated assumptions and open questions, kept apart on purpose.</p></div>')
        html = HEAD.format(title=E(title), prefix=prefix) + f'''
<body><a class="skip" href="#main">Skip to content</a><div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">&#9672;</span><span>TWO-PROPERTY<br>DECISION BRIEF</span></a>
<p class="sidebar-note">A home to inherit.<br>A home already owned.</p>
<nav aria-label="Main navigation">{nav_html(key, prefix)}</nav>
<div class="sidebar-bottom">Figures rounded to $10 &middot; no private identity<br>Sources checked {DATE}</div></aside>
<div class="workspace"><header class="topbar"><span>BRIEF / {E(cat.upper())}</span>
<div><span class="privacy-dot" aria-hidden="true"></span> Privacy first
<button class="print-button" id="print-page" type="button">Print</button></div></header>
<main id="main">{heading}{body}</main>
<footer><strong>Planning, not advice.</strong> Not tax, legal, insurance, appraisal or investment advice. A link verifies a rule, never a private fact. Blank cells mean missing evidence, not zero. Every dollar figure is rounded to $10 and every projection is arithmetic on stated assumptions.<br>
<a href="{prefix}pages/privacy.html">Privacy and rounding</a> &middot; <a href="{prefix}pages/sources.html">Source ledger</a> &middot; <a href="{prefix}pages/flagged-for-review.html">Flagged for review</a></footer>
</div></div></body></html>'''
        target.write_text(html, encoding='utf-8')
        manifest.append(str(target.relative_to(ROOT)))
    for old, new in REDIRECTS.items():
        (ROOT / 'pages' / f'{old}.html').write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer">'
            f'<meta http-equiv="refresh" content="0; url={new}.html"><title>Page moved</title></head>'
            f'<body><a href="{new}.html">Continue to the updated page</a></body></html>', encoding='utf-8')
    # CSV of the case projections, rounded at write time.
    with (ROOT / 'assets' / 'case-projections.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['property', 'transfer_year', 'year', 'market_value', 'assessed_if_rented',
                    'assessed_if_occupied', 'bill_if_rented', 'bill_if_occupied', 'insurance',
                    'water', 'electricity', 'maintenance', 'rent', 'assumption_note'])
        for ty in (2040, 2045, 2050):
            for r in projection('A', transfer=ty):
                w.writerow(['A', ty, r['year'], rounded(r['value']), rounded(r['tax_assessed']),
                            rounded(r['tax_qualified']), rounded(r['bill_full']),
                            rounded(r['bill_qualified']), rounded(r['insurance']),
                            rounded(r['water']), rounded(r['electric']),
                            rounded(r['maintenance']), rounded(r['rent']),
                            'assumed 4% growth, 2% cap, assumed rent yield'])
        for r in projection('B'):
            w.writerow(['B', '', r['year'], rounded(r['value']), rounded(r['tax_assessed']),
                        rounded(r['tax_qualified']), rounded(r['bill_full']),
                        rounded(r['bill_qualified']), rounded(r['insurance']),
                        rounded(r['water']), rounded(r['electric']), rounded(r['maintenance']),
                        rounded(r['rent']), 'assumed 4% growth, 2% cap, owner rent held at 2.5% growth'])
    (ROOT / '_7adb71fc' / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Built {len(manifest)} pages, {len(REDIRECTS)} redirects and the case CSV.')


if __name__ == '__main__':
    build()
