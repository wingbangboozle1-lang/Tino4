#!/usr/bin/env python3
"""Structural, sourcing, privacy-boundary and navigation checks for the site."""
from __future__ import annotations

import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "site-manifest.json"

# Currency policy (owner-directed, 2026-11-15): published dollar amounts are
# either (a) exact official statutory/agency figures listed below — IRS
# thresholds/exclusions, BOE Proposition 19 amounts, 2026 LTCG brackets and
# NIIT MAGI thresholds, the homeowners' exemption, and the proposed
# $3,500,000 exclusion in S.4196's introduced text — or (b) privacy-rounded
# to the nearest ten dollars, i.e. the amount must end in 0. Owner-supplied
# property figures are published only in rounded form and are badged
# Owner-supplied; names, street addresses and parcel identifiers stay
# forbidden. An unrounded or decimal amount fails closed.
PUBLIC_CURRENCY_AMOUNTS = {
    "15000000", "15480000", "19000", "20000",          # IRS estate/gift amounts
    "250000", "500000", "7000", "3500000",             # §121 exclusion, homeowners' exemption, S.4196 proposal
    "1044586", "1022600", "1000000",                   # BOE Prop 19 exclusion amounts (official)
    "49450", "98900", "545500", "613700", "200000",    # 2026 LTCG brackets / NIIT MAGI (Rev. Proc. 2025-32)
    # Published statutory/tariff amounts that do not end in $10, shown exactly
    # as published (ported from session 377ea96a / PR #88):
    "16000", "11700", "3300", "16250",                 # Rev. Proc. 2025-32 estate/trust brackets
    "171", "189", "212",                               # SFPUC Prop 218 notice — published average combined bills FYE 2026-2028
}
# Five-digit identifiers: cited code sections, CBO report identifiers, and the
# two owner-directed region ZIP codes. Region ZIPs carry no street address and
# are used only for ZIP-specific insurance/utility/rate context.
REGION_ZIP_CODES = {"95014", "94122"}
PUBLIC_STATUTE_IDS = {"13301", "16061", "62809", "61882", "61270", "25009", "26138", "70106", "65912"}
FIVE_DIGIT_ALLOWED = PUBLIC_STATUTE_IDS | REGION_ZIP_CODES
LEGACY_PRIVATE_PREFIXES = (
    "_7adb71fc", "_7eff7e24", "_1775f697/review", "_a3de132b/audit",
    "_s8bb142d0/audit", "_s95cf9249/audit",
)
OFFICIAL_HOST_SUFFIXES = (
    "irs.gov", "legislature.ca.gov", "boe.ca.gov", "sco.ca.gov", "ca.gov",
    "waterboards.ca.gov", "cpuc.ca.gov", "insurance.ca.gov", "cslb.ca.gov",
    "treasurydirect.gov", "federalreservehistory.org", "bls.gov", "cbo.gov",
    "huduser.gov", "fhfa.gov", "investor.gov", "github.com", "congress.gov",
    "ftb.ca.gov", "stlouisfed.org", "sf.gov", "sftreasurer.org",
    "santaclaracounty.gov", "boj.or.jp",
    # Owner-directed official-context hosts (2026-11-15): the official daily
    # Treasury yield curve, the statute text, and the utility providers that
    # serve the two regions discussed on the site.
    "treasury.gov", "uscode.house.gov", "sjwater.com", "pge.com", "sfpuc.gov", "sfpuc.org",
)

