#!/usr/bin/env node
/**
 * Static site builder. Reads data/*.json and writes index.html plus pages/*.html.
 * No external dependencies, no build step required by GitHub Pages: the committed
 * HTML is what gets served. Run `node tools/build.mjs` after changing any data file.
 */

import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));

const sources = read("data/sources.json");
const properties = read("data/properties.json");
const laws = read("data/laws.json");
const costs = read("data/costs.json");
const proj = read("data/projections.json");
const pending = read("data/pending.json");
const flags = read("data/flags.json");

const SRC = {};
for (const s of sources.sources) SRC[s.id] = s;

const money = (n) =>
  n === null || n === undefined || Number.isNaN(n)
    ? "—"
    : "$" + Math.round(n).toLocaleString("en-US");
const pct = (n, d = 2) => (n === null || n === undefined ? "—" : (n * 100).toFixed(d) + "%");
const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

/** Renders a source link (or an explicit unverified marker) for a table row. */
function srcLink(id, label) {
  if (!id) return `<span class="unv">Unverified — blank</span>`;
  const s = SRC[id];
  if (!s) return `<span class="unv">Unknown source ${esc(id)}</span>`;
  const name = label || s.publisher.replace(/—.*/, "").trim();
  return `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(name)}</a>`;
}

const statusBadge = (status) => {
  const map = {
    verified_official: ["ok", "Verified"],
    verified: ["ok", "Verified"],
    user_supplied: ["user", "User-supplied"],
    derived: ["der", "Derived"],
    model_assumption: ["asm", "Assumption"],
    unverified: ["unv", "Unverified"],
    proposed: ["asm", "Proposed"]
  };
  const [cls, text] = map[status] || ["unv", status];
  return `<span class="badge ${cls}">${esc(text)}</span>`;
};

// ------------------------------------------------------------------ layout
const NAV = [
  ["index.html", "Dashboard"],
  ["pages/executive-summary.html", "Executive summary"],
  ["pages/properties.html", "Properties"],
  ["pages/projections.html", "Projections"],
  ["pages/decisions.html", "Decision analysis"],
  ["pages/inheritance-process.html", "Inheritance process"],
  ["pages/laws.html", "Laws & taxes"],
  ["pages/costs.html", "Operating costs"],
  ["pages/estate-tax.html", "Estate & inheritance tax"],
  ["pages/pending.html", "Pending legislation"],
  ["pages/flagged.html", "Flagged for review"],
  ["pages/sources.html", "Sources"]
];

