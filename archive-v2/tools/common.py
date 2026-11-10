"""Shared helpers for the static site build."""
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    ("index", "Overview", ""),
    ("properties", "Properties", "properties.html"),
    ("taxes", "Taxes & Projections", "taxes.html"),
    ("costs", "Operating Costs", "costs.html"),
    ("decisions", "Decision Analysis", "decisions.html"),
    ("process", "Inheritance Process", "process.html"),
    ("laws", "Law Tracker", "laws.html"),
    ("sources", "Sources", "sources.html"),
    ("flagged", "Flagged for Review", "flagged.html"),
]


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
FACTS = load("facts.json")["facts"]
PROJ = load("projections.json")
DEC = load("decisions.json")
ASSUM = load("assumptions.json")

RETRIEVED = "2026-11-10"


def money(n, dash_zero=False):
    if n is None or n == "":
        return "<span class='small'>—</span>"
    try:
        n = float(n)
    except (TypeError, ValueError):
        return escape(str(n))
    if dash_zero and n == 0:
        return "<span class='small'>—</span>"
    neg = n < 0
    s = f"{abs(n):,.0f}"
    return ("-$" if neg else "$") + s


def num(n):
    return f"{n:,.0f}"


def pct(x, d=2):
    return f"{x*100:.{d}f}%"


def esc(t):
    return escape(str(t))


def badge(status):
    m = {
        "verified": ("b-ok", "Verified"),
        "reported": ("b-warn", "Owner-reported"),
        "flagged": ("b-bad", "Flagged"),
        "projected": ("b-blue", "Projected"),
        "assumption": ("b-warn", "Assumption"),
        "pending": ("b-neutral", "Monitor"),
    }
    cls, label = m.get(status, ("b-neutral", status.title()))
    return f'<span class="badge {cls}">{label}</span>'


def src_link(sid, label=None):
    if not sid or sid not in SOURCES:
        return '<span class="small">no official source</span>'
    s = SOURCES[sid]
    host = s["publisher"].split("—")[0].strip()
    text = label or host
    return f'<a class="src" href="{s["url"]}" target="_blank" rel="noopener">{esc(text)}</a>'


def table(caption, headers, rows, note="", cls="", head_num_from=None):
    out = [f'<div class="tablewrap"><table class="{cls}">']
    if caption:
        out.append(f"<caption>{caption}</caption>")
    out.append("<thead><tr>")
    for i, h in enumerate(headers):
        if head_num_from is not None and i >= head_num_from:
            out.append(f'<th class="num">{h}</th>')
        else:
            out.append(f"<th>{h}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for cell in r:
            if isinstance(cell, tuple) and cell and cell[0] == "num":
                out.append(f'<td class="num">{cell[1]}</td>')
            else:
                out.append(f"<td>{cell}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if note:
        out.append(f'<p class="tnote">{note}</p>')
    return "\n".join(out)


def nav_html(active, prefix):
    items = []
    for slug, label, path in PAGES:
        if slug == active:
            cls = ' class="active"'
        else:
            cls = ""
        href = f"{prefix}index.html" if slug == "index" else f"{prefix}pages/{path}"
        items.append(f'<a{cls} href="{href}">{label}</a>')
    return '<nav class="main">' + "".join(items) + "</nav>"


def layout(slug, title, body, prefix="", description=None):
    active_label = dict((s, l) for s, l, _ in PAGES).get(slug, "")
    desc = description or "Internal decision analysis for two Bay Area residential properties. No personal identifiers."
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Bay Area Inheritance Analysis</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
<header class="top"><div class="wrap top-inner">
  <div class="brand"><span class="dot"></span> Bay Area Inheritance Analysis</div>
  {nav_html(slug, prefix)}
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
  <div><strong>Internal decision analysis.</strong> No names, addresses, parcel numbers or trust identifiers appear on this site.
  Parcel figures are rounded for privacy. <a href="{prefix}archive-v1/index.html">Earlier rules-only analysis (archived)</a>.</div>
  <div>Sources retrieved {RETRIEVED}. Figures rounded to the nearest $10. Not legal, tax or investment advice.</div>
</div></footer>
<script src="{prefix}assets/js/app.js"></script>
</body>
</html>
"""
    return doc


def write(path, html_text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(html_text)
    return full


# ---- derived numbers used on several pages -------------------------------
CU = PROJ["cupertino_series"]
SF = PROJ["sf_series"]
P19 = PROJ["prop19"]
SCEN = {s["key"]: s for s in PROJ["scenarios"]}
BY_YEAR = {r["year"]: r for r in CU}
SF_BY_YEAR = {r["year"]: r for r in SF}


# ---- Prop 19 helper (single source of truth: tools/model.py) -------------
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("model", os.path.join(ROOT, "tools", "model.py"))
MODEL = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(MODEL)


def prop19_at(year):
    return MODEL.prop19(year)