CURRENCY_RE = re.compile(r"(?<![\w])\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
POSTAL_RE = re.compile(r"(?<![0-9])([0-9]{5})(?:-[0-9]{4})?(?![0-9])")
ADDRESS_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])\d{1,6}\s+(?:[A-Za-z0-9.'-]+\s+){1,4}"
    r"(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Blvd|Boulevard|Ln|Lane|"
    r"Way|Ct|Court|Pl|Place|Pkwy|Parkway|Hwy|Highway)\b"
)
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")

# Record identifiers. A parcel or assessor number is the single most direct
# link from a published figure back to a named owner, so the build fails closed
# on one even when every amount is rounded. The patterns are deliberately
# narrow: they require the label or a recognisable county format, so ordinary
# prose about "a parcel" or a statute section does not trip them.
APN_RE = re.compile(
    r"(?i)\b(?:APN|APN\s*#?|parcel\s*(?:number|no\.?|id|#)|"
    r"assessor'?s?\s+parcel\s*(?:number|no\.?|#)?|APN\s*number)\b"
    r"\s*[:#]?\s*([0-9][0-9\-.\s]{4,})"
)
# Santa Clara County: nnn-nn-nnn. San Francisco: block/lot and nnnn-nnn forms.
APN_BARE_RE = re.compile(r"(?<![0-9-])\d{3}-\d{2}-\d{3}(?![0-9-])|(?<![0-9-])\d{4}-\d{3}(?![0-9-])")
ACCOUNT_RE = re.compile(
    r"(?i)\b(?:account\s*(?:number|no\.?|#)|acct\.?\s*(?:no\.?|#)?|"
    r"trust\s*(?:number|no\.?\s*|#)\s*|escrow\s*(?:number|no\.?\s*|#)\s*|"
    r"loan\s*(?:number|no\.?\s*|#)\s*|policy\s*(?:number|no\.?\s*|#)\s*)\b"
    r"\s*[:#]?\s*([A-Z0-9][A-Z0-9-]{4,})"
)
DOB_RE = re.compile(
    r"(?i)\b(?:date\s+of\s+birth|d\.?o\.?b\.?|born\s+on)\b\s*[:]?\s*"
    r"([0-9]{1,2}\s*/\s*[0-9]{1,2}\s*/\s*[0-9]{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})"
)


def identifier_problems(content: str) -> list[str]:
    """Record-identifier checks that must never be skipped by rounding."""
    problems = []
    for pattern, label in (
        (APN_RE, "appears to contain a labelled parcel or assessor identifier"),
        (APN_BARE_RE, "appears to contain a county parcel number"),
        (ACCOUNT_RE, "appears to contain an account, trust, loan or policy number"),
        (DOB_RE, "appears to contain a date of birth"),
    ):
        if pattern.search(content):
            problems.append(label)
    return problems


class PageAudit(HTMLParser):
    def __init__(self, page: Path):
        super().__init__(convert_charrefs=True)
        self.page = page
        self.h1_count = 0
        self.has_noindex = False
        self.has_csp = False
        self.external_links: list[str] = []
        self.local_links: list[str] = []
        self.inline_script = False
        self.remote_resource = False
        self.form_action = False
        self.rows: list[dict[str, int]] = []
        self.current_row: dict[str, int] | None = None
        self.table_depth = 0
        self.table_caption_open = False
        self.table_caption_count: list[int] = []
        self.ids: set[str] = set()

    @staticmethod
    def attrs_dict(attrs):
        return {key: value or "" for key, value in attrs}

    def handle_starttag(self, tag, attrs):
        values = self.attrs_dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.has_noindex = "noindex" in values.get("content", "").lower()
        if tag == "meta" and values.get("http-equiv", "").lower() == "content-security-policy":
            csp = values.get("content", "").lower()
            self.has_csp = "default-src 'self'" in csp and "connect-src 'none'" in csp and "object-src 'none'" in csp
        if tag == "table":
            self.table_depth += 1
            self.table_caption_count.append(0)
        elif tag == "caption" and self.table_depth:
            self.table_caption_open = True
            self.table_caption_count[-1] += 1
        if tag == "tr" and self.table_depth:
            self.current_row = {"th": 0, "td": 0, "source": 0, "badge": 0}
        if self.current_row is not None:
            if tag == "th":
                self.current_row["th"] += 1
            elif tag == "td":
                self.current_row["td"] += 1
            elif tag == "a" and "source" in values.get("class", "").split():
                self.current_row["source"] += 1
            elif tag == "span" and "badge" in values.get("class", "").split():
                self.current_row["badge"] += 1

        if tag == "script":
            if not values.get("src"):
                self.inline_script = True
            else:
                self._check_resource(values["src"])
        if tag in {"link", "img", "iframe", "source", "video", "audio"}:
            resource = values.get("href") if tag == "link" else values.get("src")
            if resource:
                self._check_resource(resource)
        if tag == "form" and values.get("action"):
            self.form_action = True
        if tag == "a" and values.get("href"):
            self._check_anchor(values["href"], values.get("rel", ""))

    def handle_endtag(self, tag):
        if tag == "caption":
            self.table_caption_open = False
        if tag == "tr" and self.current_row is not None:
            if self.current_row["td"]:
                self.rows.append(self.current_row)
            self.current_row = None
        if tag == "table" and self.table_depth:
            if self.table_caption_count[-1] != 1:
                self.rows.append({"table_caption_error": self.table_caption_count[-1]})
            self.table_caption_count.pop()
            self.table_depth -= 1

    def _check_resource(self, value: str):
        url = urlsplit(value)
        if url.scheme or url.netloc:
            self.remote_resource = True
        elif value and not value.startswith("data:"):
            self.local_links.append(value)

    def _check_anchor(self, value: str, rel: str):
        url = urlsplit(value)
        if url.scheme or url.netloc:
            self.external_links.append(value)
            if url.scheme.lower() != "https":
                self.local_links.append("[non-HTTPS external link]")
            rel_tokens = set(rel.lower().split())
            if not {"noopener", "noreferrer"}.issubset(rel_tokens):
                self.local_links.append("[external link missing safe rel attributes]")
        elif url.path:
            self.local_links.append(value)


def currency_amount_ok(amount: str) -> bool:
    digits = amount.replace(",", "")
    if "." in digits:
        return False
    if digits in PUBLIC_CURRENCY_AMOUNTS:
        return True
    return len(digits) >= 2 and digits.endswith("0")


def postal_code_ok(identifier: str) -> bool:
    return identifier in FIVE_DIGIT_ALLOWED


def host_is_official(host: str) -> bool:
    host = host.lower().split(":", 1)[0].rstrip(".")
    return any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_HOST_SUFFIXES)


