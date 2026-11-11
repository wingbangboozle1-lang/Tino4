"""Static site generator.  Standard library only.  Every table row carries an official source link."""
import html, os
from content import SOURCES, VERIFIED_ON

ESC = html.escape

NAV = [
    ("index", "Overview"),
    ("executive-summary", "Executive summary"),
    ("properties", "The two properties"),
    ("decision-analysis", "Decision: live, rent or sell"),
    ("projections", "Year-by-year projections"),
    ("property-tax", "Property tax & assessment"),
    ("operating-costs", "Insurance, utilities, upkeep"),
    ("estate-thresholds", "Cash inheritance & tax-free limits"),
    ("inheritance-law", "Estate & inheritance tax rules"),
    ("inheritance-process", "Step-by-step process"),
    ("black-swan-scenarios", "Black-swan scenarios"),
    ("law-watchlist", "Law changes to watch"),
    ("methodology", "Methodology & assumptions"),
    ("sources", "Official sources"),
    ("flagged-for-review", "Flagged for Review"),
    ("privacy", "Privacy"),
]

STATUS_HELP = {
    "Verified": "Read on the linked official page by this project on " + VERIFIED_ON + ".",
    "Owner input": "Supplied by the owner and shown rounded to the nearest $10. Not checked against any record on purpose: no parcel, address or account is ever looked up.",
    "Model": "Calculated by this project from the linked official rules or statistics and the stated assumptions. Not an official figure.",
    "Assumption": "A planning assumption chosen by this project. Not an official figure.",
    "Guidance": "A practical step suggested by this project. Not an official requirement; the link gives the related official rule.",
    "Unverified": "Could not be confirmed from an official source, so the value is left blank. Listed on Flagged for Review.",
}


def r10(x):
    import math
    return int(math.floor(x / 10.0 + 0.5)) * 10


def money(x, blank=""):
    if x is None:
        return blank
    v = r10(x)
    return ("-$" if v < 0 else "$") + f"{abs(v):,}"


def mill(x):
    """$ in millions with two decimals (already coarser than $10)."""
    return f"${x / 1e6:,.2f} million"


def pct(x, d=1):
    if x is None:
        return ""
    return f"{x * 100:.{d}f}%"


def link(sid):
    ag, label, title, url, _ = SOURCES[sid]
    return f'<a class="src" href="{ESC(url, quote=True)}" title="{ESC(ag + ": " + title, quote=True)}" rel="noopener noreferrer">{ESC(label)}</a>'


def srcs(ids):
    return " · ".join(link(i) for i in ids)


def badge(status):
    cls = status.lower().replace(" ", "-")
    return f'<span class="badge b-{cls}" title="{ESC(STATUS_HELP.get(status, ""), quote=True)}">{ESC(status)}</span>'


class Counter:
    rows = 0
    tables = 0


def table(headers, rows, caption=None, cls="", raw=False):
    """rows: list of (cells, source_ids, status).  A row without a source is refused."""
    Counter.tables += 1
    head = "".join(f'<th scope="col">{ESC(h)}</th>' for h in headers)
    head += '<th scope="col">Status</th><th scope="col">Official source</th>'
    body = []
    for cells, sids, status in rows:
        if not sids:
            raise ValueError(f"table row without an official source: {cells!r}")
        if len(cells) != len(headers):
            raise ValueError(f"column mismatch: {cells!r} vs {headers!r}")
        tds = "".join(f"<td>{c if raw else ESC(str(c))}</td>" for c in cells)
        body.append(f"<tr>{tds}<td>{badge(status)}</td><td>{srcs(sids)}</td></tr>")
        Counter.rows += 1
    cap = f"<caption>{ESC(caption)}</caption>" if caption else ""
    return (f'<div class="tablewrap {cls}"><table>{cap}<thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def cards(items):
    """items: list of (label, big value, small text)."""
    out = "".join(f'<div class="card"><span class="k">{ESC(k)}</span><strong>{ESC(v)}</strong>'
                  f'<span class="s">{ESC(s)}</span></div>' for k, v, s in items)
    return f'<div class="cards">{out}</div>'


def note(text, kind="note"):
    return f'<div class="{kind}">{text}</div>'


def legend():
    items = "".join(f"<li>{badge(k)} {ESC(v)}</li>" for k, v in STATUS_HELP.items())
    return f'<details class="legend"><summary>What the status labels mean</summary><ul>{items}</ul></details>'


# ------------------------------------------------------------------ small inline charts (no scripts)
PALETTE = ["#1d4e89", "#c8553d", "#2a9d8f", "#8d6a9f", "#b08900"]


def line_chart(title, series, ylab="", height=260, fmt=lambda v: f"${v / 1e6:.1f}M"):
    """series: list of (label, [(x, y), ...])."""
    W, H, L, R, T, Bm = 720, height, 64, 16, 28, 34
    xs = [x for _, pts in series for x, _ in pts]
    ys = [y for _, pts in series for _, y in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(0, min(ys)), max(ys) * 1.05
    sx = lambda x: L + (x - x0) / (x1 - x0) * (W - L - R)
    sy = lambda y: T + (1 - (y - y0) / (y1 - y0)) * (H - T - Bm)
    g = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{ESC(title, quote=True)}" class="chart">',
         f'<text x="{L}" y="16" class="ct">{ESC(title)}</text>']
    for i in range(5):
        yv = y0 + (y1 - y0) * i / 4
        g.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(yv):.1f}" y2="{sy(yv):.1f}" class="grid"/>')
        g.append(f'<text x="{L - 6}" y="{sy(yv) + 4:.1f}" class="ax" text-anchor="end">{ESC(fmt(yv))}</text>')
    step = max(1, int((x1 - x0) / 7))
    for xv in range(int(x0), int(x1) + 1, step):
        g.append(f'<text x="{sx(xv):.1f}" y="{H - 12}" class="ax" text-anchor="middle">{xv}</text>')
    for i, (lab, pts) in enumerate(series):
        d = " ".join(f"{'M' if j == 0 else 'L'}{sx(x):.1f},{sy(y):.1f}" for j, (x, y) in enumerate(pts))
        c = PALETTE[i % len(PALETTE)]
        g.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2"/>')
        g.append(f'<rect x="{L + 8 + i * 170}" y="{T + 2}" width="10" height="10" fill="{c}"/>')
        g.append(f'<text x="{L + 22 + i * 170}" y="{T + 11}" class="lg">{ESC(lab)}</text>')
    g.append("</svg>")
    return f'<figure>{"".join(g)}<figcaption>{ESC(ylab)}</figcaption></figure>'


