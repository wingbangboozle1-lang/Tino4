#!/usr/bin/env python3
"""Generate a public, source-linked, local-only historical market stress page."""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_7adb71fc"))

from phased_history import (  # noqa: E402
    SERIES,
    TREASURY_CURVE,
    compare_paths,
    official_observations,
    price_only_peak_to_trough,
    public_series_payload,
)


def pct(value: float) -> str:
    return f"{value:+.1f}%" if value else "0.0% (start)"


def index_value(value: float, frequency: str) -> str:
    places = 2 if frequency == "monthly" else 6
    return f"{value:.{places}f}"


def observation_table(series_key: str) -> str:
    series = SERIES[series_key]
    rows = []
    for row in official_observations(series_key):
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{escape(str(row['label']))}</th>"
            f"<td>{escape(str(row['date']))}</td>"
            f"<td>{index_value(float(row['value']), series.frequency)}</td>"
            f"<td>{pct(float(row['change_pct_from_start']))}</td>"
            f"<td><a href=\"{escape(series.source_url, quote=True)}\" rel=\"noopener noreferrer\">FRED series {escape(series.series_id)}</a></td>"
            "</tr>"
        )
    return (
        "<div class=\"table-scroll\"><table><caption>Published price-index observations — "
        f"{escape(series.period_note)}. All rows source to the same series page.</caption>"
        "<thead><tr><th scope=\"col\">Observation</th><th scope=\"col\">Date</th>"
        f"<th scope=\"col\">Index level ({escape(series.unit)})</th>"
        "<th scope=\"col\">Change from first observation</th><th scope=\"col\">Primary source</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def drawdown_note(series_key: str) -> str:
    item = price_only_peak_to_trough(series_key)
    series = SERIES[series_key]
    return (
        f"<p class=\"evidence-note\"><strong>Observed price-only drawdown in this sampled 10-year slice:</strong> "
        f"{item['drawdown_pct']:.1f}% from {escape(str(item['peak_date']))} to "
        f"{escape(str(item['trough_date']))} ({index_value(float(item['peak_index']), series.frequency)} "
        f"to {index_value(float(item['trough_index']), series.frequency)} index units). "
        f"This calculation uses monthly/quarterly observations only; it is not a total-return decline. "
        f"<a href=\"{escape(series.source_url, quote=True)}\" rel=\"noopener noreferrer\">Source: FRED series {escape(series.series_id)}</a>.</p>"
    )


def path_table(series_key: str) -> str:
    results = compare_paths(series_key)
    rows = []
    for result in results:
        if result.path_key == "immediate":
            path_name = "Immediate equity price-index exposure"
            wait_text = "No Treasury wait"
            phase_text = "Buy at start; hold to the 10-year endpoint"
        else:
            wait_text = f"{result.wait_months} months"
            phase_text = (
                f"Four quarterly buys at month {result.wait_months}, "
                f"+3, +6, and +9 months; 10-year endpoint {escape(result.terminal_date)}"
            )
            if result.path_key == "bill-roll":
                path_name = "3-month bill-roll yield scenario"
            else:
                path_name = "Four-rung equal-notional ladder scenario (3m / 6m / 1y / 2y)"
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{escape(path_name)}</th>"
            f"<td>{escape(wait_text)}</td>"
            f"<td>{escape(phase_text)}</td>"
            f"<td>{result.terminal_per_starting_unit:.4f}</td>"
            f"<td>{result.maximum_observed_drawdown_pct:.1f}%</td>"
            "</tr>"
        )
    series = SERIES[series_key]
    return (
        "<div class=\"table-scroll\"><table><caption>Hybrid illustration: historical price-only equity series plus a current-yield scenario. "
        "Ending gross value per 1.000 normalized starting unit; not dollars, not after-tax, and not an observed historical portfolio.</caption>"
        "<thead><tr><th scope=\"col\">Path</th><th scope=\"col\">Cash wait</th>"
        "<th scope=\"col\">Equity purchases</th><th scope=\"col\">10-year ending gross value / starting unit</th>"
        f"<th scope=\"col\">Maximum observed drawdown ({escape(series.frequency)} points)</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def treasury_table() -> str:
    rows = []
    for months, label in ((3, "3-month"), (6, "6-month"), (12, "1-year"), (24, "2-year")):
        rate = TREASURY_CURVE["rates_percent"][months]
        term = TREASURY_CURVE["terms"][months]
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{escape(label)}</th>"
            f"<td>{rate:.2f}%</td>"
            f"<td>{escape(term)}</td>"
            f"<td><a href=\"{escape(TREASURY_CURVE['source_url'], quote=True)}\" rel=\"noopener noreferrer\">U.S. Treasury daily par yield curve, {escape(TREASURY_CURVE['as_of'])}</a></td>"
            "</tr>"
        )
    return (
        "<div class=\"table-scroll\"><table><caption>Official Treasury par-yield curve observations on "
        f"{escape(TREASURY_CURVE['as_of'])}; these are scenario inputs, not promised returns.</caption>"
        "<thead><tr><th scope=\"col\">Term</th><th scope=\"col\">Observed par yield</th>"
        "<th scope=\"col\">Instrument/curve point</th><th scope=\"col\">Source</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def render() -> str:
    series_links = []
    result_sections = []
    observation_sections = []
    for key, section_id, heading in (
        ("1929", "depression-series", "1929-era: September 1929 to September 1939"),
        ("2008", "financial-crisis-series", "2008-era: 2007 Q4 to 2017 Q4"),
    ):
        series = SERIES[key]
        series_links.append(
            f"<li><a href=\"#{section_id}\">{escape(heading)}</a> — {escape(series.provider)}; "
            f"series {escape(series.series_id)}, {escape(series.frequency)}; {escape(series.unit)}.</li>"
        )
        observation_sections.append(
            f"<section id=\"{section_id}\"><h3>{escape(heading)}</h3>"
            f"<p>{escape(series.title)} is a <strong>price-only index</strong>; dividends are excluded. "
            f"Source metadata lists {escape(series.period_note)} and {escape(series.unit)}.</p>"
            f"{observation_table(key)}{drawdown_note(key)}</section>"
        )
        result_sections.append(
            f"<section><h3>{escape(heading)}</h3>"
            f"<p>All equity purchase dates and the 10-year endpoint are sampled from {escape(series.frequency)} observations in "
            f"<a href=\"{escape(series.source_url, quote=True)}\" rel=\"noopener noreferrer\">FRED series {escape(series.series_id)}</a>.</p>"
            f"{path_table(key)}</section>"
        )
    payload = json.dumps(public_series_payload(), separators=(",", ":"), ensure_ascii=True)
    navigation = """<nav class="site-nav" aria-label="Main navigation">
      <div><strong>Decision</strong><a href="../index.html">Start / decision gates</a><a href="phased-investing.html">Treasury staging framework</a><a href="historical-market-stress.html" aria-current="page">Historical stress</a></div>
      <div><strong>Evidence &amp; law</strong><a href="what-we-need.html">Evidence needed</a><a href="deadline-timeline.html">Inheritance timeline</a><a href="glossary.html">Glossary</a></div>
      <div><strong>Review &amp; advisers</strong><a href="attorney-cpa-brief.html">Attorney &amp; CPA brief</a><a href="suggestions.html">Review suggestions</a><a href="privacy.html">Privacy</a></div>
    </nav>"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer">
<title>Historical price-only market stress · Private decision framework</title>
<link rel="stylesheet" href="../assets/history.css">
<script src="../assets/history.js" defer></script>
</head>
<body>
<header class="hero"><p class="eyebrow">Historical evidence · public series only</p><h1>Historical market stress: price-only replay</h1>
<p>Compare immediate equity exposure with 24- or 36-month Treasury parking followed by quarterly equity purchases. The historical stock-market observations are real published price-index points; the Treasury return assumptions are a separate, current-rate scenario.</p>
<div class="notice"><strong>Important:</strong> neither historical series includes dividends. The combined path results below are a hybrid illustration, not a realized historical portfolio, forecast, or probability estimate. No household values or property projections are used.</div>
{navigation}</header>
<main>
<section class="panel"><h2>What changes the answer?</h2>
<ul class="gates"><li><strong>Wait length:</strong> a 24- or 36-month Treasury wait changes when equity is purchased; it can avoid some early price decline but can miss a rebound.</li>
<li><strong>Cash yield:</strong> short yields can reset at every maturity; a two-year yield does not lock a three-year cash plan.</li>
<li><strong>Risk capacity:</strong> liquidity needs, tax situation, investment policy, and tolerance for a large loss can outweigh a single historical path.</li>
<li><strong>Not a property recommendation:</strong> this comparison does not decide whether to occupy, rent, or sell either property; see the decision gates and missing-evidence checklist.</li></ul>
</section>
<section class="panel"><h2>Source observations</h2>
<p>Each observation row below links directly to the underlying FRED table-data page and identifies its series ID. Values are index levels, not dollars of household wealth. Percent changes are arithmetic price-index changes from the first observation in that series slice.</p>
{''.join(observation_sections)}
</section>
<section class="panel"><h2>Immediate versus Treasury staging, then phased equity</h2>
<p>These static tables use the historical series for equity entry prices and exit levels. A normalized starting unit keeps the results scale-free; it is not a default portfolio size or a dollar recommendation.</p>
{''.join(result_sections)}
</section>
<section class="panel"><h2>Treasury inputs and ladder assumptions</h2>
<p>The U.S. Treasury's daily curve for {escape(TREASURY_CURVE['as_of'])} reported the following par-yield curve observations. The calculator uses the quoted annualized rates as simplified effective annual cash-yield assumptions, compounded monthly; actual bill discount conventions, auction results, note prices/coupons, taxes, fees, and future reinvestment rates differ.</p>
{treasury_table()}
<ul><li><strong>3-month roll:</strong> the full uninvested balance is modeled at the observed 3-month rate throughout, as if each reinvestment received that same rate. That rate is not guaranteed to persist.</li>
<li><strong>Four-rung ladder scenario:</strong> one quarter of the initial amount is assigned to each 3-month, 6-month, 1-year, and 2-year rung at the corresponding curve point. When each initial rung matures, proceeds are modeled as rolling into 3-month bills at the same 3-month rate until equity purchases begin.</li>
<li><strong>Phasing:</strong> four equal base-principal equity purchases occur at the end of the wait and then every three months (+3, +6, +9 months). Interest accrued on the remaining cash is swept into the final purchase.</li>
<li><strong>Reinvestment risk:</strong> falling future short rates reduce cash income; rising rates may increase it. The 2-year curve point is not an auction quote and the model does not price an actual note.</li>
</ul>
<p class="source-line"><a href="{escape(TREASURY_CURVE['source_url'], quote=True)}" rel="noopener noreferrer">U.S. Treasury Daily Treasury Par Yield Curve Rates</a> · <a href="{escape(public_series_payload()['treasury']['bills_url'], quote=True)}" rel="noopener noreferrer">TreasuryDirect: bill terms and auction rates</a> · <a href="{escape(public_series_payload()['treasury']['reinvest_url'], quote=True)}" rel="noopener noreferrer">TreasuryDirect: reinvestment mechanics</a>.</p>
</section>
<section class="panel interactive-only" aria-labelledby="calculator-title"><h2 id="calculator-title">Local-only what-if calculator</h2>
<p>Enter a generic amount if you want dollar outputs. No amount is prefilled. The browser performs the calculation using the data embedded in this page; it does not save or send your inputs. Dollar outputs are rounded to the nearest $10.</p>
<form id="market-form">
<div class="controls">
<label>Historical slice<select id="market-series" name="series"><option value="1929">1929-era · monthly Dow-Jones price index</option><option value="2008">2008-era · quarterly OECD U.S. share-price index</option></select></label>
<label>Treasury wait<select id="market-wait" name="wait"><option value="24">24 months</option><option value="36">36 months</option></select></label>
<label>Cash path<select id="market-path" name="path"><option value="bill-roll">3-month bill roll</option><option value="four-rung-ladder">Four-rung 3m / 6m / 1y / 2y ladder scenario</option></select></label>
<label>Optional starting amount in dollars<input id="market-principal" name="principal" type="number" min="10" step="10" inputmode="decimal" value="" placeholder="Leave blank or enter amount" autocomplete="off"></label>
</div>
<div class="actions"><button type="button" id="market-reset">Clear amount and reset</button></div>
</form>
<div id="market-output" class="output" aria-live="polite" aria-atomic="true">Enter a positive amount to see rounded dollar outputs. No amount is prefilled, stored, or sent anywhere.</div>
<p class="small">Calculator outcomes are gross and pretax. Personal taxes, cost basis, dividends, inflation, transaction costs, and fund expenses are not modeled. A 1929 or 2008 price-index path is not evidence of likely future returns.</p>
</section>
<section class="panel"><h2>Not calculated: after-tax and property economics</h2>
<p>There is no verified public input for either property's market value, tax bill, insurance quote, utility usage or rates, repair budget, rent, vacancy, debt, or tax status. These cells are intentionally blank rather than inferred. Obtain dated assessor/appraisal records, written insurer and contractor quotes, utility statements, executed lease details, and CPA-reviewed tax inputs privately.</p>
<p>After-tax sale proceeds and rental cash flow are not computed here. A decision model must separately account for sale price, basis, selling costs, debt payoff, applicable tax, rent collected, vacancy, management, property tax, insurance, utilities, repairs/capital work, and tax effects. The applicable values depend on private documents, local law, and future rules.</p>
</section>
<section class="panel"><h2>Limitations and source list</h2>
<ul><li>1929-era: {escape(SERIES['1929'].provider)}, series <code>{escape(SERIES['1929'].series_id)}</code>, {escape(SERIES['1929'].frequency)}, {escape(SERIES['1929'].unit)}. <a href="{escape(SERIES['1929'].source_url, quote=True)}" rel="noopener noreferrer">FRED table data</a>.</li>
<li>2008-era: {escape(SERIES['2008'].provider)}, series <code>{escape(SERIES['2008'].series_id)}</code>, {escape(SERIES['2008'].frequency)}, {escape(SERIES['2008'].unit)}. <a href="{escape(SERIES['2008'].source_url, quote=True)}" rel="noopener noreferrer">FRED table data</a>.</li>
<li>Rates are from the <a href="{escape(TREASURY_CURVE['source_url'], quote=True)}" rel="noopener noreferrer">U.S. Treasury curve</a>, not historical bill/note yields for either crash-entry window.</li></ul>
<p>Historical rows are point observations, not a full dividend-adjusted portfolio record. The monthly 1929 series and quarterly 2008 series have different providers, scales, and frequencies. The scenarios omit income tax, capital-gains tax, inflation, reinvested dividends, fund fees, and any specific asset allocation. No result is a recommendation or a probability statement.</p>
</section>
</main>
<footer><p>Privacy: no account, storage, analytics, external script, or network submission is used by the what-if tool. Do not enter confidential or identifying information into a public site.</p><p>Planning framework only — not financial, tax, legal, insurance, or investment advice. Recheck official sources and future law before acting.</p></footer>
<script id="market-data" type="application/json">{payload}</script>
</body></html>
"""


def main() -> None:
    path = ROOT / "pages" / "historical-market-stress.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(), encoding="utf-8")
    print(f"Built {path.relative_to(ROOT)} from public historical series only.")


if __name__ == "__main__":
    main()
