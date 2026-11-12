#!/usr/bin/env python3
"""Shared CSS, layout shell, SVG chart generators, and strict $10-rounded row helpers."""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Dict, Iterable, List

BASE_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = BASE_DIR / "evidence" / "official_ledger.json"


def load_ledger_map() -> Dict[str, dict]:
    items = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    return {item["id"]: item for item in items}


def fmt_usd(val: int | float | None, signed: bool = False) -> str:
    """Format an integer $10-rounded amount; return blank em-dash marker if None."""
    if val is None:
        return '<span class="blank-cell" title="Unverified / not supplied — intentionally left blank; see Flagged for Review"></span>'
    iv = int(round(val / 10.0) * 10)
    if iv < 0:
        return f"-${abs(iv):,d}"
    if signed and iv > 0:
        return f"+${iv:,d}"
    return f"${iv:,d}"


def badge(kind: str) -> str:
    labels = {
        "verified": ("chip-verified", "Verified Official"),
        "owner": ("chip-owner", "Owner Input ($10-Rounded)"),
        "proj": ("chip-proj", "Projection ($10-Rounded)"),
        "assumed": ("chip-assumed", "Explicit Assumption"),
        "flagged": ("chip-flagged", "Flagged — Needs Review"),
    }
    cls, text = labels[kind]
    return f'<span class="chip {cls}">{html.escape(text)}</span>'


def clean_display_text(text: str) -> str:
    """Ensure rendered prose/tooltips use strict jurisdiction placeholders and $10-rounded amounts >=$100."""
    import re
    replacements = [
        ("City & County of San Francisco", "[Jurisdiction B — Consolidated City-County]"),
        ("San Francisco", "[Jurisdiction B]"),
        ("County of Santa Clara", "[County A]"),
        ("Santa Clara", "[County A]"),
        ("San Jose Water Company (San Jose Water)", "Regulated Class A Water Utility"),
        ("San Jose Water Company", "Regulated Class A Water Utility"),
        ("San Jose, Palo Alto, & Mountain View", "Three Charter Cities in [County A]"),
        ("San Jose, Palo Alto, and Mountain View", "Three Charter Cities in [County A]"),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)

    def _round_dollar(m: "re.Match[str]") -> str:
        raw = m.group(0)
        val = float(raw[1:].replace(",", ""))
        if val < 100.0:
            return raw
        r = int(round(val / 10.0) * 10)
        return f"${r:,d}"

    return re.sub(r"\$[0-9][0-9,]*(?:\.[0-9]+)?", _round_dollar, out)


def src_links(src_ids: Iterable[str], ledger_map: Dict[str, dict]) -> str:
    parts = []
    for sid in src_ids:
        entry = ledger_map[sid]
        url = html.escape(entry["url"], quote=True)
        short = html.escape(f'{entry["id"]}')
        title = html.escape(clean_display_text(f'{entry["agency"]} — {entry["title"]}'), quote=True)
        parts.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer" title="{title}">{short}</a>')
    return " · ".join(parts)


def tr_row(cells: List[str], src_ids: List[str], status_kind: str, ledger_map: Dict[str, dict], row_cls: str = "") -> str:
    cls_attr = f' class="{row_cls}"' if row_cls else ""
    tds = "".join(cells)
    srcs = f'<td class="src-col">{src_links(src_ids, ledger_map)}</td>'
    stat = f'<td class="stat-col">{badge(status_kind)}</td>'
    return f"<tr{cls_attr}>{tds}{srcs}{stat}</tr>\n"


def td(text: str, num: bool = False, bold: bool = False) -> str:
    classes = []
    if num:
        classes.append("num")
    if bold:
        classes.append("bold")
    c = f' class="{" ".join(classes)}"' if classes else ""
    return f"<td{c}>{text}</td>"


