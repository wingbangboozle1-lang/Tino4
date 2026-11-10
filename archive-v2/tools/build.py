#!/usr/bin/env python3
"""Render the static site from data/*.json.

Run:  python3 tools/build.py
Out:  index.html, pages/*.html
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pages_core
import pages_analysis
import pages_legal
from common import write

BUILD = [
    ("index.html", pages_core.index),
    ("pages/properties.html", pages_core.properties),
    ("pages/taxes.html", pages_core.taxes),
    ("pages/costs.html", pages_analysis.costs),
    ("pages/decisions.html", pages_analysis.decisions),
    ("pages/process.html", pages_legal.process),
    ("pages/laws.html", pages_legal.laws),
    ("pages/sources.html", pages_legal.sources),
    ("pages/flagged.html", pages_legal.flagged),
]


def main():
    total = 0
    for path, fn in BUILD:
        html = fn()
        write(path, html)
        total += len(html)
        print(f"  wrote {path} ({len(html):,} bytes)")
    print(f"Built {len(BUILD)} pages, {total:,} bytes total.")


if __name__ == "__main__":
    main()
