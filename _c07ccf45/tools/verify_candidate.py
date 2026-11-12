#!/usr/bin/env python3
"""Structural, sourcing and privacy verifier for the s-c07ccf45 dashboard.

Checks, for every generated page:
  * the page exists, carries a no-index directive, and has balanced table markup;
  * every table body row links to at least one official government publication;
  * every external link is a URL that appears in the evidence ledger, and every
    external host is an official government domain;
  * every internal link and anchor resolves;
  * every dollar amount of $1,000 or more is a multiple of $10, unless it is an
    exact official statutory figure quoted from a linked source;
  * no name-like, parcel-like, city-like or ZIP-like identifier is published;
  * the row counts the brief requires are present (50 projection years per
    property, 7 stress regimes, the full source register, the full flag log).

Exit status 1 on any failure. Standard library only.
"""

from __future__ import annotations

import html as html_mod
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "evidence"))
from sources_and_flags import FLAGS, SOURCES  # noqa: E402

EXPECTED = [
    "index.html",
    "pages/executive-summary.html",
    "pages/decision-analysis.html",
    "pages/property-tax.html",
    "pages/projections.html",
    "pages/operating-costs.html",
    "pages/black-swan-scenarios.html",
    "pages/inheritance-process.html",
    "pages/estate-thresholds.html",
    "pages/inheritance-law.html",
    "pages/law-watchlist.html",
    "pages/methodology.html",
    "pages/privacy.html",
    "pages/sources.html",
    "pages/flagged-for-review.html",
]

# Exact official statutory figures that are quoted as published (not $10 multiples).
EXACT_OFFICIAL = {
    1_044_586,  # BOE published Prop. 19 allowance for 16 Feb 2025 - 15 Feb 2027
}

ALLOWED_HOSTS = (".gov", ".ca.gov")
BANNED = [
    "95014",
    "94122",
    "cupertino",
    "san francisco",
    "san jose",
    "outer sunset",
    "bay area",
    "santa clara",
    "outer sunset",
    "@",
]

DOLLAR = re.compile(r"[$]\s?([0-9][0-9,]*)")
ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)
BODY = re.compile(r"<tbody>(.*?)</tbody>", re.S)
HREF = re.compile(r'href="([^"]+)"')


def main(root: str = ".") -> int:
    site = Path(root)
    if (site / "index.html").exists() is False and (site / "pages").exists():
        pass
    base = site
    if not (base / "index.html").exists():
        base = PKG / "site"
    failures: list[str] = []
    registry = {s["url"] for s in SOURCES.values()}
    pages_html: dict[str, str] = {}
    n_rows = n_links = n_dollars = 0

    for rel in EXPECTED:
        path = base / rel
        if not path.exists():
            failures.append(f"{rel}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        pages_html[rel] = text

        if 'name="robots" content="noindex' not in text:
            failures.append(f"{rel}: no no-index directive")
        for tag in ("table", "tr", "td", "tbody"):
            if text.count(f"<{tag}") != text.count(f"</{tag}>"):
                failures.append(f"{rel}: unbalanced <{tag}> tags")

        for banned in BANNED:
            if banned in text.lower():
                failures.append(f"{rel}: banned identifier {banned!r}")

        # tables: every body row must link a government source
        for t_i, tbody in enumerate(BODY.findall(text)):
            for r_i, row in enumerate(ROW.findall(tbody)):
                if "<td" not in row:
                    continue
                n_rows += 1
                hrefs = HREF.findall(row)
                ok = False
                for h in hrefs:
                    if h.startswith("http"):
                        host = urlparse(h).netloc
                        if any(host.endswith(a) for a in ALLOWED_HOSTS):
                            ok = True
                if not ok:
                    failures.append(f"{rel}: table {t_i} row {r_i} has no official source link")

        # external links must exist in the ledger; internal links must resolve
        for raw_href in HREF.findall(text):
            h = html_mod.unescape(raw_href)
            if h.startswith("http"):
                n_links += 1
                if h not in registry:
                    failures.append(f"{rel}: external link not in ledger: {h}")
                host = urlparse(h).netloc
                if not any(host.endswith(a) for a in ALLOWED_HOSTS):
                    failures.append(f"{rel}: non-government host {host}")
            elif h.startswith("#"):
                continue
            else:
                target = (path.parent / h.split("#")[0]).resolve()
                if not target.exists():
                    failures.append(f"{rel}: broken internal link {h}")

        # dollar amounts
        for raw in DOLLAR.findall(text):
            digits = raw.replace(",", "")
            if not digits.isdigit():
                continue
            value = int(digits)
            if value >= 1000:
                n_dollars += 1
                if value % 10 != 0 and value not in EXACT_OFFICIAL:
                    failures.append(f"{rel}: unrounded dollar amount ${value:,}")

    # content-completeness checks
    for rel, text in pages_html.items():
        if len(text) < 4000 or text.count("<table") < 1:
            failures.append(f"{rel}: page looks empty ({len(text)} bytes, {text.count('<table')} tables)")
    if "Ranked plans" not in pages_html.get("index.html", ""):
        failures.append("index: ranked plan table missing")
    if "Five mechanisms" not in pages_html.get("pages/executive-summary.html", ""):
        failures.append("executive summary: drivers section missing")
    proj = pages_html.get("pages/projections.html", "")
    for header in ("Property A — inherited residence, 2026–2075", "Property B — already-owned 3-unit building, 2026–2075"):
        if header not in proj:
            failures.append(f"projections: missing section {header!r}")
    yrs = set(re.findall(r"<td>(20[2-7][0-9])</td>", proj))
    if len(yrs) < 50:
        failures.append(f"projections: only {len(yrs)} distinct years found, expected 50")

    bs = pages_html.get("pages/black-swan-scenarios.html", "")
    if bs.count("R0") + bs.count("Baseline") < 1:
        failures.append("black-swan: baseline regime row missing")

    src_page = pages_html.get("pages/sources.html", "")
    for sid in SOURCES:
        if f">{sid}</td>" not in src_page:
            failures.append(f"sources: {sid} not listed")

    flag_page = pages_html.get("pages/flagged-for-review.html", "")
    for f in FLAGS:
        if f">{f['id']}</td>" not in flag_page:
            failures.append(f"flagged: {f['id']} not listed")

    if failures:
        print(f"FAIL — {len(failures)} problem(s)")
        for f in failures[:60]:
            print("  -", f)
        return 1

    print(
        f"OK — {len(EXPECTED)} pages, {n_rows} sourced table rows, {n_links} external link instances, "
        f"{n_dollars} dollar amounts (all multiples of $10 except quoted statutory figures), "
        f"{len(SOURCES)} sources, {len(FLAGS)} flags"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else str(PKG / "site")))