NAV_ITEMS = [
    ("index.html", "Overview"),
    ("pages/executive-summary.html", "Executive Summary"),
    ("pages/decision-analysis.html", "Decision Matrix"),
    ("pages/properties.html", "Properties & Roll Audit"),
    ("pages/operating-costs.html", "Operating Costs"),
    ("pages/projections.html", "50-Yr Projections"),
    ("pages/black-swan-scenarios.html", "Black-Swan Stress"),
    ("pages/inheritance-law.html", "Tax & Property Law"),
    ("pages/estate-thresholds.html", "Estate & Cash Headroom"),
    ("pages/inheritance-process.html", "Trust Process"),
    ("pages/law-watchlist.html", "Law Watchlist"),
    ("pages/flagged-for-review.html", "Flagged for Review"),
    ("pages/audit-reconciliation.html", "Model Audit"),
    ("pages/methodology.html", "Methodology"),
    ("pages/sources.html", "Official Sources"),
]


SITE_CSS = """\
:root {
  --bg: #f6f8fb;
  --surface: #ffffff;
  --surface-alt: #f0f4f9;
  --ink: #0f172a;
  --muted: #475569;
  --border: #cbd5e1;
  --accent: #0f4c81;
  --accent-soft: #e0f2fe;
  --good: #065f46;
  --good-bg: #d1fae5;
  --warn: #92400e;
  --warn-bg: #fef3c7;
  --bad: #991b1b;
  --bad-bg: #fee2e2;
  --info: #1e40af;
  --info-bg: #dbeafe;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.55;
  font-size: 15px;
}
header.site-header {
  background: #0b2545;
  color: #f8fafc;
  border-bottom: 3px solid #1d4ed8;
}
.header-inner {
  max-width: 1320px;
  margin: 0 auto;
  padding: 16px 24px 10px;
}
.brand-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}
.brand-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #ffffff;
  text-decoration: none;
}
.privacy-pill {
  font-size: 0.78rem;
  background: rgba(255,255,255,0.14);
  color: #e2e8f0;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.25);
}
nav.top-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
  padding-bottom: 4px;
}
nav.top-nav a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.82rem;
  padding: 5px 9px;
  border-radius: 6px;
  transition: background 0.15s;
}
nav.top-nav a:hover {
  background: rgba(255,255,255,0.12);
  color: #ffffff;
}
nav.top-nav a.active {
  background: #2563eb;
  color: #ffffff;
  font-weight: 600;
}
main.container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 26px 24px 56px;
}
h1 {
  font-size: 1.85rem;
  margin: 0 0 8px;
  color: #0b2545;
  letter-spacing: -0.02em;
}
h2 {
  font-size: 1.32rem;
  margin: 30px 0 10px;
  color: #0f2942;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 6px;
}
h3 {
  font-size: 1.06rem;
  margin: 20px 0 8px;
  color: #1e3a5f;
}
p.lead {
  font-size: 1.04rem;
  color: var(--muted);
  margin: 0 0 20px;
  max-width: 980px;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(235px, 1fr));
  gap: 14px;
  margin: 18px 0 26px;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 4px solid var(--accent);
  border-radius: 10px;
  padding: 15px 16px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}
.kpi-card.winner { border-top-color: #059669; }
.kpi-card.warn { border-top-color: #d97706; }
.kpi-label {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
  font-weight: 600;
}
.kpi-value {
  font-size: 1.52rem;
  font-weight: 800;
  color: var(--ink);
  margin: 4px 0;
  font-variant-numeric: tabular-nums;
}
.kpi-sub {
  font-size: 0.83rem;
  color: var(--muted);
}
.callout {
  background: var(--surface);
  border-left: 4px solid var(--accent);
  border: 1px solid var(--border);
  border-left-width: 5px;
  border-radius: 8px;
  padding: 14px 18px;
  margin: 16px 0;
}
.callout.rec { border-left-color: #059669; background: #f0fdf4; }
.callout.warn { border-left-color: #d97706; background: #fffbeb; }
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
  margin: 16px 0;
}
.nav-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 14px 16px;
}
.nav-card h3 { margin-top: 0; font-size: 1rem; }
.nav-card a { color: var(--accent); font-weight: 600; text-decoration: none; }
.nav-card a:hover { text-decoration: underline; }
.table-wrap {
  overflow-x: auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin: 14px 0 24px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}
thead th {
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 700;
  text-align: left;
  padding: 10px 11px;
  border-bottom: 2px solid var(--border);
  white-space: nowrap;
}
thead th.num { text-align: right; }
tbody td {
  padding: 8px 11px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #f8fafc; }
tbody tr.highlight-row { background: #ecfdf5; }
tbody tr.warn-row { background: #fffbeb; }
td.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
td.bold { font-weight: 700; }
td.src-col {
  font-size: 0.8rem;
  white-space: nowrap;
}
td.src-col a {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
}
td.src-col a:hover { text-decoration: underline; }
td.stat-col { white-space: nowrap; }
.chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
}
.chip-verified { background: var(--good-bg); color: var(--good); }
.chip-owner { background: var(--info-bg); color: var(--info); }
.chip-proj { background: #ede9fe; color: #5b21b6; }
.chip-assumed { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }
.chip-flagged { background: var(--warn-bg); color: var(--warn); }
.blank-cell::after {
  content: "— (blank)";
  color: #92400e;
  font-style: italic;
  font-size: 0.8rem;
}
.svg-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin: 16px 0 22px;
}
footer.site-footer {
  max-width: 1320px;
  margin: 0 auto;
  padding: 20px 24px 40px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.82rem;
}
@media (max-width: 760px) {
  .header-inner, main.container { padding-left: 14px; padding-right: 14px; }
  h1 { font-size: 1.45rem; }
}
"""


