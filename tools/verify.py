#!/usr/bin/env python3
"""Structural, sourcing, rounding and privacy-boundary checks for the site.

What this verifier enforces:

  * Every data-table row carries at least one official source link and an
    evidence badge.
  * Every external link points at an approved official host, uses HTTPS and
    carries noopener/noreferrer.
  * Every page is local-only: no remote resource, no inline script, no form
    action, plus noindex and a restrictive Content Security Policy.
  * No personal identifier: no street address, email address or telephone
    number anywhere in the tracked tree.
  * No unexplained five-digit identifier. Only approved statute identifiers and
    the two public postal areas used for utility and insurance research are
    permitted.
  * Every working dollar figure is rounded to the nearest ten dollars, unless
    it is a published statutory amount that is not a multiple of ten.

This verifier deliberately does not scan Git history. Prior public history is an
unresolved exposure and is documented on the privacy page instead.
"""
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

# Published statutory or official amounts that are not multiples of ten dollars.
# Everything else must be rounded to the nearest ten dollars.
NON_ROUND_OFFICIAL_AMOUNTS = {
    "1044586",  # BOE Proposition 19 adjusted amount, Letter To Assessors 2025/009
}
# Public geographic areas used to reproduce the utility and insurance research.
# These are not personal identifiers, but they are the only five-digit
# identifiers permitted alongside approved statute references.
APPROVED_POSTAL_AREAS = {"95014", "94122"}
APPROVED_STATUTE_IDS = {
    "13301",  # Revenue and Taxation Code section 13301
    "16061",  # Probate Code section 16061.7
    "62809",  # Congressional Budget Office publication identifier
    "1044586",  # BOE Proposition 19 adjusted amount
    "25009",  # BOE Letter To Assessors No. 2025/009 document number
}

LEGACY_PRIVATE_PREFIXES = (
    "_7adb71fc", "_7eff7e24", "_1775f697/review", "_a3de132b/audit",
    "_s8bb142d0/audit", "_s95cf9249/audit",
)
RETIRED_CASE_FILES = {
    "case_data.py", "case_model.py", "case-projections.csv",
    "content_part1.py", "content_part2.py", "content_part3.py", "content_part4.py",
}

OFFICIAL_HOST_SUFFIXES = (
    "irs.gov", "legislature.ca.gov", "boe.ca.gov", "sco.ca.gov", "ca.gov",
    "sf.gov", "cupertino.gov", "sfpuc.gov", "sjwater.com",
    "cupertinosanitarydistrict.org",
    "waterboards.ca.gov", "cpuc.ca.gov", "insurance.ca.gov", "cslb.ca.gov",
    "treasurydirect.gov", "treasury.gov", "federalreservehistory.org", "bls.gov",
    "cbo.gov", "huduser.gov", "fhfa.gov", "investor.gov", "github.com",
    "congress.gov", "ftb.ca.gov", "stlouisfed.org",
)

CURRENCY_RE = re.compile(r"(?<![\w])\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)(?![0-9])")
POSTAL_RE = re.compile(r"(?<![0-9.])([0-9]{5})(?:-[0-9]{4})?(?![0-9])")
ADDRESS_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])\d{1,6}\s+(?:[A-Za-z0-9.'-]+\s+){1,4}"
    r"(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Blvd|Boulevard|Ln|Lane|"
    r"Way|Ct|Court|Pl|Place|Pkwy|Parkway|Hwy|Highway)\b"
)
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")
APN_RE = re.compile(r"(?i)\b(?:APN|parcel\s+(?:number|id|no\.?)|assessor'?s?\s+parcel)\b\s*[:#]?\s*[0-9-]{5,}")


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
        self.rows: list[dict] = []
        self.owner_figures: list[tuple[str, str]] = []
        self.current_row: dict | None = None
        self.current_cell: dict | None = None
        self.table_depth = 0
        self.table_caption_count: list[int] = []

    @staticmethod
    def attrs_dict(attrs):
        return {key: (value or "") for key, value in attrs}

    def handle_starttag(self, tag, attrs):
        values = self.attrs_dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.has_noindex = "noindex" in values.get("content", "").lower()
        if tag == "meta" and values.get("http-equiv", "").lower() == "content-security-policy":
            csp = values.get("content", "").lower()
            self.has_csp = (
                "default-src 'self'" in csp
                and "connect-src 'none'" in csp
                and "object-src 'none'" in csp
            )
        if tag == "table":
            self.table_depth += 1
            self.table_caption_count.append(0)
        elif tag == "caption" and self.table_depth:
            self.table_caption_count[-1] += 1
        if tag == "tr" and self.table_depth:
            self.current_row = {"th": 0, "td": 0, "source": 0, "badge": 0}
        if self.current_row is not None:
            if tag in {"td", "th"}:
                self.current_cell = {
                    "tag": tag,
                    "owner": "owner-figure" in values.get("class", "").split(),
                    "text": "",
                }
                if tag == "th":
                    self.current_row["th"] += 1
                else:
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

    def handle_data(self, data):
        if self.current_cell is not None:
            self.current_cell["text"] += data

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.current_cell is not None:
            if self.current_cell["owner"]:
                self.owner_figures.append((str(self.page.name), self.current_cell["text"]))
            self.current_cell = None
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


def host_is_official(host: str) -> bool:
    host = host.lower().split(":", 1)[0].rstrip(".")
    return any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_HOST_SUFFIXES)


