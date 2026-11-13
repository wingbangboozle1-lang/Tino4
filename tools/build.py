#!/usr/bin/env python3
"""Build public pages and the case projection CSV from rounded owner inputs
and labeled assumptions only. No network, external package or private file."""
import csv
import sys
from pathlib import Path
from html import escape
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7eff7e24'))
from content import PAGES, content
from case import (INHERITANCE_YEARS, START, END, a_projection, b_projection, rounded)
from evidence import SOURCES, DATE


def build():
    (ROOT / 'pages').mkdir(exist_ok=True)
    (ROOT / 'assets').mkdir(exist_ok=True)
    manifest = []
    for key, title, category in PAGES:
        home = key == 'index'
        prefix = '' if home else '../'
        target = ROOT / 'index.html' if home else ROOT / 'pages' / f'{key}.html'
        nav = ''
        group = None
        for k, t, c in PAGES:
            if c != group:
                nav += f'<div class="nav-group">{escape(c)}</div>'
                group = c
            url = prefix + 'index.html' if k == 'index' else prefix + f'pages/{k}.html'
            nav += f'<a href="{url}"' + (' aria-current="page"' if key == k else '') + f'>{escape(t)}</a>'
        body = content(key)
        heading = '' if home else f'<div class="page-heading"><span class="eyebrow">{escape(category.upper())}</span><h1>{escape(title)}</h1><p class="lead">Rounded case figures, labeled assumptions and verified rules \u2014 separated clearly so nothing reads as a promise.</p></div>'
        html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Two-property inheritance decision brief. Rounded case figures, verified rules, projections and a ranked conditional plan.">
<title>{escape(title)} · Two-property decision brief</title><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>THE PROPERTY<br>DECISION BRIEF</span></a><p class="sidebar-note">One inheritance.<br>A whole-household decision.</p><nav aria-label="Main navigation">{nav}</nav><div class="sidebar-bottom">Figures rounded to $10 · Sources checked {DATE}<br>Research product — not advice</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / {escape(category.upper())}</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy first <button class="print-button" id="print-page" type="button">Print brief</button></div></header>
<main id="main">{heading}{body}</main><footer><strong>Planning, not execution.</strong> Not tax, legal, insurance, appraisal or investment advice. Official links verify only the stated source scope. Owner-supplied figures are rounded to $10 and unverified; projections are assumption outputs, not forecasts. Blank cells mean missing evidence, not zero.<br><a href="{prefix}pages/privacy.html">Privacy boundary</a> · <a href="{prefix}pages/methodology.html">Methods</a> · <a href="{prefix}pages/flagged-for-review.html">Open flags</a></footer></div></div></body></html>'''
        target.write_text(html, encoding='utf-8')
        manifest.append(str(target.relative_to(ROOT)))
    for old, new in {'costs': 'operating-costs', 'decisions': 'decision-analysis', 'flagged': 'flagged-for-review', 'open-questions': 'questions'}.items():
        (ROOT / 'pages' / f'{old}.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta http-equiv="refresh" content="0; url={new}.html"><title>Page moved</title></head><body><a href="{new}.html">Continue to the updated page</a></body></html>')
    with (ROOT / 'assets' / 'projections.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['kind', 'transfer_year', 'year', 'a_market_value', 'a_assessment_rent_sell',
                         'a_tax_rent_sell', 'a_assessment_live', 'a_tax_live', 'b_market_value',
                         'b_assessment', 'b_tax', 'official_context'])
        bmap = {r['year']: r for r in b_projection()}
        for y in INHERITANCE_YEARS:
            for r in a_projection(y):
                b = bmap[r['year']]
                writer.writerow(['CASE_PROJECTION_ASSUMPTIONS', y, r['year'],
                                 rounded(r['value']), rounded(r['av_rent']), rounded(r['tax_rent']),
                                 rounded(r['av_live']), rounded(r['tax_live']),
                                 rounded(b['value']), rounded(b['av']), rounded(b['tax']),
                                 SOURCES['prop13'][1]])
    stale = ROOT / 'assets' / 'synthetic-projections.csv'
    if stale.exists():
        stale.unlink()
    (ROOT / '_7eff7e24' / 'manifest.json').write_text(__import__('json').dumps(manifest, indent=2) + '\n')
    print(f'Built {len(manifest)} public pages and 561 case projection CSV rows from rounded inputs.')


if __name__ == '__main__':
    build()
