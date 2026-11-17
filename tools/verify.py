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
EXPECTED_PAGES = 23
OFFICIAL_HOSTS = {
    "irs.gov", "ca.gov", "leginfo.legislature.ca.gov", "boe.ca.gov", "sco.ca.gov",
    "congress.gov", "uscode.house.gov", "treasurydirect.gov", "treasury.gov",
    "federalreservehistory.org", "bls.gov", "cbo.gov", "fhfa.gov", "sec.gov",
    "insurance.ca.gov", "cslb.ca.gov", "ftb.ca.gov", "sos.ca.gov",
    "huduser.gov", "investor.gov", "github.com",
}
OFFICIAL_AMOUNTS = {
    "15000000", "15480000", "20000", "1044586", "1022600", "1000000",
    "250000", "500000", "7000",
}
CURRENCY = re.compile(r"(?<![\w])\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
POSTAL = re.compile(r"(?<!\d)\d{5}(?!\d)")
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")
STREET = re.compile(r"(?i)\b\d{1,6}\s+(?:[A-Za-z0-9.'-]+\s+){1,4}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Court|Ct)\b")

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
        self.text.extend(value for key, value in a.items() if key not in {"href", "src"})
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
        if POSTAL.search(visible): errors.append(f"{label}: five-digit location-like identifier in visible text")
        if EMAIL.search(visible): errors.append(f"{label}: email address in visible text")
        if PHONE.search(visible): errors.append(f"{label}: phone number in visible text")
        if STREET.search(visible): errors.append(f"{label}: street-address pattern in visible text")
        if audit.h1 != 1: errors.append(f"{label}: expected exactly one h1")
        if not audit.noindex: errors.append(f"{label}: noindex metadata missing")
        if not audit.csp: errors.append(f"{label}: restrictive CSP missing")
        if audit.inline_script or audit.remote_resource: errors.append(f"{label}: inline script or remote resource found")
        if "Owner-supplied" in raw or "owner-supplied" in raw or "PROPERTY_A" in raw or "PROPERTY_B" in raw:
            errors.append(f"{label}: household-data marker found")
        if "localStorage" in raw: errors.append(f"{label}: browser storage is not permitted")
        for amount in CURRENCY.findall(raw):
            normalized = amount.replace(",", "")
            if "." in normalized or (normalized not in OFFICIAL_AMOUNTS and not (len(normalized) >= 2 and normalized.endswith("0"))):
                errors.append(f"{label}: unsupported or unrounded currency amount ${amount}")
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
    # The generator is intentionally self-contained; it must not import or read
    # an external household-data file.
    builder = (ROOT / "tools/sitebuild.py").read_text(encoding="utf-8")
    if ".read_text(" in builder or "open(" in builder or "import models" in builder:
        errors.append("site builder reads external files or imports a model")
    if errors:
        return errors
    return []

if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures: print(f"FAIL: {failure}")
        raise SystemExit(1)
    print(f"OK — {EXPECTED_PAGES} pages; every table row has an official source and status; no household model, browser storage, or remote resource.")