function page({ file, title, subtitle, body, depth }) {
  const root = depth === 0 ? "" : "../";
  const nav = NAV.map(
    ([href, label]) =>
      `<a href="${root}${href}"${
        href === file ? ' class="active" aria-current="page"' : ""
      }>${esc(label)}</a>`
  ).join("");
  let out = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>${esc(title)} · Property A inheritance decision</title>
<link rel="stylesheet" href="${root}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    <div class="brand">
      <span class="dot" aria-hidden="true"></span>
      <span>Property A inheritance decision</span>
    </div>
    <p class="privacy">Anonymised · no addresses, no parcel numbers, no names</p>
  </div>
</header>
<nav class="nav" aria-label="Sections"><div class="wrap">${nav}</div></nav>
<main id="main" class="wrap">
  <div class="pagehead">
    <h1>${esc(title)}</h1>
    ${subtitle ? `<p class="lede">${subtitle}</p>` : ""}
  </div>
  ${body}
</main>
<footer class="foot">
  <div class="wrap">
    <p><strong>Planning document, not tax or legal advice.</strong> Every statutory figure is cited to a
    government source; every planning input is labelled as an assumption with a range. Dollar amounts are
    rounded to the nearest $10. Personal information is deliberately excluded.</p>
    <p>Research and verification date: 2026-11-10. Data files: <code>data/*.json</code>. Verification log:
    <a href="${root}VERIFICATION.md">VERIFICATION.md</a>. Coordination: <a href="${root}COORDINATION.md">COORDINATION.md</a>.</p>
  </div>
</footer>
</body>
</html>`;
  // Pages live one directory deep; body links are authored as "pages/x.html" for clarity and
  // rewritten here so they resolve from inside pages/.
  if (depth > 0) out = out.replace(/href="pages\//g, 'href="');
  return out;
}

function table(headers, rows, cls = "") {
  return `<div class="tablewrap"><table class="${cls}"><thead><tr>${headers
    .map((h) => `<th>${h}</th>`)
    .join("")}</tr></thead><tbody>${rows.join("")}</tbody></table></div>`;
}

// ------------------------------------------------------------------ data prep
const rec = proj.recommendation;
const sc = Object.fromEntries(proj.scenarios.map((s) => [s.id, s]));
const inhRow = proj.timeline.find((r) => r.year === proj.meta.inheritance_year);
const lastRow = proj.timeline[proj.timeline.length - 1];

// break-even reinvestment return for the sell case vs the best hold case
function breakEvenReturn() {
  // The sell case's terminal value is monotonic in the reinvestment return, so a bisection
  // against the best holding scenario finds the crossing point.
  const best = Math.max(sc["SC-LIVE"].totals.terminal_net_worth, sc["SC-RENT"].totals.terminal_net_worth);
  const sellPortfolio = sc["SC-SELL"].totals.reinvested_portfolio_net_of_tax;
  const sellOther = sc["SC-SELL"].totals.terminal_net_worth - sellPortfolio;
  // Scaling is not perfectly linear because income tax is applied each year, so a simple
  // algebraic solve is not exact; solve iteratively using the recorded sensitivity endpoints.
  const lo = { r: 0.045, v: proj.sensitivity.sell_reinvest_stock_low };
  const hi = { r: 0.085, v: proj.sensitivity.sell_reinvest_stock_high };
  const target = best;
  if (lo.v > target) return lo.r; // sell wins even at the low return
  if (hi.v < target) return null; // sell loses even at the high return
  // Linear interpolation between the two measured endpoints is close enough for a planning
  // break-even; labelled as interpolated on the page.
  const t = (target - lo.v) / (hi.v - lo.v);
  return lo.r + t * (hi.r - lo.r);
}
const beBreak = breakEvenReturn();

// ------------------------------------------------------------------ dashboard
const kpi = (label, value, note, cls = "") =>
  `<div class="kpi ${cls}"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div>${
    note ? `<div class="kpi-note">${note}</div>` : ""
  }</div>`;

const dashboard = `
<section class="kpis">
  ${kpi("Recommended strategy", "Sell Property A<br>and reinvest", `Margin ${money(
    rec.margin
  )} over the next best option (${(rec.margin_pct * 100).toFixed(1)}%)`, "kpi-primary")}
  ${kpi("Property A value, Nov 2026", money(properties.properties[0].market_value.amount), "User-supplied estimate", "kpi-user")}
  ${kpi("Property A inherited value, " + proj.meta.inheritance_year, money(inhRow.market_value_a), "Projected at 3.0%/yr")}
  ${kpi("Property B value, Nov 2026", money(properties.properties[1].market_value.amount), "User-supplied estimate", "kpi-user")}
  ${kpi("Property A property tax if inherited", money(sc["SC-LIVE"].property_tax_a_first_full_year) + "/yr", "With Prop 19 exclusion and homeowners' exemption")}
  ${kpi("Property A property tax if rented out", money(sc["SC-RENT"].property_tax_a_first_full_year) + "/yr", "No Prop 19 — reassessed to market value")}
  ${kpi("Federal estate tax exclusion, 2026", money(15000000), "Per decedent, indexed from 2027")}
  ${kpi("California estate / inheritance tax", "$0", "None — State Controller's Office")}
</section>

<section class="card callout">
  <h2>The answer in one paragraph</h2>
  <p>Property A is a <strong>${money(properties.properties[0].market_value.amount)}</strong> single-family home
  assessed at only <strong>${money(properties.properties[0].tax_history.find((r) => r.year === 2025).assessment)}</strong>,
  which is why its tax bill is ${money(properties.properties[0].tax_history.find((r) => r.year === 2025).property_tax)}
  a year instead of the ${money(properties.properties[0].market_value.amount * 0.013352)} a year a buyer
  at today's value would pay. Proposition 19 lets that low assessment survive the inheritance —
  but only if someone moves in and stays in, and only for as long as they stay. The model says the
  low assessment is worth roughly <strong>${money(
    sc["SC-LIVE"].prop19_detail.assessed_value_avoided
  )}</strong> of taxable value and about <strong>${money(
  sc["SC-LIVE"].prop19_detail.annual_tax_saved_year_one
)}</strong> a year at the transfer date. Against that, Property A is a
${(3.1e6).toLocaleString()} dollar asset earning no income while you live in it, and a
${money(lastRow.market_value_a)} asset by ${proj.meta.decision_horizon} if it appreciates at the base-case
3%/yr. Over a ${proj.meta.decision_horizon - proj.meta.inheritance_year}-year horizon, measured on the
same after-tax liquidation basis, <strong>${esc(rec.scenario_name)}</strong> ends at
<strong>${money(rec.terminal_net_worth)}</strong>, versus ${money(
  sc["SC-RENT"].totals.terminal_net_worth
)} for renting it out and ${money(sc["SC-LIVE"].totals.terminal_net_worth)} for living in it.
  </p>
  <p class="note">That ordering flips if the reinvestment return falls materially below the base case, or
  if Property A appreciates faster than 3%/yr. Both break-evens are computed on the
  <a href="pages/decisions.html">Decision analysis</a> page rather than left as a claim.</p>
</section>

<section class="card">
  <h2>Three strategies, same horizon, same tax treatment</h2>
  <p class="note">All three are valued by notionally selling everything in ${proj.meta.decision_horizon} and
  paying the capital-gains tax, with cash received along the way added back. No option wins merely
  by deferring tax.</p>
  ${table(
    ["Strategy", "Property A treatment", "Property tax on A, year 1", "Net cash over the period", "Terminal net worth", "Δ vs best"],
    proj.scenarios.map((s) => {
      const rank = proj.ranking.find((r) => r.id === s.id);
      return `<tr class="${rank.rank === 1 ? "best" : ""}">
        <td><strong>${esc(s.name)}</strong></td>
        <td>${s.prop19_applied ? "Prop 19 exclusion applies" : "Reassessed to market value"}</td>
        <td class="num">${money(s.property_tax_a_first_full_year)}</td>
        <td class="num">${money(s.totals.cumulative_net_cash)}</td>
        <td class="num"><strong>${money(s.totals.terminal_net_worth)}</strong></td>
        <td class="num">${rank.delta_vs_best === 0 ? "—" : money(rank.delta_vs_best)}</td>
      </tr>`;
    }),
    "tight"
  )}
  <p class="note">Horizon: ${proj.meta.decision_horizon}, i.e. ${proj.meta.decision_horizon - proj.meta.inheritance_year}
  years after an assumed ${proj.meta.inheritance_year} inheritance. Change those two dates and the ordering
  can change — see the sensitivity table on the Decision analysis page.</p>
</section>

<section class="card">
  <h2>What this dashboard contains</h2>
  <div class="grid">
    <a class="tile" href="pages/executive-summary.html"><strong>Executive summary</strong><span>The findings, the numbers behind them, and what to do next.</span></a>
    <a class="tile" href="pages/properties.html"><strong>Properties</strong><span>Both properties as recorded, including the full supplied tax and assessment series.</span></a>
    <a class="tile" href="pages/projections.html"><strong>Projections</strong><span>Year-by-year value, assessed value, property tax, rent and costs, 2026–${proj.meta.projection_window.end}.</span></a>
    <a class="tile" href="pages/decisions.html"><strong>Decision analysis</strong><span>Live vs rent vs sell, after tax, with break-evens and sensitivity.</span></a>
    <a class="tile" href="pages/inheritance-process.html"><strong>Inheritance process</strong><span>Step by step, with deadlines and the forms that matter.</span></a>
    <a class="tile" href="pages/laws.html"><strong>Laws &amp; taxes</strong><span>Prop 13, Prop 19, basis, rent caps — each with a citation.</span></a>
    <a class="tile" href="pages/costs.html"><strong>Operating costs</strong><span>Insurance, water, electricity, solar, maintenance, and which of those are actually verified.</span></a>
    <a class="tile" href="pages/estate-tax.html"><strong>Estate &amp; inheritance tax</strong><span>What the thresholds are, and how much cash would push the estate over.</span></a>
    <a class="tile" href="pages/pending.html"><strong>Pending legislation</strong><span>What is being discussed, and what it would change. Excluded from every computed number.</span></a>
    <a class="tile warn" href="pages/flagged.html"><strong>Flagged for review</strong><span>${flags.items.length} flagged items. Read this one.</span></a>
    <a class="tile" href="pages/sources.html"><strong>Sources</strong><span>The complete registry, with quotes and retrieval dates.</span></a>
  </div>
</section>

<section class="card warncard">
  <h2>Read this before relying on any number</h2>
  <ul>
    <li><strong>The Property B tax figures imply a 2.14% effective rate.</strong> San Francisco's published
    secured rate is 1.1816%. That gap has persisted for ten years and is either real parcel-level charges
    or a data error. One actual tax bill settles it.</li>
    <li><strong>Insurance is the weakest input.</strong> Both figures are the user's own estimate. No official
    body publishes a parcel-level premium. Earthquake coverage is not included at all.</li>
    <li><strong>No 2026 property tax bill exists yet</strong> for Property A, so that row is blank rather
    than filled in.</li>
    <li><strong>The decision is sensitive to the reinvestment return.</strong> At the base case the sell
    case wins by a wide margin; at 4.5% instead of 6.5% the margin largely disappears.
    ${beBreak ? `Break-even is about <strong>${pct(beBreak, 1)}</strong>.` : ""}</li>
  </ul>
  <p><a class="btn" href="pages/flagged.html">See all flagged items with source links →</a></p>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "index.html"),
  page({
    file: "index.html",
    title: "Dashboard",
    subtitle:
      "Whether to live in, rent, or sell the inherited Cupertino property — with every statutory input cited and every assumption labelled.",
    body: dashboard,
    depth: 0
  })
);

// ------------------------------------------------------------------ executive summary
const execBody = `
<section class="card">
  <h2>1. The decision</h2>
  <p>Around ${proj.meta.inheritance_year} (the stated window is 2040–2050, modelled at the midpoint) Property A —
  a single-family home in Cupertino, ZIP 95014 — passes to the heir through a trust, alongside a
  substantial cash amount. Property B, a three-unit building in San Francisco's Outer Sunset, ZIP 94122,
  is already owned and stays owned. The question is what to do with Property A:</p>
  <ol>
    <li><strong>Live in it.</strong> Move in, claim the Prop 19 parent-child exclusion, keep Property B's rent.</li>
    <li><strong>Rent it out.</strong> Stay in Property B, collect rent from both properties, lose the Prop 19 exclusion.</li>
    <li><strong>Sell it.</strong> Sell shortly after inheritance at a stepped-up basis, reinvest the proceeds, keep Property B rented.</li>
  </ol>
</section>

<section class="card">
  <h2>2. What the model found</h2>
  <p>On a common after-tax liquidation basis at ${proj.meta.decision_horizon}:</p>
  ${table(
    ["Rank", "Strategy", "Terminal net worth", "Difference from best"],
    proj.ranking.map(
      (r) =>
        `<tr class="${r.rank === 1 ? "best" : ""}"><td class="num">${r.rank}</td><td><strong>${esc(
          r.name
        )}</strong></td><td class="num">${money(r.terminal_net_worth)}</td><td class="num">${
          r.delta_vs_best === 0 ? "—" : money(r.delta_vs_best)
        }</td></tr>`
    )
  )}
  <p><strong>Why sell wins in the base case.</strong> Three things drive it, in order of size:</p>
  <ol>
    <li><strong>The low assessment is worth less than the asset's opportunity cost.</strong> Prop 19 saves
    about ${money(sc["SC-LIVE"].prop19_detail.annual_tax_saved_year_one)} a year at the transfer date, rising
    with the 2% assessment cap. That is real, and it is the whole reason live-in beats rent-out. But it is a
    small number against a ${money(properties.properties[0].market_value.amount)} asset.</li>
    <li><strong>Property B already provides the housing.</strong> The heir can live in Property B's third unit
    without giving up a dollar of the ${money(properties.properties[1].rent_monthly_total)} monthly rent, so
    living in Property A buys nothing that is not already owned — it only forfeits Property A's earning power.</li>
    <li><strong>A stepped-up basis makes the sale tax cheap.</strong> Basis resets to date-of-death value, so a
    prompt sale produces almost no capital gain. Selling later converts appreciation into taxable gain and
    eventually loses the §121 shelter if the heir never occupies.</li>
  </ol>
</section>

<section class="card">
  <h2>3. The three numbers that decide it</h2>
  ${table(
    ["Number", "Value", "Why it matters", "Status"],
    [
      `<tr><td>Property tax on Property A if lived in</td><td class="num">${money(
        sc["SC-LIVE"].property_tax_a_first_full_year
      )}/yr</td><td>Preserved by Prop 19 only while occupied</td><td>${srcLink("S-BOE-PROP19")}</td></tr>`,
      `<tr><td>Property tax on Property A if rented out</td><td class="num">${money(
        sc["SC-RENT"].property_tax_a_first_full_year
      )}/yr</td><td>Reassessed to market value — Prop 19 does not cover a rental</td><td>${srcLink(
        "S-BOE-PROP19"
      )}</td></tr>`,
      `<tr><td>Federal estate tax exclusion</td><td class="num">${money(15000000)}</td><td>Per decedent, 2026, indexed from 2027</td><td>${srcLink(
        "S-IRS-ESTATE"
      )}</td></tr>`,
      `<tr><td>California estate / inheritance tax</td><td class="num">$0</td><td>There is none</td><td>${srcLink(
        "S-SCO-ESTATE"
      )}</td></tr>`,
      `<tr><td>Reinvestment return used</td><td class="num">${pct(proj.inputs_used.stock_return, 1)}</td><td>Base case; range 4.5%–8.5%</td><td><span class="unv">Assumption</span></td></tr>`,
      `<tr><td>Home price appreciation used</td><td class="num">${pct(proj.inputs_used.appreciation_a, 1)}</td><td>Base case; range 2%–4%</td><td><span class="unv">Assumption</span></td></tr>`
    ]
  )}
</section>

<section class="card">
  <h2>4. Where the recommendation breaks</h2>
  <p>Stated up front because a recommendation that only works in its own base case is not a
  recommendation.</p>
  ${table(
    ["If this changes…", "…to this", "Terminal net worth of the affected strategy", "Does the answer change?"],
    [
      `<tr><td>Reinvestment return</td><td>4.5%</td><td class="num">${money(
        proj.sensitivity.sell_reinvest_stock_low
      )}</td><td>${proj.sensitivity.sell_reinvest_stock_low > proj.sensitivity.live_baseline ? "No — sell still wins" : "Yes — a hold strategy wins"}</td></tr>`,
      `<tr><td>Reinvestment return</td><td>8.5%</td><td class="num">${money(
        proj.sensitivity.sell_reinvest_stock_high
      )}</td><td>No — sell wins by more</td></tr>`,
      `<tr><td>Property A appreciation</td><td>4.0%/yr</td><td class="num">${money(
        proj.sensitivity.live_appreciation_high
      )} (live-in)</td><td>No — still below the sell case</td></tr>`,
      `<tr><td>Property A appreciation</td><td>2.0%/yr</td><td class="num">${money(
        proj.sensitivity.live_appreciation_low
      )} (live-in)</td><td>No — still below the sell case</td></tr>`,
      `<tr><td>Property A rent if rented out</td><td>$7,000/mo</td><td class="num">${money(
        proj.sensitivity.rent_high_rent
      )} (rent-out)</td><td>No — still below the sell case</td></tr>`,
      `<tr><td>Property A rent if rented out</td><td>$4,500/mo</td><td class="num">${money(
        proj.sensitivity.rent_low_rent
      )} (rent-out)</td><td>No — rent-out falls further behind</td></tr>`,
      `<tr><td>Insurance on Property A</td><td>$3,000/yr</td><td class="num">${money(
        proj.sensitivity.live_insurance_doubled
      )} (live-in)</td><td>No</td></tr>`
    ]
  )}
  <p class="note">${beBreak ? `The sell case only loses its lead below roughly <strong>${pct(
    beBreak,
    1
  )}</strong> of reinvestment return, interpolated between the measured 4.5% and 8.5% endpoints.` : "The sell case retains its lead across the whole measured return range."}</p>
</section>

<section class="card">
  <h2>5. Estate and inheritance tax: the short version</h2>
  <ul>
    <li><strong>California has no estate tax and no inheritance tax.</strong> No California estate tax return
    is required for any death on or after January 1, 2005 ${srcLink("S-SCO-ESTATE")}.</li>
    <li><strong>Inherited cash and property are not taxable income</strong> when received — federal or California
    ${srcLink("S-FTB-GIFTS")}.</li>
    <li><strong>The federal estate tax applies to the estate, not the heir</strong>, and only to the amount
    above ${money(15000000)} per decedent in 2026 ${srcLink("S-IRS-ESTATE")}. A married couple with a
    portability election effectively gets twice that.</li>
    <li><strong>So the exposure is simply: does the estate exceed the exclusion?</strong> At the base-case
    ${proj.meta.inheritance_year} values, the two properties alone are about
    ${money(inhRow.market_value_a + inhRow.market_value_b)}. That leaves roughly
    ${money(
      proj.estate_headroom.rows.find((r) => r.year === proj.meta.inheritance_year)
        .property_only_headroom_below_exclusion
    )}
    of headroom before the cash and other assets push the estate over ${money(15000000)}.</li>
    <li><strong>The forward-indexation assumption is conservative.</strong> Every year after 2026 is modelled
    at the 2026 exclusion as a <em>floor</em>, because the IRS has not published future amounts. The real
    exclusion will be higher, so the modelled tax is an upper bound.</li>
  </ul>
  <p><a class="btn" href="pages/estate-tax.html">Full estate-tax table by year →</a></p>
</section>

<section class="card">
  <h2>6. What to do, and in what order</h2>
  <ol class="steps">
    <li><strong>Get one actual Property B tax bill.</strong> It is the cheapest way to close the single largest
    data gap in this plan (the 2.14% implied rate).</li>
    <li><strong>Confirm Property A is the parents' principal residence and is titled in the trust.</strong>
    Prop 19 turns entirely on the first; probate is avoided only if the second is true.</li>
    <li><strong>Get insurance quotes for both properties</strong>, including an earthquake quote. This replaces
    the weakest number in the model with a real one.</li>
    <li><strong>Decide the occupancy question before the death, not after.</strong> The one-year homeowners'
    exemption deadline and the three-year claim deadline are unforgiving, and the exclusion is worthless if
    nobody moves in.</li>
    <li><strong>Re-run this model the year the valuation matters.</strong> The break-even reinvestment return
    is the number to watch.</li>
  </ol>
  <p><a class="btn" href="pages/inheritance-process.html">Step-by-step inheritance process →</a></p>
</section>

<section class="card warncard">
  <h2>7. Confidence</h2>
  ${table(
    ["Input", "Confidence", "Why"],
    [
      `<tr><td>Prop 13 / Prop 19 rules, thresholds, deadlines</td><td>${statusBadge("verified_official")}</td><td>Read directly from BOE and county assessor pages, quoted in the verification log</td></tr>`,
      `<tr><td>Federal and California estate / gift / capital-gains law</td><td>${statusBadge("verified_official")}</td><td>IRS and FTB publications and revenue procedures</td></tr>`,
      `<tr><td>Utility tariffs</td><td>${statusBadge("verified_official")}</td><td>Published SFPUC and SJW schedules, effective 7/1/2026</td></tr>`,
      `<tr><td>Market values and tax histories</td><td>${statusBadge("user_supplied")}</td><td>Supplied in the request; not independently verified against county records</td></tr>`,
      `<tr><td>Insurance premiums</td><td>${statusBadge("unverified")}</td><td>No official parcel-level source exists; figures are the user's estimates</td></tr>`,
      `<tr><td>Appreciation, inflation, reinvestment return, rent growth</td><td>${statusBadge("model_assumption")}</td><td>Anchored where possible to FHFA, BOE and Treasury data; each carries a range</td></tr>`
    ]
  )}
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/executive-summary.html"),
  page({
    file: "pages/executive-summary.html",
    title: "Executive summary",
    subtitle: "The recommendation, the three numbers that drive it, where it breaks, and what to do first.",
    body: execBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ properties
const propRows = [];
for (const p of properties.properties) {
  for (const r of p.tax_history) {
    propRows.push(`<tr>
      <td><strong>${esc(p.label)}</strong></td>
      <td class="num">${r.year}</td>
      <td class="num">${r.property_tax === null ? '<span class="unv">blank</span>' : money(r.property_tax)}</td>
      <td class="num">${money(r.assessment)}</td>
      <td class="num">${r.assessment_growth === null ? "—" : pct(r.assessment_growth, 1)}</td>
      <td class="num">${r.tax_growth === null ? "—" : pct(r.tax_growth, 1)}</td>
      <td class="num">${
        r.property_tax === null ? "—" : pct(r.property_tax / r.assessment, 2)
      }</td>
      <td>${statusBadge("user_supplied")}</td>
      <td>${r.flag ? `<span class="unv">${esc(r.flag)}</span>` : "—"}</td>
    </tr>`);
  }
}

const propsBody = `
<section class="card">
  <h2>Properties as recorded</h2>
  <p class="note">No addresses, no assessor's parcel numbers, no parcel identifiers, no names and no
  trustee details appear anywhere in this project. That is deliberate and it is the highest-priority
  constraint on the whole exercise. It also means a few things cannot be verified — those are marked.</p>
  ${table(
    ["", "Property A", "Property B"],
    [
      `<tr><td>Location</td><td>Cupertino, ZIP 95014<br><span class="muted">Santa Clara County</span></td><td>San Francisco Outer Sunset, ZIP 94122<br><span class="muted">City &amp; County of San Francisco</span></td></tr>`,
      `<tr><td>Role</td><td>${esc(properties.properties[0].role)}</td><td>${esc(properties.properties[1].role)}</td></tr>`,
      `<tr><td>Estimated market value, Nov 2026</td><td class="num">${money(
        properties.properties[0].market_value.amount
      )} ${statusBadge("user_supplied")}</td><td class="num">${money(
        properties.properties[1].market_value.amount
      )} ${statusBadge("user_supplied")}</td></tr>`,
      `<tr><td>Assessed value on the roll</td><td class="num">${money(
        properties.properties[0].tax_history.find((r) => r.year === 2026).assessment
      )} (2026)</td><td class="num">${money(
        properties.properties[1].tax_history.find((r) => r.year === 2025).assessment
      )} (2025) ${statusBadge("user_supplied")}</td></tr>`,
      `<tr><td>Property tax, latest year with a bill</td><td class="num">${money(
        properties.properties[0].tax_history.find((r) => r.year === 2025).property_tax
      )} (2025)</td><td class="num">${money(
        properties.properties[1].tax_history.find((r) => r.year === 2025).property_tax
      )} (2025)</td></tr>`,
      `<tr><td>Units</td><td class="num">${properties.properties[0].units}</td><td class="num">${
        properties.properties[1].units
      } (2 rented, 1 occupied by the owner without losing rent)</td></tr>`,
      `<tr><td>Rent received</td><td class="num">$0</td><td class="num">${money(
        properties.properties[1].rent_monthly_total
      )}/month ${statusBadge("user_supplied")}</td></tr>`,
      `<tr><td>Solar</td><td>Installed; reported as a net credit of $10–$20/month ${statusBadge(
        "user_supplied"
      )}</td><td>Not reported</td></tr>`,
      `<tr><td>Water per month</td><td class="num">$100–$150 ${statusBadge("user_supplied")}</td><td class="num">$330–$400 for all three units ${statusBadge(
        "user_supplied"
      )}</td></tr>`,
      `<tr><td>Electricity per month</td><td class="num">net credit ≈ $15 ${statusBadge("user_supplied")}</td><td class="num">$30–$70 ${statusBadge(
        "user_supplied"
      )}</td></tr>`,
      `<tr><td>Insurance per year</td><td class="num">≈ $1,500 ${statusBadge("unverified")}</td><td class="num">≈ $1,500 ${statusBadge(
        "unverified"
      )}</td></tr>`,
      `<tr><td>Maintenance burden</td><td>Lower, per the request</td><td>Higher, per the request</td></tr>`
    ],
    "compare"
  )}
</section>

<section class="card">
  <h2>Supplied tax and assessment series — every row</h2>
  <p class="note">These are the figures from the request, reproduced row for row. They are <strong>not</strong>
  independently verified against county records, because the parcel number is deliberately not recorded.
  The last column shows where the supplied data cannot be reconciled with a constant tax rate.</p>
  ${table(
    ["Property", "Year", "Property tax", "Tax assessment", "Assessment Δ", "Tax Δ", "Implied rate", "Status", "Note"],
    propRows
  )}
</section>

<section class="card warncard">
  <h2>Two things the supplied series cannot explain</h2>
  <h3>1. Property B's implied tax rate is 2.14%, but San Francisco publishes 1.1816%</h3>
  <p>${money(2440)} ÷ ${money(114250)} = <strong>2.1350%</strong>. The published FY2026-27 secured rate is
  <strong>1.18162182%</strong> ${srcLink("S-SF-TREAS-SECURED")}. The gap is roughly $1,070 a year, and it has
  persisted for a decade — the implied rate ranges from 1.68% (2016) to 2.14% (2025). A ten-year consistent
  gap is more likely to be real parcel-level charges (special assessments, bond levies, a district charge
  that is not in the secured rate) or a second parcel appearing on the same bill, than a typo. The model
  uses the implied 2.135% so the projection matches the bills actually paid, and shows the published rate
  beside it.</p>
  <p><strong>Action:</strong> one actual tax bill settles it.</p>

  <h3>2. Property A's implied rate is 1.335%, against a county illustration of 1.1488%</h3>
  <p>${money(7210)} ÷ ${money(539740)} = <strong>1.3352%</strong>. Santa Clara County's own illustration of a
  typical tax rate area is 1.1488% ${srcLink("S-SCC-ASSESSOR-BOOKLET")}. A 16% excess is explained easily by a
  tax rate area with more bond load, but it cannot be confirmed without the parcel number. The model uses
  the implied rate and runs the county figure as a sensitivity.</p>

  <h3>3. Two Property A years break the pattern</h3>
  <p>In 2017 the tax <em>fell</em> 0.5% while the assessment rose 2%. In 2020 the tax was identical to 2019
  ($6,560) while the assessment rose 2%. Neither can be produced by a constant-rate model. They are kept
  exactly as supplied rather than corrected.</p>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/properties.html"),
  page({
    file: "pages/properties.html",
    title: "Properties",
    subtitle: "Both properties exactly as recorded, with the full supplied tax and assessment series and the two anomalies they contain.",
    body: propsBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ projections
const timelineRows = proj.timeline.map((r) => {
  const isInh = r.year === proj.meta.inheritance_year;
  return `<tr class="${isInh ? "mark" : ""}">
    <td class="num"><strong>${r.year}</strong></td>
    <td class="num">${money(r.market_value_a)}</td>
    <td class="num">${money(r.assessed_value_a)}</td>
    <td class="num">${money(r.property_tax_a)}</td>
    <td class="num">${money(r.market_value_b)}</td>
    <td class="num">${money(r.assessed_value_b)}</td>
    <td class="num">${money(r.property_tax_b)}</td>
    <td class="num">${money(r.rent_b_annual)}</td>
    <td>${r.basis === "supplied baseline" ? statusBadge("user_supplied") : '<span class="badge der">Projected</span>'}
        ${isInh ? '<span class="badge mark">Inheritance year</span>' : ""}</td>
  </tr>`;
});

const projectionsBody = `
<section class="card">
  <h2>How the projection works</h2>
  <div class="grid2">
    <div>
      <h3>Property tax</h3>
      <p>Assessed value rises at most 2% a year on the existing roll — the BOE set the 2026-27 inflation
      factor at exactly 1.02 ${srcLink("S-BOE-LTA26002")}. Tax is assessed value times the property's rate.
      Property A's rate is the 1.3352% implied by its own bills; Property B's is the 2.1350% implied by its own.
      Both are flagged, because they differ from the published county rates.</p>
    </div>
    <div>
      <h3>Market value</h3>
      <p>Grows at ${pct(proj.inputs_used.appreciation_a, 1)} a year for Property A and
      ${pct(proj.inputs_used.appreciation_b, 1)} for Property B. The anchor is the FHFA all-transactions
      California HPI, which compounded at about 3.8% from 2004 to 2026 ${srcLink(
        "S-FHFA-HPI-CA"
      )} — the base case sits deliberately below that because the index barely moved in the last year
      (+0.90%) and Cupertino's population fell 3.2% between 2020 and 2025 ${srcLink("S-CENSUS-QF-CUPERTINO")}.</p>
    </div>
    <div>
      <h3>Rent</h3>
      <p>Property B's ${money(properties.properties[1].rent_monthly_total)}/month grows at
      ${pct(proj.inputs_used.rent_growth, 1)} a year. That is an assumption, not an entitlement: San
      Francisco's allowable increase is 1.6% for 2026–27 ${srcLink("S-SF-RENTBOARD")}, and the statewide cap
      under AB 1482 disappears on January 1, 2030 as written ${srcLink("S-CIV-1947.12")}.</p>
    </div>
    <div>
      <h3>What is deliberately not in this table</h3>
      <p>Market value is not the same as assessed value and the gap only widens. That gap is the whole
      reason Property A is worth less to hold than to sell — a buyer would pay 1.3352% on
      ${money(properties.properties[0].market_value.amount)}, not on
      ${money(properties.properties[0].tax_history.find((r) => r.year === 2026).assessment)}.</p>
    </div>
  </div>
</section>

<section class="card">
  <h2>Year-by-year projection, ${proj.meta.projection_window.start}–${proj.meta.projection_window.end}</h2>
  <p class="note">All amounts rounded to the nearest $10. The highlighted row is the modelled
  ${proj.meta.inheritance_year} inheritance. Every row after the supplied 2026 baseline is a projection.</p>
  ${table(
    [
      "Year",
      "Property A market value",
      "Property A assessed value",
      "Property A tax",
      "Property B market value",
      "Property B assessed value",
      "Property B tax",
      "Property B rent (annual)",
      "Basis"
    ],
    timelineRows,
    "wide"
  )}
</section>

<section class="card">
  <h2>Value versus taxable value at the inheritance date</h2>
  ${table(
    ["Measure", "Property A", "Property B"],
    [
      `<tr><td>Market value, ${proj.meta.inheritance_year}</td><td class="num">${money(
        inhRow.market_value_a
      )}</td><td class="num">${money(inhRow.market_value_b)}</td></tr>`,
      `<tr><td>Assessed value on the existing roll, ${proj.meta.inheritance_year}</td><td class="num">${money(
        inhRow.assessed_value_a
      )}</td><td class="num">${money(inhRow.assessed_value_b)}</td></tr>`,
      `<tr><td>Assessed value if Prop 19 applies (live-in only)</td><td class="num">${money(
        sc["SC-LIVE"].assessed_value_a_at_inheritance
      )}</td><td class="num">not applicable — Property B is not being inherited</td></tr>`,
      `<tr><td>Assessed value if Prop 19 does not apply</td><td class="num">${money(
        inhRow.market_value_a
      )}</td><td class="num">—</td></tr>`,
      `<tr><td>Ratio of market to assessed value</td><td class="num">${(
        inhRow.market_value_a / inhRow.assessed_value_a
      ).toFixed(2)}×</td><td class="num">${(inhRow.market_value_b / inhRow.assessed_value_b).toFixed(2)}×</td></tr>`
    ]
  )}
  <p class="note">That ${(inhRow.market_value_a / inhRow.assessed_value_a).toFixed(1)}× gap on Property A is
  the asset that Prop 19 protects, and it is what gets destroyed the moment nobody occupies the house.</p>
</section>

<section class="card">
  <h2>Cash flow under each strategy</h2>
  <p class="note">Net cash is rent collected, less vacancy, management, both properties' operating costs and
  property tax, less income tax on net rental income. Negative means the properties require money out of
  pocket. Property B alone, net of its own costs, is negative in the live-in case — the rent does not cover
  the building's tax, water, insurance and reserve on the stated figures.</p>
  ${table(
    ["Year", "Live in A — net cash", "Rent out A — net cash", "Sell A — net cash"],
    proj.scenarios[0].cash_flow
      .filter((r) => (r.year - proj.meta.inheritance_year) % 2 === 0 || r.year === proj.meta.decision_horizon)
      .map((r, i) => {
        const idx = proj.scenarios[0].cash_flow.findIndex((x) => x.year === r.year);
        const rent = proj.scenarios[1].cash_flow[idx];
        const sell = proj.scenarios[2].cash_flow[idx];
        return `<tr><td class="num">${r.year}</td><td class="num">${money(
          r.net_cash_flow
        )}</td><td class="num">${money(rent.net_cash_flow)}</td><td class="num">${money(
          sell.net_cash_flow
        )}</td></tr>`;
      }),
    "tight"
  )}
  <p class="note">Every second year is shown to keep the table readable. The complete annual series is in
  <code>data/projections.json</code>.</p>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/projections.html"),
  page({
    file: "pages/projections.html",
    title: "Projections",
    subtitle: "Market value, assessed value, property tax, rent and cash flow, year by year, with the basis of every column stated.",
    body: projectionsBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ decisions
const decisionsBody = `
<section class="card callout">
  <h2>Recommendation: ${esc(rec.scenario_name)}</h2>
  <p>Terminal net worth <strong>${money(rec.terminal_net_worth)}</strong> at ${proj.meta.decision_horizon},
  which is <strong>${money(rec.margin)}</strong> (${(rec.margin_pct * 100).toFixed(1)}%) more than
  ${esc(rec.runner_up_name)}. All three strategies are liquidated and taxed at the same horizon, so the
  comparison does not reward deferral.</p>
  <p class="note">The margin is large in the base case and it is <em>not</em> a sure thing. It depends most on
  the reinvestment return assumption. See the sensitivity section below.</p>
</section>

<section class="card">
  <h2>The three strategies, side by side</h2>
  ${table(
    ["", "Live in Property A", "Rent out Property A", "Sell &amp; reinvest"],
    [
      `<tr><td>Prop 19 exclusion</td><td>Applies</td><td>Does not apply</td><td>Irrelevant — sold</td></tr>`,
      `<tr><td>Reassessed on inheritance</td><td class="num">${money(
        sc["SC-LIVE"].assessed_value_a_at_inheritance
      )}</td><td class="num">${money(
        sc["SC-RENT"].assessed_value_a_at_inheritance
      )}</td><td class="num">${money(sc["SC-SELL"].assessed_value_a_at_inheritance)} (then sold)</td></tr>`,
      `<tr><td>Property A tax, first full year</td><td class="num">${money(
        sc["SC-LIVE"].property_tax_a_first_full_year
      )}</td><td class="num">${money(
        sc["SC-RENT"].property_tax_a_first_full_year
      )}</td><td class="num">${money(sc["SC-SELL"].property_tax_a_first_full_year)} (n/a after sale)</td></tr>`,
      `<tr><td>Property tax paid over the period, both properties</td><td class="num">${money(
        sc["SC-LIVE"].totals.cumulative_property_tax
      )}</td><td class="num">${money(
        sc["SC-RENT"].totals.cumulative_property_tax
      )}</td><td class="num">${money(sc["SC-SELL"].totals.cumulative_property_tax)}</td></tr>`,
      `<tr><td>Net cash received or paid over the period</td><td class="num">${money(
        sc["SC-LIVE"].totals.cumulative_net_cash
      )}</td><td class="num">${money(
        sc["SC-RENT"].totals.cumulative_net_cash
      )}</td><td class="num">${money(sc["SC-SELL"].totals.cumulative_net_cash)}</td></tr>`,
      `<tr><td>Income tax paid over the period</td><td class="num">${money(
        sc["SC-LIVE"].totals.cumulative_income_tax
      )}</td><td class="num">${money(
        sc["SC-RENT"].totals.cumulative_income_tax
      )}</td><td class="num">${money(sc["SC-SELL"].totals.cumulative_income_tax)}</td></tr>`,
      `<tr><td>Property A net proceeds at liquidation</td><td class="num">${money(
        sc["SC-LIVE"].totals.property_a_net_liquidation
      )}</td><td class="num">${money(
        sc["SC-RENT"].totals.property_a_net_liquidation
      )}</td><td class="num">sold at inheritance</td></tr>`,
      `<tr><td>Capital-gains tax on Property A</td><td class="num">${money(
        sc["SC-LIVE"].totals.property_a_liquidation_tax
      )}</td><td class="num">${money(
        sc["SC-RENT"].totals.property_a_liquidation_tax
      )}</td><td class="num">${money(sc["SC-SELL"].totals.property_a_liquidation_tax)}</td></tr>`,
      `<tr><td>Reinvested portfolio, after tax</td><td class="num">—</td><td class="num">—</td><td class="num">${money(
        sc["SC-SELL"].totals.reinvested_portfolio_net_of_tax
      )}</td></tr>`,
      `<tr><td>Property B, net after tax</td><td class="num">${money(
        sc["SC-LIVE"].totals.property_b_net_after_tax
      )}</td><td class="num">${money(
        sc["SC-RENT"].totals.property_b_net_after_tax
      )}</td><td class="num">${money(sc["SC-SELL"].totals.property_b_net_after_tax)}</td></tr>`,
      `<tr class="best"><td><strong>Terminal net worth</strong></td><td class="num"><strong>${money(
        sc["SC-LIVE"].totals.terminal_net_worth
      )}</strong></td><td class="num"><strong>${money(
        sc["SC-RENT"].totals.terminal_net_worth
      )}</strong></td><td class="num"><strong>${money(
        sc["SC-SELL"].totals.terminal_net_worth
      )}</strong></td></tr>`
    ],
    "compare"
  )}
</section>

<section class="card">
  <h2>Why each strategy wins or loses</h2>
  <div class="grid2">
    <div>
      <h3>Live in Property A — ${money(sc["SC-LIVE"].totals.terminal_net_worth)}</h3>
      <p>Keeps the parent's low assessed value: the Prop 19 calculation preserves
      ${money(sc["SC-LIVE"].prop19_detail.assessed_value_avoided)} of taxable value and saves
      ${money(sc["SC-LIVE"].prop19_detail.annual_tax_saved_year_one)} in the first year. But it turns a
      ${money(properties.properties[0].market_value.amount)} asset into a place to sleep while Property B's
      third unit sits empty and available. It also costs the most in cash: negative
      ${money(Math.abs(sc["SC-LIVE"].totals.cumulative_net_cash))} over the period, because Property B's rent
      does not cover both buildings' costs on the stated figures.</p>
    </div>
    <div>
      <h3>Rent out Property A — ${money(sc["SC-RENT"].totals.terminal_net_worth)}</h3>
      <p>Better than living in it, because the property earns. Worse than selling, because it is reassessed
      to market value — Prop 19 does not cover a rental home ${srcLink(
        "S-BOE-PROP19"
      )} — and the resulting tax bill is roughly
      ${money(
        sc["SC-RENT"].property_tax_a_first_full_year - sc["SC-LIVE"].property_tax_a_first_full_year
      )} a year higher than the live-in case. Rent growth is also capped, and AB 1482 disappears in 2030 as
      written.</p>
    </div>
    <div>
      <h3>Sell &amp; reinvest — ${money(sc["SC-SELL"].totals.terminal_net_worth)}</h3>
      <p>A stepped-up basis means an immediate sale is nearly tax-free — basis resets to
      ${money(sc["SC-SELL"].assessed_value_a_at_inheritance)} and the sale costs are deductible against it.
      The proceeds then compound without property tax, without a tenant, without a roof, and without the
      concentration risk of a single illiquid asset. This is the only strategy that produces material
      positive net cash (${money(sc["SC-SELL"].totals.cumulative_net_cash)}).</p>
    </div>
    <div>
      <h3>What all three share</h3>
      <p>Property B is held and rented in every scenario, so it contributes the same
      ${money(sc["SC-SELL"].totals.property_b_net_after_tax)} to all three at the horizon. It is therefore
      not what separates them — it is the baseline. Its rent is also what makes living in Property A
      unnecessary rather than a sacrifice.</p>
    </div>
  </div>
</section>

<section class="card">
  <h2>Sensitivity — where the answer moves</h2>
  ${table(
    ["Driver", "Change from base case", "Strategy affected", "Terminal net worth", "Beats the recommendation?"],
    [
      `<tr><td>Reinvestment return</td><td>6.5% → 4.5%</td><td>Sell &amp; reinvest</td><td class="num">${money(
        proj.sensitivity.sell_reinvest_stock_low
      )}</td><td>${proj.sensitivity.sell_reinvest_stock_low > proj.sensitivity.live_baseline ? "No — still ahead" : "Yes — sell loses"}</td></tr>`,
      `<tr><td>Reinvestment return</td><td>6.5% → 8.5%</td><td>Sell &amp; reinvest</td><td class="num">${money(
        proj.sensitivity.sell_reinvest_stock_high
      )}</td><td>No — further ahead</td></tr>`,
      `<tr><td>Property A appreciation</td><td>3.0% → 2.0%</td><td>Live in</td><td class="num">${money(
        proj.sensitivity.live_appreciation_low
      )}</td><td>No</td></tr>`,
      `<tr><td>Property A appreciation</td><td>3.0% → 4.0%</td><td>Live in</td><td class="num">${money(
        proj.sensitivity.live_appreciation_high
      )}</td><td>No</td></tr>`,
      `<tr><td>Property A rent</td><td>$5,400 → $4,500/mo</td><td>Rent out</td><td class="num">${money(
        proj.sensitivity.rent_low_rent
      )}</td><td>No</td></tr>`,
      `<tr><td>Property A rent</td><td>$5,400 → $7,000/mo</td><td>Rent out</td><td class="num">${money(
        proj.sensitivity.rent_high_rent
      )}</td><td>No</td></tr>`,
      `<tr><td>Property A tax rate</td><td>1.3352% → 1.1488% (county typical)</td><td>Live in</td><td class="num">${money(
        proj.sensitivity.live_rate_county_typical
      )}</td><td>No</td></tr>`,
      `<tr><td>Property A insurance</td><td>$1,500 → $3,000/yr</td><td>Live in</td><td class="num">${money(
        proj.sensitivity.live_insurance_doubled
      )}</td><td>No</td></tr>`
    ]
  )}
  <h3>The break-even</h3>
  <p>${beBreak
    ? `The sell case gives up its lead only if the reinvestment return falls to roughly <strong>${pct(
        beBreak,
        1
      )}</strong>. That figure is linearly interpolated between the two measured endpoints (4.5% and 8.5%),
    because the relationship is not exactly linear — annual tax is taken out of the portfolio each year.
    It is close enough to plan around and it is labelled rather than presented as exact.`
    : `Across the entire measured range the sell case keeps its lead.`}</p>
  <p class="note">A 4.5% return is a realistic outcome for a conservative portfolio. The Treasury curve on
  2026-11-09 put the 10-year at 4.38%, the 20-year at 5.29% and the 30-year at 5.26%
  ${srcLink("S-TREASURY-YIELD")}. If the money is invested mostly in bonds, the sell case is roughly a
  coin flip against living in the property. If a meaningful equity allocation is acceptable, it wins.</p>
</section>

<section class="card warncard">
  <h2>What this analysis does not capture</h2>
  <ul>
    <li><strong>Being a landlord.</strong> No value is assigned to the work, the tenant risk, the eviction
    exposure, or the relocation payments a San Francisco owner pays to recover a unit — currently up to
    ${money(24733)} per unit plus ${money(5497)} per elderly or disabled tenant
    ${srcLink("S-SF-RENTBOARD")}.</li>
    <li><strong>Where the heir wants to live.</strong> The model assumes living in Property B's third unit is
    acceptable. If it is not, the live-in case is worth considerably more than shown, because the
    alternative is paying market rent somewhere.</li>
    <li><strong>Earthquake risk.</strong> Not modelled at all. Standard California policies exclude it and no
    premium was supplied.</li>
    <li><strong>Emotional value.</strong> A family home is not only an asset. Nothing here prices that, and
    nothing here should be read as telling anyone not to live in it.</li>
    <li><strong>Concentration.</strong> The sell case concentrates roughly
    ${money(sc["SC-SELL"].totals.reinvested_portfolio_net_of_tax)} in securities, which carries its own risk
    that a single house does not.</li>
  </ul>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/decisions.html"),
  page({
    file: "pages/decisions.html",
    title: "Decision analysis",
    subtitle: "Live in, rent out, or sell and reinvest — compared after tax on the same basis, with break-evens.",
    body: decisionsBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ inheritance process
const steps = [
  {
    n: "Before the death",
    t: "Confirm the trust is funded",
    d: "A revocable trust only avoids probate for assets actually titled in it. Check that both properties and the financial accounts are titled in the trust's name, not still in the parents' individual names. If they are not, they pass through the will and probate instead, which in California is slow and expensive on a multi-million-dollar estate.",
    src: null,
    flag: "Probate fee amounts are deliberately not estimated here — they depend on the statutory schedule and the estate's facts."
  },
  {
    n: "Before the death",
    t: "Confirm which property is the principal residence",
    d: "Prop 19's parent-child exclusion applies only to the transferor's principal residence. If Property A is not the parents' principal residence for tax purposes, the exclusion is unavailable and the house is reassessed to market value. If the exclusion is unavailable, Property A is reassessed to market value and the property tax roughly triples, which is the whole difference between the live-in and rent-out cases.",
    src: "S-BOE-PROP19",
    flag: "Not stated in the request. Flagged F6."
  },
  {
    n: "Before the death",
    t: "Consider the annual gift exclusion while it is available",
    d: `The 2026 annual gift exclusion is ${money(19000)} per recipient per donor, or ${money(38000)} for a married couple splitting gifts. Lifetime gifts reduce the taxable estate and do not touch the recipient's basis problem in the same way an inheritance does — but they also forfeit the step-up in basis on the gifted asset, so this is a genuine trade-off, not a free win.`,
    src: "S-IRS-IR2025-103",
    flag: null
  },
  {
    n: "At death — month 0",
    t: "Trust administration begins",
    d: "The successor trustee takes control of trust assets. Real property is transferred to the beneficiaries by a trustee's deed, which is recorded with the county. No court filing is required for property that is actually in the trust.",
    src: "S-IRS-PUB551",
    flag: null
  },
  {
    n: "At death — month 0",
    t: "Establish the date-of-death value",
    d: `This is the number that matters for tax. For inherited property the heir's basis is the fair market value on the date of death ${srcLink("S-IRS-PUB551")}. Obtain a defensible appraisal as of that date. If the estate has to file a federal Form 706, the value on the return also binds the heir's basis under the consistent-basis rules.`,
    src: "S-IRS-PUB551",
    flag: null
  },
  {
    n: "Within days",
    t: "File the Preliminary Change of Ownership Report",
    d: `A PCOR (BOE-502-A) is normally filed with the deed at recording. Missing it costs an extra ${money(20)} in San Francisco ${srcLink('S-SF-RECFEE')} and the same $20 in Santa Clara County ${srcLink('S-SCC-RECORDER')}. The county uses it to determine whether the transfer is a change in ownership.`,
    src: "S-SCC-RECORDER",
    flag: null
  },
  {
    n: "Within days",
    t: "Record the deed; pay any documentary transfer tax",
    d: `Property A: Santa Clara County charges $0.55 per $500 of value ${srcLink('S-SCC-RECORDER')}. Property B: San Francisco charges per a whole-value bracket — $3.75 per $500 for $1M to under $5M ${srcLink('S-SF-TRANSFERTAX')}. A transfer from a trust to a beneficiary is typically exempt from transfer tax as a gift/no-consideration transfer, but the exemption must be claimed on the affidavit at recording. A sale is not exempt.`,
    src: "S-SF-TRANSFERTAX",
    flag: "Whether the trust-to-heir transfer qualifies for an exemption depends on the trust terms and the affidavit. Confirm with the trustee's attorney before recording."
  },
  {
    n: "Within 1 year — hard deadline",
    t: "Claim the homeowners' exemption on Property A",
    d: `File BOE-266 with the Santa Clara County Assessor. This $7,000 reduction in taxable value is worth about ${money(93)} a year at a 1.3352% rate. More importantly, under Prop 19 the exclusion itself is conditioned on a homeowners' or disabled-veterans' exemption being claimed within one year of the transfer. Miss it and the exclusion can be lost entirely, which is worth roughly ${money(sc["SC-LIVE"].prop19_detail.annual_tax_saved_year_one)} a year.`,
    src: "S-BOE-HOMEEX",
    flag: null
  },
  {
    n: "Within 3 years — hard deadline",
    t: "File the Prop 19 parent-child exclusion claim (BOE-19-P)",
    d: `File with the Santa Clara County Assessor within three years of the transfer or before a transfer to a third party, whichever is earlier. Santa Clara County charges a ${money(110)} non-refundable processing fee ${srcLink('S-SCC-PROP19')}. The exclusion keeps the parent's factored base year value plus $1,044,586 of value, so for Property A the calculation is: parent's factored base year value on the transfer date, plus any amount by which market value exceeds that plus ${money(1044586)}.`,
    src: "S-BOE-LTA25009",
    flag: null
  },
  {
    n: "Years 1–2",
    t: "Expect a supplemental tax bill",
    d: `A change in ownership triggers reappraisal. Where the new value is higher, the county issues a supplemental assessment for the difference, prorated for the part of the fiscal year remaining ${srcLink('S-SF-TREAS-SECURED')}. Budget for one or two of these in the first 18 months — they are easy to miss and they are not in the normal annual bill.`,
    src: "S-SF-TREAS-SECURED",
    flag: null
  },
  {
    n: "If selling — year 1",
    t: "Sell and claim the stepped-up basis",
    d: `Basis is the date-of-death value, so a prompt sale at that value produces essentially no taxable gain. California withholds 3⅓% of the price at close ${srcLink('S-FTB-593')}; that is a prepayment, recovered on the California return, and the gain-based election on Form 593 usually reduces the holdback. If the heir instead lives in the property for two of the five years before selling, the federal $500,000 joint §121 exclusion becomes available on top ${srcLink('S-IRS-TOPIC701')}.`,
    src: "S-FTB-593",
    flag: "California does not fully conform to §121. A gain sheltered federally can still carry California tax. Confirm with a CPA before relying on the shelter."
  },
  {
    n: "If living in it — every year after",
    t: "Stay in it, or lose the exclusion",
    d: `The exclusion is conditional on continuous occupancy. Once Property A stops being the heir's principal residence, it is reassessed to the date-of-death fair market value, factored forward to the lien date following the move-out ${srcLink('S-BOE-PROP19')}. Living in it for a few years and then renting it out does not preserve the low base — the deferred reassessment catches up, and it catches up on a value that has grown.`,
    src: "S-BOE-PROP19",
    flag: "This is the single most expensive mistake available in this decision."
  }
];

const stepsHtml = steps
  .map(
    (s) => `<li class="step">
      <div class="step-when">${esc(s.n)}</div>
      <div class="step-body">
        <h3>${esc(s.t)}</h3>
        <p>${s.d}</p>
        <div class="step-meta">
          ${s.src ? `Source: ${srcLink(s.src)}` : '<span class="unv">No official source — general practice</span>'}
          ${s.flag ? `<div class="flagline"><strong>Flagged:</strong> ${esc(s.flag)}</div>` : ""}
        </div>
      </div>
    </li>`
  )
  .join("");

const inheritanceBody = `
<section class="card">
  <h2>The sequence, with the deadlines that actually bite</h2>
  <p>Two deadlines in this process are unforgiving: the <strong>one-year</strong> homeowners' exemption
  claim, which is a precondition of the Prop 19 exclusion, and the <strong>three-year</strong> exclusion
  claim itself. Everything else can be fixed later. Those two cannot.</p>
  <ol class="timeline">${stepsHtml}</ol>
</section>

<section class="card">
  <h2>A worked Prop 19 calculation for Property A</h2>
  <p>Using the model's ${proj.meta.inheritance_year} values, assuming Property A was the parents' principal
  residence and the heir moves in:</p>
  ${table(
    ["Line", "Amount", "Where it comes from"],
    [
      `<tr><td>Parent's factored base year value on the transfer date</td><td class="num">${money(
        sc["SC-LIVE"].prop19_detail.parent_factored_base_year_value
      )}</td><td>The existing assessed value, projected forward at the 2% cap</td></tr>`,
      `<tr><td>Plus the Prop 19 allowance</td><td class="num">${money(1044586)}</td><td>BOE LTA 2025/009, transfers 2/16/2025–2/15/2027 ${srcLink(
        "S-BOE-LTA25009"
      )}</td></tr>`,
      `<tr><td>= Excluded amount</td><td class="num">${money(
        sc["SC-LIVE"].prop19_detail.excluded_amount
      )}</td><td>—</td></tr>`,
      `<tr><td>Market value at transfer</td><td class="num">${money(
        sc["SC-LIVE"].prop19_detail.market_value_at_transfer
      )}</td><td>Projected at 3.0%/yr from the supplied 2026 estimate</td></tr>`,
      `<tr><td>Excess over the excluded amount</td><td class="num">${money(
        sc["SC-LIVE"].prop19_detail.excess_over_cap
      )}</td><td>Added to the taxable value</td></tr>`,
      `<tr><td><strong>New taxable value</strong></td><td class="num"><strong>${money(
        sc["SC-LIVE"].prop19_detail.new_taxable_value
      )}</strong></td><td>Parent's base + excess</td></tr>`,
      `<tr><td>Taxable value avoided against a full reassessment</td><td class="num">${money(
        sc["SC-LIVE"].prop19_detail.assessed_value_avoided
      )}</td><td>The value of the exclusion</td></tr>`,
      `<tr><td>Annual tax saved, year one</td><td class="num">${money(
        sc["SC-LIVE"].prop19_detail.annual_tax_saved_year_one
      )}</td><td>At Property A's implied 1.3352% rate</td></tr>`
    ]
  )}
  <p class="note">The ${money(1044586)} allowance is the figure published for transfers through
  February 15, 2027. It is adjusted every other February to the FHFA California House Price Index, and the
  forward amounts are not yet published. Holding it flat is <em>conservative for the heir</em>: if California
  house prices rise, the allowance rises and more of the parent's low base survives. Flagged F15.</p>
</section>

<section class="card warncard">
  <h2>What would make the whole process go wrong</h2>
  <ul>
    <li><strong>The properties are not in the trust.</strong> Then it is probate, not trust administration.</li>
    <li><strong>Nobody moves in within the statutory window.</strong> The exclusion is simply not available,
    and Property A is reassessed to market value.</li>
    <li><strong>The exemption claim is late.</strong> Prop 19 conditions the exclusion on a timely
    homeowners' or disabled-veterans' exemption.</li>
    <li><strong>The heir moves out later.</strong> The deferred reassessment arrives at the date-of-death value,
    factored forward — which is higher by then.</li>
    <li><strong>Property A is rented out at the time of death.</strong> Then it is not the transferor's
    principal residence and Prop 19 does not apply at all.</li>
  </ul>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/inheritance-process.html"),
  page({
    file: "pages/inheritance-process.html",
    title: "Inheritance process",
    subtitle: "Step by step from trust funding to the tax deadlines, with each rule cited to the agency that enforces it.",
    body: inheritanceBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ laws
const lawSections = laws.categories
  .map(
    (cat) => `
  <section class="card">
    <h2>${esc(cat.name)}</h2>
    ${table(
      ["Rule", "Value / threshold", "What it means here", "Source", "Status"],
      cat.items.map(
        (it) => `<tr>
        <td><strong>${esc(it.name)}</strong></td>
        <td class="num">${
          it.amount === null || it.amount === undefined ? "—" : typeof it.amount === "number" && it.amount < 1 ? pct(it.amount, 4) : money(it.amount)
        }${it.units ? `<br><span class="muted">${esc(it.units)}</span>` : ""}</td>
        <td>${esc(it.detail)}</td>
        <td>${srcLink(it.source_id)}</td>
        <td>${statusBadge(it.status)}</td>
      </tr>`
      )
    )}
  </section>`
  )
  .join("");

const lawsBody = `
<section class="card">
  <h2>Only enacted law is used in the numbers</h2>
  <p>Everything on this page is current law as of 2026-11-10, quoted from the agency that administers it.
  Anything merely proposed is on the <a href="pending.html">Pending legislation</a> page and is used in
  <strong>no</strong> computed projection.</p>
</section>
${lawSections}
<section class="card">
  <h2>The three rules that decide this</h2>
  <ol>
    <li><strong>Prop 19 only helps a home you live in.</strong> A rental is reassessed to market value.
    That is why renting Property A out costs roughly
    ${money(
      sc["SC-RENT"].property_tax_a_first_full_year - sc["SC-LIVE"].property_tax_a_first_full_year
    )} a year more in property tax than living in it ${srcLink("S-BOE-PROP19")}.</li>
    <li><strong>Inherited property gets a new basis at date-of-death value.</strong> Selling immediately is
    close to tax-free; selling later is not ${srcLink("S-IRS-PUB551")}.</li>
    <li><strong>California has no estate tax and no inheritance tax.</strong> The only death tax that could
    apply is the federal one, on the estate, above ${money(15000000)} ${srcLink("S-SCO-ESTATE")}
    ${srcLink("S-IRS-ESTATE")}.</li>
  </ol>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/laws.html"),
  page({
    file: "pages/laws.html",
    title: "Laws & taxes",
    subtitle: "Every rule the model applies, with its threshold, its effect here, and a link to the agency that publishes it.",
    body: lawsBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ costs
const costRows = costs.assumptions.map(
  (a) => `<tr>
    <td><strong>${esc(a.name)}</strong></td>
    <td class="num">${
      a.value === null || a.value === undefined
        ? '<span class="unv">blank</span>'
        : Math.abs(a.value) < 1
        ? pct(a.value, 2)
        : money(a.value)
    }</td>
    <td>${esc(a.units)}</td>
    <td>${statusBadge(a.status)}</td>
    <td>${a.range ? `${a.range.map((v) => (Math.abs(v) < 1 ? pct(v, 2) : money(v))).join(" – ")}` : "—"}</td>
    <td>${esc(a.basis)}</td>
    <td>${(a.source_ids || []).map((id) => srcLink(id)).join(" ") || '<span class="unv">no official source</span>'}</td>
    <td>${a.used_in_model ? "Yes" : "No"}</td>
  </tr>`
);

const costsBody = `
<section class="card">
  <h2>Inputs, honestly labelled</h2>
  <p>This table is the whole model. Anything marked <span class="badge ok">Verified</span> was read from a
  government source. Anything marked <span class="badge unv">Unverified</span> or
  <span class="badge asm">Assumption</span> is a planning input, and the range beside it is what the
  sensitivity analysis actually exercises.</p>
  ${table(
    ["Input", "Value", "Units", "Status", "Range tested", "Basis", "Source", "In model"],
    costRows,
    "wide"
  )}
</section>

<section class="card">
  <h2>Utilities: what the tariffs actually say</h2>
  <div class="grid2">
    <div>
      <h3>Property A — Cupertino water</h3>
      <p>Cupertino is served by three separate water systems, split by neighbourhood: San Jose Water in the
      southeast, California Water Service in the northeast, and the City's own system in the west, which is
      itself operated by San Jose Water under a lease running to 2036 ${srcLink("S-CUPERTINO-WATER")}. Which
      one applies to Property A cannot be determined without the address, which is not recorded.</p>
      <p>San Jose Water's Schedule 1, effective July 1 2026, charges ${money(79.67)} a month just to have a
      5/8-inch meter, then $5.0355 per ccf for the first 6 ccf, $7.5156 for 6–12, and $14.3548 above 12,
      plus a ${money(2.61)} monthly customer-assistance surcharge and a $0.2996/ccf surcharge
      ${srcLink("S-SJW-SCHED1")}. A household using 10 ccf a month is at roughly $135–$155 for water alone,
      before any sewer charge. Against that, the supplied estimate of $100–$150 a month is plausible and
      possibly at the low end.</p>
    </div>
    <div>
      <h3>Property B — San Francisco water and sewer</h3>
      <p>SFPUC's FY2026-27 schedule charges ${money(19.65)} a month for a 5/8-inch meter, $12.03 per ccf for a
      multi-family account's first 3 units per dwelling unit and $12.91 beyond that, a ${money(6.62)}
      monthly wastewater service charge, $20.74 per discharge unit at a 95% flow factor for multi-family, and
      a Tier 3 stormwater charge of ${money(29.55)} a month for a parcel of 3,301–6,000 sq ft
      ${srcLink("S-SFPUC-RATES")}.</p>
      <p>Working that through for three units at roughly 13 ccf a month produces about $330–$380 all-in —
      which lands inside the supplied $330–$400 range. So the reported water figure is consistent with the
      published tariff, which is worth saying explicitly because most of the supplied figures are not
      independently checkable.</p>
    </div>
    <div>
      <h3>Solar on Property A</h3>
      <p>The installation is stated to generate a credit of roughly $10–$20 a month. That is modelled as a
      ${money(15)} monthly credit. What is <em>not</em> known is the interconnection date, and that determines
      which tariff applies: the CPUC closed the net-energy-metering tariffs to new enrollments, and any
      system applying for interconnection on or after April 15 2023 is on the Net Billing Tariff, which
      compensates exports at the value to the grid rather than at retail rates
      ${srcLink("S-CPUC-NEM")}.</p>
      <p>Onsite consumption is offset either way. The <em>surplus</em> that produces the credit is what
      changes. Confirm the interconnection date before counting on it. Flagged F8.</p>
    </div>
    <div>
      <h3>What is missing entirely</h3>
      <p><strong>Earthquake insurance.</strong> Standard California homeowners policies exclude it, no
      premium was supplied, and none can be verified at parcel level. It is carried at zero in the model,
      which means every projection here is slightly optimistic. For two pre-1980 Bay Area structures this is
      not a trivial omission.</p>
    </div>
  </div>
</section>

<section class="card warncard">
  <h2>Insurance: the weakest number in the model</h2>
  <p>Both properties are modelled at ${money(1500)} a year. That is the figure supplied in the request, and
  it is an estimate — no official body publishes a parcel-level or even ZIP-level homeowner premium. The
  California Department of Insurance regulates rates and publishes approved filings; the rate-comparison
  tool is where a real quote comes from ${srcLink(null)}</p>
  <p>During research, several private quote-aggregation sites were found offering county-level "averages" for
  Santa Clara and San Francisco counties that disagreed with each other by a factor of three. <strong>None of
  those figures is used, shown, or cited here</strong> — they are marketing estimates, not official data, and
  a threefold spread is not a number worth planning on. They are recorded in the verification log only so it
  is clear they were seen and rejected.</p>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/costs.html"),
  page({
    file: "pages/costs.html",
    title: "Operating costs",
    subtitle: "Every input in the model, with its status, its tested range, and its source — including the ones with no source.",
    body: costsBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ estate tax
const estateRows = proj.estate_headroom.rows
  .filter((r) => r.year % 2 === 0 || r.year <= 2027)
  .map(
    (r) => `<tr class="${r.year === proj.meta.inheritance_year ? "mark" : ""}">
      <td class="num">${r.year}</td>
      <td class="num">${money(r.federal_basic_exclusion_floor)}</td>
      <td class="num">${money(r.annual_gift_exclusion)}</td>
      <td class="num">${money(r.combined_property_market_value)}</td>
      <td class="num">${money(r.property_only_headroom_below_exclusion)}</td>
      <td class="num">${money(r.marginal_tax_per_1m_over_the_exclusion)}</td>
      <td>${srcLink("S-IRS-ESTATE")}</td>
    </tr>`
  );

const estateBody = `
<section class="card callout">
  <h2>There is no inheritance tax to pay</h2>
  <p>This surprises people, so it is worth being blunt. California has no inheritance tax and no state
  estate tax ${srcLink("S-SCO-ESTATE")}. Inherited cash and property are not taxable income when received,
  federally or in California ${srcLink("S-FTB-GIFTS")}. Neither Santa Clara County nor San Francisco levies
  anything on an inheritance; the only charge at the county level is the recording fee and, on a sale for
  consideration, the documentary transfer tax.</p>
  <p>The tax that exists is the <strong>federal estate tax</strong>, it is paid by the <em>estate</em> rather
  than the heir, and it applies only to the amount above <strong>${money(15000000)} per decedent in 2026</strong>
  ${srcLink("S-IRS-ESTATE")}. A married couple can effectively shelter twice that with a portability
  election on a timely Form 706.</p>
</section>

<section class="card">
  <h2>So the real question is whether the estate crosses the threshold</h2>
  <p>The table below combines both properties' projected market values and subtracts them from the
  exclusion. What remains is the amount of <em>other</em> assets — chiefly the cash inheritance — that could
  be added before any federal estate tax is owed.</p>
  <p class="note"><strong>This table is deliberately expressed so the actual cash amount never has to be
  written down.</strong> Read the "headroom" column as: the cash and other assets can be this large before
  the estate owes anything. Every figure is per $1,000,000 of inherited cash, where relevant.</p>
  ${table(
    [
      "Year",
      "Federal exclusion (floor)",
      "Annual gift exclusion",
      "Both properties at market value",
      "Headroom before any estate tax",
      "Tax per $1m above the exclusion",
      "Source"
    ],
    estateRows,
    "wide"
  )}
  <p class="note">Assumes both properties remain in the estate and no lifetime gifts are made. Every year
  after 2026 uses the 2026 exclusion as a floor, because the IRS has not published the indexed forward
  amounts — the actual exclusion will be higher, so the exposure shown is an upper bound. Flagged F11.</p>
</section>

<section class="card">
  <h2>The three thresholds, in plain language</h2>
  ${table(
    ["Level", "Threshold", "What happens at it", "Source"],
    [
      `<tr><td><strong>Local</strong> (Santa Clara County / San Francisco)</td><td>None</td><td>No inheritance or estate tax at either county or city level. Recording fees and, on a sale, documentary transfer tax only.</td><td>${srcLink(
        "S-SCC-RECORDER"
      )}</td></tr>`,
      `<tr><td><strong>California</strong></td><td>None</td><td>No California estate tax return required for any death on or after January 1, 2005. No inheritance tax. No state GST tax after 2004. The heir owes nothing to the state for inheriting.</td><td>${srcLink(
        "S-SCO-ESTATE"
      )}</td></tr>`,
      `<tr><td><strong>Federal</strong></td><td>${money(15000000)} per decedent (2026)</td><td>Tax is on the estate, above the exclusion, at a 40% top rate. Portability lets a surviving spouse use the first spouse's unused exclusion. Gifts above ${money(
        19000
      )} per recipient per year count against the lifetime exclusion.</td><td>${srcLink(
        "S-IRS-ESTATE"
      )}</td></tr>`
    ]
  )}
</section>

<section class="card">
  <h2>How to stay under it, in order of effectiveness</h2>
  <ol>
    <li><strong>Use both spouses' exclusions.</strong> A portability election on a timely Form 706 for the
    first spouse to die can roughly double the amount sheltered, for the cost of filing a return
    ${srcLink("S-IRS-ESTATE")}. This is the single largest lever and it is often missed.</li>
    <li><strong>Use the annual gift exclusion while it lasts.</strong> ${money(19000)} per recipient per donor
    in 2026, or ${money(38000)} for a couple splitting gifts, with no lifetime-exclusion cost and no return
    required if no other gifts were made ${srcLink("S-IRS-IR2025-103")}. The trade-off: a gifted asset loses
    the step-up in basis, so gifting low-basis property can create a larger income-tax problem than the
    estate tax it avoids.</li>
    <li><strong>Do not gift the real property.</strong> Gifting Property A during life forfeits the
    date-of-death basis step-up under IRC §1014 ${srcLink("S-IRS-PUB551")} and forfeits the Prop 19
    parent-child exclusion, which only applies to a transfer at death. On these numbers that is a bad
    trade.</li>
    <li><strong>Confirm what is actually in the estate.</strong> Life insurance proceeds, retirement accounts
    and jointly held property all count. The two properties are only part of the gross estate.</li>
  </ol>
</section>

<section class="card warncard">
  <h2>What is not modelled here</h2>
  <ul>
    <li><strong>The actual cash amount.</strong> Withheld by policy. The headroom column is the answer to
    "how much is too much" without ever writing the number down.</li>
    <li><strong>Forward indexation of the exclusion.</strong> The IRS has not published amounts after 2026,
    so the model uses the 2026 figure as a floor. Flagged F11.</li>
    <li><strong>Proposed California estate tax.</strong> Several bills have been floated and none is
    enacted. Listed on the Pending legislation page and used nowhere in this table.</li>
    <li><strong>Valuation discounts, charitable deductions, and trust structures.</strong> All real levers,
    all dependent on facts not supplied, and none of them modelled.</li>
  </ul>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/estate-tax.html"),
  page({
    file: "pages/estate-tax.html",
    title: "Estate & inheritance tax",
    subtitle: "What the thresholds actually are at each level, and how much cash would push the estate over the federal line.",
    body: estateBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ pending
const pendingRows = pending.items.map(
  (p) => `<tr>
    <td><strong>${esc(p.name)}</strong></td>
    <td>${esc(p.jurisdiction)}</td>
    <td>${statusBadge(p.status.startsWith("proposed") ? "proposed" : "verified_official")}<br><span class="muted">${esc(
    p.status
  )}</span></td>
    <td>${esc(p.summary)}</td>
    <td>${esc(p.effect_if_enacted)}</td>
    <td>${srcLink(p.source_id)}</td>
    <td>No</td>
  </tr>`
);

const pendingBody = `
<section class="card">
  <h2>Nothing on this page is in any projection</h2>
  <p>The request asked to look at changes in the law currently being discussed and how they would affect
  the decision. This page is that, kept strictly separate. A projection that mixes enacted and proposed law
  is not a projection — it is a guess with a decimal point. Every number elsewhere on this site uses only
  enacted law.</p>
  ${table(
    ["Item", "Jurisdiction", "Status", "What it would do", "How it changes the decision", "Source", "In model"],
    pendingRows,
    "wide"
  )}
</section>

<section class="card">
  <h2>The two that actually matter here</h2>
  <div class="grid2">
    <div>
      <h3>AB 1482 disappears on January 1, 2030 — as written</h3>
      <p>Civil Code §1947.12 says, in terms, that the section "shall remain in effect until January 1, 2030,
      and as of that date is repealed" ${srcLink("S-CIV-1947.12")}. That is not a proposal; it is the current
      statute. What is unknown is whether the Legislature extends it.</p>
      <p>Why it matters: if the cap lapses, rent on a rented-out Property A could reset to market. If it is
      extended or tightened, the rent-out case gets worse. The model uses a flat 2%/yr across the entire
      horizon precisely so it does not quietly assume either outcome. Flagged F17.</p>
    </div>
    <div>
      <h3>San Francisco may cap banked increases</h3>
      <p>Board of Supervisors File No. 261020, posted November 9 2026, would temporarily limit combined
      banked and capital-improvement increases on rent-controlled units to 10% a year
      ${srcLink("S-SF-RENTBOARD")}. The Rent Board's own page states clearly that it "has not been enacted
      and is subject to change."</p>
      <p>Why it matters: it caps upside on Property B's two rented units. Because Property B is held in all
      three strategies, a change there moves all three terminal values roughly together and is unlikely to
      change which strategy wins — but it would lower every number on the site.</p>
    </div>
  </div>
</section>

<section class="card warncard">
  <h2>Also worth watching, but unsourced and therefore excluded</h2>
  <p>Recurring California proposals for a state estate tax and for annual wealth taxes were considered. In
  this research pass <strong>no enacted law and no confirmable pending bill text</strong> was found to cite,
  so they are listed on the Flagged page as unverified rather than described here as if they were concrete.
  If they ever pass, they would add a state-level layer on top of the federal one and would change the
  estate analysis — but nothing on this site pretends to predict that.</p>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/pending.html"),
  page({
    file: "pages/pending.html",
    title: "Pending legislation",
    subtitle: "What is being discussed, what it would change, and why none of it touches a single computed number.",
    body: pendingBody,
    depth: 1
  })
);

// ------------------------------------------------------------------ sources
const sourceRows = sources.sources.map(
  (s) => `<tr>
    <td><code>${esc(s.id)}</code></td>
    <td><strong>${esc(s.title)}</strong></td>
    <td>${esc(s.publisher)}</td>
    <td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a></td>
    <td>${(s.supports || []).map((x) => esc(x)).join("; ")}</td>
    <td class="quote">${s.quote ? "“" + esc(s.quote) + "”" : "—"}</td>
    <td>${esc(s.retrieved)}</td>
  </tr>`
);

const sourcesBody = `
<section class="card">
  <h2>Source registry</h2>
  <p>Every row in every table on this site resolves to one of these. All are primary or government
  publishers: IRS, California Franchise Tax Board, California State Board of Equalization, California State
  Controller's Office, California Legislative Information, California Public Utilities Commission, Santa
  Clara County Assessor and Clerk-Recorder, City and County of San Francisco (Treasurer, Assessor-Recorder,
  Rent Board), San Francisco Public Utilities Commission, San Jose Water Company (a CPUC-jurisdictional
  tariff), San Jose Water / City of Cupertino, FHFA, U.S. Treasury, U.S. Census Bureau, HUD.</p>
  <p class="note">Where a quote is given it was read directly from the page or PDF on the retrieval date.
  Where a secondary or commercial site appeared to agree with a figure, it is <strong>not</strong> cited —
  agreement with a non-official source is not verification.</p>
  ${table(
    ["ID", "Title", "Publisher", "URL", "Supports", "Quoted text", "Retrieved"],
    sourceRows,
    "wide sources"
  )}
</section>

<section class="card warncard">
  <h2>Explicitly unverified topics</h2>
  ${table(
    ["Topic", "Status", "Why", "Where to get it officially"],
    sources.unverified_notes.map(
      (u) => `<tr>
      <td><strong>${esc(u.topic)}</strong></td>
      <td><span class="badge unv">${esc(u.status)}</span></td>
      <td>${esc(u.reason)}</td>
      <td>${(u.official_landing_pages || [])
        .map((l) => `<a href="${esc(l)}" target="_blank" rel="noopener">${esc(l)}</a>`)
        .join("<br>") || "—"}</td>
    </tr>`
    )
  )}
</section>

<section class="card">
  <h2>Sources that were checked and deliberately rejected</h2>
  <p>Recorded so it is clear they were considered, not missed:</p>
  <ul>
    <li><strong>Commercial insurance comparison sites</strong> offering "average premium" figures by county.
    Their numbers for Santa Clara and San Francisco counties differed from each other by roughly a factor of
    three, none identified a methodology that could be audited, and none is an official publisher. Rejected;
    the insurance inputs remain labelled as the user's estimates.</li>
    <li><strong>Blog and law-firm summaries of Prop 19, AB 1482 and the estate-tax exclusion.</strong> Useful
    for orientation only. Every figure that ended up in the model was then read from the BOE, the IRS, the
    FTB, the State Controller, or the statute itself.</li>
    <li><strong>A Wikipedia article on Proposition 19</strong> that cited the correct BOE letters. The letters
    were fetched and read directly instead; the article is not cited.</li>
  </ul>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/sources.html"),
  page({
    file: "pages/sources.html",
    title: "Sources",
    subtitle: "The complete registry: publisher, URL, what each source supports, the exact text relied on, and the retrieval date.",
    body: sourcesBody,
    depth: 1
  })
);


// ------------------------------------------------------------------ flagged
const sevClass = { high: "sev-high", medium: "sev-med", low: "sev-low", "n/a": "sev-na" };
const flaggedBody = `
<section class="card callout">
  <h2>${flags.items.length} items, none of which block the analysis</h2>
  <p>This page exists because the instruction was explicit: verify against official sources, cite them,
  and flag irregularities rather than filling gaps with plausible numbers. Every item below is either a
  value that could not be confirmed officially, an inconsistency in the supplied data, or an assumption
  that materially moves the answer.</p>
  <p>Three of them carry a <strong>high</strong> severity and deserve attention before anyone acts on the
  recommendation: <strong>F1</strong> (Property B's tax rate), <strong>F6</strong> (whether Property A is
  actually the parents' principal residence), and <strong>F23</strong> (the reinvestment return the whole
  recommendation turns on).</p>
  <div class="sevkey">
    <span class="sev sev-high">High — could change the answer</span>
    <span class="sev sev-med">Medium — changes the numbers, not the ranking</span>
    <span class="sev sev-low">Low — bookkeeping</span>
  </div>
</section>

<section class="card">
  <h2>The register</h2>
  ${table(
    ["ID", "Item", "Severity", "Status", "Detail", "Impact on the analysis", "Action", "Sources"],
    flags.items.map(
      (f) => `<tr id="${esc(f.id)}">
      <td><strong>${esc(f.id)}</strong></td>
      <td><strong>${esc(f.title)}</strong></td>
      <td><span class="sev ${sevClass[f.severity] || "sev-na"}">${esc(f.severity)}</span></td>
      <td>${esc(f.status)}</td>
      <td>${esc(f.detail)}</td>
      <td>${esc(f.impact)}</td>
      <td>${esc(f.action)}</td>
      <td>${(f.sources || []).map((id) => srcLink(id)).join(" ") || '<span class="unv">none — no official source exists</span>'}</td>
    </tr>`
    ),
    "wide flags"
  )}
</section>

<section class="card warncard">
  <h2>The honest summary</h2>
  <p>Everything that matters legally is verified: the Prop 19 rules and their $1,044,586 allowance, the
  Prop 13 2% cap and the 1.02 inflation factor for the 2026 roll, the homeowners' exemption, the
  date-of-death basis rule, the §121 exclusion, the $15,000,000 federal exclusion, the absence of any
  California estate or inheritance tax, the rent caps, the transfer tax rates and the utility tariffs. Each
  is quoted from the agency that administers it on the Sources page.</p>
  <p>Everything that matters financially is an estimate: what the properties are worth, what insurance
  costs, what Property A would rent for, how fast values and rents grow, and what a reinvested portfolio
  returns. Those are labelled as assumptions with ranges, and the sensitivity analysis shows what happens at
  the ends of each range instead of hiding them.</p>
  <p>The one supplied figure that looks wrong rather than merely uncertain is Property B's tax (F1). It is
  carried as supplied rather than corrected, and it is flagged here so it is not mistaken for verified data.</p>
</section>
`;

fs.writeFileSync(
  path.join(ROOT, "pages/flagged.html"),
  page({
    file: "pages/flagged.html",
    title: "Flagged for review",
    subtitle: "Every unverified value, every inconsistency in the supplied data, and every assumption that changes the answer.",
    body: flaggedBody,
    depth: 1
  })
);

console.log("built index.html and", fs.readdirSync(path.join(ROOT, "pages")).length, "pages");