def bar_chart(title, bars, caption="", fmt=lambda v: f"${v / 1e6:.2f}M"):
    """bars: list of (label, value)."""
    W, rowh, L = 720, 34, 190
    H = 30 + rowh * len(bars) + 8
    vmax = max(v for _, v in bars) * 1.12
    g = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{ESC(title, quote=True)}" class="chart">',
         f'<text x="0" y="16" class="ct">{ESC(title)}</text>']
    for i, (lab, v) in enumerate(bars):
        y = 28 + i * rowh
        w = max(1.0, v / vmax * (W - L - 90))
        g.append(f'<text x="{L - 8}" y="{y + 17}" class="lg" text-anchor="end">{ESC(lab)}</text>')
        g.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="22" fill="{PALETTE[i % len(PALETTE)]}" rx="3"/>')
        g.append(f'<text x="{L + w + 6:.1f}" y="{y + 16}" class="lg">{ESC(fmt(v))}</text>')
    g.append("</svg>")
    return f'<figure>{"".join(g)}<figcaption>{ESC(caption)}</figcaption></figure>'


# ------------------------------------------------------------------ page shell
def page(slug, title, lead, body, out_dir):
    sub = slug != "index"
    root = "../" if sub else ""
    nav = "".join(
        f'<a href="{root}{"index.html" if key == "index" else "pages/" + key + ".html"}"'
        + (' aria-current="page"' if key == slug else "")
        + (' class="flag"' if key == "flagged-for-review" else "") + f">{ESC(label)}</a>"
        for key, label in NAV)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="Inheritance decision dashboard: an inherited home and an already-owned rental building, with official sources.">
