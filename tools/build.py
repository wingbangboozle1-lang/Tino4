#!/usr/bin/env python3
"""Build generic, source-linked public content with blank household values.
Never reads household input files or the retired calculation model. No network, external package or Jekyll plugin.
"""
import json
import sys
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'_7eff7e24'))
from content import PAGES, content
from evidence import DATE


def build():
    (ROOT/'pages').mkdir(exist_ok=True)
    (ROOT/'assets').mkdir(exist_ok=True)
    manifest=[]
    for key,title,category in PAGES:
        home=key=='index'
        prefix='' if home else '../'
        target=ROOT/'index.html' if home else ROOT/'pages'/f'{key}.html'
        nav=''; group=None
        for k,t,c in PAGES:
            if c!=group:
                nav+=f'<div class="nav-group">{escape(c)}</div>'; group=c
            url=prefix+'index.html' if k=='index' else prefix+f'pages/{k}.html'
            nav+=f'<a href="{url}"'+(' aria-current="page"' if key==k else '')+f'>{escape(t)}</a>'
        body=content(key)
        heading='' if home else f'<div class="page-heading"><span class="eyebrow">{escape(category.upper())}</span><h1>{escape(title)}</h1><p class="lead">A clear distinction between current law, missing evidence and review-only comparisons.</p></div>'
        html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Privacy-first inheritance decision research. Current official rules, evidence gaps, review-only suggestions and blank household projections.">
<title>{escape(title)} · Two-property decision brief</title><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>THE PROPERTY<br>DECISION BRIEF</span></a><p class="sidebar-note">One inheritance.<br>A whole-household decision.</p><nav aria-label="Main navigation">{nav}</nav><div class="sidebar-bottom">Public research · private details withheld<br>Review updated {DATE}</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / {escape(category.upper())}</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy first <button class="print-button" id="print-page" type="button">Print brief</button></div></header>
<main id="main">{heading}{body}</main><footer><strong>Planning, not execution.</strong> Not tax, legal, insurance, appraisal or investment advice. Official links verify only the stated source scope. Blank cells mean missing evidence, not zero; no household numerical forecast is published.<br><a href="{prefix}pages/privacy.html">Privacy boundary</a> · <a href="{prefix}pages/methodology.html">Methods</a> · <a href="{prefix}pages/flagged-for-review.html">Open flags</a></footer></div></div></body></html>'''
        target.write_text(html,encoding='utf-8')
        manifest.append(str(target.relative_to(ROOT)))
    for old, new in {'costs':'operating-costs','decisions':'decision-analysis','flagged':'flagged-for-review','open-questions':'questions'}.items():
        (ROOT/'pages'/f'{old}.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta http-equiv="refresh" content="0; url={new}.html"><title>Page moved</title></head><body><a href="{new}.html">Continue to the updated page</a></body></html>')
    (ROOT/'_7eff7e24'/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(manifest)} public pages. No household inputs or monetary projections loaded.')

if __name__=='__main__': build()
