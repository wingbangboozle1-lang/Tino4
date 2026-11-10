#!/usr/bin/env python3
"""Dependency-free structural/privacy audit for the static site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_NON_GOV = {"sfassessor.org", "sfelections.org"}
class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.all_links = []
        self.rows = []
        self.row = None
        self.cell = None
        self.in_table = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            href = attrs.get("href", "")
            self.all_links.append(href)
            if self.row is not None and self.cell is not None and href.startswith("https://"):
                self.cell.append(href)
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def official(url):
    host = (urlparse(url).hostname or "").lower()
    return host.endswith(".gov") or any(host == domain or host.endswith("." + domain) for domain in OFFICIAL_NON_GOV)

errors = []
for page in sorted(ROOT.glob("*.html")):
    text = page.read_text(encoding="utf-8")
    audit = Audit()
    audit.feed(text)
    for row_no, row in enumerate(audit.rows, 1):
        if not any(cell for cell in row):
            continue  # header rows
        citations = [url for cell in row for url in cell]
        if not citations:
            errors.append(f"{page.name}: table row {row_no} has no HTTPS source link")
        elif not all(official(url) for url in citations):
            errors.append(f"{page.name}: table row {row_no} has a non-official citation: {citations}")
    for href in audit.all_links:
        if not href or href.startswith(("https://", "http://", "mailto:", "tel:", "#")):
            continue
        local = href.split("#", 1)[0]
        if local and not (page.parent / local).resolve().exists():
            errors.append(f"{page.name}: broken local link {href}")
    print(f"checked {page.name}: {len(audit.rows)} table rows, {len(audit.all_links)} links")

if errors:
    print("\nFAIL")
    print("\n".join(f"- {e}" for e in errors))
    raise SystemExit(1)
print("PASS: table citations and local links")