def path_within_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def amount_rounded_to_ten(amount: str) -> bool:
    digits = amount.replace(",", "")
    if "." in digits:
        return False
    try:
        return int(digits) % 10 == 0
    except ValueError:
        return False


def scan_text_file(relative: str, content: str) -> list[str]:
    errors: list[str] = []
    scan = content
    if relative.lower().endswith(".css"):
        scan = re.sub(r"#[0-9a-fA-F]{3,8}\b", "<color>", scan)
    for amount in CURRENCY_RE.findall(content):
        digits = amount.replace(",", "")
        if "." in digits and not amount_rounded_to_ten(digits):
            errors.append(f"{relative} contains a currency amount with cents")
        elif "." not in digits and digits not in NON_ROUND_OFFICIAL_AMOUNTS and not amount_rounded_to_ten(digits):
            errors.append(f"{relative} contains a currency amount not rounded to ten dollars")
    for match in POSTAL_RE.finditer(scan):
        if match.group(1) not in APPROVED_POSTAL_AREAS | APPROVED_STATUTE_IDS:
            errors.append(f"{relative} contains an unexplained five-digit identifier")
    for pattern, label in (
        (ADDRESS_RE, "appears to contain a street address"),
        (EMAIL_RE, "appears to contain an email address"),
        (PHONE_RE, "appears to contain a phone number"),
        (APN_RE, "appears to contain a parcel identifier"),
    ):
        if pattern.search(content):
            errors.append(f"{relative} {label}")
    return errors


def verify() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["tools/site-manifest.json is missing"]
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["tools/site-manifest.json is unreadable or invalid"]
    if not isinstance(manifest, list) or not manifest or not all(isinstance(i, str) for i in manifest):
        return ["site manifest must be a non-empty list of relative paths"]
    if len(manifest) != len(set(manifest)):
        errors.append("site manifest contains duplicate output paths")

    actual_pages = ["index.html", *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "pages").glob("*.html"))]]
    if set(actual_pages) != set(manifest):
        errors.append("generated HTML pages do not match tools/site-manifest.json")

    skip_dirs = {".git", ".venv", "node_modules", "__pycache__", ".cache", ".arena"}
    tree_files: list[Path] = []
    for directory, child_dirs, names in os.walk(ROOT):
        child_dirs[:] = [name for name in child_dirs if name not in skip_dirs]
        tree_files.extend(Path(directory) / name for name in names)
    if any(path.name in RETIRED_CASE_FILES for path in tree_files):
        errors.append("a retired case-input or case-projection file remains in the current tree")
    for prefix in LEGACY_PRIVATE_PREFIXES:
        legacy_dir = ROOT / prefix
        if legacy_dir.exists() and any(p.is_file() for p in legacy_dir.rglob("*")):
            errors.append("legacy case or audit material remains in the current tree")

    page_set = {(ROOT / item).resolve() for item in manifest if isinstance(item, str)}
    text_suffixes = {".html", ".md", ".py", ".txt", ".yml", ".yaml", ".json", ".css", ".js", ".cjs"}
    for path in tree_files:
        if path.resolve() in page_set or path.suffix.lower() not in text_suffixes:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        errors.extend(scan_text_file(path.relative_to(ROOT).as_posix(), content))

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

        for cell_text in [value for name, value in audit.owner_figures if name == page.name]:
            stripped = cell_text.strip()
            if not stripped.startswith("$"):
                continue
            digits = stripped[1:].replace(",", "")
            if not amount_rounded_to_ten(digits):
                errors.append(f"{relative} has a working figure not rounded to ten dollars")

        for link in audit.external_links:
            parsed = urlsplit(link)
            if not host_is_official(parsed.hostname or ""):
                errors.append(f"{relative} links to an unapproved external host: {parsed.hostname}")
        for link in audit.local_links:
            if link.startswith("["):
                errors.append(f"{relative} has an unsafe external link: {link}")
                continue
            parsed = urlsplit(link)
            if not parsed.path:
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if not path_within_root(target) or not target.is_file():
                errors.append(f"{relative} has a broken local link: {link}")

        errors.extend(scan_text_file(relative, text))

    js = ROOT / "assets" / "app.js"
    if js.exists():
        script = js.read_text(encoding="utf-8")
        if re.search(r"\b(?:fetch|XMLHttpRequest|sendBeacon|WebSocket)\b", script):
            errors.append("browser script contains a network API")
        if "runtime-payload" not in script:
            errors.append("browser script does not read the local runtime payload")
    css = ROOT / "assets" / "style.css"
    if css.exists() and re.search(r"@import\s+(?:url\()?\s*['\"]?https?://", css.read_text(encoding="utf-8"), re.I):
        errors.append("stylesheet imports a remote asset")
    return errors


if __name__ == "__main__":
    problems = verify()
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(
        f"OK - {len(manifest)} pages; every table row sourced and status-tagged; local-only "
        "resources; working figures rounded to ten dollars; no personal identifier found "
        "(Git history excluded from this scan)."
    )