def path_within_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def verify() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["tools/site-manifest.json is missing"]
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["tools/site-manifest.json is unreadable or invalid"]
    if not isinstance(manifest, list) or not manifest or not all(isinstance(item, str) for item in manifest):
        return ["site manifest must be a non-empty list of relative paths"]
    if len(manifest) != len(set(manifest)):
        errors.append("site manifest contains duplicate output paths")

    actual_pages = ["index.html", *[str(path.relative_to(ROOT)) for path in sorted((ROOT / "pages").glob("*.html"))]]
    if set(actual_pages) != set(manifest):
        errors.append("generated HTML pages do not match tools/site-manifest.json")

    confidential_names = {
        "case_data.py", "case_model.py", "case-projections.csv",
        "content_part1.py", "content_part2.py", "content_part3.py", "content_part4.py",
    }
    skip_dirs = {".git", ".venv", "node_modules", "__pycache__", ".cache"}
    tree_files: list[Path] = []
    for directory, child_dirs, names in os.walk(ROOT):
        child_dirs[:] = [name for name in child_dirs if name not in skip_dirs]
        tree_files.extend(Path(directory) / name for name in names)
    if any(path.name in confidential_names for path in tree_files):
        errors.append("a retired case-input or case-projection file remains in the current tree")
    for prefix in LEGACY_PRIVATE_PREFIXES:
        legacy_dir = ROOT / prefix
        if legacy_dir.exists() and any(path.is_file() for path in legacy_dir.rglob("*")):
            errors.append("legacy case or audit material remains in the current tree")

    page_set = { (ROOT / item).resolve() for item in manifest if isinstance(item, str) }
    text_suffixes = {".html", ".md", ".py", ".txt", ".yml", ".yaml", ".json", ".css", ".js", ".cjs"}
    for path in tree_files:
        if path.resolve() in page_set or path.suffix.lower() not in text_suffixes:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if any(not currency_amount_ok(amount.group(1)) for amount in CURRENCY_RE.finditer(content)):
            errors.append(f"{relative} contains a non-rounded or unapproved currency amount")
        scan_text = content
        if path.suffix.lower() == ".css":
            scan_text = re.sub(r"#[0-9a-fA-F]{3,8}\b", "<color>", scan_text)
        for public_number in FIVE_DIGIT_ALLOWED | PUBLIC_CURRENCY_AMOUNTS:
            scan_text = re.sub(rf"(?<![0-9]){public_number}(?![0-9])", "<public-number>", scan_text)
        if any(not postal_code_ok(match.group(1)) for match in POSTAL_RE.finditer(scan_text)):
            errors.append(f"{relative} contains an unexplained five-digit identifier")
        if ADDRESS_RE.search(content):
            errors.append(f"{relative} appears to contain a street address")
        if EMAIL_RE.search(content):
            errors.append(f"{relative} appears to contain an email address")
        if PHONE_RE.search(content):
            errors.append(f"{relative} appears to contain a phone number")
        for problem in identifier_problems(content):
            errors.append(f"{relative} {problem}")

    pages: list[Path] = []
    for relative in manifest:
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append("site manifest contains an unsafe output path")
            continue
        page = (ROOT / relative).resolve()
        if not path_within_root(page) or not page.is_file():
            errors.append(f"manifest page is missing: {relative}")
            continue
        pages.append(page)

    for page in pages:
        relative = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        audit = PageAudit(page)
        try:
            audit.feed(text)
            audit.close()
        except Exception:
            errors.append(f"{relative} is not parseable HTML")
            continue
        if audit.h1_count != 1:
            errors.append(f"{relative} must contain exactly one h1")
        if not audit.has_noindex:
            errors.append(f"{relative} is missing noindex")
        if not audit.has_csp:
            errors.append(f"{relative} is missing the restrictive Content Security Policy")
        if audit.inline_script:
            errors.append(f"{relative} contains inline JavaScript")
        if audit.remote_resource:
            errors.append(f"{relative} loads a remote resource")
        if audit.form_action:
            errors.append(f"{relative} has a form that could submit user inputs")

        for row in audit.rows:
            if "table_caption_error" in row:
                errors.append(f"{relative} has a table without exactly one caption")
            elif row["td"] and (row["source"] < 1 or row["badge"] < 1):
                errors.append(f"{relative} has a table row missing a source link or evidence badge")

        for link in audit.external_links:
            parsed = urlsplit(link)
            if not host_is_official(parsed.hostname or ""):
                errors.append(f"{relative} links to an unapproved external host")
        for link in audit.local_links:
            if link.startswith("["):
                errors.append(f"{relative} has an unsafe external link")
                continue
            parsed = urlsplit(link)
            if not parsed.path:
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if not path_within_root(target) or not target.is_file():
                errors.append(f"{relative} has a broken local link")

        for match in CURRENCY_RE.finditer(text):
            if not currency_amount_ok(match.group(1)):
                errors.append(f"{relative} contains a non-rounded or unapproved currency amount")
        for match in POSTAL_RE.finditer(text):
            if not postal_code_ok(match.group(1)):
                errors.append(f"{relative} contains an unexplained five-digit identifier")
        if ADDRESS_RE.search(text):
            errors.append(f"{relative} appears to contain a street address")
        if EMAIL_RE.search(text):
            errors.append(f"{relative} appears to contain an email address")
        if PHONE_RE.search(text):
            errors.append(f"{relative} appears to contain a phone number")
        for problem in identifier_problems(text):
            errors.append(f"{relative} {problem}")

    if (ROOT / "assets" / "case-projections.csv").exists():
        errors.append("case-projection file exists in public assets")
    js = (ROOT / "assets" / "app.js")
    if js.exists():
        script = js.read_text(encoding="utf-8")
        if re.search(r"\b(?:fetch|XMLHttpRequest|sendBeacon)\b", script):
            errors.append("browser script contains a network API")
    css = (ROOT / "assets" / "style.css")
    if css.exists() and re.search(r"@import\s+(?:url\()?\s*['\"]?https?://", css.read_text(encoding="utf-8"), re.I):
        errors.append("stylesheet imports a remote asset")
    return errors


if __name__ == "__main__":
    problems = verify()
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"OK — {len(manifest)} pages; rows sourced and status-tagged; currency $10-rounded or officially listed; region-ZIP allowlist applied; local-only resources; current-tree privacy checks pass (Git history excluded).")
