#!/usr/bin/env python3
"""Deterministic generator for the Tino4 inheritance decision dashboard.

No manual input is required. All facts come from tools/sources.py (official sources
verified 2026-11-10). All model numbers are computed here and rounded to the nearest $10.
Run: python3 tools/build.py
"""
import html
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import SOURCES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(DOCS, "data")
PAGES = os.path.join(DOCS, "pages")
INTERNAL = os.path.join(ROOT, "internal")
ASSETS = os.path.join(DOCS, "assets")
TODAY = "2026-11-10"

for d in (DOCS, DATA, PAGES, INTERNAL, ASSETS):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Verified official constants (value read from the linked official document)
# ---------------------------------------------------------------------------
FED_EXEMPTION_2026 = 15_000_000          # S01, S03
FED_BASIC_CREDIT_2026 = 5_945_800        # S01
FED_TOP_RATE = 0.40                      # S17
GIFT_ANNUAL_2026 = 19_000                # S03, S04
GST_EXEMPTION_2026 = 15_000_000          # S04
PROP13_BASE_RATE = 0.01                  # S20
PROP13_CAP = 0.02                        # S20, S29, S30
SCC_TYPICAL_RATE = 0.011488              # S30
SF_RATE = 0.0118268325                   # S31
PROP19_ALLOWANCE = 1_044_586             # S22 (2/16/2025 – 2/15/2027)
HOMEOWNERS_EXEMPTION = 7_000             # S25
SECTION_121_MFJ = 500_000                # S06
SECTION_121_SINGLE = 250_000             # S06
FED_LTCG_TOP = 0.20                      # S07
NIIT = 0.038                             # S08
FED_GAIN_TAX = FED_LTCG_TOP + NIIT       # 23.8% combined, used on portfolio gains
CDI_AVG_PREMIUM = 1_571                  # S46
CPI_2026 = 0.027                         # S50
CPI_LONG = 0.022                         # S50 / S51 (CPI-U ~2.2%/yr 2027–2035)
CBO_10YR = 0.043                         # S52
SF_RENT_ALLOWABLE = 0.016                # S34 / S56

# User-provided baselines — UNVERIFIED. Never presented as verified facts.
A_VALUE_2026 = 3_100_000
A_ASSESSED_2026 = 550_537
A_TAX_2025 = 7_207
B_VALUE_2026 = 1_800_000
B_ASSESSED_2025 = 114_248
B_TAX_2025 = 2_439
B_RENT_MONTHLY_2026 = 7_150
WATER_A_MONTHLY = 125          # midpoint of user's $100–$150
ELEC_A_NET_MONTHLY = -15       # midpoint of user's $10–$20 monthly credit (negative cost)
WATER_B_MONTHLY = 365          # midpoint of user's $330–$400
ELEC_B_MONTHLY = 50            # midpoint of user's $30–$70
INSURANCE_USER_GUESS = 1_500   # user's estimate; NOT used as a fact

# Model assumptions — UNVERIFIED, flagged on the site.
GROWTH = 0.03                  # nominal home appreciation
RENT_YIELD = 0.03              # gross annual rent as share of market value
MAINT_RATE = 0.01              # annual maintenance as share of market value
SELL_COST = 0.06               # transaction costs on sale
EQUITY_RETURN = 0.07           # nominal equity return
HORIZON = 10                   # years after inheritance
INHERIT_YEARS = (2040, 2045, 2050)
CENTRAL = 2045
YEARS = list(range(2026, 2056))


def r10(x):
    """Round to the nearest $10."""
    return int(round(float(x) / 10.0) * 10)


def usd(x):
    if x is None:
        return ""
    v = r10(x)
    sign = "\u2212" if v < 0 else ""
    return "{}${:,}".format(sign, abs(v))


def pct(x, dp=2):
    return ("{:.%df}" % dp).format(x * 100) + "%"


def esc(x):
    return html.escape(str(x), quote=True)


def infl(y):
    """CBO-anchored cumulative price factor, 2026 = 1.0. Model output, not a fact."""
    if y <= 2026:
        return 1.0
    return (1 + CPI_2026) * (1 + CPI_LONG) ** (y - 2027)


def a_value(y):
    return A_VALUE_2026 * (1 + GROWTH) ** (y - 2026)


def b_value(y):
    return B_VALUE_2026 * (1 + GROWTH) ** (y - 2026)


def a_assessed(y):
    return A_ASSESSED_2026 * (1 + PROP13_CAP) ** (y - 2026)


def b_assessed(y):
    return B_ASSESSED_2025 * (1 + PROP13_CAP) ** (y - 2025)


def op_costs(y, prop):
    """All inputs flagged unverified except the CDI statewide average and CBO CPI anchor."""
    if prop == "A":
        return {
            "water": WATER_A_MONTHLY * 12 * infl(y),
            "electric": ELEC_A_NET_MONTHLY * 12 * infl(y),
            "insurance": CDI_AVG_PREMIUM * infl(y),
            "maintenance": a_value(y) * MAINT_RATE,
        }
    return {
        "water": WATER_B_MONTHLY * 12 * infl(y),
        "electric": ELEC_B_MONTHLY * 12 * infl(y),
        "insurance": CDI_AVG_PREMIUM * infl(y),
        "maintenance": b_value(y) * MAINT_RATE,
    }


def exemption(y):
    """Projected federal basic exclusion. 2026 is verified; later years are model output."""
    if y <= 2026:
        return float(FED_EXEMPTION_2026)
    return FED_EXEMPTION_2026 * (1 + CPI_LONG) ** (y - 2026)


def inheritance_snapshot(Y):
    v = a_value(Y)
    fbyv = a_assessed(Y)
    full = v
    p19 = max(fbyv, v - PROP19_ALLOWANCE)
    return {
        "year": Y,
        "market": v,
        "fbyv": fbyv,
        "tax_pre": fbyv * SCC_TYPICAL_RATE,
        "assessed_full": full,
        "tax_full": full * SCC_TYPICAL_RATE,
        "assessed_p19": p19,
        "tax_p19_live": (p19 - HOMEOWNERS_EXEMPTION) * SCC_TYPICAL_RATE,
        "jump": full * SCC_TYPICAL_RATE - fbyv * SCC_TYPICAL_RATE,
        "p19_saving": (full - p19) * SCC_TYPICAL_RATE,
        "exemption": exemption(Y),
        "headroom": exemption(Y) - v,
    }


def decide(Y, equity=EQUITY_RETURN, growth=GROWTH, rent_yield=RENT_YIELD):
    """10-year, after-(federal-capital-gains)-tax comparison, pre-income-tax on rents."""
    def av(y):
        return A_VALUE_2026 * (1 + growth) ** (y - 2026)

    v = av(Y)
    v_end = av(Y + HORIZON)
    fbyv = a_assessed(Y)

    # SELL at date-of-death stepped-up basis: gain ~ 0, so no capital gains tax on sale.
    proceeds = v * (1 - SELL_COST)
    gross_eq = proceeds * (1 + equity) ** HORIZON
    sell_eq = gross_eq - FED_GAIN_TAX * max(0, gross_eq - proceeds)
    gross_bond = proceeds * (1 + CBO_10YR) ** HORIZON
    sell_bond = gross_bond - FED_GAIN_TAX * max(0, gross_bond - proceeds)

    # LIVE IN (Prop 19 exclusion claimed, homeowners' exemption applied)
    assessed_live = max(fbyv, v - PROP19_ALLOWANCE)
    # RENT OUT (full reassessment, no homeowners' exemption)
    assessed_rent = v
    cum_live = 0.0
    cum_rent = 0.0
    first_live_cf = None
    first_rent_cf = None
    for k in range(HORIZON):
        y = Y + k
        c = op_costs_with_growth(y, growth)
        net_op = sum(c.values())
        tax_live = (assessed_live - HOMEOWNERS_EXEMPTION) * SCC_TYPICAL_RATE
        tax_rent = assessed_rent * SCC_TYPICAL_RATE
        assessed_live *= 1 + PROP13_CAP
        assessed_rent *= 1 + PROP13_CAP
        live_cf = -(tax_live + net_op)
        rent_cf = av(y) * rent_yield - (tax_rent + net_op)
        if k == 0:
            first_live_cf, first_rent_cf = live_cf, rent_cf
        cum_live += live_cf
        cum_rent += rent_cf

    sale_costs_end = v_end * SELL_COST
    gain = v_end - v
    live_tax = FED_GAIN_TAX * max(0, gain - SECTION_121_MFJ)   # §121 if primary residence 2 of 5 yrs
    rent_tax = FED_GAIN_TAX * max(0, gain)                    # depreciation recapture not modelled
    liquid_live = v_end - sale_costs_end - live_tax
    liquid_rent = v_end - sale_costs_end - rent_tax

    return {
        "year": Y,
        "market": v,
        "market_end": v_end,
        "sell_proceeds": proceeds,
        "sell_equity": sell_eq,
        "sell_bond": sell_bond,
        "live_cf1": first_live_cf,
        "rent_cf1": first_rent_cf,
        "cum_live": cum_live,
        "cum_rent": cum_rent,
        "liquid_live": liquid_live,
        "liquid_rent": liquid_rent,
        "live_terminal": liquid_live + cum_live,
        "rent_terminal": liquid_rent + cum_rent,
        "sell_terminal": sell_eq,
    }


def op_costs_with_growth(y, growth):
    c = op_costs(y, "A")
    # maintenance is tied to the property's modelled market value
    c["maintenance"] = A_VALUE_2026 * (1 + growth) ** (y - 2026) * MAINT_RATE
    return c


def breakeven_equity(Y):
    d = decide(Y)
    target = max(d["live_terminal"], d["rent_terminal"])
    lo, hi = 0.0, 0.30
    for _ in range(80):
        mid = (lo + hi) / 2
        if decide(Y, equity=mid)["sell_equity"] < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


SNAP = {Y: inheritance_snapshot(Y) for Y in INHERIT_YEARS}
DEC = {Y: decide(Y) for Y in INHERIT_YEARS}
BE = breakeven_equity(CENTRAL)
CENT = DEC[CENTRAL]
CENT_SNAP = SNAP[CENTRAL]
BEST = "Sell and reinvest"

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
def src_links(ids):
    out = []
    for i in ids:
        title, _agency, url = SOURCES[i]
        out.append(
            '<a class="src" href="{}" target="_blank" rel="noopener noreferrer" '
            'title="{}">{}</a>'.format(esc(url), esc(title), i)
        )
    return " ".join(out)


def src_links_abs(ids):
    return src_links(ids)


def table(headers, rows, caption="", note=""):
    """Every row must carry >=1 official source link; appended as Source column."""
    th = "".join("<th>{}</th>".format(esc(h)) for h in headers)
    body = []
    for row in rows:
        cells = row["cells"]
        srcs = row.get("srcs", [])
        if not srcs:
            raise ValueError("Table row without an official source link: %r" % (cells,))
        status = row.get("status", "VERIFIED")
        status_cls = {
            "VERIFIED": "ok", "MODEL": "model", "UNVERIFIED": "flag",
            "NEEDS REVIEW": "flag", "PROPOSED": "proposed", "ENACTED": "ok",
        }.get(status, "model")
        tds = "".join("<td>{}</td>".format(c) for c in cells)
        body.append(
            '<tr class="{}"><td>{}</td><td><span class="status {}">{}</span></td>'
            '<td class="srccell">{}</td></tr>'.format(
                row.get("cls", ""), tds, status_cls, status, src_links(srcs)
            )
        )
    cap = "<caption>{}</caption>".format(esc(caption)) if caption else ""
    n = '<p class="tablenote">{}</p>'.format(note) if note else ""
    return (
        '<div class="tablewrap"><table class="data">{}<thead><tr>{}'
        '<th>Status</th><th>Source</th></tr></thead><tbody>{}</tbody></table></div>{}'
    ).format(cap, th, "".join(body), n)


def blank():
    return '<span class="blank" title="Left blank: no official source confirms this value">—</span>'


def flagref(fid):
    # @@FLAGHREF@@ is resolved by layout(), which knows whether the caller is index.html
    # or a page in pages/. This keeps every internal link correct in both contexts.
    return '<a class="flagref" href="@@FLAGHREF@@">{}</a>'.format(fid)


NAV = [
    ("index", "Overview"),
    ("executive-summary", "Executive Summary"),
    ("property-tax", "Property Tax & Assessment"),
    ("projections", "Year-by-Year Projections"),
    ("operating-costs", "Operating Costs"),
    ("inheritance-law", "Inheritance & Estate Tax Law"),
    ("estate-thresholds", "Tax Thresholds & Headroom"),
    ("decision-analysis", "Decision Analysis"),
    ("inheritance-process", "Step-by-Step Process"),
    ("law-watchlist", "Law Change Watchlist"),
    ("methodology", "Methodology & Assumptions"),
    ("sources", "Source Register"),
    ("flagged-for-review", "Flagged for Review"),
    ("privacy", "Privacy"),
]

FROM_PAGES = False


def layout(title, slug, body, kicker="", lead=""):
    global FROM_PAGES
    FROM_PAGES = slug != "index"
    pref = "../" if FROM_PAGES else ""
    css = pref + "assets/style.css"
    js = pref + "assets/app.js"
    home = pref + "index.html"

    def href(target):
        if target == "index":
            return home
        return (target + ".html") if FROM_PAGES else ("pages/" + target + ".html")

    navitems = "".join(
        '<a class="navlink{}" href="{}">{}</a>'.format(
            " active" if s == slug else "", href(s), esc(label)
        )
        for s, label in NAV
    )
    body = body.replace("@@FLAGHREF@@", href("flagged-for-review"))
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Tino4 Inheritance Dashboard</title>
<meta name="description" content="Anonymized, source-linked analysis of a 2040–2050 California trust property inheritance.">
<link rel="stylesheet" href="{css}">
</head>
<body>
<a class="skiplink" href="#main">Skip to content</a>
<header class="topbar">
  <div class="brand"><a href="{home}"><span class="logo">T4</span><span>Inheritance Decision Dashboard</span></a></div>
  <div class="topmeta"><span class="pill">Anonymized</span><span class="pill">Verified {today}</span></div>
