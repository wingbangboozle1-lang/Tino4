#!/usr/bin/env python3
"""s-179ec133 — shared helpers for the dashboard generator (standard library only)."""
import glob, html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, ".."))
R = json.load(open(os.path.join(WORK, "data", "results.json")))
INP = json.load(open(os.path.join(WORK, "data", "inputs.json")))
LEDGER = {}
for f in sorted(glob.glob(os.path.join(WORK, "research", "ledger", "*.json"))):
    for s in json.load(open(f)):
        s["file"] = os.path.basename(f)
        LEDGER[s["id"]] = s

# Short link labels (agency first, so a reader sees who published it)
SHORT = {
    "IRS-ESTATE": "IRS: Estate tax", "IRS-RP-2026-35": "IRS: Rev. Proc. 2026-35", "IRS-EG-WHATSNEW": "IRS: What's new, estate and gift tax",
    "IRS-ESTATE-FAQ": "IRS: Estate tax FAQ", "IRS-INHERIT-FAQ": "IRS: Sale of inherited property", "CA-RTC-13301": "California law: R&T Code 13301",
    "CA-SCO-ESTATE": "State Controller: California estate tax", "BOE-PROP19": "BOE: Proposition 19", "BOE-LTA-2025-009": "BOE: Letter 2025/009",
    "BOE-LTA-2026-026": "BOE: Letter 2026/026", "FTB-CAPGAINS": "FTB: Capital gains", "FTB-RATES-2025": "FTB: 2025 rate schedules",
    "FTB-DEDUCTIONS": "FTB: Deductions", "FTB-540ES-2026": "FTB: Form 540-ES instructions", "IRS-TC409": "IRS: Topic 409",
    "IRS-TC559": "IRS: Topic 559", "IRS-TC701": "IRS: Topic 701", "IRS-SCHA-2025": "IRS: Schedule A instructions",
    "IRS-VITA-SALT": "IRS: 2025 deduction changes", "IRS-P527": "IRS: Publication 527", "IRS-RR-2023-2": "IRS: Rev. Rul. 2023-2",
    "IRS-I706": "IRS: Form 706 instructions", "TD-FAQ": "TreasuryDirect: FAQ", "BOE-LTA-2026-002": "BOE: Letter 2026/002 (inflation factors)",
    "BOE-CIO-FAQ": "BOE: Change in ownership FAQ", "BOE-HOX": "BOE: Homeowners' exemption", "BOE-PUB800-9": "BOE: Death of a real property owner",
    "SF-TTX-SECURED": "SF Treasurer: Secured property taxes", "SCC-TAXRATEBOOK-2025": "Santa Clara County: Tax rate book 2025-26",
    "CA-RTC-11911": "California law: R&T Code 11911", "CFPB-WORKSHEET": "CFPB: Monthly payment worksheet", "EIA-T5A-2024": "EIA: Table 5A, 2024",
    "CPUC-NEM": "CPUC: Net energy metering", "CPUC-EO-N-5-24": "CPUC: Response to Executive Order N-5-24", "SFPUC-RATES-FY27": "SFPUC: Rate schedule FY 2026-27",
    "HUD-FMR-FY2027": "HUD: FY2027 fair market rents", "HUD-SAFMR-METHOD": "HUD: Small-area rent method", "SF-RENT-RATES": "SF Rent Board: Current rates",
    "SF-RENT-LEARN": "SF Rent Board: Rent increases", "SF-EHT": "SF Treasurer: Empty Homes Tax", "CA-AG-RENTCAPS": "California Attorney General: Rent caps",
    "CDI-SHOP": "California Dept. of Insurance: Shopping for residential insurance", "CA-COURTS-ESTATE-PLAN": "California Courts: Estate planning",
    "CA-COURTS-SIMPLE": "California Courts: When probate is not needed", "CA-PROB-16061-7": "California law: Probate Code 16061.7",
    "CA-PROB-16061-7-SB202": "California law: Probate Code 16061.7(f)", "CA-SOS-RESULTS-2026": "Secretary of State: 2026 ballot measure results",
    "CA-SOS-QUALIFIED-2026": "Secretary of State: Qualified measures 2026", "CA-SOS-PR26-96": "Secretary of State: News release PR26-96", "US-S587": "Congress.gov: S.587", "CA-SB974-2026": "California law: SB 974 (2026)",
    "CBO-OUTLOOK-2026": "CBO: Outlook 2026-2036", "CBO-61912": "CBO: Treasury yield projections", "FRED-SERIES": "St. Louis Fed (FRED): FHFA, BLS and Treasury series",
    "ERP-B55": "Economic Report of the President: Table B-55", "ERP-B56": "Economic Report of the President: Table B-56", "TSP-RETURNS": "Thrift Savings Plan: Rates of return",
}
missing = [k for k in LEDGER if k not in SHORT] + [k for k in SHORT if k not in LEDGER]
assert not missing, missing

