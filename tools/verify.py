#!/usr/bin/env python3
"""Fail-closed checks for the public privacy-first site."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools/site-manifest.json"
EXPECTED_PAGES = 26
OFFICIAL_HOSTS = {
    "irs.gov", "ca.gov", "leginfo.legislature.ca.gov", "boe.ca.gov", "sco.ca.gov",
    "congress.gov", "uscode.house.gov", "treasurydirect.gov", "treasury.gov",
    "federalreservehistory.org", "federalreserve.gov", "bls.gov", "cbo.gov", "fhfa.gov", "sec.gov",
    "insurance.ca.gov", "cslb.ca.gov", "ftb.ca.gov", "sos.ca.gov",
    "huduser.gov", "investor.gov", "github.com", "docs.github.com",
    "home.treasury.gov",
}
# The few non-$10 currency amounts allowed on the public site are official
# figures cited on the Verified lookups page. A new non-rounded amount must be
# reviewed and sourced before it can be added here; all household amounts are
# prohibited regardless of rounding.
OFFICIAL_AMOUNTS = {'1044586'}
CODE_FILES = ["tools/sitebuild.py"]
MARKER = re.compile(r"(?i)owner[- ]supplied")
UNCOMMA = re.compile(r"(?<![\w.$])\d{7,}(?![\w.,])")
CURRENCY = re.compile(r"(?<![\w])\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
POSTAL = re.compile(r"(?<!\d)\d{5}(?!\d)")
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")
STREET = re.compile(r"(?i)\b\d{1,6}\s+(?:[A-Za-z0-9.'-]+\s+){1,4}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Court|Ct)\b")

STATUTE_CONTEXT = re.compile(r"(?i)(?:§|section|sec\.|no\.|lta|letter to assessors|publication|usc|code)\s*$")

def scan_currency(label: str, text: str, errors: list[str]) -> None:
    """Require public currency values to be officially sourced or coarsely stated."""
    for amount in CURRENCY.findall(text):
        normalized = amount.replace(",", "")
        if normalized in OFFICIAL_AMOUNTS:
            continue
        if "." in normalized:
            errors.append(f"{label}: a cent-precision amount could be traced to a single bill or roll entry")
        elif not (len(normalized) >= 2 and normalized.endswith("0")):
            errors.append(f"{label}: amount is not a published official figure and is not rounded to the nearest ten dollars")


def scan_identifiers(label: str, text: str, errors: list[str], full: bool = True) -> None:
    """Privacy scan shared by rendered pages and public builder code."""
    if MARKER.search(text):
        errors.append(f"{label}: household-input marker naming the source of an unpublished figure")
    if full:
        if EMAIL.search(text): errors.append(f"{label}: email address")
        if PHONE.search(text): errors.append(f"{label}: phone number")
        if STREET.search(text): errors.append(f"{label}: street-address pattern")


def postal_hits(text: str) -> list[str]:
    """Five-digit runs that look like location identifiers.

    A five-digit California code-section number, a publication number or a
    letter-to-assessors number is not a postal identifier, so runs directly
    preceded by a statute or document prefix are ignored.
    """
    hits: list[str] = []
    for match in POSTAL.finditer(text):
        prefix = text[max(0, match.start() - 24): match.start()]
        if STATUTE_CONTEXT.search(prefix):
            continue
        hits.append(match.group(0))
    return hits


class Audit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.noindex = False
        self.csp = False
        self.inline_script = False
        self.remote_resource = False
        self.tables: list[dict[str, object]] = []
        self.table: dict[str, object] | None = None
        self.row: dict[str, int] | None = None
        self.links: list[tuple[str, bool]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        # Privacy checks cover metadata and non-visible attributes too: sensitive
        # text can leak through titles, labels, alt text, or data attributes.
        self.text.extend(value for key, value in a.items() if key not in {"href", "src", "class", "style"})
        if tag == "h1": self.h1 += 1
        if tag == "meta" and a.get("name", "").lower() == "robots": self.noindex = "noindex" in a.get("content", "").lower()
        if tag == "meta" and a.get("http-equiv", "").lower() == "content-security-policy":
            c = a.get("content", "").lower()
            self.csp = "default-src 'self'" in c and "connect-src 'none'" in c and "object-src 'none'" in c
        if tag == "table":
            self.table = {"rows": [], "caption": 0}
        if tag == "caption" and self.table is not None: self.table["caption"] = int(self.table["caption"]) + 1
        if tag == "tr" and self.table is not None: self.row = {"th": 0, "td": 0, "source": 0, "badge": 0}
        if self.row is not None:
            if tag == "th": self.row["th"] += 1
            if tag == "td": self.row["td"] += 1
            if tag == "a" and "source" in a.get("class", "").split(): self.row["source"] += 1
            if tag == "span" and "badge" in a.get("class", "").split(): self.row["badge"] += 1
        if tag == "script":
            if not a.get("src"): self.inline_script = True
            elif urlsplit(a["src"]).scheme or urlsplit(a["src"]).netloc: self.remote_resource = True
        if tag in {"link", "img", "iframe", "source", "video", "audio"}:
            ref = a.get("href") if tag == "link" else a.get("src")
            if ref and (urlsplit(ref).scheme or urlsplit(ref).netloc): self.remote_resource = True
        if tag == "a" and a.get("href"):
            self.links.append((a["href"], "source" in a.get("class", "").split()))
            if urlsplit(a["href"]).scheme and not {"noopener", "noreferrer"}.issubset(set(a.get("rel", "").split())):
                self.text.append("[unsafe external rel]")
        if tag in {"p", "td", "th", "h1", "h2", "h3", "li", "label"}:
            pass

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.row is not None and self.table is not None:
            if self.row["td"]: self.table["rows"].append(self.row)
            self.row = None
        if tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def handle_comment(self, data: str) -> None:
        # Comments are not user-visible, but they are still distributed publicly.
        self.text.append(data)


def host_allowed(host: str) -> bool:
    h = host.lower().rstrip(".")
    return any(h == suffix or h.endswith("." + suffix) for suffix in OFFICIAL_HOSTS)


def verify() -> list[str]:
    errors: list[str] = []
    try:
        paths = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"manifest unavailable or invalid: {exc}"]
    if not isinstance(paths, list) or len(paths) != EXPECTED_PAGES or len(set(paths)) != len(paths):
        return [f"manifest must contain exactly {EXPECTED_PAGES} unique page paths"]
    for relative in paths:
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            errors.append(f"manifest path is missing or outside repository: {relative}")
            continue
        raw = target.read_text(encoding="utf-8")
        audit = Audit()
        audit.feed(raw)
        label = str(relative)
        visible = " ".join(audit.text)
        scan_identifiers(label, visible, errors)
        if postal_hits(visible):
            errors.append(f"{label}: five-digit location-like identifier in visible text")
        if UNCOMMA.search(visible):
            errors.append(f"{label}: a multi-digit run written without separators could match a public record")
        if "[inline style block]" in " ".join(audit.text):
            errors.append(f"{label}: inline style block is not permitted")
        if audit.h1 != 1: errors.append(f"{label}: expected exactly one h1")
        if not audit.noindex: errors.append(f"{label}: noindex metadata missing")
        if not audit.csp: errors.append(f"{label}: restrictive CSP missing")
        if audit.inline_script or audit.remote_resource: errors.append(f"{label}: inline script or remote resource found")
        if "localStorage" in raw or "sessionStorage" in raw or "indexedDB" in raw:
            errors.append(f"{label}: browser storage is not permitted")
        if "fetch(" in raw or "XMLHttpRequest" in raw or "sendBeacon" in raw:
            errors.append(f"{label}: network call from a page is not permitted")
        scan_currency(label, raw, errors)
        for table in audit.tables:
            if table["caption"] != 1: errors.append(f"{label}: table must have exactly one caption")
            for row in table["rows"]:
                if row["td"] and (row["source"] < 1 or row["badge"] < 1):
                    errors.append(f"{label}: table data row lacks official source link or evidence badge")
        for href, is_source in audit.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                if parsed.scheme != "https": errors.append(f"{label}: non-HTTPS external link {href}")
                if is_source and not host_allowed(parsed.hostname or ""):
                    errors.append(f"{label}: source host is not on official allowlist: {parsed.hostname}")
                continue
            if not parsed.path: continue
            dest = (target.parent / parsed.path).resolve()
            if not dest.is_file() or not dest.is_relative_to(ROOT.resolve()):
                errors.append(f"{label}: broken local link {href}")
    # Every verified figure must carry a read date, so a stale number cannot
    # quietly survive an annual review.
    lookups = ROOT / "pages/verified-lookups.html"
    if lookups.is_file():
        text = lookups.read_text(encoding="utf-8")
        for required in ["2026-11-17", "Read", "deliberately blank", "How to re-verify"]:
            if required not in text:
                errors.append(f"verified-lookups.html: missing required element {required!r}")
        if text.count("15,480,000") < 1:
            errors.append("verified-lookups.html: 2027 estate exclusion figure missing")
        if "1,044,586" not in text:
            errors.append("verified-lookups.html: Proposition 19 indexed cap missing")

    # The generator is self-contained and contains no household model or input file.
    for name in CODE_FILES:
        code = (ROOT / name).read_text(encoding="utf-8")
        scan_identifiers(name, code, errors, full=False)
        if ".read_text(" in code or "open(" in code or "import models" in code:
            errors.append(f"{name}: generator code reads external files or imports a data model")
        for marker in ("case_data", "household.json", "assessor_roll", "grant_deed"):
            if marker in code:
                errors.append(f"{name}: household-data marker {marker}")
    return errors

if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures: print(f"FAIL: {failure}")
        raise SystemExit(1)
    print(f"OK - {EXPECTED_PAGES} generic pages; every table row carries an official source and evidence status; "
          "no household model, browser storage, network call or remote resource is present.")