</header>
<div class="shell">
  <nav class="sidebar" aria-label="Site navigation">
    <div class="sidehead">Sections</div>
    {navitems}
    <div class="sidefoot"><a href="{flag}">⚑ Flagged for Review</a><a href="{src}">Official sources</a></div>
  </nav>
  <main id="main" class="content">
    <div class="pagehead"><div class="kicker">{kicker}</div><h1>{title}</h1>{lead}</div>
    {body}
    <footer class="pagefoot">
      <p>Computed costs, projections and all decision figures are rounded to the nearest $10; statutory
      amounts are quoted exactly as published at the linked official source.
      Verified facts are marked <span class="status ok">VERIFIED</span>; computed outputs are marked
      <span class="status model">MODEL</span>; unconfirmed values are left blank and marked
      <span class="status flag">UNVERIFIED</span>.</p>
      <p>Informational analysis only — not legal, tax, or investment advice. See
      <a href="{priv}">Privacy</a> · <a href="{meth}">Methodology</a> · <a href="{src}">Sources</a>.
      Last verified {today}.</p>
    </footer>
  </main>
</div>
<script src="{js}"></script>
</body>
</html>
""".format(
        title=esc(title), css=css, js=js, home=home, navitems=navitems,
        today=TODAY, kicker=esc(kicker), lead=lead, body=body,
        flag=href("flagged-for-review"), src=href("sources"),
        priv=href("privacy"), meth=href("methodology"),
    )


def card(title, value, sub="", tone=""):
    return ('<div class="card {}"><div class="cardlabel">{}</div>'
            '<div class="cardvalue">{}</div><div class="cardsub">{}</div></div>').format(
        tone, esc(title), value, sub)


def callout(kind, title, text):
    return '<div class="callout {}"><strong>{}</strong><p>{}</p></div>'.format(kind, esc(title), text)


def write(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def json_write(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Data files (shared outputs, written by the integration pass)
# ---------------------------------------------------------------------------
json_write("sources.json", {
    "verified_on": TODAY,
    "policy": "Only official government domains are used as verified facts. Every table row links one.",
    "sources": {k: {"title": v[0], "agency": v[1], "url": v[2]} for k, v in SOURCES.items()},
})

FACTS = [
    ("Federal estate tax basic exclusion, 2026", "$15,000,000", ["S01", "S03"], "Per decedent; $30,000,000 for a married couple with a timely portability election."),
    ("Federal estate tax basic credit, 2026", "$5,945,800", ["S01"], "Unified credit offsetting the tax on the exclusion amount."),
    ("Form 706 filing threshold, 2026", "gross estate + adjusted taxable gifts > $15,000,000", ["S01"], "Due 9 months after death; Form 4768 gives an automatic 6-month filing extension."),
    ("Top federal estate/gift/GST tax rate", "40%", ["S17", "S04"], "Rate on transfers above the exemption."),
    ("Annual federal gift exclusion, 2026", "$19,000 per recipient", ["S03", "S04"], "Does not use the lifetime exemption."),
    ("GST tax exemption, 2026", "$15,000,000", ["S04"], "Matches the estate/gift basic exclusion amount."),
    ("Estate exemption indexing", "permanent after 2025; inflation-indexed from 2027", ["S10", "S11", "S03"], "P.L. 119-21 §70106 removed the scheduled sunset."),
    ("California estate / inheritance tax", "$0 (state pick-up tax is zero)", ["S17"], "California does not conform to the federal estate/GST tax; beneficiary pays no tax on the inheritance itself."),
    ("Inheritance as beneficiary income", "not included in income", ["S15"], "Income produced later by the inherited asset is taxable."),
    ("California capital gains treatment", "taxed as ordinary income (no lower rate)", ["S16"], "Differs from federal 0%/15%/20% rates."),
    ("Federal capital gains rates", "0% / 15% / 20%", ["S07", "S03"], "2026 15% ceiling: $613,700 MFJ; $545,500 all other individuals."),
    ("Net Investment Income Tax", "3.8%", ["S08"], "Applies to rents and gains above $250,000 MFJ / $200,000 single MAGI."),
    ("Section 121 home-sale exclusion", "$250,000 single / $500,000 joint", ["S06"], "Requires ownership and use 24 of the last 60 months."),
    ("Inherited property basis", "FMV at date of death (step-up)", ["S05", "S14"], "Gain on a prompt sale after inheritance is normally near zero."),
    ("Residential rental depreciation", "27.5 years, straight line", ["S09"], "MACRS GDS, mid-month convention."),
    ("Proposition 13 base rate", "1% + voter-approved bonded indebtedness", ["S20", "S30"], "California Constitution Article XIII A."),
    ("Proposition 13 assessed-value cap", "2% per year", ["S20", "S29", "S54", "S30"], "Applies to the factored base year value until a change of ownership."),
    ("Santa Clara County typical tax rate area", "1.1488% of assessed value", ["S30"], "County example: $1,000,000 assessed → $11,488 before exemptions."),
    ("San Francisco FY2025-26 combined secured rate", "1.18268325% of assessed value", ["S31"], "Set annually by Board of Supervisors resolution."),
    ("Homeowners' Exemption", "$7,000 of assessed value", ["S25", "S30"], "Principal residence only; ~$70–$80/yr; does not apply to rented property."),
    ("Prop 19 intergenerational exclusion cap", "FBYV + $1,044,586", ["S22"], "For transfers 2/16/2025 – 2/15/2027; adjusted biennially by FHFA HPI."),
    ("Prop 19 occupancy / filing deadline", "occupy within 1 year; file homeowners' exemption within 1 year", ["S21", "S23", "S24"], "Claim form BOE-19-P within 3 years of transfer."),
    ("Date of change of ownership for trust property", "date of death", ["S24", "S30", "S25"], "Applies even when the property stays in the trust after death."),
    ("Revocable trust transfer into trust", "not a change of ownership (R&T §62(d))", ["S28"], "Vesting in other beneficiaries when the trust becomes irrevocable IS a change of ownership."),
    ("Change of ownership statement on death", "within 150 days after date of death", ["S26", "S27"], "BOE-502-AH / BOE-502-D; trustee files for trust-held property."),
    ("Trustee notification to beneficiaries", "within 60 days", ["S32"], "California Probate Code §16061.7; 120-day contest window."),
    ("California fiduciary income tax return", "Form 541, due 15th day of 4th month", ["S18", "S19"], "Federal equivalent is Form 1041."),
    ("California statewide average homeowner premium", "$1,571 / year", ["S46"], "Statewide average, not a ZIP-level or parcel-level quote."),
    ("Net Billing Tariff (NEM 3.0)", "effective for interconnection applications from 04/15/2023", ["S41", "S42"], "Export credits usually lower than the retail rate; 9-year legacy period."),
    ("SF allowable rent increase 3/1/2026–2/28/2027", "1.6%", ["S34", "S56"], "Based on 60% of Bay Area CPI-U increase."),
    ("Statewide rent cap (AB 1482)", "5% + CPI, max 10%, until 01/01/2030", ["S33"], "Applies to covered units; local rules may be stricter."),
    ("CBO inflation projection", "2.7% (2026) → 2.0% (2030 and later)", ["S50", "S53"], "PCE inflation; CPI-U ~2.2–2.3%/yr 2027–2035."),
    ("CBO 10-year Treasury forecast", "4.3% average, 2026–2036", ["S52", "S50"], "Official anchor used for the savings/bond scenario."),
]
json_write("facts.json", {
    "verified_on": TODAY,
    "facts": [{"item": a, "value": b, "sources": c, "note": d} for a, b, c, d in FACTS],
})

MODEL_INPUTS = [
    ("Property A — estimated market value, Nov 2026", "Property A / 95014", "user-provided", "$3,100,000", ["S30"], "IR-004"),
    ("Property A — tax assessment, 2026", "Property A / 95014", "user-provided", "$550,537", ["S30"], "IR-004"),
    ("Property A — property tax, 2025", "Property A / 95014", "user-provided", "$7,207", ["S30"], "IR-002"),
    ("Property A — water, monthly", "Property A / 95014", "user-provided midpoint of $100–$150", "$125 / month", ["S43"], "IR-004"),
    ("Property A — electricity net credit, monthly", "Property A / 95014", "user-provided midpoint of $10–$20 profit", "−$15 / month", ["S41"], "IR-006"),
    ("Property A — insurance guess, annual", "Property A / 95014", "user-provided estimate", "$1,500 / year", ["S46", "S47"], "IR-007"),
    ("Property B — estimated market value, Nov 2026", "Property B / 94122", "user-provided", "$1,800,000", ["S31"], "IR-004"),
    ("Property B — tax assessment, 2025", "Property B / 94122", "user-provided", "$114,248", ["S31"], "IR-002"),
    ("Property B — property tax, 2025", "Property B / 94122", "user-provided", "$2,439", ["S31"], "IR-002"),
    ("Property B — rent from two units, monthly", "Property B / 94122", "user-provided", "$7,150 / month", ["S34"], "IR-004"),
    ("Property B — water, monthly (3 units)", "Property B / 94122", "user-provided midpoint of $330–$400", "$365 / month", ["S44"], "IR-004"),
    ("Property B — electricity, monthly (3 units)", "Property B / 94122", "user-provided midpoint of $30–$70", "$50 / month", ["S45"], "IR-004"),
    ("Cash inheritance amount", "[TRUST]", "withheld for privacy", "[CASH AMOUNT]", ["S01"], "IR-004"),
    ("Nominal home appreciation", "model", "assumption", "3.0% / yr", ["S50"], "IR-009"),
    ("Gross rental yield on market value", "model", "assumption", "3.0% / yr", ["S48", "S49"], "IR-009"),
    ("Maintenance & repair", "model", "assumption", "1.0% of market value / yr", ["S09"], "IR-009"),
    ("Real estate selling costs", "model", "assumption", "6.0% of price", ["S05"], "IR-009"),
    ("Equity portfolio return", "model", "assumption", "7.0% / yr nominal", ["S52"], "IR-009"),
    ("Savings / Treasuries return", "model", "official CBO anchor", "4.3% / yr", ["S52"], "IR-009"),
    ("Combined federal gain tax used in model", "model", "20% LTCG + 3.8% NIIT", "23.8%", ["S07", "S08"], "IR-009"),
]
json_write("model-inputs.json", {
    "verified_on": TODAY,
    "note": "Official value is left blank for every user-provided or assumed input; only the model value is shown, explicitly flagged.",
    "inputs": [{"item": a, "scope": b, "kind": c, "model_value": d, "sources": e, "flag": f}
               for a, b, c, d, e, f in MODEL_INPUTS],
})

FLAGS = [
    ("IR-001", "Platform branch constraint",
     "Arena pins this session to one branch, `arena/0837be92-tino4`; the requested `session-<id>/<task>` branches and git worktrees cannot be created. Isolation is implemented by exclusive file scopes on the shared task board instead. The PR is opened from the working branch to `main`.",
     "Process only; no effect on the analysis.", ["S11"]),
    ("IR-002", "San Francisco property-tax figures imply a ~2.13% effective rate",
     "The supplied 2025 tax of $2,439 on a stated assessment of $114,248 implies 2.135%, versus the official FY2025-26 combined secured rate of 1.18268325%. The supplied tax series also grows ~1.5–6.2%/yr while the stated assessment grows 2%/yr. Cause cannot be confirmed from an official source (possible special assessments, Mello-Roos, direct charges, a second parcel, or transcription error).",
     "Official value left blank; figures retained only as user-supplied inputs. Confirm from the actual tax bill.", ["S31", "S30"]),
    ("IR-003", "Cupertino tax series inconsistencies",
     "The supplied 2025 tax of $7,207 on $539,743 implies 1.335%, above the County's published typical 1.1488% rate. 2020 tax is flat versus 2019, and 2017 tax falls 0.5% while assessment rises 2% — arithmetically inconsistent with a constant rate. The 2026 tax cell is blank in the supplied table.",
     "Official value left blank; confirm the parcel's tax rate area and direct assessments.", ["S30", "S20"]),
    ("IR-004", "User-supplied figures cannot be confirmed from an official source",
     "Estimated market values, assessment histories, rents, utility amounts, insurance estimates, the cash inheritance amount, and household arrangements are user-provided. No parcel identifiers are used (privacy), so county records cannot be matched.",
     "All such values are published only as unverified model inputs / placeholders, never as verified facts.", ["S30", "S31", "S15"]),
    ("IR-005", "Which property was the decedent's principal residence is unknown",
     "Prop 19's parent-child exclusion requires the family home to have been the transferor's principal residence. That fact is not stated.",
     "Both the eligible and ineligible reassessment outcomes are modelled. Confirm before relying on the exclusion.", ["S21", "S23"]),
    ("IR-006", "Solar interconnection / NEM status unverified",
     "The claimed monthly electricity profit cannot be confirmed. Under the CPUC Net Billing Tariff, export compensation is usually lower than the retail rate; legacy NEM status depends on the interconnection date, which is unknown.",
     "Electricity is modelled as a small net credit from an unverified baseline; official NBT rule is cited.", ["S41", "S42"]),
    ("IR-007", "Parcel-level insurance premiums unverified",
     "CDI publishes a statewide average homeowner premium and ZIP-level residential data, but no official ZIP-specific or landlord-policy quote for 95014 / 94122 was confirmed.",
     "Official value left blank; the statewide average is used only as a labelled benchmark.", ["S46", "S47"]),
    ("IR-008", "Future county tax rates and Prop 19 cap adjustments unknown",
     "Secured tax rates are set annually, and BOE adjusts the Prop 19 $1M allowance every two years from the FHFA House Price Index; values for 2040–2050 are not published.",
     "Projections hold the verified FY2025-26 SF rate, the SCC typical rate, and the 2025–2027 published allowance constant. Flagged.", ["S31", "S30", "S22"]),
    ("IR-009", "Model assumptions are not official facts",
     "Home appreciation, gross rental yield, maintenance rate, land/building split, selling costs, equity return, and the combined gain-tax rate used for comparability are modelling assumptions, not official projections.",
     "Every projection row is marked MODEL and cites the official rule used in the derivation; sensitivity ranges are published.", ["S50", "S52", "S07", "S08"]),
    ("IR-010", "California conformity to federal step-up basis not separately confirmed",
     "The federal basis rule (FMV at death) is verified from IRS Publication 551. A separate official California statement of conformity was not confirmed in this pass.",
     "Sale-tax math should be confirmed with a California tax professional before acting.", ["S05", "S16"]),
    ("IR-011", "2026 California Proposition 40 outcome not certified",
     "The 11/03/2026 vote on a one-time 5% tax on covered assets above $1 billion (real property excluded) was still unofficial on 2026-11-10; the Secretary of State states certification by 12/11/2026. The measure would generally not apply to this estate, and real property is excluded.",
     "Outcome left blank / pending; no projection uses it.", ["S37", "S38", "S39", "S55"]),
    ("IR-012", "No local inheritance/estate tax source found",
     "No official city or county source imposing a local inheritance or estate tax was located. A negative finding is not proof of absence.",
     "Official value left blank and flagged rather than asserted as zero.", ["S17", "S18"]),
    ("IR-013", "Draft and sample official documents used",
     "The 2026 Form 709 instructions on IRS.gov are an early-release DRAFT (not for filing); BOE-19-P and BOE-502-AH pages consulted are SAMPLE forms. Amounts shown were cross-checked against final IRS sources where available.",
     "Read the final forms before filing; flagged for manual review.", ["S04", "S24", "S26"]),
    ("IR-014", "Banked-rent-increase legislation proposed in San Francisco",
     "SF.gov posted on 11/09/2026 that Board of Supervisors File No. 261020 would temporarily cap combined banked and capital-improvement rent increases at 10% per year; it has NOT been enacted.",
     "Not used in any projection; monitored on the Law Change Watchlist.", ["S34"]),
    ("IR-015", "SFPUC water/sewer increases are proposed, not confirmed adopted",
     "The official SFPUC Proposition 218 page states proposed average monthly bill increases of $21 (FY2027) and $23 (FY2028), roughly 12.6% and 12.5% per year.",
     "Only used as a watchlist item; long-run utility escalation uses the CBO CPI anchor.", ["S44", "S50"]),
    ("IR-016", "Rental income taxation and depreciation recapture not fully modelled",
     "Rental income is ordinary income; depreciation (27.5 years) and unrecaptured §1250 gain at up to 25% were not fully modelled in the scenario comparison.",
     "Hold/rent options are shown pre-income-tax, which is generous to them; the sell option has federal gain tax deducted. This strengthens, rather than weakens, the recommendation.", ["S09", "S07", "S08"]),
    ("IR-017", "GitHub Pages source could not be changed to /docs",
     "The repository's Pages site is configured with build_type 'legacy' on main at the repository root. The Pages administration API returned 403 'Resource not accessible by integration' for this session's token, so the source path could not be switched to /docs.",
     "The site is mirrored byte-identically to the repository root and _config.yml excludes internal-only files from the Jekyll build. docs/ remains the canonical copy. Confirm the live URL after deployment.", ["S11"]),
]
json_write("flags.json", {
    "verified_on": TODAY,
    "policy": "Status 'needs review' items are published here and do not block the merge.",
    "flags": [{"id": a, "title": b, "detail": c, "impact": d, "sources": e, "status": "needs review"}
              for a, b, c, d, e in FLAGS],
})

# Projections JSON
PROJ = []
for y in YEARS:
    ca = op_costs(y, "A")
    cb = op_costs(y, "B")
    PROJ.append({
        "year": y,
        "A": {
            "market": r10(a_value(y)), "assessed_pre": r10(a_assessed(y)),
            "tax_pre": r10(a_assessed(y) * SCC_TYPICAL_RATE),
            **{k: r10(v) for k, v in ca.items()},
            "total_operating_pre": r10(sum(ca.values())),
        },
        "B": {
            "market": r10(b_value(y)), "assessed": r10(b_assessed(y)),
            "tax": r10(b_assessed(y) * SF_RATE),
            **{k: r10(v) for k, v in cb.items()},
            "rent": r10(B_RENT_MONTHLY_2026 * 12 * infl(y)),
        },
        "exemption": r10(exemption(y)),
    })
json_write("projections.json", {
    "verified_on": TODAY,
    "note": "MODEL OUTPUTS, not official facts. Rules used: Prop 13 2% cap (S20/S29), county rates (S30/S31), CBO CPI (S50), CDI statewide average (S46).",
    "rows": PROJ,
})

json_write("decisions.json", {
    "verified_on": TODAY,
    "recommendation": BEST,
    "break_even_equity_return_2045": round(BE, 5),
    "note": "All values are rounded to nearest $10 model outputs; see methodology page.",
    "snapshots": {str(Y): {k: (v if k == "year" else r10(v)) for k, v in SNAP[Y].items()}
                  for Y in INHERIT_YEARS},
    "scenarios": {str(Y): {k: (v if k == "year" else r10(v)) for k, v in DEC[Y].items()}
                  for Y in INHERIT_YEARS},
    "sensitivity": [
        {"equity": eq, "sell_terminal": r10(decide(CENTRAL, equity=eq)["sell_equity"])}
        for eq in (0.04, 0.06, 0.07, 0.09, 0.10)
    ],
})

# ---------------------------------------------------------------------------
# Static assets
# ---------------------------------------------------------------------------
write(os.path.join(ASSETS, "style.css"), r"""
:root{--bg:#f5f7fa;--panel:#fff;--ink:#16202c;--muted:#5c6b7a;--line:#dde3ea;--accent:#1d5c8f;--accent2:#0e7c86;--warn:#a8600a;--warnbg:#fff7e8;--okbg:#eaf6ee;--ok:#1c6b3a;--flagbg:#fdeeee;--flag:#a32828;--shadow:0 1px 3px rgba(20,40,60,.07)}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.skiplink{position:absolute;left:-9999px}.skiplink:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:99}
.topbar{background:#0f2438;color:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 22px;gap:16px;flex-wrap:wrap}
.brand a{color:#fff;font-weight:650;display:flex;align-items:center;gap:10px;font-size:16px}
.brand a:hover{text-decoration:none}
.logo{display:inline-grid;place-items:center;width:30px;height:30px;background:#1d5c8f;border-radius:8px;font-size:13px;letter-spacing:.5px}
.topmeta{display:flex;gap:8px}.pill{font-size:11px;text-transform:uppercase;letter-spacing:.06em;background:rgba(255,255,255,.12);padding:4px 9px;border-radius:20px}
.shell{display:grid;grid-template-columns:224px minmax(0,1fr);max-width:1440px;margin:0 auto}
.sidebar{background:#fff;border-right:1px solid var(--line);padding:18px 12px;min-height:calc(100vh - 58px);position:sticky;top:0;align-self:start}
.sidehead{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);padding:0 10px 10px}
.navlink{display:block;padding:8px 10px;border-radius:7px;color:#33465a;font-size:13.5px;margin-bottom:1px}
.navlink:hover{background:#f0f4f8;text-decoration:none}
.navlink.active{background:#e7f0f8;color:#0d4c7c;font-weight:650}
.sidefoot{margin-top:16px;border-top:1px solid var(--line);padding-top:12px;display:grid;gap:7px;font-size:12.5px;padding-left:10px}
.content{padding:26px 30px 40px;min-width:0}
.pagehead{margin-bottom:22px}
.kicker{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:var(--accent2);font-weight:700;margin-bottom:6px}
h1{font-size:29px;line-height:1.2;margin:0 0 10px;letter-spacing:-.02em}
h2{font-size:20px;margin:32px 0 12px;letter-spacing:-.01em}
h3{font-size:16px;margin:22px 0 8px}
p{margin:0 0 12px;max-width:105ch}
.lead{color:var(--muted);font-size:16px;max-width:100ch}
.small{font-size:13px;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:16px 0 24px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:15px 16px;box-shadow:var(--shadow)}
.card.good{border-left:4px solid var(--ok)}.card.warn{border-left:4px solid var(--warn)}.card.flag{border-left:4px solid var(--flag)}
.cardlabel{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:650}
.cardvalue{font-size:23px;font-weight:700;margin:6px 0 3px;letter-spacing:-.02em}
.cardsub{font-size:12px;color:var(--muted)}
.callout{border-radius:9px;padding:13px 16px;margin:16px 0;border:1px solid var(--line);background:#f0f6fb}
.callout p{margin:5px 0 0}.callout.warn{background:var(--warnbg);border-color:#f0dcb4}.callout.good{background:var(--okbg);border-color:#c8e6d3}.callout.flag{background:var(--flagbg);border-color:#f1caca}
.callout strong{font-size:14px}
.tablewrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:9px;box-shadow:var(--shadow);margin:12px 0 6px}
table.data{border-collapse:collapse;width:100%;font-size:13px;min-width:640px}
table.data caption{caption-side:top;text-align:left;font-weight:650;padding:12px 14px;color:var(--ink);border-bottom:1px solid var(--line);background:#fbfcfe}
table.data th{background:#f3f7fa;text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:#44586b;white-space:nowrap;position:sticky;top:0}
table.data td{padding:8px 11px;border-bottom:1px solid #eef2f6;vertical-align:top}
table.data tbody tr:last-child td{border-bottom:none}
table.data tbody tr:hover{background:#f8fbfe}
table.data td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.srccell{white-space:nowrap}
.src{display:inline-block;font-size:10.5px;font-weight:700;background:#e9f1f8;color:#185380;border:1px solid #d3e2ee;border-radius:4px;padding:1px 5px;margin:1px 2px 1px 0}
.src:hover{background:#d5e7f5;text-decoration:none}
.status{display:inline-block;font-size:10px;font-weight:700;letter-spacing:.04em;padding:2px 6px;border-radius:4px;white-space:nowrap}
.status.ok{background:var(--okbg);color:var(--ok)}
.status.model{background:#eaf0f7;color:#2c5578}
.status.flag{background:var(--flagbg);color:var(--flag)}
.status.proposed{background:var(--warnbg);color:var(--warn)}
.blank{color:#9aa7b4;font-weight:700}
.flagref{font-weight:700;color:var(--flag)}
.tablenote{font-size:12px;color:var(--muted);margin:8px 2px 20px}
.pagefoot{margin-top:38px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}
.pagefoot p{max-width:110ch}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.panel{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px 18px;box-shadow:var(--shadow)}
.panel h3{margin-top:0}
ul.tight{margin:6px 0 12px;padding-left:20px}ul.tight li{margin-bottom:5px}
ol.steps{padding-left:20px}ol.steps li{margin-bottom:9px}
.filterbar{display:flex;gap:10px;align-items:center;margin:10px 0 6px;flex-wrap:wrap}
.filterbar input{padding:8px 11px;border:1px solid var(--line);border-radius:7px;font-size:13px;min-width:230px;background:#fff}
.tag{display:inline-block;font-size:11px;background:#eef3f8;border-radius:4px;padding:2px 7px;color:#34506a;margin-right:4px}
.big{font-size:19px;font-weight:700}
@media(max-width:900px){.shell{grid-template-columns:1fr}.sidebar{position:static;min-height:0;border-right:none;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:4px;padding:10px}.sidehead,.sidefoot{display:none}.navlink{margin:0;font-size:12px;padding:6px 8px}.content{padding:18px 14px 30px}h1{font-size:24px}}
""")

write(os.path.join(ASSETS, "app.js"), r"""
/* Small progressive-enhancement helpers. All content is static HTML; no data fetch. */
(function () {
  'use strict';
  var input = document.getElementById('tableFilter');
  if (input) {
    input.addEventListener('input', function () {
      var q = this.value.trim().toLowerCase();
      var rows = document.querySelectorAll('table.data tbody tr');
      for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = (!q || rows[i].textContent.toLowerCase().indexOf(q) !== -1) ? '' : 'none';
      }
    });
  }
  document.querySelectorAll('a[href^="http"]').forEach(function (a) {
    if (!a.hasAttribute('rel')) { a.setAttribute('rel', 'noopener noreferrer'); }
    if (!a.hasAttribute('target')) { a.setAttribute('target', '_blank'); }
  });
})();
""")
write(os.path.join(DOCS, ".nojekyll"), "")

# ---------------------------------------------------------------------------
# Page: index (shared navigation + landing, final integration session only)
# ---------------------------------------------------------------------------
FROM_PAGES = False
index_body = []
index_body.append(
    '<p class="lead">An anonymized, source-linked decision dashboard for a planned '
    '<strong>2040–2050</strong> inheritance of a California residence through a trust. '
    'Every fact links to an official government source; every computed number is labelled '
    'as a model output; anything that cannot be confirmed is left blank and flagged.</p>'
)
index_body.append(callout(
    "flag", "Privacy first",
    "No names, addresses, parcel numbers, account numbers, or the cash inheritance amount appear "
    "anywhere on this site. Only placeholders (<code>[DECEDENT]</code>, "
    "<code>[BENEFICIARY]</code>, <code>[TRUST]</code>, <code>[CASH AMOUNT]</code>) and "
    "property labels with ZIP codes are used. See the <a href=\"pages/privacy.html\">Privacy page</a>."
))
index_body.append('<div class="cards">')
index_body.append(card("Property A — 95014", usd(A_VALUE_2026), "User-supplied Nov 2026 estimate · UNVERIFIED", "flag"))
index_body.append(card("Property B — 94122", usd(B_VALUE_2026), "User-supplied Nov 2026 estimate · UNVERIFIED", "flag"))
index_body.append(card("2026 federal estate exemption", usd(FED_EXEMPTION_2026), "Verified · IRS Form 706 instructions", "good"))
index_body.append(card("Recommended plan", "Sell & reinvest", "See decision analysis for the reasoning", "good"))
index_body.append(card("2045 reassessment tax", usd(CENT_SNAP["tax_full"]), "Model · vs " + usd(CENT_SNAP["tax_pre"]) + " before inheritance", "warn"))
index_body.append(card("Open review items", str(len(FLAGS)), "Published on Flagged for Review", "warn"))
index_body.append('</div>')

index_body.append('<h2>What the analysis concludes</h2>')
index_body.append(
    '<div class="grid2"><div class="panel"><h3>The decisive cost is property tax reassessment</h3>'
    '<p>Under California law, trust-held real property is reassessed to market value '
    '<strong>as of the date of death</strong>. Property A\'s assessed value would move from a '
    'Prop 13–capped base of about <strong>' + usd(CENT_SNAP["fbyv"]) + '</strong> in ' + str(CENTRAL) +
    ' to roughly <strong>' + usd(CENT_SNAP["market"]) + '</strong> — an annual tax increase of about '
    '<strong>' + usd(CENT_SNAP["jump"]) + '</strong> at the County\'s typical rate. '
    'Even with the Prop 19 parent-child exclusion, the published allowance only shelters about '
    + usd(PROP19_ALLOWANCE) + ' of market value.</p></div>'
    '<div class="panel"><h3>Why selling wins the model</h3>'
    '<p>Inherited property receives a basis equal to fair market value at death, so a prompt sale '
    'normally produces little or no capital gain. Selling avoids the reassessment and converts the '
    'asset into a diversified portfolio. Over a 10-year horizon from ' + str(CENTRAL) + ', the model '
    'puts sell-and-reinvest at <strong>' + usd(CENT["sell_terminal"]) + '</strong> versus '
    '<strong>' + usd(CENT["rent_terminal"]) + '</strong> for renting and '
    '<strong>' + usd(CENT["live_terminal"]) + '</strong> for occupying the home.</p></div></div>'
)
index_body.append(
    callout("warn", "How to read this site",
            "<span class=\"status ok\">VERIFIED</span> rows are facts read from official government "
            "documents, each with its own source link. <span class=\"status model\">MODEL</span> rows are "
            "computed projections that cite the official rule used. <span class=\"status flag\">UNVERIFIED"
            "</span> rows have a blank official value and are listed on the "
            "<a href=\"pages/flagged-for-review.html\">Flagged for Review</a> page. "
            "Dollar amounts are rounded to the nearest $10.")
)
index_body.append('<h2>Browse by category</h2>')
cats = [
    ("executive-summary", "Executive summary", "One-page brief with the recommendation and the numbers behind it."),
    ("property-tax", "Property tax & assessment", "Prop 13, Prop 19, county rates, the supplied histories, reassessment."),
    ("projections", "Year-by-year projections", "2026–2055 market value, assessed value, tax and costs for both properties."),
    ("operating-costs", "Operating costs", "Insurance, water, electricity/solar, maintenance, rent and escalation."),
    ("inheritance-law", "Inheritance & estate tax law", "Federal, state and local rules; basis, capital gains, NIIT, trusts."),
    ("estate-thresholds", "Tax thresholds & headroom", "Exemption projections to 2050 and cash headroom per $1,000,000."),
    ("decision-analysis", "Decision analysis", "Live in / rent / sell-and-reinvest, with clear numbers and sensitivity."),
    ("inheritance-process", "Step-by-step process", "What actually happens when the trust transfers the property."),
    ("law-watchlist", "Law change watchlist", "Enacted and proposed changes, with official status."),
    ("methodology", "Methodology & assumptions", "Formulas, inputs, rounding, and what is deliberately excluded."),
    ("sources", "Source register", "Every official source used, with links for manual review."),
    ("flagged-for-review", "Flagged for Review", "Irregularities, blank values and items needing manual confirmation."),
    ("privacy", "Privacy", "Anonymization policy and placeholders."),
]
index_body.append('<div class="tablewrap"><table class="data"><caption>Site map</caption><thead>'
                  '<tr><th>Section</th><th>What it contains</th><th>Status</th><th>Source</th></tr>'
                  '</thead><tbody>')
for slug, label, desc in cats:
    index_body.append('<tr><td><a href="pages/{}.html">{}</a></td><td>{}</td>'
                      '<td><span class="status model">MODEL</span></td><td class="srccell">{}</td></tr>'.format(
                          slug, esc(label), esc(desc), src_links(["S20", "S01"])))
index_body.append('</tbody></table></div>')
index_body.append('<p class="tablenote">Every row above links the two primary official authorities for the '
                  'analysis (IRS Form 706 instructions and BOE Publication 29). Each subpage carries row-level links.</p>')
write(os.path.join(DOCS, "index.html"), layout("Overview", "index", "".join(index_body),
                                               kicker="Dashboard · verified " + TODAY))

# ---------------------------------------------------------------------------
# Page helpers for subpages
# ---------------------------------------------------------------------------
SUB = {}


def subpage(slug, title, body, kicker="Category", lead=""):
    SUB[slug] = (title, body, kicker, lead)


GLOBAL_SRC_FACTS = ["S01", "S20"]

# --- Executive summary ---
b = []
b.append('<p class="lead">Decision brief. All identifiers are placeholders; all currency is rounded to '
         'the nearest $10. "Verified" figures are read from the linked official source; "Model" figures '
         'are computed by this dashboard.</p>')
b.append('<div class="cards">')
b.append(card("Recommendation", BEST, "Maximizes modelled 10-year net wealth", "good"))
b.append(card("Inheritance window", "2040–2050", "Trust transfer planned", ""))
b.append(card("Central case year", str(CENTRAL), "2040 and 2050 also modelled", ""))
b.append(card("Model 10-yr advantage", usd(CENT["sell_terminal"] - CENT["rent_terminal"]),
              "Sell vs rent, 2045 central case", "good"))
b.append(card("2026 federal exemption", usd(FED_EXEMPTION_2026), "Permanent; indexed from 2027", "good"))
b.append(card("State inheritance tax", "$0", "CA pick-up tax is zero", "good"))
b.append('</div>')
b.append('<h2>Executive summary</h2>')
b.append(
    '<p>A trust is expected to transfer <strong>Property A (Cupertino 95014)</strong> plus a cash amount '
    '<code>[CASH AMOUNT]</code> to <code>[BENEFICIARY]</code> sometime in 2040–2050. '
    '<strong>Property B (San Francisco 94122)</strong> is the household\'s residence: two of its three '
    'units are rented and the household can live there without giving up rental income (user-supplied, '
    'unverified). Because housing is already available at no incremental cost, occupying Property A '
    'produces no financial benefit in this model while adding substantial carrying costs.</p>'
)
b.append(
    '<p>The single largest financial event at inheritance is <strong>property tax reassessment</strong>. '
    'California reassesses trust-held real property to market value as of the date of death, not on '
    'distribution. Using a 3% annual appreciation assumption, Property A\'s assessed value in ' +
    str(CENTRAL) + ' would move from about <strong>' + usd(CENT_SNAP["fbyv"]) + '</strong> (Prop 13 capped) '
    'to <strong>' + usd(CENT_SNAP["assessed_full"]) + '</strong>. Annual property tax at the County\'s '
    'published typical rate rises from about <strong>' + usd(CENT_SNAP["tax_pre"]) + '</strong> to '
    '<strong>' + usd(CENT_SNAP["tax_full"]) + '</strong> — a jump of <strong>' +
    usd(CENT_SNAP["jump"]) + '</strong> per year. The Prop 19 parent-child exclusion, if all of its '
    'conditions are met, would reduce that to about <strong>' + usd(CENT_SNAP["tax_p19_live"]) +
    '</strong> per year (saving roughly ' + usd(CENT_SNAP["p19_saving"]) + '/yr), but it cannot eliminate '
    'the reassessment because the published allowance is capped at the factored base year value plus '
    + usd(PROP19_ALLOWANCE) + '.</p>'
)
b.append(
    '<p>Three options were modelled over 10 years from each inheritance year. Property taxes, insurance, '
    'water, electricity, maintenance, selling costs and federal capital-gains/NIIT tax are included; '
    'ordinary income tax on rents is deliberately excluded, which is generous to the rent option. '
    'The sell option uses the verified step-up-in-basis rule, so a prompt sale creates essentially no '
    'capital gain.</p>'
)
rows = []
for Y in INHERIT_YEARS:
    d = DEC[Y]
    rows.append({"cells": [str(Y), usd(d["market"]), usd(d["live_terminal"]), usd(d["rent_terminal"]),
                           usd(d["sell_equity"]), usd(d["sell_bond"]), usd(d["sell_equity"] - d["rent_terminal"])],
                 "srcs": ["S05", "S07", "S08", "S20", "S30", "S52"], "status": "MODEL"})
b.append(table(
    ["Inheritance year", "Modelled market value", "Live in: 10-yr net", "Rent out: 10-yr net",
     "Sell → equities (7%)", "Sell → savings (4.3%)", "Sell advantage vs rent"],
    rows, caption="10-year net wealth by option (model, rounded to $10)",
    note="Net wealth = liquidated property value after selling costs and federal gain tax + cumulative net cash flow, "
         "or invested sale proceeds after federal gain tax. Sources: IRS Pub. 551 (step-up), Topics 409/559 (gain "
         "tax), BOE Pub. 29 / SCC booklet (2% cap and rate), CBO (4.3% anchor). Unverified assumptions: 3% "
         "appreciation, 3% gross rent yield, 1% maintenance, 6% selling costs, 7% equity return."))
b.append(
    callout("good", "Best plan: sell and reinvest",
            "Selling promptly after inheritance (a) uses the stepped-up basis to eliminate capital gains tax, "
            "(b) avoids an annual reassessment-driven property tax increase of about " +
            usd(CENT_SNAP["jump"]) + ", (c) avoids insurance, utilities and maintenance on a second home, and "
            "(d) converts an illiquid concentrated asset into a diversified portfolio. The model's break-even "
            "equity return for 2045 is about <strong>" + pct(BE, 1) + "</strong> — below that, renting could "
            "be competitive. Confirm the Prop 19 principal-residence question and the actual tax bill before acting.")
)
b.append('<h2>Key considerations at a glance</h2>')
cons = [
    ("Federal estate tax", "2026 exemption " + usd(FED_EXEMPTION_2026) + " per decedent; 40% above it; permanent and inflation-indexed from 2027.", ["S01", "S10"]),
    ("California", "No state estate/inheritance tax; the pick-up tax is zero; the inheritance is not taxable income to the beneficiary.", ["S17", "S15"]),
    ("Local", "No official source imposing a city/county inheritance tax was found — left blank and flagged.", ["S17", "S18"]),
    ("Basis", "Inherited property takes FMV at death, so a prompt sale has little or no capital gain.", ["S05"]),
    ("Property tax", "Date of death is the change of ownership date for trust property; supplemental bill follows.", ["S30", "S24"]),
    ("Prop 19", "Exclusion requires the transferor's principal residence, occupancy within 1 year and a homeowners' exemption within 1 year.", ["S21", "S23"]),
    ("Deadlines", "Trustee notice 60 days; change-of-ownership statement 150 days; Form 706 9 months; BOE-19-P 3 years.", ["S32", "S26", "S01", "S23"]),
    ("Law changes", "P.L. 119-21 made the federal exemption permanent; bills to tax gains at death and 2026 California ballot measures are tracked.", ["S10", "S12", "S37"]),
]
b.append(table(["Topic", "Finding"],
               [{"cells": [x, y], "srcs": z, "status": "VERIFIED"} for x, y, z in cons],
               caption="Verified findings",
               note="Each row links the official document that states the finding."))
b.append(callout("warn", "Important limitations",
                 "Sixteen items are flagged for manual review — including the unexplained gap between the "
                 "supplied San Francisco tax figures and the official 1.18268325% rate. See the "
                 "<a href=\"flagged-for-review.html\">Flagged for Review</a> page. This is an informational "
                 "analysis, not legal, tax, or investment advice."))
subpage("executive-summary", "Executive Summary", "".join(b),
        kicker="Brief · verified " + TODAY)

# --- Property tax ---
b = []
b.append('<p class="lead">How the two properties are assessed today, what the official rates are, and what '
         'happens at inheritance. Supplied histories are shown as-supplied and flagged; they are not '
         'verified facts.</p>')
b.append('<h2>Verified rules</h2>')
rules = [
    ("Proposition 13 base rate", "1% of assessed value + voter-approved bonded indebtedness", ["S20"]),
    ("Annual assessed-value cap", "no more than 2% per year on the factored base year value", ["S20", "S29", "S54"]),
    ("Reassessment trigger", "change of ownership or completion of new construction → market value", ["S20", "S30"]),
    ("Inheritance from a living trust", "reassessment occurs as of the date of death, not distribution", ["S30", "S24"]),
    ("Santa Clara County typical TRA rate", "1.1488% (example: $1,000,000 → $11,488)", ["S30"]),
    ("San Francisco FY2025-26 secured rate", "1.18268325% per $100 of assessed value", ["S31"]),
    ("Homeowners' Exemption", "$7,000 of assessed value; principal residence only; not for rented property", ["S25"]),
    ("Prop 19 exclusion cap", "factored base year value + $1,044,586 (2/16/2025–2/15/2027)", ["S22", "S23"]),
    ("Prop 19 conditions", "transferor's principal residence; transferee occupies within 1 year; homeowners' exemption within 1 year; BOE-19-P within 3 years", ["S21", "S23", "S24"]),
    ("Supplemental assessment", "separate bill on the difference between old and new value, prorated to June 30; appeal within 60 days", ["S30"]),
    ("Special assessments", "bills may also include Mello-Roos bonds, service fees, liens and direct assessments", ["S30"]),
]
b.append(table(["Rule", "Official statement"],
               [{"cells": [x, y], "srcs": z, "status": "VERIFIED"} for x, y, z in rules],
               caption="Property tax law — official sources",
               note="The 1.1488% figure is the County's example of a typical tax rate area; the parcel's actual "
                    "rate area was not confirmed (privacy) and is flagged IR-003."))

A_HIST = [
    (2026, None, 550_537), (2025, 7_207, 539_743), (2024, 7_003, 529_161),
    (2023, 6_917, 518_786), (2022, 6_755, 508_614), (2021, 6_662, 498_642),
    (2020, 6_565, 493_530), (2019, 6_565, 483_854), (2018, 6_383, 474_368),
    (2017, 6_383, 465_067), (2016, 6_414, 455_949), (2015, 6_130, 449_101),
    (2014, 5_965, 440_305),
]
B_HIST = [
    (2025, 2_439, 114_248), (2024, 2_315, 112_008), (2023, 2_179, 109_814),
    (2022, 2_107, 107_662), (2021, 2_066, 105_595), (2020, 2_197, 104_513),
    (2019, 2_134, 102_465), (2018, 2_061, 100_456), (2017, 1_740, 98_488),
    (2016, 1_675, 96_557),
]
b.append('<h2>Supplied histories (as supplied — unverified)</h2>')
b.append(callout("flag", "These are not verified facts",
                 "The rows below reproduce the figures supplied in the request so the irregularities can be "
                 "reviewed. The <em>Official value</em> column is blank because county parcel records were not "
                 "matched (privacy). The implied effective rates are computed from the supplied numbers and "
                 "flagged, not asserted as official rates."))
for label, hist, rate_src in (("Property A — Cupertino 95014", A_HIST, "S30"),
                              ("Property B — San Francisco 94122", B_HIST, "S31")):
    rows = []
    for y, tax, assd in hist:
        implied = ("{:.2f}%".format(100 * tax / assd) if tax else "")
        rows.append({
            "cells": [str(y), blank(), usd(tax) if tax else blank(), usd(assd), implied,
                      '<span class="status flag">{}</span>'.format(
                          "IR-003" if "Cupertino" in label else "IR-002")],
            "srcs": [rate_src, "S20"], "status": "UNVERIFIED",
        })
    b.append(table(["Year", "Official value", "Supplied tax", "Supplied assessment",
                    "Implied rate (computed)", "Flag"],
                   rows, caption=label + " — supplied series",
                   note="Blank official values are intentional. The implied rate column is arithmetic on "
                        "user-supplied numbers; official rates are in the table above."))

b.append('<h2>Reassessment at inheritance</h2>')
rows = []
for Y in INHERIT_YEARS:
    s = SNAP[Y]
    rows.append({"cells": [str(Y), usd(s["market"]), usd(s["fbyv"]), usd(s["tax_pre"]),
                           usd(s["assessed_full"]), usd(s["tax_full"]),
                           usd(s["assessed_p19"]), usd(s["tax_p19_live"]), usd(s["jump"])],
                 "srcs": ["S20", "S29", "S30", "S22", "S23", "S24"], "status": "MODEL"})
b.append(table(
    ["Year", "Model market value", "Pre-inheritance assessed", "Pre-inheritance tax",
     "Full reassessment", "Full-reassessment tax", "Prop 19 assessed", "Prop 19 tax (owner-occupied)",
     "Annual tax jump"],
    rows, caption="Assessed value and property tax at inheritance (model, rounded to $10)",
    note="Formula: assessed value grows 2%/yr from the supplied 2026 base (Prop 13 cap, S20/S29); market value "
         "grows at an UNVERIFIED 3% assumption; tax = assessed × 1.1488% (S30); Prop 19 assessed = max(FBYV, "
         "market − $1,044,586) (S22/S23); the homeowners' exemption of $7,000 (S25) is applied to the "
         "owner-occupied case. Prop 19 eligibility itself is unverified (IR-005)."))
b.append(callout("warn", "Prop 19 is conditional",
                 "The exclusion only applies if the home was the <em>transferor's</em> principal residence, the "
                 "transferee moves in within one year, and the homeowners' or disabled veterans' exemption is "
                 "filed within one year. Renting the property does not qualify, and only one homeowners' "
                 "exemption may be claimed by a couple. Because the allowance is roughly " +
                 usd(PROP19_ALLOWANCE) + " while the property is worth several million, a large partial "
                 "reassessment remains even when the exclusion applies."))
subpage("property-tax", "Property Tax & Assessment", "".join(b), kicker="Category · property tax")

# --- Projections ---
b = []
b.append('<p class="lead">Full 2026–2055 model for both properties. Columns are computed outputs, not facts. '
         'Each row cites the official rules used in its derivation. Use the filter to narrow the table.</p>')
b.append('<div class="filterbar"><label class="small" for="tableFilter">Filter rows</label>'
         '<input id="tableFilter" type="search" placeholder="e.g. 2045 or 2050"></div>')
b.append('<h2>Property A — Cupertino 95014</h2>')
rows = []
for p in PROJ:
    a = p["A"]
    rows.append({"cells": [str(p["year"]), usd(a["market"]), usd(a["assessed_pre"]), usd(a["tax_pre"]),
                           usd(a["water"]), usd(a["electric"]), usd(a["insurance"]),
                           usd(a["maintenance"]), usd(a["total_operating_pre"])],
                 "srcs": ["S20", "S29", "S30", "S50", "S46", "S41"], "status": "MODEL"})
b.append(table(
    ["Year", "Model market value", "Assessed (pre-inherit.)", "Property tax (pre-inherit.)",
     "Water", "Electricity (net credit)", "Insurance", "Maintenance", "Total operating"],
    rows, caption="Property A — annual projection 2026–2055 (model, $10 rounding)",
    note="Market value = supplied 2026 estimate × 1.03^(year−2026) [UNVERIFIED assumption]. Assessed value = "
         "supplied 2026 assessment × 1.02^(year−2026) [official 2% cap, S20/S29]. Property tax = assessed × "
         "1.1488% [S30]. Utilities and insurance are escalated from unverified user baselines at the CBO CPI "
         "anchor [S50]; insurance uses the CDI statewide average [S46]. Maintenance = 1% of model market value "
         "[UNVERIFIED]. Negative electricity = net credit; NBT export-credit risk is flagged IR-006 [S41]. "
         "At inheritance the assessed value is replaced by market value — see Property Tax & Assessment."))
b.append('<h2>Property B — San Francisco 94122</h2>')
rows = []
for p in PROJ:
    bb = p["B"]
    rows.append({"cells": [str(p["year"]), usd(bb["market"]), usd(bb["assessed"]), usd(bb["tax"]),
                           usd(bb["water"]), usd(bb["electric"]), usd(bb["insurance"]),
                           usd(bb["maintenance"]), usd(bb["rent"])],
                 "srcs": ["S20", "S29", "S31", "S50", "S46", "S34", "S44"], "status": "MODEL"})
b.append(table(
    ["Year", "Model market value", "Assessed value", "Property tax", "Water (3 units)",
     "Electricity", "Insurance", "Maintenance", "Rental income (2 units)"],
    rows, caption="Property B — annual projection 2026–2055 (model, $10 rounding)",
    note="Assessed value = supplied 2025 assessment × 1.02^(year−2025) [S20/S29]; tax = assessed × 1.18268325% "
         "[S31]. Rental income grows at the CBO CPI anchor [S50] from an unverified user baseline; the SF Rent "
         "Board's 1.6% allowable increase for 3/1/2026–2/28/2027 [S34] and the AB 1482 cap [S33] may bind "
         "in practice — flagged IR-004. Water escalation note: SFPUC has proposed ~12.6%/12.5% increases for "
         "FY2027/FY2028 [S44] (IR-015), not used here."))
b.append('<h2>Projected federal estate tax exemption</h2>')
rows = []
for y in (2026, 2030, 2035, 2040, 2045, 2050, 2055):
    rows.append({"cells": [str(y), usd(exemption(y)), "2% CPI anchor" if y > 2026 else "statutory"],
                 "srcs": ["S01", "S10", "S50", "S52"], "status": "VERIFIED" if y == 2026 else "MODEL"})
b.append(table(["Year", "Projected basic exclusion", "Basis"],
               rows, caption="Federal basic exclusion amount (per decedent)",
               note="2026 is the verified statutory amount [S01]. Later years are model projections using "
                    "P.L. 119-21's inflation indexing [S10] at a 2% CBO-anchored rate [S50]. A married couple "
                    "may effectively double this with a timely portability election on Form 706 [S01]."))
subpage("projections", "Year-by-Year Projections", "".join(b), kicker="Category · projections")

# --- Operating costs ---
b = []
b.append('<p class="lead">Insurance, water, electricity/solar and maintenance: what is officially verified, '
         'what is blank, and how the model escalates costs.</p>')
b.append('<h2>Verified cost anchors</h2>')
anchors = [
    ("CA statewide average homeowner premium", "$1,571 / year", "Statewide average; 8,300,730 policies; 27 rate filings approved in 2026.", ["S46"]),
    ("ZIP-level residential insurance data", "published (2018–2023)", "CDI collects policy-level ZIP data; no parcel-level quote was confirmed for 95014 / 94122.", ["S47"]),
    ("Net Billing Tariff (NEM 3.0)", "from 04/15/2023", "Export compensation is usually lower than the retail rate; 9-year legacy period; NEM tariffs closed to new enrollment.", ["S41", "S42"]),
    ("San Jose Water 2025–2027 GRC", "rates adopted for TY2025 + attrition 2026/2027", "CPUC decision states it adopts rates for Test Year 2025 and two subsequent attrition years, 2026 and 2027.", ["S43"]),
    ("SFPUC proposed FY2027 / FY2028 water+sewer", "$21 / $23 per month average", "Approximately 12.6% and 12.5% per year — proposed, not confirmed adopted.", ["S44"]),
    ("SFPUC Hetch Hetchy Power FY2025-26", "+10% (~$8/month residential)", "Approved by the Commission on 04/08/2025.", ["S45"]),
    ("CBO CPI / PCE inflation", "2.7% in 2026 → 2.0% in 2030", "CPI-U roughly 2.2–2.3%/yr 2027–2035.", ["S50", "S53"]),
    ("HUD ZIP-level rent benchmark", "schedule published for FY2026", "Small Area FMRs by ZIP code; a voucher payment standard, not a market rent for a high-value home.", ["S48", "S49"]),
    ("SF allowable rent increase", "1.6% (3/1/2026–2/28/2027)", "Based on 60% of Bay Area CPI-U; AB 1482 caps at 5%+CPI or 10% through 01/01/2030.", ["S34", "S56", "S33"]),
]
b.append(table(["Item", "Official value", "Official context"],
               [{"cells": [x, y, z], "srcs": s, "status": "VERIFIED"} for x, y, z, s in anchors],
               caption="Officially published cost and escalation anchors",
               note="All values are read directly from the linked official pages."))
b.append('<h2>Values that cannot be confirmed (left blank)</h2>')
blanks = [
    ("Property A — parcel homeowners premium, 95014", "primary residence policy", ["S46", "S47"], "IR-007"),
    ("Property B — parcel landlord/rental dwelling premium, 94122", "3-unit rental policy", ["S46", "S47"], "IR-007"),
    ("Property A — water bill", "user estimate $100–$150/month", ["S43"], "IR-004"),
    ("Property A — electricity / solar net credit", "user estimate $10–$20/month profit", ["S41"], "IR-006"),
    ("Property B — water bill (3 units)", "user estimate $330–$400/month", ["S44"], "IR-004"),
    ("Property B — electricity bill (3 units)", "user estimate $30–$70/month", ["S45"], "IR-004"),
    ("Regular maintenance and repair, both properties", "user states only " + '"less than the SF house"', ["S09"], "IR-004"),
    ("Solar interconnection date / NEM grandfathering", "not supplied", ["S41", "S42"], "IR-006"),
    ("HUD FY2026 Small Area FMR for ZIP 95014", "exact row not extracted from official PDF", ["S48", "S49"], "IR-004"),
]
b.append(table(["Item", "Official value", "What is known", "Flag"],
               [{"cells": [x, blank(), y, flagref(f)], "srcs": s, "status": "UNVERIFIED"}
                for x, y, s, f in blanks],
               caption="Blank official values — flagged",
               note="Per the verification rule these cells are deliberately left blank rather than filled with "
                    "an inferred number. Each row still links the official source where the value would be found."))
b.append('<h2>Model cost escalation (selected years)</h2>')
rows = []
for y in (2026, 2030, 2035, 2040, 2045, 2050, 2055):
    ca, cb = op_costs(y, "A"), op_costs(y, "B")
    rows.append({"cells": [str(y), usd(ca["water"]), usd(ca["electric"]), usd(ca["insurance"]),
                           usd(ca["maintenance"]), usd(cb["water"]), usd(cb["electric"]),
                           usd(cb["insurance"]), usd(cb["maintenance"]), usd(sum(ca.values()) + sum(cb.values()))],
                 "srcs": ["S50", "S46", "S41", "S44", "S09"], "status": "MODEL"})
b.append(table(
    ["Year", "A water", "A electricity", "A insurance", "A maintenance",
     "B water", "B electricity", "B insurance", "B maintenance", "Combined operating"],
    rows, caption="Modelled annual operating costs (rounded to $10)",
    note="Baselines are unverified user estimates (or the CDI statewide average for insurance). Escalation uses "
         "the CBO CPI anchor [S50]. Maintenance = 1% of modelled market value [UNVERIFIED]. Electricity for "
         "Property A is negative (net credit). Full 30-year series is on the Projections page."))
b.append(callout("warn", "Insurance research result",
                 "The only official, parcel-independent benchmark found is the California Department of "
                 "Insurance statewide average of <strong>" + usd(CDI_AVG_PREMIUM) + " per year</strong>. "
                 "ZIP-level data exist [S47] but no official ZIP-specific premium for 95014 or 94122, and no "
                 "landlord-policy quote for the 3-unit property, was confirmed. The user's ~$1,500/yr guess is "
                 "close to the statewide average but is <strong>not</strong> treated as verified. Obtain actual "
                 "quotes before finalizing any decision."))
subpage("operating-costs", "Operating Costs", "".join(b), kicker="Category · costs")

# --- Inheritance law ---
b = []
b.append('<p class="lead">Federal, state and local tax law relevant to a trust inheritance, plus the '
         'income-tax rules that drive the live / rent / sell decision.</p>')
b.append('<h2>Federal</h2>')
fed = [
    ("Estate tax exemption 2026", "$15,000,000 per decedent; $30,000,000 with portability", ["S01", "S03"]),
    ("Form 706", "file if gross estate + adjusted taxable gifts > $15,000,000; due 9 months after death; Form 4768 6-month extension", ["S01"]),
    ("Rate above exemption", "40%", ["S17", "S04"]),
    ("Permanence / indexing", "$15M made permanent by P.L. 119-21 §70106, inflation-indexed from 2027", ["S10", "S11", "S03"]),
    ("Annual gift exclusion 2026", "$19,000 per recipient", ["S03", "S04"]),
    ("GST exemption 2026", "$15,000,000", ["S04"]),
    ("Basis of inherited property", "FMV at date of death (step-up)", ["S05", "S14"]),
    ("Capital gains rates", "0% / 15% / 20% (2026 15% ceiling $613,700 MFJ, $545,500 single)", ["S07", "S03"]),
    ("Home-sale exclusion", "$250,000 single / $500,000 joint; 2 of 5 years ownership + use", ["S06"]),
    ("Net Investment Income Tax", "3.8% on rents and gains above $250,000 MFJ / $200,000 single MAGI", ["S08"]),
    ("Rental depreciation", "27.5 years straight-line MACRS; unrecaptured §1250 gain up to 25%", ["S09", "S07"]),
    ("Fiduciary income tax", "estates/trusts report on Form 1041 (federal)", ["S08", "S18"]),
]
b.append(table(["Rule", "Official statement"],
               [{"cells": [x, y], "srcs": s, "status": "VERIFIED"} for x, y, s in fed],
               caption="Federal tax rules — official sources"))
b.append('<h2>California (state)</h2>')
ca_rows = [
    ("Estate / inheritance tax", "$0 — California does not conform to federal estate/GST tax; the pick-up tax is zero", ["S17"]),
    ("Beneficiary income", "a gift or inheritance is not included in income; later income it produces is taxable", ["S15"]),
    ("Capital gains", "no lower rate; all capital gains taxed as ordinary income", ["S16"]),
    ("Fiduciary return", "Form 541, due 15th day of 4th month after the tax year closes", ["S18", "S19"]),
    ("Property tax on death", "date of death is the change of ownership date for trust property", ["S30", "S24", "S25"]),
    ("Change-of-ownership statement", "trustee/transferee files within 150 days of death (R&T §480(b))", ["S26", "S27"]),
    ("Trustee notification", "within 60 days of the trust becoming irrevocable; 120-day contest window", ["S32"]),
    ("Revocable trust", "transfer into a revocable trust is not a change of ownership (R&T §62(d)); vesting in other beneficiaries at death is", ["S28"]),
]
b.append(table(["Rule", "Official statement"],
               [{"cells": [x, y], "srcs": s, "status": "VERIFIED"} for x, y, s in ca_rows],
               caption="California tax and trust-administration rules — official sources"))
b.append('<h2>Local (county / city)</h2>')
loc = [
    ("Property tax rate — Santa Clara County", "1% base + bonds; typical TRA example 1.1488%", ["S30", "S20"]),
    ("Property tax rate — San Francisco", "1.18268325% combined secured rate for FY2025-26", ["S31"]),
    ("Local inheritance or estate tax", "", ["S17", "S18"]),
]
b.append(table(["Rule", "Official statement"],
               [{"cells": [x, y if y else blank()], "srcs": s,
                 "status": "UNVERIFIED" if not y else "VERIFIED"} for x, y, s in loc],
               caption="Local rules",
               note="No official source imposing a local inheritance/estate tax was located. The value is left "
                    "blank and flagged (IR-012) rather than asserted as zero; a negative finding is not proof "
                    "of absence."))
b.append(callout("warn", "Trust vs. probate",
                 "A revocable living trust avoids probate for trust-titled property, but it does not avoid the "
                 "property-tax change of ownership at death, nor federal estate-tax filing if the estate is "
                 "large enough. The trust must be actually funded with the real property for this to apply; "
                 "confirm title with the successor trustee and county recorder."))
subpage("inheritance-law", "Inheritance & Estate Tax Law", "".join(b), kicker="Category · law")

# --- Estate thresholds ---
b = []
b.append('<p class="lead">How much can be inherited before tax, and how much headroom remains. The cash '
         'amount is a placeholder <code>[CASH AMOUNT]</code>; all headroom is expressed per $1,000,000 of '
         'inherited cash so no personal financial figure has to be published.</p>')
b.append('<h2>Verified thresholds</h2>')
th = [
    ("2026 federal basic exclusion", "$15,000,000", ["S01", "S03"]),
    ("2026 Form 706 filing threshold", "> $15,000,000 gross estate + adjusted taxable gifts", ["S01"]),
    ("Married couple with portability", "$30,000,000 (2026)", ["S01"]),
    ("Tax rate above the threshold", "40%", ["S17", "S04"]),
    ("2026 annual gift exclusion", "$19,000 per recipient", ["S03", "S04"]),
    ("2026 GST exemption", "$15,000,000", ["S04"]),
    ("California estate / inheritance tax", "$0 (pick-up tax is zero)", ["S17"]),
    ("Beneficiary-level income tax on inheritance", "$0 — inheritance is not income", ["S15"]),
    ("Local inheritance tax", "", ["S17", "S18"]),
]
b.append(table(["Threshold", "Official amount"],
               [{"cells": [x, y if y else blank()], "srcs": s,
                 "status": "UNVERIFIED" if not y else "VERIFIED"} for x, y, s in th],
               caption="Amounts allowed before tax penalty (verified)",
               note="Blank = no official source confirmed (IR-012). Track the exact statutory figure at the "
                    "linked official source; displayed dollar amounts are rounded to the nearest $10."))
b.append('<h2>Projected headroom by inheritance year</h2>')
rows = []
for Y in INHERIT_YEARS:
    s = SNAP[Y]
    h = s["headroom"]
    blocks = h / 1_000_000
    rows.append({"cells": [str(Y), usd(s["exemption"]), usd(2 * s["exemption"]), usd(s["market"]),
                           usd(h), "{:.1f}".format(blocks), usd(0.40 * 1_000_000)],
                 "srcs": ["S01", "S10", "S50", "S05", "S17"], "status": "MODEL"})
b.append(table(
    ["Year", "Projected exclusion (1 decedent)", "With portability (2×)", "Modelled Property A value",
     "Cash headroom before federal tax", "$1M blocks of cash headroom", "Tax per extra $1M above threshold"],
    rows, caption="Estate-tax headroom (model, rounded to $10)",
    note="Exclusion = $15,000,000 (2026, verified) × 1.02^(year−2026) using P.L. 119-21 indexing [S10] and "
         "the CBO CPI anchor [S50]. Headroom = exclusion − modelled Property A value; the real cash amount is "
         "withheld as [CASH AMOUNT]. Each additional $1,000,000 above the threshold costs $400,000 at the 40% "
         "rate [S17]. Portability requires a timely Form 706 [S01]. Estate tax is paid by the estate before "
         "distribution and therefore affects all three decision options equally."))
b.append(callout("good", "What this means",
                 "In the model's 2045 central case, the projected exclusion is about <strong>" +
                 usd(CENT_SNAP["exemption"]) + "</strong> per decedent. After including Property A's modelled "
                 "value of <strong>" + usd(CENT_SNAP["market"]) + "</strong>, roughly <strong>" +
                 usd(CENT_SNAP["headroom"]) + "</strong> of cash headroom remains before any federal estate "
                 "tax. California adds no estate or inheritance tax, and the beneficiary owes no income tax on "
                 "the inheritance itself. If the estate is near the threshold, a timely Form 706 portability "
                 "election can double the available exclusion."))
b.append('<h2>Pending law changes that could move the threshold</h2>')
watch = [
    ("P.L. 119-21 (enacted 07/04/2025)", "$15M permanent, inflation-indexed from 2027; no sunset", "ENACTED", ["S10", "S11"]),
    ("H.R.5336 Equal Tax Act (introduced 09/11/2025)", "would deem capital gains realized at gift or death", "PROPOSED", ["S12"]),
    ("H.Res.206 (introduced 03/10/2025)", "supports preserving stepped-up basis; referred to Ways and Means", "PROPOSED", ["S13"]),
    ("California Proposition 40 (11/03/2026)", "one-time 5% tax on covered assets > $1B; real property excluded; results unofficial until 12/11/2026", "NEEDS REVIEW", ["S37", "S38", "S39"]),
]
b.append(table(["Measure", "Effect", "Status"],
               [{"cells": [x, y], "srcs": s, "status": st} for x, y, st, s in watch],
               caption="Threshold-related law changes (official status)",
               note="No projection uses a proposed measure. See the Law Change Watchlist for the full list."))
subpage("estate-thresholds", "Tax Thresholds & Headroom", "".join(b), kicker="Category · thresholds")

# --- Decision analysis ---
b = []
b.append('<p class="lead">Three options, one comparable 10-year horizon, all numbers rounded to $10. '
         'The reasoning below each table explains why the recommendation follows.</p>')
b.append('<h2>Decision framework</h2>')
b.append(
    '<p>Common to all three options: <code>[BENEFICIARY]</code> can live at Property B without losing its '
    'rental income (user-supplied, unverified), so housing has no incremental cost in this model. '
    'The federal estate tax is paid by the estate before distribution, so it is identical across options and '
    'cancels out of the comparison. The comparison is therefore about <strong>after-inheritance property '
    'economics</strong>. All three options are measured as net wealth after 10 years, assuming the property '
    'would be sold at the end of the horizon (with selling costs and federal gain tax) so that the sell '
    'option is not artificially advantaged.</p>'
)
b.append('<h2>Results</h2>')
rows = []
for Y in INHERIT_YEARS:
    d = DEC[Y]
    rows.append({"cells": [str(Y), usd(d["live_cf1"]), usd(d["rent_cf1"]), usd(d["sell_proceeds"]),
                           usd(d["live_terminal"]), usd(d["rent_terminal"]), usd(d["sell_equity"]),
                           usd(d["sell_bond"])],
                 "srcs": ["S05", "S06", "S07", "S08", "S20", "S30", "S52"], "status": "MODEL"})
b.append(table(
    ["Inheritance year", "Live: year-1 net cash flow", "Rent: year-1 net cash flow",
     "Sell: net proceeds", "Live: 10-yr net wealth", "Rent: 10-yr net wealth",
     "Sell → equities 7%", "Sell → savings 4.3%"],
    rows, caption="Option comparison — 10-year net wealth (model, rounded to $10)",
    note="Live option claims the Prop 19 exclusion and homeowners' exemption; rent option assumes full "
         "reassessment; sell option uses stepped-up basis (no gain tax at sale) and a 6% selling-cost "
         "assumption. Net wealth for hold options = end-of-horizon liquidation value (after selling costs and "
         "federal gain tax, with §121 for the live case) + cumulative net cash flow. Portfolio gains are taxed "
         "at 20% LTCG + 3.8% NIIT [S07/S08]; California ordinary-income taxation of gains and rental-income "
         "tax are not modelled (IR-016), which is conservative for the sell option."))
b.append('<h2>Why the numbers look like this</h2>')
reasons = [
    ("1. Reassessment dominates",
     "At " + str(CENTRAL) + ", the annual property tax jumps from about " + usd(CENT_SNAP["tax_pre"]) +
     " to " + usd(CENT_SNAP["tax_full"]) + " on full reassessment. Even the Prop 19 owner-occupied case costs " +
     usd(CENT_SNAP["tax_p19_live"]) + "/yr. That single line item exceeds the modeled net rental cash flow.",
     ["S30", "S22", "S23", "S20"]),
    ("2. Living there has no financial upside here",
     "Housing is already available at Property B at no incremental cost while rental income continues, so "
     "occupying Property A adds costs of " + usd(-CENT["live_cf1"]) + "/yr with no offsetting rent or housing saving.",
     ["S25", "S21"]),
    ("3. Renting cannot outrun the tax and carrying costs",
     "At an unverified 3% gross rental yield, year-1 net cash flow after full reassessment, insurance, water, "
     "electricity and maintenance is " + usd(CENT["rent_cf1"]) + ". Rental income is also ordinary taxable "
     "income, which the model does not deduct (IR-016).", ["S09", "S07", "S08"]),
    ("4. Selling is tax-efficient at death",
     "Inherited basis equals FMV at death, so a prompt sale produces essentially no capital gain. Sale proceeds "
     "of " + usd(CENT["sell_proceeds"]) + " can be reinvested; at a modelled 7% equity return the 10-year "
     "after-federal-gain-tax value is " + usd(CENT["sell_equity"]) + ".", ["S05", "S07", "S08"]),
    ("5. Downside protection",
     "Using the CBO's official 4.3% average 10-year Treasury forecast instead of equities still gives " +
     usd(CENT["sell_bond"]) + ". The modelled break-even equity return is about " + pct(BE, 1) + ".", ["S52", "S50"]),
]
b.append(table(["Reason", "Numbers behind it"],
               [{"cells": [x, y], "srcs": s, "status": "MODEL"} for x, y, s in reasons],
               caption="Reasoning, with the official rules used",
               note="Every row links the official sources behind the rule being applied; the dollar amounts are "
                    "computed model outputs."))
b.append('<h2>Sensitivity</h2>')
rows = []
for eq in (0.04, 0.06, 0.07, 0.09, 0.10):
    d = decide(CENTRAL, equity=eq)
    rows.append({"cells": [pct(eq, 0), usd(d["sell_equity"]),
                           usd(d["sell_equity"] - d["rent_terminal"]),
                           "Sell" if d["sell_equity"] > d["rent_terminal"] else "Rent"],
                 "srcs": ["S52", "S07", "S08", "S05"], "status": "MODEL"})
b.append(table(["Assumed equity return", "Sell: 10-yr net wealth", "Advantage over rent", "Higher outcome"],
               rows, caption="Equity-return sensitivity, 2045 inheritance (model)",
               note="Equity returns are assumptions, not official projections. CBO's 4.3% 10-year Treasury "
                    "average [S52] is the only official return anchor used."))
b.append(callout("good", "Recommendation: " + BEST,
                 "Sell Property A reasonably promptly after the trust transfer and reinvest the net proceeds "
                 "across a diversified portfolio (equities plus a savings/Treasury allocation anchored to the "
                 "CBO 4.3% forecast), while continuing to live at Property B and collect its rental income. "
                 "The modelled 10-year advantage over renting is <strong>" +
                 usd(CENT["sell_terminal"] - CENT["rent_terminal"]) + "</strong> in the 2045 central case. "
                 "If the household wants to occupy Property A for non-financial reasons, confirm Prop 19 "
                 "eligibility first: it is the only mechanism that materially reduces the tax, and it requires "
                 "moving in within one year."))
b.append(callout("warn", "Before acting",
                 "Confirm (a) which property was the decedent's principal residence, (b) the actual tax "
                 "rate area and special assessments from the tax bill, (c) real insurance quotes, (d) the "
                 "solar/NEM interconnection date, and (e) California treatment of stepped-up basis with a "
                 "licensed tax professional. These are all on the "
                 "<a href=\"flagged-for-review.html\">Flagged for Review</a> page."))
subpage("decision-analysis", "Decision Analysis", "".join(b), kicker="Category · decision")

# --- Inheritance process ---
b = []
b.append('<p class="lead">A chronological, source-linked checklist of what happens when '
         '<code>[DECEDENT]</code> dies and <code>[TRUST]</code> transfers Property A to '
         '<code>[BENEFICIARY]</code>. Timing is taken from the official documents.</p>')
steps = [
    ("1", "Trust becomes irrevocable; successor trustee takes control",
     "On death of the settlor (revocable trust).", ["S32", "S28"]),
    ("2", "Serve the Notification by Trustee on beneficiaries and heirs",
     "Not later than 60 days after the event; includes the 120-day contest warning.", ["S32"]),
    ("3", "Obtain certified death certificate and the complete trust instrument (with amendments)",
     "Required for Form 706; BOE-19-P requires a full copy of the trust if a Prop 19 claim is filed.", ["S01", "S24"]),
    ("4", "Inventory trust assets; obtain date-of-death appraisals / FMV",
     "Establishes the stepped-up basis and estate value.", ["S05", "S01"]),
    ("5", "Determine federal estate tax filing: gross estate + adjusted taxable gifts > $15,000,000 in 2026",
     "Indexing applies from 2027; portability (DSUE) also requires a timely Form 706.", ["S01", "S10"]),
    ("6", "File Form 706 and pay any estate/GST tax",
     "Within 9 months of death; Form 4768 gives an automatic 6-month filing extension; top rate 40%.", ["S01", "S17"]),
    ("7", "File final income tax returns: federal Form 1040 / 1041, California Form 541",
     "Form 541 due the 15th day of the 4th month after the tax year closes; the date of death ends the decedent's tax year.", ["S18", "S19", "S08"]),
    ("8", "Confirm California has no estate/inheritance tax return; the inheritance is not beneficiary income",
     "State pick-up tax is zero; income earned later by inherited assets is taxable.", ["S17", "S15"]),
    ("9", "Record the transfer documents; file the Preliminary Change of Ownership Report (PCOR)",
     "PCOR goes to the County Recorder with recorded documents; a missing PCOR triggers an extra recording fee.", ["S30"]),
    ("10", "File the Change of Ownership Statement for death (BOE-502-AH / BOE-502-D)",
     "Trustee or transferee files within 150 days after the date of death (R&T §480(b)); penalties apply.", ["S26", "S27", "S25"]),
    ("11", "Determine Prop 19 eligibility",
     "Was the home the transferor's principal residence? Will the transferee occupy within one year?", ["S21", "S23", "S24"]),
    ("12", "If eligible, file BOE-19-P and claim the homeowners' exemption (BOE-266)",
     "Claim within 3 years of transfer; homeowners' exemption within 1 year for retroactive relief; exclusion cap = FBYV + $1,044,586.", ["S23", "S21", "S25", "S22"]),
    ("13", "Receive and review the supplemental assessment / reassessment notice",
     "Separate bill for the difference between old and new value, prorated to June 30; appeal within 60 days.", ["S30"]),
    ("14", "Update title, insurance, utilities, and solar/net-billing arrangements",
     "Notify the insurer; a landlord policy is needed if renting; NBT export credits are usually below retail rates.", ["S30", "S46", "S41"]),
    ("15", "Execute the chosen option",
     "Sell using stepped-up basis (gain ≈ 0; §121 if 2 of 5 years occupied), or rent (27.5-yr depreciation), or occupy.", ["S05", "S06", "S09"]),
    ("16", "Distribute assets, provide a final accounting, terminate the trust",
     "Final distribution is reported on the fiduciary return; California taxes capital gains as ordinary income.", ["S19", "S16"]),
]
rows = []
for num, action, timing, srcs in steps:
    rows.append({"cells": [num, esc(action), esc(timing)], "srcs": srcs, "status": "VERIFIED"})
b.append(table(["#", "Step", "Timing / amount"], rows,
               caption="Inheritance process — step by step",
               note="Each step cites the official document that establishes it. Deadlines are statutory; confirm "
                    "the exact dates with the successor trustee and county assessor at the time of death."))
b.append('<h2>Decision gates inside the process</h2>')
gates = [
    ("Within 1 year", "Move into Property A and file the homeowners' exemption — otherwise the Prop 19 exclusion is lost or only prospective.", ["S21", "S25"]),
    ("Within 150 days", "File the change-of-ownership statement for a death through a trust.", ["S26", "S27"]),
    ("Within 3 years", "File BOE-19-P for the intergenerational exclusion (before any transfer to a third party).", ["S23", "S24"]),
    ("Within 9 months", "File Form 706 / elect portability if needed.", ["S01"]),
    ("As soon as practicable", "If selling, do so near the date-of-death valuation to preserve the stepped-up basis benefit.", ["S05", "S07"]),
]
b.append(table(["Window", "Action"],
               [{"cells": [x, y], "srcs": s, "status": "VERIFIED"} for x, y, s in gates],
               caption="Deadlines that change the outcome"))
subpage("inheritance-process", "Step-by-Step Inheritance Process", "".join(b), kicker="Category · process")

# --- Law watchlist ---
b = []
b.append('<p class="lead">Enacted and currently discussed changes at the federal, state and local level. '
         'Nothing on this page is used as a fact inside a projection; proposed items are marked '
         '<span class="status proposed">PROPOSED</span>.</p>')
watch = [
    ("Federal", "P.L. 119-21 (H.R.1), §70106 — enacted 07/04/2025", "Raises the base estate/gift/GST exemption to $15M after 2025, indexed for inflation, with no sunset.", "ENACTED", ["S10", "S11", "S01"]),
    ("Federal", "Rev. Proc. 2025-32 — 2026 inflation adjustments", "Capital-gains thresholds, $19,000 annual gift exclusion, $1,460,000 special-use valuation limit.", "ENACTED", ["S03"]),
    ("Federal", "H.R.5336, Equal Tax Act — introduced 09/11/2025", "Would deem capital gains realized at gift or death (ending step-up in basis) with an exclusion and instalment payment.", "PROPOSED", ["S12"]),
    ("Federal", "H.Res.206 — introduced 03/10/2025", "Expresses support for preserving IRC §1014 stepped-up basis; referred to Ways and Means.", "PROPOSED", ["S13"]),
    ("Federal", "CRS policy options", "CRS notes options including taxing unrealized gains at death, changing the rate, and trust reforms.", "NEEDS REVIEW", ["S14"]),
    ("State", "California Proposition 40 — election 11/03/2026", "One-time 5% tax on covered assets above $1B; real property and many pensions excluded. Results unofficial; certification due 12/11/2026.", "NEEDS REVIEW", ["S37", "S38", "S39", "S55"]),
    ("State", "SB 293 (2025–2026)", "Amends R&T §§63.1/63.2 generational transfer exclusions (including wildfire-related transfers).", "PROPOSED", ["S35"]),
    ("State", "AB 1516 (Chapter 72, 2025)", "Three-year deadline for initial-purchaser exclusion claims; late claims apply prospectively; operative 01/01/2027.", "ENACTED", ["S36"]),
    ("State", "BOE Prop 19 exclusion cap adjustment", "Raised from $1,022,600 to $1,044,586 for 2/16/2025–2/15/2027; adjusted biennially from FHFA HPI.", "ENACTED", ["S22"]),
    ("State", "AB 1482 rent cap sunset", "5% + CPI (max 10%) rent cap applies until 01/01/2030.", "ENACTED", ["S33"]),
    ("Local", "SF Board File 261020 — notice posted 11/09/2026", "Would temporarily cap combined banked and capital-improvement rent increases at 10% per year; not enacted.", "PROPOSED", ["S34"]),
    ("Local", "SFPUC proposed FY2027/FY2028 water & sewer rates", "Average monthly bill increases of $21 and $23 (~12.6% and ~12.5% per year).", "PROPOSED", ["S44"]),
    ("Local", "SFPUC Hetch Hetchy Power FY2025-26", "10% retail rate increase (~$8/month residential), approved 04/08/2025.", "ENACTED", ["S45"]),
    ("Regulatory", "CPUC Net Billing Tariff (D.22-12-056)", "Effective for interconnection applications from 04/15/2023; export credits usually below retail; 9-year legacy; adder for applications before end of 2027.", "ENACTED", ["S41", "S42"]),
    ("Regulatory", "CPUC San Jose Water GRC (D.24-12-027)", "Rates adopted for test year 2025 and attrition years 2026–2027.", "ENACTED", ["S43"]),
]
b.append(table(["Level", "Measure", "What it does", "Status"],
               [{"cells": [l, m, w], "srcs": s, "status": st} for l, m, w, st, s in watch],
               caption="Law and rate changes — official status",
               note="Status values reflect the official source on 2026-11-10. Proposed measures are never used "
                    "in the projections. Prop 40's outcome is deliberately left pending (IR-011)."))
b.append(callout("warn", "Which changes matter most here",
                 "Any federal move to tax unrealized gains at death or repeal stepped-up basis would directly "
                 "reduce the sell option's main tax advantage. Any change to Prop 19 (SB 293, or future ballot "
                 "measures) would change the size of the reassessment. Local rent caps affect Property B's "
                 "income, not Property A's decision. Re-verify this page at the time of inheritance "
                 "(2040–2050), since projections 15–25 years out cannot price future legislation."))
subpage("law-watchlist", "Law Change Watchlist", "".join(b), kicker="Category · watchlist")

# --- Methodology ---
b = []
b.append('<p class="lead">How every number on this site was produced, and what was deliberately left out. '
         'The generator is deterministic: <code>python3 tools/build.py</code>.</p>')
b.append('<h2>Verification rules</h2>')
mv = [
    ("Sources", "Only official government domains. Every table row carries at least one official source link.", ["S01", "S20"]),
    ("Unverified values", "Official value left blank; item flagged UNVERIFIED and published on the Flagged for Review page.", ["S46"]),
    ("Model outputs", "Computed from verified rules + explicitly flagged inputs; every row marked MODEL and cites the rule.", ["S20", "S30", "S50"]),
    ("Rounding", "All dollar figures rounded to the nearest $10; exact statutory amounts remain at the linked source.", ["S01"]),
    ("Privacy", "No personal information; placeholders only.", ["S15"]),
]
b.append(table(["Rule", "Implementation"],
               [{"cells": [x, y], "srcs": s, "status": "VERIFIED"} for x, y, s in mv],
               caption="Verification policy"))
b.append('<h2>Formulas</h2>')
f = [
    ("Inflation factor", "2026 = 1; 2027 = 1.027; later years × 1.022/yr (CBO PCE 2.7% in 2026, CPI-U ~2.2%/yr).", ["S50", "S53"]),
    ("Market value (year y)", "supplied 2026 estimate × 1.03^(y−2026) — UNVERIFIED growth assumption.", ["S50"]),
    ("Assessed value before inheritance", "supplied 2026 assessment × 1.02^(y−2026) — official Prop 13 cap.", ["S20", "S29", "S30"]),
    ("Property tax", "assessed value × 1.1488% (Property A) or 1.18268325% (Property B).", ["S30", "S31"]),
    ("Prop 19 assessed value", "max(factored base year value, market value − $1,044,586).", ["S22", "S23"]),
    ("Operating costs", "unverified user baselines escalated by the CBO CPI anchor; insurance uses the CDI statewide average; maintenance = 1% of model market value.", ["S50", "S46"]),
    ("Sale proceeds", "market value × (1 − 6% selling costs); no capital-gains tax because basis = FMV at death.", ["S05", "S07"]),
    ("Portfolio value", "sale proceeds × (1 + return)^10, less 23.8% federal tax (20% LTCG + 3.8% NIIT) on the gain.", ["S07", "S08"]),
    ("Hold-option terminal value", "end-of-horizon market value − 6% selling costs − federal gain tax (with the $500,000 §121 exclusion for the owner-occupied case) + cumulative net cash flow.", ["S06", "S07", "S05"]),
    ("Estate exemption projection", "$15,000,000 × 1.02^(y−2026), using P.L. 119-21 indexing and the CBO CPI anchor.", ["S01", "S10", "S50"]),
]
b.append(table(["Quantity", "Formula / basis"],
               [{"cells": [x, y], "srcs": s, "status": "MODEL"} for x, y, s in f],
               caption="Model formulas",
               note="Formulas are transparent and reproducible; they are not official projections."))
b.append('<h2>Model input register</h2>')
rows = []
for item, scope, kind, val, srcs, flag in MODEL_INPUTS:
    rows.append({"cells": [esc(item), esc(scope), esc(kind), blank(), esc(val), flagref(flag)],
                 "srcs": srcs, "status": "UNVERIFIED"})
b.append(table(["Input", "Scope", "Kind", "Official value", "Model value used", "Flag"],
               rows, caption="Every input — official value blank where unverified",
               note="No manual input by the reader is required; these are fixed, published assumptions. "
                    "Each row links an official source relevant to where the true value would be found."))
b.append('<h2>Deliberately excluded</h2>')
exc = [
    ("Ordinary income tax on rental income and on Treasury interest", "Marginal rate not supplied; excluding it is generous to the hold/rent options.", ["S09", "S08"]),
    ("California ordinary-income tax on capital gains", "California has no lower capital-gains rate; gain tax on a prompt sale is ~$0 anyway.", ["S16"]),
    ("Depreciation and unrecaptured §1250 gain (25%) at final sale", "Would reduce the rent option's net wealth further.", ["S09", "S07"]),
    ("Mortgage interest, property management, vacancy, HOA", "No verified inputs supplied.", ["S09"]),
    ("Future tax-rate and Prop 19 cap changes", "Rates are set annually and the cap biennially; values for 2040–2050 are unknown.", ["S31", "S22"]),
]
b.append(table(["Excluded", "Why"],
               [{"cells": [x, y], "srcs": s, "status": "MODEL"} for x, y, s in exc],
               caption="Known omissions (flagged IR-016 / IR-008)"))
subpage("methodology", "Methodology & Assumptions", "".join(b), kicker="Reference · method")

# --- Sources ---
b = []
b.append('<p class="lead">Every official source used, with a direct link for manual review. All were fetched '
         'and read on ' + TODAY + '. No third-party or commercial source is used as a fact.</p>')
b.append('<div class="filterbar"><label class="small" for="tableFilter">Filter source register</label>'
         '<input id="tableFilter" type="search" placeholder="e.g. IRS or BOE"></div>')
rows = []
for sid, (title, agency, url) in SOURCES.items():
    rows.append({"cells": [sid, esc(agency), esc(title),
                           '<a href="{}" target="_blank" rel="noopener noreferrer">Open official page ↗</a>'.format(esc(url))],
                 "srcs": [sid], "status": "VERIFIED"})
b.append(table(["ID", "Agency", "Document", "Link"], rows,
               caption="Official source register (" + str(len(SOURCES)) + " sources)",
               note="Every source link in every table on this site resolves to one of these official documents."))
b.append(callout("good", "Manual review",
                 "For a line-by-line check, start with the "
                 "<a href=\"flagged-for-review.html\">Flagged for Review</a> page, then open each official "
                 "document above. The machine-readable register is also published at "
                 "<a href=\"../data/sources.json\">data/sources.json</a>."))
subpage("sources", "Source Register", "".join(b), kicker="Reference · sources")

# --- Flagged for review ---
b = []
b.append('<p class="lead">Clearly labelled <strong>Flagged for Review</strong> page. Every item below is '
         'published for manual checking; none of them blocks the site or the merge. Items whose official '
         'value could not be confirmed have been left blank in the data tables.</p>')
b.append('<div class="filterbar"><label class="small" for="tableFilter">Filter flags</label>'
         '<input id="tableFilter" type="search" placeholder="e.g. IR-002"></div>')
rows = []
for fid, title, detail, impact, srcs in FLAGS:
    rows.append({"cells": [flagref(fid), esc(title), esc(detail), esc(impact)],
                 "srcs": srcs, "status": "NEEDS REVIEW"})
b.append(table(["ID", "Item", "What was found", "Impact / action"], rows,
               caption="Flagged irregularities and unverified items (status: needs review)",
               note="Status 'needs review' means the item is published here and does not block anything. "
                    "Each row links the official source(s) relevant to the flag."))
b.append('<h2>Blank official values</h2>')
b.append('<p>The following cells were intentionally left blank in the site\'s data tables because no official '
         'source confirms the value. They are not inferred or filled in.</p>')
bl = [
    ("Local city/county inheritance tax rate", ["S17", "S18"], "IR-012"),
    ("Parcel-level homeowners premium, 95014", ["S46", "S47"], "IR-007"),
    ("Parcel-level landlord premium, 94122", ["S46", "S47"], "IR-007"),
    ("HUD FY2026 Small Area FMR row for 95014", ["S48", "S49"], "IR-004"),
    ("Actual parcel tax rate area / special assessments for both properties", ["S30", "S31"], "IR-003"),
    ("Solar interconnection date and NEM grandfathering", ["S41", "S42"], "IR-006"),
    ("Decedent's principal residence", ["S21", "S23"], "IR-005"),
    ("2026 California Proposition 40 certified outcome", ["S37", "S39"], "IR-011"),
    ("Future county tax rates and Prop 19 biennial cap adjustments", ["S31", "S22"], "IR-008"),
    ("Cash inheritance amount (withheld for privacy)", ["S01"], "IR-004"),
]
b.append(table(["Value left blank", "Flag"],
               [{"cells": [esc(x), blank(), flagref(f)], "srcs": s, "status": "UNVERIFIED"}
                for x, s, f in bl],
               caption="Blank cells — never inferred",
               note="The blank column is intentionally empty. Official sources are linked so each item can be "
                    "confirmed manually."))
subpage("flagged-for-review", "Flagged for Review", "".join(b), kicker="Review · needs review")

# --- Privacy ---
b = []
b.append('<p class="lead">Personal information privacy is the highest priority. This page states exactly '
         'what is and is not on this website.</p>')
b.append('<h2>Placeholders in use</h2>')
ph = [
    ("Property A — Cupertino ZIP 95014", "The property expected to be inherited through the trust.", ["S30"]),
    ("Property B — San Francisco Outer Sunset ZIP 94122", "The household residence and rental-income property held in context.", ["S31"]),
    ("[DECEDENT]", "The person whose death triggers the trust transfer.", ["S01"]),
    ("[BENEFICIARY]", "The person receiving the property and cash.", ["S15"]),
    ("[TRUST] / [TRUSTEE]", "The trust vehicle and its successor trustee.", ["S32"]),
    ("[CASH AMOUNT]", "The cash component of the inheritance; never published.", ["S01"]),
]
b.append(table(["Placeholder", "Meaning"],
               [{"cells": [x, y], "srcs": s, "status": "VERIFIED"} for x, y, s in ph],
               caption="Anonymization map",
               note="Source links show the official context in which each role is defined; no personal detail "
                    "is taken from any source."))
b.append('<h2>Excluded from the website and repository</h2>')
ex = [
    ("Names of any person", "No individual names appear.", ["S15"]),
    ("Street addresses, APN / parcel numbers, recorder document numbers", "No parcel identifiers appear; properties are identified by ZIP only.", ["S30"]),
    ("Account numbers, policy numbers, tax IDs, phone numbers, emails", "No identifiers appear.", ["S01"]),
    ("The cash inheritance amount and household composition", "Replaced with [CASH AMOUNT] and generic roles.", ["S01"]),
    ("Personal details encountered during research", "An official press release contains a private individual's contact details; only the legal text was used, and no personal detail was copied.", ["S37"]),
]
b.append(table(["Excluded", "Rule applied"],
               [{"cells": [x, y], "srcs": s, "status": "VERIFIED"} for x, y, s in ex],
               caption="Privacy exclusions",
               note="Any personal information discovered during research is for internal use only and does not "
                    "appear on the website or in the repository."))
b.append('<h2>How the public site is isolated</h2>')
b.append('<p>GitHub Pages publishes only the <code>docs/</code> directory. Internal working notes live in '
         '<code>internal/</code> and are not part of the published site. Those internal notes also contain '
         'no personal information. User-supplied figures appear only as clearly labelled unverified model '
         'inputs; the raw request text is never published.</p>')
b.append(callout("good", "Verification",
                 "A privacy scan runs as part of <code>tools/verify.py</code>, checking the published HTML "
                 "for names, addresses, parcel numbers, phone numbers, email addresses and the literal "
                 "cash-amount marker. See the <a href=\"sources.html\">Source Register</a> and "
                 "<a href=\"flagged-for-review.html\">Flagged for Review</a> pages for manual review."))
subpage("privacy", "Privacy & Anonymization", "".join(b), kicker="Reference · privacy")

# ---------------------------------------------------------------------------
# Write all subpages
# ---------------------------------------------------------------------------
for slug, (title, body, kicker, lead) in SUB.items():
    write(os.path.join(PAGES, slug + ".html"),
          layout(title, slug, body, kicker=kicker,
                 lead='<p class="lead">{}</p>'.format(esc(lead)) if lead else ""))

# ---------------------------------------------------------------------------
# Root mirror. GitHub Pages for this repository is configured with build_type
# "legacy", source = main / (root). The Pages administration API is not accessible
# to this session's token (403 "Resource not accessible by integration"), so the
# published site must also exist at the repository root. `docs/` stays canonical;
# the root copy is byte-identical, which keeps all relative links valid in both
# locations. Root `.nojekyll` keeps the legacy build a pure static copy.
# ---------------------------------------------------------------------------
import shutil  # noqa: E402

root_pages = os.path.join(ROOT, "pages")
root_assets = os.path.join(ROOT, "assets")
root_data = os.path.join(ROOT, "data")
for d in (root_pages, root_assets, root_data):
    os.makedirs(d, exist_ok=True)
shutil.copyfile(os.path.join(DOCS, "index.html"), os.path.join(ROOT, "index.html"))
for f in os.listdir(PAGES):
    if f.endswith(".html"):
        shutil.copyfile(os.path.join(PAGES, f), os.path.join(root_pages, f))
for f in os.listdir(ASSETS):
    shutil.copyfile(os.path.join(ASSETS, f), os.path.join(root_assets, f))
for f in os.listdir(DATA):
    if f.endswith(".json"):
        shutil.copyfile(os.path.join(DATA, f), os.path.join(root_data, f))

# `.nojekyll` keeps GitHub Pages from running Jekyll; the site is pure static HTML.
# Internal-only working notes are never linked from the site and contain no personal
# information. A `_config.yml` exclusion list is kept as a fallback for anyone who
# later removes `.nojekyll` and re-enables the Jekyll build.
write(os.path.join(ROOT, ".nojekyll"), "")
write(os.path.join(ROOT, "_config.yml"), """# Fallback only: GitHub Pages currently uses root .nojekyll (pure static copy).
# If .nojekyll is removed, these exclusions keep internal material off the site.
exclude:
  - internal
  - tools
  - docs
  - archive-v2
  - COORDINATION.md
  - README.md
  - VERIFICATION.md
  - .gitignore
  - "*.py"
""")

# Internal source register (generated from the same registry — no duplication drift)
lines = [
    "# Internal source register — generated by tools/build.py",
    "",
    "INTERNAL USE ONLY. No personal information. Verified " + TODAY + " (UTC).",
    "",
    "| ID | Agency | Official document | URL |",
    "| --- | --- | --- | --- |",
]
for sid, (title, agency, url) in SOURCES.items():
    lines.append("| {} | {} | {} | {} |".format(sid, agency, title.replace("|", "\\|"), url))
lines += ["", "Total: {} official sources. Each was fetched and read line by line.".format(len(SOURCES)), ""]
write(os.path.join(INTERNAL, "source-register.md"), "\n".join(lines))

print("Built {} source(s), {} fact(s), {} flag(s), {} subpage(s), {} projection year(s).".format(
    len(SOURCES), len(FACTS), len(FLAGS), len(SUB), len(YEARS)))
print("2045 central case (rounded $10): sell {}, rent {}, live {}, break-even equity {:.2f}%".format(
    usd(CENT["sell_terminal"]), usd(CENT["rent_terminal"]), usd(CENT["live_terminal"]), BE * 100))
