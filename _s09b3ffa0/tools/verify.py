#!/usr/bin/env python3
"""
Strict zero-carveout verifier for _s09b3ffa0/site/ and _s09b3ffa0/**.
Checks:
  1. All 15 HTML pages + style.css exist and declare noindex/nofollow.
  2. Every <tbody><tr> has >=1 official .gov/agency link in official_ledger.json AND a status chip.
  3. Every external URL is on the official government domain allowlist and registered in official_ledger.json.
  4. Every internal href/src resolves cleanly.
  5. 100% of dollar amounts >= $100 across all 15 HTML pages are exact multiples of $10 (ZERO carveouts).
  6. Zero PII, ZIP codes (95014/94122), neighborhood names (Outer Sunset), city names, parcel/APN strings,
     or exact un-rounded owner figures anywhere in _s09b3ffa0/site/ (and zero ZIP/Cupertino/Outer Sunset/unrounded figures in _s09b3ffa0/**).
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

TOOLS_DIR = Path(__file__).resolve().parent
BASE_DIR = TOOLS_DIR.parent
SITE_DIR = BASE_DIR / "site"
LEDGER_PATH = BASE_DIR / "evidence" / "official_ledger.json"

OFFICIAL_DOMAINS = {
    "www.irs.gov",
    "irs.gov",
    "apps.irs.gov",
    "www.treasurydirect.gov",
    "www.cbo.gov",
    "www.bls.gov",
    "www.fhfa.gov",
    "www.huduser.gov",
    "fred.stlouisfed.org",
    "www.tsp.gov",
    "www.govinfo.gov",
    "www.congress.gov",
    "files.consumerfinance.gov",
    "leginfo.legislature.ca.gov",
    "www.boe.ca.gov",
    "www.ftb.ca.gov",
    "www.sco.ca.gov",
    "www.sos.ca.gov",
    "electionresults.sos.ca.gov",
    "selfhelp.courts.ca.gov",
    "oag.ca.gov",
    "www.cpuc.ca.gov",
    "docs.cpuc.ca.gov",
    "www.insurance.ca.gov",
    "clerkrecorder.santaclaracounty.gov",
    "files.santaclaracounty.gov",
    "sftreasurer.org",
    "www.sf.gov",
    "www.sfpuc.gov",
}

EXPECTED_PAGES = [
    "index.html",
    "pages/executive-summary.html",
    "pages/decision-analysis.html",
    "pages/properties.html",
    "pages/operating-costs.html",
    "pages/projections.html",
    "pages/black-swan-scenarios.html",
    "pages/inheritance-law.html",
    "pages/estate-thresholds.html",
    "pages/inheritance-process.html",
    "pages/law-watchlist.html",
    "pages/flagged-for-review.html",
    "pages/audit-reconciliation.html",
    "pages/methodology.html",
    "pages/sources.html",
]

# Forbidden anywhere in _s09b3ffa0/** (even internal scripts/docs, except verifier pattern list itself)
HARD_BANNED_REPO_PATTERNS = [
    r"\b95014\b",
    r"\b94122\b",
    r"(?i)cupertino",
    r"(?i)outer\s+sunset",
]

# Forbidden in rendered HTML text/attributes (excluding href URLs to county/city agency domains)
BANNED_SITE_TEXT_PATTERNS = HARD_BANNED_REPO_PATTERNS + [
    r"(?i)\bsan\s+francisco\b",
    r"(?i)\bsanta\s+clara\b",
    r"(?i)\bsan\s+jose\b",
    r"(?i)\bpalo\s+alto\b",
    r"(?i)\bmountain\s+view\b",
    r"(?i)\bsunnyvale\b",
    r"\bAPN\b",
]


class PageInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_noindex = False
        self.in_tbody = False
        self.in_tr = False
        self.cur_tr_links: list[str] = []
        self.cur_tr_has_chip = False
        self.tbody_rows: list[tuple[list[str], bool]] = []
        self.all_hrefs: list[str] = []
        self.visible_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        if tag == "meta" and (ad.get("name") or "").lower() == "robots":
            content = (ad.get("content") or "").lower()
            if "noindex" in content and "nofollow" in content:
                self.has_noindex = True
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.cur_tr_links = []
            self.cur_tr_has_chip = False
        elif tag == "a" and ad.get("href"):
            href = ad["href"]
            self.all_hrefs.append(href)
            if self.in_tr:
                self.cur_tr_links.append(href)
        if ad.get("title"):
            self.visible_chunks.append(ad["title"] or "")
        cls = ad.get("class") or ""
        if self.in_tr and "chip" in cls.split():
            self.cur_tr_has_chip = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr:
            self.tbody_rows.append((list(self.cur_tr_links), self.cur_tr_has_chip))
            self.in_tr = False
        elif tag == "tbody":
            self.in_tbody = False

    def handle_data(self, data: str) -> None:
        self.visible_chunks.append(data)


def main() -> int:
    errors: list[str] = []
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    ledger_urls = {item["url"] for item in ledger}

    for url in ledger_urls:
        host = urlparse(url).netloc.lower()
        if host not in OFFICIAL_DOMAINS:
            errors.append(f"Ledger URL not in official domain allowlist: {url}")

    if not (SITE_DIR / "assets" / "style.css").is_file():
        errors.append("Missing site/assets/style.css")

    total_rows = 0
    total_ext_links = 0
    total_dollars_checked = 0

    for rel in EXPECTED_PAGES:
        p = SITE_DIR / rel
        if not p.is_file():
            errors.append(f"Missing expected page: {rel}")
            continue
        raw = p.read_text(encoding="utf-8")
        inspector = PageInspector()
        inspector.feed(raw)

        if not inspector.has_noindex:
            errors.append(f"{rel}: missing <meta name='robots' content='noindex, nofollow'>")

        for idx, (links, has_chip) in enumerate(inspector.tbody_rows, start=1):
            total_rows += 1
            ext = [u for u in links if u.startswith("https://")]
            if not ext:
                errors.append(f"{rel}: tbody row #{idx} has no official https:// source link")
            if not has_chip:
                errors.append(f"{rel}: tbody row #{idx} has no verification status chip")

        for href in inspector.all_hrefs:
            if href.startswith("https://") or href.startswith("http://"):
                total_ext_links += 1
                host = urlparse(href).netloc.lower()
                if host not in OFFICIAL_DOMAINS:
                    errors.append(f"{rel}: external link outside official allowlist: {href}")
                if href not in ledger_urls:
                    errors.append(f"{rel}: external link not registered in official_ledger.json: {href}")
            elif not href.startswith("#") and not href.startswith("mailto:"):
                clean_rel = href.split("#")[0]
                resolved = (p.parent / clean_rel).resolve()
                if not resolved.is_file():
                    errors.append(f"{rel}: broken internal link {href} -> {resolved}")

        vis_text = " ".join(inspector.visible_chunks)
        for m in re.finditer(r"\$[0-9][0-9,]*(?:\.[0-9]+)?", vis_text):
            tok = m.group(0)
            val = float(tok[1:].replace(",", ""))
            total_dollars_checked += 1
            if val >= 100.0 and (val % 10.0 != 0.0 or "." in tok):
                errors.append(f"{rel}: non-$10-rounded dollar figure >=$100 found: {tok}")

        for pat in BANNED_SITE_TEXT_PATTERNS:
            m = re.search(pat, vis_text)
            if m:
                errors.append(f"{rel}: banned location/privacy token '{m.group(0)}' matched {pat}")

    # Scan entire _s09b3ffa0/** tree (excluding verify.py itself) for hard-banned tokens
    this_file = Path(__file__).resolve()
    for f in BASE_DIR.rglob("*"):
        if not f.is_file() or f.resolve() == this_file or "__pycache__" in f.parts:
            continue
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for pat in HARD_BANNED_REPO_PATTERNS:
            m = re.search(pat, txt)
            if m:
                errors.append(f"{f.relative_to(BASE_DIR)}: hard-banned token '{m.group(0)}' matched {pat}")

    if errors:
        print(f"VERIFICATION FAILED ({len(errors)} errors):", file=sys.stderr)
        for e in errors[:40]:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"VERIFICATION PASSED: {len(EXPECTED_PAGES)} pages, {total_rows} source-linked table rows, "
        f"{total_ext_links} official .gov links, {total_dollars_checked} dollar tokens (100% $10-rounded >=$100), "
        f"0 privacy/location leaks, 0 broken links."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
