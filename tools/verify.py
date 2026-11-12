#!/usr/bin/env python3
"""s-179ec133 — verify a built dashboard.  Usage: python3 verify.py [site directory] [page-list restriction]
Checks, for every page:
  1. every table body row links to at least one official source and carries a status label;
  2. every external link is a URL recorded in the evidence ledger (i.e. a page this session read);
  3. every internal link and anchor resolves;
  4. every dollar amount of $1,000 or more is a multiple of $10, unless the exact figure is quoted from an official source in the ledger;
  5. no ZIP code, neighbourhood name, e-mail address or parcel wording appears;
  6. the page asks search engines not to index it.
Exit status 1 on any failure."""
import glob, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(ROOT, "s179ec133", "_work")
OFFICIAL = ("irs.gov", "boe.ca.gov", "ftb.ca.gov", "sco.ca.gov", "legislature.ca.gov", "sos.ca.gov", "cpuc.ca.gov", "oag.ca.gov", "insurance.ca.gov",
            "courts.ca.gov", "sftreasurer.org", "sf.gov", "sfpuc.gov", "santaclaracounty.gov", "consumerfinance.gov", "eia.gov", "huduser.gov",
            "treasurydirect.gov", "congress.gov", "cbo.gov", "stlouisfed.org", "govinfo.gov", "tsp.gov")
LEDGER_URLS, LEDGER_TEXT = set(), ""
for f in glob.glob(os.path.join(WORK, "research", "ledger", "*.json")):
    for s in json.load(open(f)):
        LEDGER_URLS.add(s["url"])
        LEDGER_TEXT += " " + s["title"] + " " + " ".join(c["claim"] + " " + c["quote"] for c in s["verified"])
OFFICIAL_NUMBERS = {int(x.replace(",", "")) for x in re.findall(r"\d[\d,]{3,}", LEDGER_TEXT) if x.replace(",", "").isdigit()}
FORBIDDEN = [r"\b95014\b", r"\b94122\b", r"Outer Sunset", r"\bSunset\b", r"[\w.+-]+@[\w-]+\.[\w.]+", r"\bAPN\b", r"parcel number \d", r"\b\d{3}-\d{2}-\d{3}\b"]


def official(url):
    host = urlparse(url).netloc.lower()
    return any(host == d or host.endswith("." + d) for d in OFFICIAL)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.rows, self.text, self.meta = [], set(), [], [], {}
        self.in_tbody = False; self.row = None; self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag in ("style", "script"):
            self.skip += 1
        if tag == "meta" and a.get("name"):
            self.meta[a["name"]] = a.get("content", "")
        if tag == "tbody":
            self.in_tbody = True
        if tag == "tr" and self.in_tbody:
            self.row = dict(links=[], chip=False)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
            if self.row is not None:
                self.row["links"].append(a["href"])
        if tag == "span" and "chip" in a.get("class", "") and self.row is not None:
            self.row["chip"] = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip -= 1
        if tag == "tbody":
            self.in_tbody = False
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row); self.row = None

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def main(site):
    files = sorted(glob.glob(os.path.join(site, "index.html")) + glob.glob(os.path.join(site, "pages", "*.html")))
    only = None
    if len(sys.argv) > 2:
        only = set(sys.argv[2].split(","))
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in only]
    pages = {}
    for f in files:
        p = Page(); p.feed(open(f, encoding="utf-8").read()); pages[f] = p
    fails, n_rows, n_links, n_money = [], 0, 0, 0
    for f, p in pages.items():
        rel = os.path.relpath(f, site)
        if "noindex" not in p.meta.get("robots", ""):
            fails.append("%s: missing robots noindex" % rel)
        for i, r in enumerate(p.rows):
            n_rows += 1
            if not any(l.startswith("http") and official(l) for l in r["links"]):
                fails.append("%s: table row %d has no official source link" % (rel, i + 1))
            if not r["chip"]:
                fails.append("%s: table row %d has no status label" % (rel, i + 1))
        for l in p.links:
            n_links += 1
            if l.startswith("http"):
                if l not in LEDGER_URLS:
                    fails.append("%s: external link not in the evidence ledger: %s" % (rel, l))
                elif not official(l):
                    fails.append("%s: external link is not on the official-domain list: %s" % (rel, l))
            elif l.startswith("#"):
                if l[1:] not in p.ids:
                    fails.append("%s: missing anchor %s" % (rel, l))
            else:
                path, _, anchor = l.partition("#")
                target = os.path.normpath(os.path.join(os.path.dirname(f), path))
                if not os.path.isfile(target):
                    fails.append("%s: broken internal link %s" % (rel, l))
                elif anchor and target in pages and anchor not in pages[target].ids:
                    fails.append("%s: missing anchor in %s" % (rel, l))
        text = " ".join(p.text)
        for m in re.finditer(r"\$(\d[\d,]*)(\.\d+)?", text):
            n_money += 1
            if m.group(2):
                continue
            v = int(m.group(1).replace(",", ""))
            if v >= 1000 and v % 10 and v not in OFFICIAL_NUMBERS:
                fails.append("%s: $%s is not rounded to $10 and is not an official published figure" % (rel, m.group(1)))
        for pat in FORBIDDEN:
            m = re.search(pat, text)
            if m:
                fails.append("%s: forbidden text %r" % (rel, m.group(0)))
    for d in ("archive-v2", "internal", "docs", "data"):
        if os.path.isdir(os.path.join(ROOT, d)):
            fails.append("old public tree remains: %s" % d)
    if os.path.exists(os.path.join(ROOT, ".nojekyll")):
        fails.append(".nojekyll present: Pages would publish working files again")
    cfg = open(os.path.join(ROOT, "_config.yml"), encoding="utf-8").read()
    for x in ("tools", "COORDINATION.md", "README.md"):
        if "  - %s" % x not in cfg:
            fails.append("_config.yml is missing the exclusion for %s" % x)
    for f, p in pages.items():
        raw = open(f, encoding="utf-8").read()
        if p.rows and "Status</th>" not in raw:
            fails.append("%s: table lacks a Status column" % os.path.relpath(f, ROOT))
    print("pages %d | table rows %d | links %d | dollar amounts %d | failures %d" % (len(pages), n_rows, n_links, n_money, len(fails)))
    for x in fails[:60]:
        print("FAIL", x)
    return 1 if fails else 0


if __name__ == "__main__":
    site = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    sys.exit(main(site))
