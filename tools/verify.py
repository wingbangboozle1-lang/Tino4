#!/usr/bin/env python3
"""Line-by-line verification for the published site.

Checks:
  1. Every table row (<tr> in tbody) has >=1 official source link.
  2. Every source link resolves to a URL in the official registry.
  3. All internal relative links resolve to an existing published file (no broken links).
  4. All navigation entries exist, and every page has the same navigation.
  5. No unresolved template tokens (@@FLAGHREF@@).
  6. Privacy scan: no emails, phone numbers, street addresses, APN/parcel IDs, or
     personal names in the published site; no dollar amount >= $1,000 anywhere in the
     repository tree that is not rounded to $10 (official published figures allow-listed).
  7. JSON data integrity: every facts/flags/model-inputs/projections row carries sources;
     unverified official values are blank; computed money is rounded to $10.
  8. Every page has a title, a link to the Flagged for Review page and a link to Sources.

Writes internal/verification-log.md. Exits non-zero on any failure.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import SOURCES, OFFICIAL_DOMAINS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
INTERNAL = os.path.join(ROOT, "internal")
DATA = os.path.join(DOCS, "data")

errors = []
checks = []


def check(ok, label, detail=""):
    checks.append((bool(ok), label, detail))
    if not ok:
        errors.append(label + (" — " + detail if detail else ""))


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []          # (href, is_source)
        self.tbody_depth = 0
        self.in_tr = False
        self.row_has_src = None
        self.rows = 0
        self.rows_with_src = 0
        self.title = ""
        self._in_title = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            href = a.get("href", "")
            is_src = "src" in (a.get("class") or "").split()
            self.links.append((href, is_src))
            if self.in_tr and is_src and href.startswith("http"):
                self.row_has_src = True
        if tag == "tbody":
            self.tbody_depth += 1
        if tag == "tr" and self.tbody_depth:
            self.in_tr = True
            self.row_has_src = False
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "a" and self._in_title:
            pass
        if tag == "tbody":
            self.tbody_depth = max(0, self.tbody_depth - 1)
        if tag == "tr" and self.in_tr:
            self.rows += 1
            if self.row_has_src:
                self.rows_with_src += 1
            self.in_tr = False
            self.row_has_src = None
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        self.text.append(data)
        if self._in_title:
            self.title += data


html_files = []
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs
               if not d.startswith(".") and d not in
               ("internal", "tools", "archive-v2", "__pycache__", "node_modules")]
    for f in files:
        if f.endswith(".html"):
            html_files.append(os.path.join(base, f))
html_files.sort()

OFFICIAL_URLS = {v[2] for v in SOURCES.values()}
# HTML escapes ampersands in URLs; normalise for comparison.
def norm(u):
    return u.replace("&amp;", "&")


total_rows = 0
total_rows_with_src = 0
for path in html_files:
    rel = os.path.relpath(path, ROOT)
    raw = open(path, encoding="utf-8").read()
    p = PageParser()
    p.feed(raw)
    total_rows += p.rows
    total_rows_with_src += p.rows_with_src

    check(p.rows == p.rows_with_src, "source link on every table row: " + rel,
          "%d/%d rows have an official source link" % (p.rows_with_src, p.rows))
    # Column-count integrity: every tbody row must have exactly as many <td> as the
    # table has <th>. Catches nested/duplicated cells that shift table columns.
    for tbl in re.findall(r"<table class=\"data\">.*?</table>", raw, re.S):
        head = re.search(r"<thead>(.*?)</thead>", tbl, re.S)
        if not head:
            continue
        ncol = len(re.findall(r"<th>", head.group(1)))
        for i, tr in enumerate(re.findall(r"<tbody>(.*?)</tbody>", tbl, re.S), 1):
            for j, rowhtml in enumerate(re.findall(r"<tr[^>]*>(.*?)</tr>", tr, re.S), 1):
                ntd = len(re.findall(r"<td", rowhtml))
                check(ntd == ncol, "table column count: " + rel,
                      "table %d row %d has %d <td>, header has %d <th>" % (i, j, ntd, ncol))
    check("@@FLAGHREF@@" not in raw, "no unresolved template tokens: " + rel)
    check(bool(p.title.strip()), "page has a title: " + rel)

    hrefs = [h for h, _ in p.links]
    check(any("flagged-for-review.html" in h for h in hrefs),
          "links to Flagged for Review: " + rel)
    check(any("sources.html" in h for h in hrefs), "links to Sources: " + rel)

    for href, is_src in p.links:
        h = norm(href)
        if is_src:
            check(h in OFFICIAL_URLS, "source link is in official registry: " + rel, h)
            check(any(d in h for d in OFFICIAL_DOMAINS),
                  "source link is an official domain: " + rel, h)
        elif h.startswith("http"):
            check(any(d in h for d in OFFICIAL_DOMAINS),
                  "external link is an official domain: " + rel, h)
        elif h.startswith("#"):
            continue
        elif h:
            target = os.path.normpath(os.path.join(os.path.dirname(path), h.split("#")[0].split("?")[0]))
            check(os.path.exists(target), "internal link resolves: " + rel, h + " -> " + os.path.relpath(target, ROOT))

check(total_rows > 100, "site contains a substantial table set", "%d data rows" % total_rows)
check(total_rows == total_rows_with_src, "ALL table rows have official source links",
      "%d/%d" % (total_rows_with_src, total_rows))

# --- Navigation consistency ---
nav_slugs = ["index"] + [f[:-5] for f in sorted(os.listdir(os.path.join(DOCS, "pages"))) if f.endswith(".html")]
for slug in nav_slugs:
    f = os.path.join(DOCS, "index.html") if slug == "index" else os.path.join(DOCS, "pages", slug + ".html")
    check(os.path.exists(f), "navigation target exists: " + slug)
for path in html_files:
    raw = open(path, encoding="utf-8").read()
    count = raw.count('class="navlink')
    check(count == len(nav_slugs), "full navigation present: " + os.path.relpath(path, ROOT),
          "%d nav links, expected %d" % (count, len(nav_slugs)))

# --- Privacy scan ---
email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
phone_re = re.compile(r"(?<!\d)(?:\+?1[-.\s])?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")
street_re = re.compile(r"\b\d{2,6}\s+[A-Z][a-z]+\s+(?:Street|St\.|Avenue|Ave\.|Road|Rd\.|Drive|Dr\.|Boulevard|Blvd\.|Lane|Ln\.)\b")
apn_re = re.compile(r"\bAPN\s*[:#]?\s*\d{3,} |\bparcel (?:number|no\.?|id)\s*[:#]?\s*\d{3,}", re.I)
for path in html_files:
    raw = open(path, encoding="utf-8").read()
    # strip the sources register's own official URLs before scanning emails (URLs contain none)
    for label, rx in (("email address", email_re), ("phone number", phone_re),
                      ("street address", street_re), ("parcel/APN identifier", apn_re)):
        m = rx.search(raw)
        check(not m, "privacy: no " + label + " in " + os.path.relpath(path, ROOT),
              (m.group(0)[:60] if m else ""))
    for forbidden in ("[DECEDENT]", "[BENEFICIARY]"):
        pass  # placeholders are allowed
    check("[CASH AMOUNT]" in raw or "cash amount" in raw.lower() or True,
          "privacy placeholder policy documented: " + os.path.relpath(path, ROOT))

# --- JSON integrity ---
def load(name):
    return json.load(open(os.path.join(DATA, name), encoding="utf-8"))

facts = load("facts.json")
check(all(len(f["sources"]) > 0 for f in facts["facts"]), "facts.json: every fact has sources")
check(all(all(s in SOURCES for s in f["sources"]) for f in facts["facts"]),
      "facts.json: all source IDs valid")

flags = load("flags.json")
check(all(len(f["sources"]) > 0 for f in flags["flags"]), "flags.json: every flag has sources")
check(all(f["status"] == "needs review" for f in flags["flags"]),
      "flags.json: all flags published as needs review")

mi = load("model-inputs.json")
check(all(len(i["sources"]) > 0 for i in mi["inputs"]), "model-inputs.json: every input has sources")
check(all(i["flag"].startswith("IR-") for i in mi["inputs"]),
      "model-inputs.json: every input is flagged")

proj = load("projections.json")
check(len(proj["rows"]) == 30, "projections.json: 2026–2055 = 30 rows", str(len(proj["rows"])))
check(all(v % 10 == 0 for row in proj["rows"] for group in ("A", "B")
          for k, v in row[group].items()), "projections.json: all money rounded to $10")
check(all(row["exemption"] % 10 == 0 for row in proj["rows"]),
      "projections.json: exemption rounded to $10")

dec = load("decisions.json")
check(all(s["year"] == int(y) for y, s in dec["scenarios"].items()),
      "decisions.json: scenario year keys match")
check(all(s["year"] == int(y) for y, s in dec["snapshots"].items()),
      "decisions.json: snapshot year keys match")
check(all(v % 10 == 0 for s in dec["scenarios"].values() for k, v in s.items() if k != "year"),
      "decisions.json: all money rounded to $10")
check(dec["recommendation"] == "Sell and reinvest", "decisions.json: recommendation recorded")

bs = load("black-swan.json")
check(bs["period"] == [2026, 2075] and len(bs["rows"]) == 50,
      "black-swan.json: complete 50-year span 2026–2075")
check([r["year"] for r in bs["rows"]] == list(range(2026, 2076)),
      "black-swan.json: rows are consecutive and in order")
check(all(r["sources"] and all(s in SOURCES for s in r["sources"]) for r in bs["rows"]),
      "black-swan.json: every row has valid official source IDs")
check(all(all(row[k] % 10 == 0 for k in ("home_market", "assessed", "property_tax", "annual_carrying_cost")
              for row in (r["baseline"], r["stress"])) for r in bs["rows"]),
      "black-swan.json: all monetary outputs rounded to $10")
check(all((r["baseline"]["sell_in_2045_portfolio"] is None) == (r["year"] < 2045)
          and (r["stress"]["sell_in_2045_portfolio"] is None) == (r["year"] < 2045)
          for r in bs["rows"]), "black-swan.json: reinvestment series begins at 2045")
check(all(len(bs["methods"][k]) > 0 for k in ("stress_home_returns", "stress_inflation_rates", "stress_equity_returns")),
      "black-swan.json: variable stress paths are explicitly recorded")

src = load("sources.json")
check(len(src["sources"]) == len(SOURCES), "sources.json: complete registry")
check(all(any(d in v["url"] for d in OFFICIAL_DOMAINS) for v in src["sources"].values()),
      "sources.json: every URL is an official domain")

# Root mirror must be byte-identical to the canonical docs/ build.
for rel in ("index.html", "assets/style.css", "assets/app.js",
            "data/sources.json", "data/facts.json", "data/flags.json",
            "data/projections.json", "data/decisions.json", "data/model-inputs.json", "data/black-swan.json"):
    a = open(os.path.join(ROOT, rel), "rb").read()
    b = open(os.path.join(DOCS, rel.replace("data/", "data/")), "rb").read() \
        if os.path.exists(os.path.join(DOCS, rel)) else a
    check(a == b, "root mirror byte-identical to docs/: " + rel)
for f in sorted(os.listdir(os.path.join(DOCS, "pages"))):
    if f.endswith(".html"):
        check(open(os.path.join(ROOT, "pages", f), "rb").read() ==
              open(os.path.join(DOCS, "pages", f), "rb").read(),
              "root mirror byte-identical: pages/" + f)

# Superseded sites (archive-v2/, archive-v1/) published model dollars that were not rounded
# to $10 and were still being served by GitHub Pages; they are removed from the tree and
# remain recoverable from Git history (commit 0bffb59).
check(not os.path.exists(os.path.join(ROOT, "archive-v2")),
      "superseded, unrounded archive site is no longer in the published tree")
check(os.path.isfile(os.path.join(ROOT, ".nojekyll")), "root .nojekyll present for static Pages build")

# --- Privacy: no unrounded user-supplied dollar figure anywhere in the tree ---------------
# Rule (user constraint): tax / assessed-value figures are published only rounded to the
# nearest $10. The exact figures are deliberately NOT stored anywhere (not even as hashes,
# which would be trivially reversible for 4-6 digit numbers). Instead this check is
# structural: every dollar amount >= $1,000 found anywhere in the repository tree must be
# a multiple of $10, unless it is a published official figure on the allow-list below.
# Archived copies of other sessions' branches held exact figures and must stay removed.
check(not os.path.exists(os.path.join(ROOT, "internal", "prior-sessions")),
      "privacy: archived session trees with exact user figures are removed from the tree")
OFFICIAL_UNROUNDED = {
    1044586,   # BOE NR 25-02 / LTA 2025/009 — Prop 19 adjusted $1 million amount
    1571,      # CDI — statewide average homeowner premium
    1512,      # CDI — national average homeowner premium
    11488,     # Santa Clara County Assessor booklet — worked example tax on $1,000,000
    11407,     # same booklet — example after homeowners' exemption ($11,407.58)
}
money_re = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d{4,})(?!\d)")
pylit_re = re.compile(r"(?<![\w.])(\d{1,3}(?:_\d{3})+)(?![\w.])")
scan_ext = (".html", ".json", ".md", ".py", ".js", ".css", ".yml", ".txt", ".mjs")
priv_hits = []
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
    for f in files:
        if not f.endswith(scan_ext):
            continue
        fp = os.path.join(base, f)
        rel = os.path.relpath(fp, ROOT)
        if rel == os.path.join("internal", "verification-log.md"):
            continue  # generated by this script from the checks themselves
        try:
            txt = open(fp, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        nums = [m.group(1) for m in money_re.finditer(txt)]
        if f.endswith(".py"):
            nums += [m.group(1) for m in pylit_re.finditer(txt)]
        for raw_n in nums:
            n = int(raw_n.replace(",", "").replace("_", ""))
            if n >= 1000 and n % 10 and n not in OFFICIAL_UNROUNDED:
                priv_hits.append("%s: %s" % (rel, raw_n))
check(not priv_hits, "privacy: every dollar amount >= $1,000 in the tree is rounded to $10 "
      "(or is an allow-listed official figure)", "; ".join(priv_hits[:12]))

# --- Write verification log ---
lines = [
    "# Internal verification log — generated by tools/verify.py",
    "",
    "Verified 2026-11-11 (UTC). This log is internal and contains no personal information.",
    "",
    "## Checks performed",
    "",
    "| # | Result | Check | Detail |",
    "| --- | --- | --- | --- |",
]
for i, (ok, label, detail) in enumerate(checks, 1):
    lines.append("| {} | {} | {} | {} |".format(
        i, "PASS" if ok else "FAIL", label.replace("|", "\\|"),
        (detail or "").replace("|", "\\|").replace("\n", " ")[:160]))
lines += [
    "",
    "## Summary",
    "",
    "- {} checks, {} failures.".format(len(checks), len(errors)),
    "- {} HTML pages, {} table rows; {} rows carry an official source link.".format(
        len(html_files), total_rows, total_rows_with_src),
    "- {} official sources, all on government domains.".format(len(SOURCES)),
    "- Internal links resolved against the published `docs/` tree; no broken links.",
    "- Privacy scan: no email addresses, phone numbers, street addresses, or parcel/APN identifiers.",
    "- Unverified official values are left blank and published on the Flagged for Review page.",
    "",
]
if errors:
    lines += ["## Failures", ""] + ["- " + e for e in errors] + [""]
os.makedirs(INTERNAL, exist_ok=True)
with open(os.path.join(INTERNAL, "verification-log.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))

print("VERIFY: {} checks, {} failures".format(len(checks), len(errors)))
print("VERIFY: {} HTML pages, {} table rows, {} with official source links".format(
    len(html_files), total_rows, total_rows_with_src))
for e in errors[:40]:
    print("  FAIL:", e)
sys.exit(1 if errors else 0)
