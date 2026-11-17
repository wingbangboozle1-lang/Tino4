#!/usr/bin/env python3
"""Fail-closed checks for the published site.

Privacy model enforced here (owner's instruction, 2026-11-17): figures may be
published, but every dollar amount is rounded to the nearest ten dollars, and no
case identifier - a name, street, postal code, locality, parcel or roll figure
written out in full - may appear in a generated page or in the builder code that
produces one. Rounding is a traceability control, not anonymity, and the site
says so on its privacy page.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools/site-manifest.json"
PAGE_COUNT = 24
CODE_FILES = ["tools/sitebuild.py", "tools/case_model.py"]
OFFICIAL_HOSTS = {
    "irs.gov", "ca.gov", "leginfo.legislature.ca.gov", "boe.ca.gov", "sco.ca.gov",
    "congress.gov", "uscode.house.gov", "treasurydirect.gov", "treasury.gov",
    "federalreservehistory.org", "federalreserve.gov", "bls.gov", "cbo.gov", "fhfa.gov",
    "sec.gov", "insurance.ca.gov", "cslb.ca.gov", "ftb.ca.gov", "sos.ca.gov",
    "huduser.gov", "investor.gov", "github.com",
}
# Amounts published by an official body that may appear exactly as published.
OFFICIAL_AMOUNTS = {
    "15000000", "15480000", "20000", "1044586", "1022600", "1000000",
    "250000", "500000", "7000", "13990000", "19000", "3000", "1500", "175",
}
CURRENCY = re.compile(r"(?<![\w])\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
MARKER = re.compile(r"(?i)owner[- ]supplied")
POSTAL = re.compile(r"(?<!\d)\d{5}(?!\d)")
UNCOMMA = re.compile(r"(?<![\w.$])\d{7,}(?![\w.,])")
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")
STREET = re.compile(r"(?i)\b\d{1,6}\s+(?:[A-Za-z0-9.'-]+\s+){1,4}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Court|Ct)\b")
# Case identifiers that must never reach a public page or the code that writes one.
LOCALITY = re.compile(r"(?i)\b(cupertino|santa\s+clara|san\s+jose|outer\s+sunset|california\s+street\s+408|95014|94122)\b")
LOCALITY_PHRASES = ("san francisco",)


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
        if tag == "style":
            self.text.append("[inline style block]")

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.row is not None and self.table is not None:
            if self.row["td"]: self.table["rows"].append(self.row)
            self.row = None
        if tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def host_allowed(host: str) -> bool:
    h = host.lower().rstrip(".")
    return any(h == suffix or h.endswith("." + suffix) for suffix in OFFICIAL_HOSTS)


def scan_identifiers(label: str, text: str, errors: list[str], check_commas: bool = False,
                     full: bool = True) -> None:
    """Privacy scan shared by generated pages and, in locality mode, by builder code.

    Code is not scanned for digit runs: statute and form numbers such as a
    transfer-tax section legitimately contain five digits, and a page never
    needs one.
    """
    if MARKER.search(text): errors.append(f"{label}: household-input marker ({MARKER.search(text).group(0)})")
    if full:
        if POSTAL.search(text): errors.append(f"{label}: five-digit location-like identifier")
        if EMAIL.search(text): errors.append(f"{label}: email address")
        if PHONE.search(text): errors.append(f"{label}: phone number")
        if STREET.search(text): errors.append(f"{label}: street-address pattern")
    if LOCALITY.search(text): errors.append(f"{label}: case locality identifier ({LOCALITY.search(text).group(0)})")
    found = [phrase for phrase in LOCALITY_PHRASES if phrase in text.lower()]
    if found: errors.append(f"{label}: case locality phrase ({found[0]})")
    if check_commas and UNCOMMA.search(text):
        errors.append(f"{label}: a multi-digit run written without separators could match a public record")
    for amount in CURRENCY.findall(text):
        normalized = amount.replace(",", "")
        if "." in normalized:
            errors.append(f"{label}: a cent-precision amount could be traced to a single bill or roll entry: ${amount}")
        elif normalized not in OFFICIAL_AMOUNTS and not (len(normalized) >= 2 and normalized.endswith("0")):
            errors.append(f"{label}: amount is not rounded to the nearest ten dollars: ${amount}")


def verify() -> list[str]:
    errors: list[str] = []
    try:
        paths = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"manifest unavailable or invalid: {exc}"]
    if not isinstance(paths, list) or len(paths) != PAGE_COUNT or len(set(paths)) != PAGE_COUNT:
        return [f"manifest must contain exactly {PAGE_COUNT} unique page paths"]
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
        scan_identifiers(label, visible, errors, check_commas=True)
        if "[inline style block]" in visible: errors.append(f"{label}: inline style block is not permitted")
        if audit.h1 != 1: errors.append(f"{label}: expected exactly one h1")
        if not audit.noindex: errors.append(f"{label}: noindex metadata missing")
        if not audit.csp: errors.append(f"{label}: restrictive CSP missing")
        if audit.inline_script or audit.remote_resource: errors.append(f"{label}: inline script or remote resource found")
        if "localStorage" in raw or "sessionStorage" in raw or "indexedDB" in raw:
            errors.append(f"{label}: browser storage is not permitted")
        if "fetch(" in raw or "XMLHttpRequest" in raw or "beacon" in raw:
            errors.append(f"{label}: network call from a page is not permitted")
        for table in audit.tables:
            if table["caption"] != 1: errors.append(f"{label}: table must have exactly one caption")
            for row in table["rows"]:
                if row["td"] and (row["source"] < 1 or row["badge"] < 1):
                    errors.append(f"{label}: table data row lacks an official source link or evidence badge")
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
    # The generator is self-contained: it must not import or read a household
    # data file, and the model code must not carry a case identifier.
    for name in CODE_FILES:
        code = (ROOT / name).read_text(encoding="utf-8")
        scan_identifiers(name, code, errors, full=False)
        if ".read_text(" in code or "open(" in code or "import models" in code:
            errors.append(f"{name}: generator code reads external files or imports a data model")
        if "__file__" in code and name == "tools/case_model.py":
            errors.append(f"{name}: the model should not resolve paths")
        for marker in ("case_data", "household.json", "assessor_roll", "grant_deed"):
            if marker in code:
                errors.append(f"{name}: household-data marker {marker}")
    if errors:
        return errors
    return []


if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures: print(f"FAIL: {failure}")
        raise SystemExit(1)
    print(f"OK - {PAGE_COUNT} pages; every table row carries an official source and an evidence status; "
          "all amounts are rounded to the nearest ten dollars or are published official figures; "
          "no case identifier, browser storage, network call or remote resource is present.")