def render_page(rel_path: str, title: str, lead: str, body_html: str) -> str:
    prefix = "" if rel_path == "index.html" else "../"
    nav_links = []
    for href, label in NAV_ITEMS:
        cls = ' class="active"' if href == rel_path else ""
        nav_links.append(f'<a href="{prefix}{href}"{cls}>{html.escape(label)}</a>')
    nav_html = "\n".join(nav_links)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <title>{html.escape(title)} — Inheritance &amp; Two-Property Decision Dashboard</title>
  <link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <div class="brand-row">
      <a class="brand-title" href="{prefix}index.html">Two-Property Trust Inheritance &amp; Tax Decision Dashboard</a>
      <span class="privacy-pill">Privacy-Hardened · Strict Placeholders · All Amounts $10-Rounded · Official .gov Verified</span>
    </div>
    <nav class="top-nav" aria-label="Primary Navigation">
      {nav_html}
    </nav>
  </div>
</header>
<main class="container">
  <h1>{html.escape(title)}</h1>
  <p class="lead">{html.escape(lead)}</p>
  {body_html}
</main>
<footer class="site-footer">
  <div><strong>Privacy &amp; Verification Notice:</strong> Personal identifiers, street addresses, parcel numbers, neighborhood names, ZIP codes, and municipality names are withheld using strict placeholders (<code>[Property A]</code> and <code>[Property B]</code>). Every owner-supplied and modeled dollar figure is rounded to the nearest <code>$10</code> increment. Every table row links directly to an official government (<code>.gov</code> / <code>.ca.gov</code> / municipal agency) source; unconfirmed values are left blank and cataloged on <a href="{prefix}pages/flagged-for-review.html">Flagged for Review</a>. Analysis for informational planning only, not legal or tax advice.</div>
</footer>
</body>
</html>
"""


def svg_strategy_bars(plans_2045: dict) -> str:
    order = [
        ("sell_stocks", "S1: Sell [Property A] -> 100% Stock Index", "#059669"),
        ("sell_60_40", "S2: Sell [Property A] -> 60/40 Stocks + U.S. Treasuries", "#0d9488"),
        ("rent_a", "R: Keep & Rent Out [Property A]", "#2563eb"),
        ("sell_treasuries", "S3: Sell [Property A] -> 100% U.S. Treasuries (0% CA Tax)", "#4f46e5"),
        ("live_a_rent_u3", "L2: Live in [Property A] + Lease [Property B] Unit 3", "#d97706"),
        ("live_a_keep_u3", "L1: Live in [Property A] (Keep Unit 3 Unrented)", "#dc2626"),
    ]
    max_v = max(plans_2045[k]["terminal_wealth_ex_b_real_2026_r10"] for k, _, _ in order)
    bars = []
    y = 38
    for key, label, color in order:
        val = plans_2045[key]["terminal_wealth_ex_b_real_2026_r10"]
        w = int(round((val / max_v) * 470))
        bars.append(
            f'<text x="12" y="{y + 18}" font-size="12.5" fill="#0f172a" font-weight="600">{html.escape(label)}</text>'
            f'<rect x="335" y="{y}" width="{w}" height="24" rx="4" fill="{color}" />'
            f'<text x="{343 + w}" y="{y + 17}" font-size="12.5" fill="#0f172a" font-weight="700">${val:,d}</text>'
        )
        y += 38
    return f"""<div class="svg-panel">
  <svg viewBox="0 0 920 275" width="100%" role="img" aria-label="20-Year Real After-Tax Terminal Wealth Comparison (2026 Dollars, Excluding Identical Property B Equity)">
    <text x="12" y="22" font-size="14" font-weight="700" fill="#0b2545">20-Year Post-Inheritance After-Tax Wealth at 2065 (2045 Transfer Anchor, Constant 2026$, Ex-[Property B])</text>
    {"".join(bars)}
  </svg>
