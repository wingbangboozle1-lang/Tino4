#!/usr/bin/env python3
"""Strict structural, link, official-domain, and $10-rounding verifier for
`_s9ad1da71/site/` (or repository root when passed `--site-dir .`)."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class PageCheck(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.rows: list[tuple[list[str], int, int]] = []
        self.row_links: list[str] | None = None
        self.in_head = False
        self.in_body = False
        self.cols = 0
        self.head_count = 0
        self.cell_count = 0
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "a":
            href = a.get("href") or ""
            self.links.append(href)
            if self.row_links is not None and urlparse(href).scheme == "https":
                self.row_links.append(href)
        elif tag == "thead":
            self.in_head = True
            self.head_count = 0
        elif tag == "tbody":
            self.in_body = True
        elif tag == "tr" and self.in_body:
            self.row_links = []
            self.cell_count = 0
        elif tag == "th" and self.in_head:
            self.head_count += 1
        elif tag == "td" and self.row_links is not None:
            self.cell_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "thead":
            self.in_head = False
            self.cols = self.head_count
        elif tag == "tbody":
            self.in_body = False
        elif tag == "tr" and self.row_links is not None:
            self.rows.append((self.row_links, self.cell_count, self.cols))
            self.row_links = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def verify_site(site_dir: Path) -> tuple[int, int, list[str]]:
    errors: list[str] = []
    files = [site_dir / "index.html", *sorted((site_dir / "pages").glob("*.html"))]
    if len(files) != 19:
        errors.append(f"Expected 19 HTML pages, found {len(files)}")
    if not (site_dir / "assets" / "style.css").is_file():
        errors.append("Missing assets/style.css")

    total_rows = 0
    for p in files:
        if not p.is_file():
            errors.append(f"Missing {p}")
            continue
        chk = PageCheck()
        chk.feed(p.read_text(encoding="utf-8"))
        if not chk.rows:
            errors.append(f"{p.name}: zero table rows")
        for rlinks, cells, cols in chk.rows:
            total_rows += 1
            if not rlinks:
                errors.append(f"{p.name}: table row missing official HTTPS source link")
            if cells != cols:
                errors.append(f"{p.name}: row has {cells} cells vs {cols} headers")
        for href in chk.links:
            u = urlparse(href)
            if u.scheme:
                host = u.hostname or ""
                if u.scheme != "https" or not (host.endswith(".gov") or host.endswith(".ca.gov")):
                    errors.append(f"{p.name}: non-.gov external link {href}")
            elif href and not href.startswith("#"):
                target = (p.parent / unquote(u.path)).resolve()
                if not target.is_file() or not target.is_relative_to(site_dir.resolve()):
                    errors.append(f"{p.name}: broken local link {href}")
        txt = " ".join(chk.text)
        for m in re.finditer(r"\$([\d,]+)(?![\d,.])", txt):
            val = int(m.group(1).replace(",", ""))
            if val % 10 != 0:
                errors.append(f"{p.name}: unrounded dollar integer ${m.group(1)}")

    return len(files), total_rows, errors


if __name__ == "__main__":
    pkg_root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", default=str(pkg_root / "site"))
    args = ap.parse_args()
    sdir = Path(args.site_dir)
    npages, nrows, errs = verify_site(sdir)
    # Also scan all code/markdown/json inside _s9ad1da71 for any integer $ >= $100 not % 10 == 0
    for f in sorted(pkg_root.rglob("*")):
        if f.is_file() and f.suffix in {".py", ".md", ".json"}:
            t = f.read_text(encoding="utf-8")
            for m in re.finditer(r"\$([\d,]{3,})(?![\d,.])", t):
                v = int(m.group(1).replace(",", ""))
                if v % 10 != 0:
                    errs.append(f"{f.relative_to(pkg_root)}: unrounded dollar integer ${m.group(1)}")
    print(f"Verified {npages} pages, {nrows} source-linked rows; {len(errs)} errors")
    for e in errs:
        print("ERROR:", e)
    sys.exit(1 if errs else 0)