e = html.escape


def money(x, sign=False):
    if x is None:
        return ""
    x = int(round(x))
    s = "${:,}".format(abs(x))
    if x < 0:
        return "−" + s
    return ("+" + s) if sign else s


def pct(x, n=1):
    return ("%." + str(n) + "f%%") % (100.0 * x)


def src(*ids):
    out = []
    for i in ids:
        s = LEDGER[i]
        out.append('<a href="%s" rel="noopener">%s</a>' % (e(s["url"]), e(SHORT[i])))
    return " · ".join(out)


STATUS = {
    "V": ("verified", "Verified", "Read on the official page by this session; the passage is quoted on the Sources page."),
    "O": ("owner", "Owner-supplied", "Figure given by the owner, rounded to the nearest $10. Not independently confirmed."),
    "P": ("model", "Projection", "Computed by the model from verified rules, owner-supplied figures and the stated assumptions."),
    "A": ("assume", "Assumption", "Chosen for this analysis because no official source fixes it. Listed on Flagged for Review."),
    "U": ("unver", "Not verified", "Could not be confirmed from an official source. The value is left blank."),
}


def chip(code):
    c, label, tip = STATUS[code]
    return '<span class="chip %s" title="%s">%s</span>' % (c, e(tip), label)


def table(headers, rows, caption=None, cls="", num=()):
    """rows: (cells, [source ids], status code).  Adds 'Official source' and 'Status' columns to every row."""
    h = ['<div class="tablewrap"><table class="%s">' % cls]
    if caption:
        h.append("<caption>%s</caption>" % caption)
    h.append("<thead><tr>%s<th>Official source</th><th>Status</th></tr></thead><tbody>" % "".join(
        '<th%s>%s</th>' % (' class="num"' if i in num else "", x) for i, x in enumerate(headers)))
    for cells, ids, st in rows:
        tds = "".join('<td%s>%s</td>' % (' class="num"' if i in num else "", c) for i, c in enumerate(cells))
        h.append('<tr>%s<td class="src">%s</td><td>%s</td></tr>' % (tds, src(*ids), chip(st)))
    h.append("</tbody></table></div>")
    return "\n".join(h)


NAV = [
    ("index", "Overview"), ("executive-summary", "Executive summary"), ("decision-analysis", "Live, rent or sell"),
    ("properties", "The two properties"), ("projections", "Year-by-year projections"), ("operating-costs", "Running costs"),
    ("inheritance-law", "Tax and property law"), ("estate-thresholds", "Estate tax thresholds"), ("inheritance-process", "Inheritance step by step"),
    ("black-swan-scenarios", "Black-swan conditions"), ("law-watchlist", "Law changes to watch"), ("flagged-for-review", "Flagged for Review"),
    ("sources", "Sources"), ("methodology", "Method and privacy"),
]


def href(slug, here):
    """Relative link between pages: index lives at the top, everything else in pages/."""
    if here == "index":
        return "index.html" if slug == "index" else "pages/%s.html" % slug
    return "../index.html" if slug == "index" else "%s.html" % slug


def link(slug, text, here, anchor=""):
    return '<a href="%s%s">%s</a>' % (href(slug, here), anchor, text)


def page(out, slug, title, lead, body):
    css = "assets/style.css" if slug == "index" else "../assets/style.css"
    nav = "".join('<a href="%s"%s>%s</a>' % (href(s, slug), ' aria-current="page"' if s == slug else "", e(t)) for s, t in NAV)
    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s — House inheritance decision dashboard</title>