<title>{ESC(title)} | Inheritance Decision Dashboard</title>
<link rel="stylesheet" href="{root}assets/style.css"></head>
<body>
<header class="top"><a class="brand" href="{root}index.html">Inheritance Decision Dashboard</a>
<span class="tag">Property A (Cupertino, to be inherited) · Property B (San Francisco, already owned)</span></header>
<div class="shell">
<nav aria-label="Sections">{nav}</nav>
<main><h1>{ESC(title)}</h1><p class="lede">{lead}</p>
{body}
</main></div>
<footer>Sources read {VERIFIED_ON}. All owner figures are rounded to the nearest $10 and all names and addresses are withheld.
Laws, rates and markets change; this is an organised reading of official sources and a planning model, not legal, tax, investment or insurance advice.
Items that could not be confirmed are on the <a href="{root}pages/flagged-for-review.html">Flagged for Review</a> page.</footer>
</body></html>
"""
    path = os.path.join(out_dir, "index.html") if not sub else os.path.join(out_dir, "pages", slug + ".html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return path


CSS = """
:root{--ink:#1c2430;--mut:#5b6675;--line:#dfe4ea;--bg:#f5f7fa;--card:#fff;--brand:#1d4e89;--accent:#c8553d;--ok:#1f7a4d;--warn:#9a6700}
*{box-sizing:border-box}html{font-size:16px}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
a{color:var(--brand)}a:hover{text-decoration:none}
.top{background:var(--brand);color:#fff;padding:14px 22px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline}
.top .brand{color:#fff;font-weight:700;font-size:1.15rem;text-decoration:none}.top .tag{opacity:.85;font-size:.9rem}
.shell{display:grid;grid-template-columns:250px minmax(0,1fr);gap:24px;max-width:1320px;margin:0 auto;padding:22px}
nav{position:sticky;top:12px;align-self:start;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}
nav a{display:block;padding:7px 10px;border-radius:7px;color:var(--ink);text-decoration:none;font-size:.93rem}
nav a:hover{background:#eef2f7}nav a[aria-current=page]{background:var(--brand);color:#fff;font-weight:600}
nav a.flag{color:var(--accent);font-weight:600}nav a.flag[aria-current=page]{background:var(--accent);color:#fff}
main{min-width:0}h1{font-size:1.75rem;margin:.1em 0 .2em}h2{font-size:1.25rem;margin:1.6em 0 .5em;padding-top:.4em;border-top:1px solid var(--line)}
h3{font-size:1.05rem;margin:1.2em 0 .4em}.lede{color:var(--mut);font-size:1.05rem;margin:.2em 0 1em;max-width:75ch}
p,li{max-width:85ch}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:13px 15px;display:flex;flex-direction:column;gap:3px}
.card .k{color:var(--mut);font-size:.8rem;text-transform:uppercase;letter-spacing:.04em}.card strong{font-size:1.35rem;line-height:1.2}.card .s{color:var(--mut);font-size:.86rem}
.answer{background:#eaf3ec;border:1px solid #b9d8c3;border-left:6px solid var(--ok);border-radius:10px;padding:14px 18px;margin:14px 0}
.answer h2{border:0;margin:.1em 0 .3em;padding:0}
.note{background:#eef4fb;border:1px solid #cfdff2;border-radius:10px;padding:10px 14px;margin:12px 0;font-size:.95rem}
.warn{background:#fff6e5;border:1px solid #f1d59a;border-left:6px solid var(--warn);border-radius:10px;padding:10px 14px;margin:12px 0;font-size:.95rem}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0 18px}
table{border-collapse:collapse;width:100%;font-size:.9rem}caption{caption-side:top;text-align:left;font-weight:600;padding:10px 12px 4px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
thead th{background:#eef2f7;position:sticky;top:0;font-size:.82rem;white-space:nowrap}
tbody tr:hover{background:#fafcff}tbody tr:last-child td{border-bottom:0}
.num td:not(:first-child):not(:nth-last-child(-n+2)){text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.num thead th:not(:first-child):not(:nth-last-child(-n+2)){text-align:right}
td:nth-last-child(1){font-size:.8rem;min-width:150px}td:nth-last-child(2){white-space:nowrap}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.72rem;font-weight:600;border:1px solid transparent;cursor:help}
.b-verified{background:#e3f3ea;color:#16603c;border-color:#b9d8c3}.b-owner-input{background:#e8eefb;color:#234a94;border-color:#c5d3f0}
.b-model{background:#f1ecf8;color:#5b3a86;border-color:#d9cbee}.b-assumption{background:#fdf3d7;color:#7a5600;border-color:#efd88f}
.b-guidance{background:#eef2f7;color:#3d4a5c;border-color:#cfd7e2}
.b-unverified{background:#fde8e4;color:#9b2c17;border-color:#f3c0b6}
a.src{white-space:nowrap}
.legend{font-size:.88rem;color:var(--mut);margin:8px 0}.legend ul{list-style:none;padding:0;margin:.5em 0}.legend li{margin:.3em 0}
figure{margin:12px 0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
figcaption{font-size:.82rem;color:var(--mut)}.chart{width:100%;height:auto}.chart .ct{font-size:13px;font-weight:600;fill:#1c2430}
.chart .ax{font-size:11px;fill:#5b6675}.chart .lg{font-size:12px;fill:#1c2430}.chart .grid{stroke:#e6eaef;stroke-width:1}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:12px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;text-decoration:none;color:var(--ink);display:block}
.tile:hover{border-color:var(--brand)}.tile b{display:block;color:var(--brand);margin-bottom:2px}.tile span{font-size:.88rem;color:var(--mut)}
.win{font-weight:700;color:var(--ok)}
footer{max-width:1320px;margin:10px auto 30px;padding:0 22px;color:var(--mut);font-size:.84rem}
@media (max-width:860px){.shell{grid-template-columns:1fr;padding:12px}nav{position:static;display:flex;flex-wrap:wrap;gap:2px}nav a{padding:5px 8px;font-size:.85rem}}
@media print{nav{display:none}.shell{display:block}}
"""