</div>"""


def svg_50yr_projection_lines(yearly: List[dict]) -> str:
    pts_val_a = []
    pts_val_b = []
    pts_av_rent = []
    pts_av_live = []
    max_val = max(r["val_a_nominal_r10"] for r in yearly)
    w_plot, h_plot = 780.0, 220.0
    x0, y0 = 80.0, 35.0
    n = len(yearly) - 1
    for i, r in enumerate(yearly):
        x = x0 + (i / n) * w_plot
        def y_of(v):
            return y0 + h_plot - (v / max_val) * h_plot
        pts_val_a.append(f"{x:.1f},{y_of(r['val_a_nominal_r10']):.1f}")
        pts_val_b.append(f"{x:.1f},{y_of(r['val_b_nominal_r10']):.1f}")
        pts_av_rent.append(f"{x:.1f},{y_of(r['av_a_rent_nominal_r10']):.1f}")
        pts_av_live.append(f"{x:.1f},{y_of(r['av_a_live_nominal_r10']):.1f}")

    x_2045 = x0 + ((2045 - 2026) / n) * w_plot
    return f"""<div class="svg-panel">
  <svg viewBox="0 0 900 300" width="100%" role="img" aria-label="50-Year Nominal Market and Assessed Value Trajectories (2026 to 2076)">
    <text x="80" y="20" font-size="13.5" font-weight="700" fill="#0b2545">50-Year Nominal Trajectory (2026–2076): [Property A] Market vs. Prop. 19 Assessed Paths &amp; [Property B] Market Value</text>
    <line x1="{x0}" y1="{y0+h_plot}" x2="{x0+w_plot}" y2="{y0+h_plot}" stroke="#94a3b8" stroke-width="1"/>
    <line x1="{x_2045:.1f}" y1="{y0}" x2="{x_2045:.1f}" y2="{y0+h_plot}" stroke="#dc2626" stroke-dasharray="4,4" stroke-width="1.5"/>
    <text x="{x_2045+5:.1f}" y="{y0+14}" font-size="11" fill="#dc2626" font-weight="700">2045 Trust Transfer Shock</text>
    <polyline fill="none" stroke="#059669" stroke-width="2.6" points="{' '.join(pts_val_a)}"/>
    <polyline fill="none" stroke="#2563eb" stroke-width="2.2" stroke-dasharray="6,3" points="{' '.join(pts_av_rent)}"/>
    <polyline fill="none" stroke="#d97706" stroke-width="2.2" points="{' '.join(pts_av_live)}"/>
    <polyline fill="none" stroke="#64748b" stroke-width="2.0" points="{' '.join(pts_val_b)}"/>
    <text x="80" y="276" font-size="11.5" fill="#0f172a">2026 ($3,100,000 [Property A])</text>
    <text x="415" y="276" font-size="11.5" fill="#0f172a">2050</text>
    <text x="775" y="276" font-size="11.5" fill="#0f172a">2076 ($20,022,310 nom.)</text>
    <text x="80" y="293" font-size="11" fill="#059669" font-weight="700">■ [Property A] Market Value</text>
    <text x="270" y="293" font-size="11" fill="#2563eb" font-weight="700">-- [Property A] Assessed (Rent = 100% FMV at Death)</text>
    <text x="585" y="293" font-size="11" fill="#d97706" font-weight="700">■ [Property A] Assessed (Live = Prop. 19 Cap)</text>
  </svg>
</div>"""