<link rel="stylesheet" href="%s">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="%s">House inheritance decision dashboard</a>
<span class="tag">Property A (inherited) · Property B (already owned)</span></div></header>
<div class="wrap layout">
<nav class="side" aria-label="Sections">%s</nav>
<main id="main">
<h1>%s</h1>
<p class="lead">%s</p>
%s
<footer><p>Figures supplied by the owner are rounded to the nearest $10. Projections are estimates, not predictions. This dashboard is
general information, not legal, tax, investment or insurance advice; confirm each step with the official source linked in its row and with a
licensed professional before acting. Sources read 11 November 2026.</p></footer>
</main>
</div>
</body>
</html>
""" % (e(title), css, href("index", slug), nav, e(title), lead, body)
    path = os.path.join(out, "index.html" if slug == "index" else os.path.join("pages", slug + ".html"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(doc)
    return path


CSS = """
:root{--ink:#17202a;--muted:#566573;--line:#d5dbdf;--bg:#f6f8f9;--card:#fff;--brand:#0b5563;--brand2:#e6f2f4;--ok:#1e7b46;--own:#1f5fa8;--mod:#6b3fa0;--ass:#9a6400;--bad:#b3261e}
*{box-sizing:border-box}
html{font-size:16px}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
a{color:var(--brand)}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
.wrap{max-width:1240px;margin:0 auto;padding:0 20px}
.top{background:var(--brand);color:#fff}
.top .wrap{display:flex;flex-wrap:wrap;gap:8px 24px;align-items:baseline;padding-top:14px;padding-bottom:14px}
.brand{color:#fff;font-weight:700;font-size:1.15rem;text-decoration:none}
.tag{opacity:.85;font-size:.9rem}
.layout{display:grid;grid-template-columns:230px minmax(0,1fr);gap:28px;padding-top:24px;padding-bottom:48px}
.side{display:flex;flex-direction:column;gap:2px;align-self:start;position:sticky;top:12px}
.side a{padding:7px 10px;border-radius:6px;text-decoration:none;color:var(--ink);font-size:.93rem}
.side a:hover{background:var(--brand2)}
.side a[aria-current=page]{background:var(--brand);color:#fff;font-weight:600}
h1{font-size:1.9rem;line-height:1.2;margin:.1em 0 .3em}
h2{font-size:1.3rem;margin:2em 0 .5em;padding-top:.6em;border-top:2px solid var(--line)}
h3{font-size:1.05rem;margin:1.4em 0 .4em}
.lead{font-size:1.08rem;color:#2c3e50;max-width:78ch}
p,li{max-width:86ch}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin:18px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.card .v{font-size:1.45rem;font-weight:700;margin:.15em 0;color:var(--brand)}
.card .n{font-size:.88rem;color:var(--muted)}
.card a.more{font-weight:600;text-decoration:none}
.answer{background:var(--brand2);border-left:6px solid var(--brand);border-radius:8px;padding:14px 18px;margin:18px 0}
.answer p{margin:.3em 0}
.warn{background:#fff6e0;border-left:6px solid var(--ass);border-radius:8px;padding:12px 16px;margin:16px 0}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:12px 0 20px}
table{border-collapse:collapse;width:100%;font-size:.9rem}
caption{text-align:left;font-weight:600;padding:10px 12px;color:var(--muted)}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
thead th{background:#eef2f4;font-size:.82rem;position:sticky;top:0}
tbody tr:nth-child(even){background:#fafbfc}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.src{font-size:.8rem;min-width:170px}
tr.hl td{background:#e9f5ee;font-weight:600}
tr.mark td{background:#fff6e0}
.chip{display:inline-block;font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:999px;white-space:nowrap;border:1px solid}
.chip.verified{color:var(--ok);border-color:var(--ok);background:#eaf6ef}
.chip.owner{color:var(--own);border-color:var(--own);background:#e9f1fb}
.chip.model{color:var(--mod);border-color:var(--mod);background:#f1eaf9}
.chip.assume{color:var(--ass);border-color:var(--ass);background:#fff3d9}
.chip.unver{color:var(--bad);border-color:var(--bad);background:#fdeceb}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:.85rem;color:var(--muted);margin:10px 0}
details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:8px 0}
summary{cursor:pointer;font-weight:600}
blockquote{margin:.5em 0;padding:.3em .9em;border-left:3px solid var(--line);color:#34495e;font-size:.88rem}
ol.steps li{margin:.35em 0}
footer{margin-top:40px;padding-top:14px;border-top:1px solid var(--line);font-size:.82rem;color:var(--muted)}
@media (max-width:860px){.layout{grid-template-columns:1fr}.side{position:static;flex-direction:row;flex-wrap:wrap}.side a{border:1px solid var(--line);background:#fff}}
@media print{.side,.skip{display:none}.layout{display:block}}
"""
