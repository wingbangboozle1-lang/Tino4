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
OFFICIAL_HOSTS = {
    "sf.gov",
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
# Tree-wide privacy scan patterns. The site policy is "no household figures at
# all", so a comma-grouped amount, a rounding map or a record identifier anywhere
# in the tracked tree is a policy violation, not just a style problem.
GROUPED_AMOUNT = re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+)(?!\d)")
# A count of repository objects is not money. The noun has to follow the number
# closely, so a bill or assessment figure never matches.
COUNT_CONTEXT = re.compile(
    r"(?i)^\s*(?:unique\s+)?(?:blobs|objects|commits|paths|files|rows|records|links|sources|items|entries|\d)"
    r"(?:\W|$)"
)
ROUNDING_MAP = re.compile(r"^\s*(?:literal:|regex:)?\s*[\d][\d,]*\s*(?:==>|->|\u2192)\s*\$?[\d][\d,]*", re.M)
SCRUB_RULES_NAME = re.compile(r"(?i)scrub[-_]rules|redaction[-_](?:rules|patterns)|figures?\.map\b")
TRACKED_SUFFIXES = {".html", ".md", ".py", ".txt", ".yml", ".yaml", ".json", ".css", ".js", ".cjs", ".mjs", ".sh"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".cache", ".pytest_cache"}


def unrounded_amount_problems(text: str) -> list[str]:
    """Comma-grouped amounts that are neither $10-rounded nor listed official figures.

    Counts of repository objects (``1,384 unique blobs``) are exempt: they are not
    money, and no other comma-grouped number in this tree is a count.
    """
    problems = []
    for match in GROUPED_AMOUNT.finditer(text):
        amount = match.group(1)
        digits = amount.replace(",", "")
        if digits in OFFICIAL_AMOUNTS:
            continue
        if digits.endswith("0"):
            continue
        after = text[match.end():match.end() + 40]
        if COUNT_CONTEXT.match(after):
            continue
        window = text[max(0, match.start() - 60):match.end() + 30]
        problems.append(f"non-rounded comma-grouped amount {amount} near {window.strip()[:70]!r}")
    return problems


def tracked_text_files():
    for path in sorted(ROOT.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() not in TRACKED_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_relative_to(ROOT):
            continue
        yield path


def tree_privacy_problems() -> list[str]:
    """Scan every tracked text file, not just the manifest pages."""
    errors = []
    for path in tracked_text_files():
        relative = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if SCRUB_RULES_NAME.search(relative):
            errors.append(f"{relative}: looks like a committed redaction-rules file; keep it outside every clone")
        scan = text
        if path.suffix.lower() == ".css":
            # Colors and alpha triples are not amounts; blank them before scanning.
            scan = re.sub(r"#[0-9a-fA-F]{3,8}\b", "<color>", scan)
            scan = re.sub(r"\b(?:rgba?|hsla?)\([^)]*\)", "<color>", scan)
        for problem in unrounded_amount_problems(scan):
            errors.append(f"{relative}: {problem}; a published amount must be $10-rounded")
        if ROUNDING_MAP.search(scan):
            errors.append(f"{relative}: contains a rounded/unrounded mapping, which would defeat the rounding policy")
        if EMAIL.search(scan):
            errors.append(f"{relative}: contains an email address")
        if PHONE.search(scan):
            errors.append(f"{relative}: contains a phone number")
        if STREET.search(scan):
            errors.append(f"{relative}: contains a street-address pattern")
        # No five-digit screen here: raw files legitimately contain statutory
        # citations and URLs (section 16061.7, LTA 2025/009). Rendered page text is
        # screened for those above, which is where a ZIP code could leak.
    return errors
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


def host_allowed(host: str) -> bool:
    h = host.lower().rstrip(".")
    return any(h == suffix or h.endswith("." + suffix) for suffix in OFFICIAL_HOSTS)


def verify() -> list[str]:
    errors: list[str] = []
    try:
        paths = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"manifest unavailable or invalid: {exc}"]
    if not isinstance(paths, list) or len(paths) != 22 or len(set(paths)) != len(paths):
        return ["manifest must contain exactly 22 unique page paths"]
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
    # A page-level check cannot see a leak in a script, plan or notes file, which is
    # how the rounded-to-unrounded map survived a review before. Scan the whole tree.
    errors.extend(tree_privacy_problems())
    if errors:
        return errors
    return []

if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures: print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("OK — 22 pages; every table row has an official source and status; no household model, browser storage, or remote resource; tree-wide privacy scan clean.")
