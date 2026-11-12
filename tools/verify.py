#!/usr/bin/env python3
"""Verify the public static dashboard's structure and privacy boundaries.

This tool checks links, row status labels, source-register coverage, rounding,
noindex metadata, basic identifier patterns, blank private projection cells,
the synthetic index horizon, compatibility redirects and build independence.
It does NOT prove that a source supports a claim, a forecast is reliable, or
public Git history, deployments, caches or forks are clean.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
STATUS_LABELS = (
    "Unverified / withheld",
    "Illustrative assumption",
    "Source-linked; check applicability",
)
# Exact official domains that are not under .gov.
ALLOWED_HOSTS = {"docs.github.com", "sftreasurer.org"}
LEGACY_PRIVATE_PATHS = ("s179ec133", "_s9ad1da71", "_research", "_a24b1c8c")
COMPATIBILITY_REDIRECTS = {
    "costs.html": "operating-costs.html",
    "decisions.html": "decision-analysis.html",
    "flagged.html": "flagged-for-review.html",
    "properties.html": "property-tax.html",
}
CONFIG_EXCLUDES = (
    "tools", "s179ec133", "_s9ad1da71", "_research", "_a24b1c8c",
    "_1775f697", "COORDINATION.md", "README.md", ".gitignore",
)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.text = []
        self.headers = []
        self.rows = []
        self.in_thead = False
        self.in_tbody = False
        self.in_row = False
        self.in_cell = False
        self.cell_tag = None
        self.cell_text = []
        self.row_cells = []
        self.row_links = []
        self.robots_noindex = False
        self.refresh_target = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            content = attrs.get("content", "").lower().replace(" ", "")
            self.robots_noindex = "noindex" in content and "nofollow" in content
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            match = re.fullmatch(r"\s*0\s*;\s*url\s*=\s*(\S+)\s*", attrs.get("content", ""), re.I)
            if match:
                self.refresh_target = unquote(match.group(1))
        if tag == "a":
            href = attrs.get("href", "")
            self.links.append(href)
            if self.in_row and urlparse(href).scheme == "https":
                self.row_links.append(href)
        elif tag == "thead":
            self.in_thead = True
            self.headers = []
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_row = True
            self.row_cells = []
            self.row_links = []
        elif tag in ("th", "td") and (self.in_thead or self.in_row):
            self.in_cell = True
            self.cell_tag = tag
            self.cell_text = []

    def handle_endtag(self, tag):
        if tag in ("th", "td") and self.in_cell and self.cell_tag == tag:
            value = " ".join("".join(self.cell_text).split())
            if tag == "th" and self.in_thead:
                self.headers.append(value)
            elif tag == "td" and self.in_row:
                self.row_cells.append(value)
            self.in_cell = False
            self.cell_tag = None
            self.cell_text = []
        elif tag == "thead":
            self.in_thead = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_row:
            self.rows.append((list(self.headers), list(self.row_cells), list(self.row_links)))
            self.in_row = False

    def handle_data(self, data):
        self.text.append(data)
        if self.in_cell:
            self.cell_text.append(data)


def parse(path):
    parser = PageParser()
    raw = path.read_text(encoding="utf-8")
    parser.feed(raw)
    return parser, raw


def is_official_https(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host.endswith(".gov") or host.endswith(".ca.gov") or host in ALLOWED_HOSTS)


def main():
    errors = []
    total_rows = 0
    external_by_page = {}
    candidates = [ROOT / "index.html", *sorted((ROOT / "pages").glob("*.html"))]
    files = [path for path in candidates if path.is_file()]
    if not (ROOT / "index.html").is_file():
        errors.append("missing root index.html")
    if not files:
        errors.append("no public HTML files found")
    for name in COMPATIBILITY_REDIRECTS:
        if not (ROOT / "pages" / name).is_file():
            errors.append(f"missing compatibility redirect: pages/{name}")

    for path in files:
        page, raw = parse(path)
        visible = " ".join(page.text)
        external_by_page[path] = {
            link for link in page.links if urlparse(link).scheme == "https"
        }
        if not page.robots_noindex:
            errors.append(f"{path.relative_to(ROOT)}: missing noindex,nofollow metadata")

        for headers, cells, row_links in page.rows:
            total_rows += 1
            if len(cells) != len(headers):
                errors.append(f"{path.relative_to(ROOT)}: row has {len(cells)} cells; expected {len(headers)}")
                continue
            if "Status" not in headers or "Official source" not in headers:
                errors.append(f"{path.relative_to(ROOT)}: table missing Status / Official source columns")
                continue
            status = cells[headers.index("Status")]
            if not any(label in status for label in STATUS_LABELS):
                errors.append(f"{path.relative_to(ROOT)}: table row lacks a recognized verification status")
            source_index = headers.index("Official source")
            if not row_links or not cells[source_index]:
                errors.append(f"{path.relative_to(ROOT)}: table row lacks an official source link")
            elif not any(is_official_https(link) for link in row_links):
                errors.append(f"{path.relative_to(ROOT)}: table row links only to non-official sources")

        for link in page.links:
            parsed = urlparse(link)
            if parsed.scheme:
                if not is_official_https(link):
                    errors.append(f"{path.relative_to(ROOT)}: non-official or non-HTTPS external link")
                continue
            if not link or link.startswith("mailto:"):
                errors.append(f"{path.relative_to(ROOT)}: empty or email link")
                continue
            target_path = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
            if not target_path.is_file() or not target_path.is_relative_to(ROOT):
                errors.append(f"{path.relative_to(ROOT)}: broken or escaping local link")
                continue
            if parsed.fragment:
                target_parser, _ = parse(target_path)
                if parsed.fragment not in target_parser.ids:
                    errors.append(f"{path.relative_to(ROOT)}: broken local anchor #{parsed.fragment}")

        # Generic patterns only: never embed household values or hashes in a
        # public verifier. Scan raw HTML as well as rendered text so metadata and
        # links are included.
        private_patterns = (
            r"\b9\d{4}(?:-\d{4})?\b",  # California ZIP / ZIP+4
            r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN-shaped identifier
            r"\bAPN\s*[:#]",  # parcel-number label with a supplied value
            r"\b\d{1,6}\s+[A-Z0-9.'-]+(?:\s+[A-Z0-9.'-]+){0,3}\s+(?:street|st\.?|avenue|ave\.?|road|rd\.?|boulevard|blvd\.?|drive|dr\.?|lane|ln\.?|place|pl\.?|way)\b",
        )
        for pattern in private_patterns:
            if re.search(pattern, raw, re.I):
                errors.append(f"{path.relative_to(ROOT)}: possible private identifier")
                break

        for match in re.finditer(r"\$([\d,]+)(?:\.(\d+))?", visible):
            amount = int(match.group(1).replace(",", ""))
            decimals = match.group(2)
            if amount >= 1000 and (decimals or amount % 10):
                errors.append(f"{path.relative_to(ROOT)}: dollar amount is not rounded to $10")
                break

        if path.name in {"flagged-for-review.html", "privacy.html"} and "Location wording." not in visible:
            errors.append(f"{path.relative_to(ROOT)}: location-wording privacy notice missing")

        if path.name == "projections.html":
            years = []
            for headers, cells, _ in page.rows:
                if not {"Year", "Market value", "Operating costs"}.issubset(headers):
                    continue
                year_index = headers.index("Year")
                first_private = headers.index("Market value")
                last_private = headers.index("Operating costs")
                if len(cells) != len(headers):
                    continue
                years.append(cells[year_index])
                if any(cells[i].strip() for i in range(first_private, last_private + 1)):
                    errors.append("pages/projections.html: case-specific projection cell is not blank")
            if years != [str(year) for year in range(2026, 2076)]:
                errors.append("pages/projections.html: expected 50 blank annual rows for 2026–2075")

        if path.name == "black-swan-scenarios.html":
            if "$" in visible:
                errors.append("pages/black-swan-scenarios.html: synthetic index page must not contain dollar amounts")
            index_years = []
            for headers, cells, _ in page.rows:
                if {"Year", "Smooth home", "Stress home", "Smooth prices", "Stress prices"}.issubset(headers):
                    if len(cells) == len(headers):
                        index_years.append(cells[headers.index("Year")])
            if index_years != [str(year) for year in range(2026, 2076)]:
                errors.append("pages/black-swan-scenarios.html: synthetic index must cover 2026–2075")

        if path.name in COMPATIBILITY_REDIRECTS:
            expected = COMPATIBILITY_REDIRECTS[path.name]
            target = (path.parent / (page.refresh_target or "")).resolve()
            if page.refresh_target != expected or not target.is_file() or not target.is_relative_to(ROOT):
                errors.append(f"{path.relative_to(ROOT)}: compatibility redirect missing or points to the wrong page")

        if not page.rows and path.name not in COMPATIBILITY_REDIRECTS:
            errors.append(f"{path.relative_to(ROOT)}: expected a sourced table")

    source_page = ROOT / "pages" / "sources.html"
    if source_page in external_by_page:
        registry_urls = external_by_page[source_page]
        for path, links in external_by_page.items():
            if path == source_page:
                continue
            missing = links - registry_urls
            if missing:
                errors.append(f"{path.relative_to(ROOT)}: external URL absent from official source register")

    if not (ROOT / "_config.yml").is_file() or (ROOT / ".nojekyll").exists():
        errors.append("missing Jekyll config or .nojekyll disables its exclusions")
    else:
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        for item in CONFIG_EXCLUDES:
            if f"  - {item}" not in config:
                errors.append(f"Jekyll config missing exclusion: {item}")

    for item in LEGACY_PRIVATE_PATHS:
        if (ROOT / item).exists():
            errors.append(f"obsolete case-derived working directory remains in current tree: {item}")

    builder_path = ROOT / "tools" / "build.py"
    if not builder_path.is_file():
        errors.append("missing standalone public-site builder")
    else:
        builder = builder_path.read_text(encoding="utf-8")
        for item in LEGACY_PRIVATE_PATHS:
            if item in builder:
                errors.append(f"public-site builder still references removed private path: {item}")

    print(f"{len(files)} pages | {total_rows} table rows | {sum(map(len, external_by_page.values()))} external links | {len(errors)} failures")
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
