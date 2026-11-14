"""Supplemental interactive tools: phased investing, attorney brief, glossary.

The investment stress tool is illustrative, pretax and assumption-driven. Its
scenario magnitudes are not presented as historical 1929/2008 return data.
"""
from html import escape as E
from content_part1 import callout, refs, table, Pj, As, Ms
from evidence import SOURCES
from case_model import rounded


def _monthly_price(month, equity_annual, crash_month, drawdown, recovery_months):
    trend = (1 + equity_annual) ** (month / 12)
    if month < crash_month:
        shock = 1.0
    elif recovery_months <= 0 or month >= crash_month + recovery_months:
        shock = 1.0 if recovery_months <= 0 else 1.0
    else:
        shock = 1 - drawdown + drawdown * (month - crash_month) / recovery_months
    return trend * shock


def compare_paths(principal=1_000_000, phase_months=30, treasury_net=0.03,
                  equity_return=0.06, drawdown=0.50, crash_month=0,
                  recovery_months=60, horizon_months=120):
    """Return nominal pretax terminal values and peak-to-trough losses.

    A generic starting amount is used, not a household sale-proceeds estimate.
    The Treasury yield is a net-of-tax assumption supplied by the user; equity
    returns and loss/recovery paths are gross synthetic inputs. No tax result is
    implied. Money is rounded to $10 only for display.
    """
    months = max(1, min(phase_months, horizon_months))
    crash_month = max(0, min(crash_month, horizon_months))
    recovery_months = max(1, recovery_months)
    principal = max(0.0, principal)
    stock_shares = principal  # immediate path buys at normalized price 1 at t=0
    reserve = principal
    phased_shares = 0.0
    immediate_values = [principal]
    phased_values = [principal]
    for month in range(1, horizon_months + 1):
        price = _monthly_price(month, equity_return, crash_month, drawdown, recovery_months)
        if month <= months:
            reserve *= (1 + treasury_net) ** (1 / 12)
            installment = principal / months
            purchase = min(installment, reserve)
            phased_shares += purchase / max(price, 1e-9)
            reserve -= purchase
            if month == months and reserve > 0:
                phased_shares += reserve / max(price, 1e-9)
                reserve = 0
        immediate_values.append(stock_shares * price)
        phased_values.append(phased_shares * price + reserve)
    def drawdown_pct(values):
        peak = values[0]
        worst = 0.0
        for value in values:
            peak = max(peak, value)
            if peak:
                worst = min(worst, value / peak - 1)
        return worst * 100
    return {
        'immediate_terminal': immediate_values[-1],
        'phased_terminal': phased_values[-1],
        'immediate_drawdown': drawdown_pct(immediate_values),
        'phased_drawdown': drawdown_pct(phased_values),
        'immediate_series': immediate_values,
        'phased_series': phased_values,
    }


def page_phased():
    early = compare_paths(crash_month=0)
    late = compare_paths(crash_month=36)
    src = refs('bills', 'treasnotes', 'stocks', 'cbo')
    html = '''<section class="decision-change"><strong>What would change the answer?</strong>
<ul><li>The trust instrument or estate plan does not permit occupancy or requires a sale.</li>
<li>Proposition 19 eligibility, the transfer-date tax base, or the whole-estate tax picture differs from the planning assumptions.</li>
<li>Written rent, insurance, repair, debt and utility evidence makes net rental cash flow materially better than the current illustrative case.</li>
<li>The inheritor cannot or does not want to live in the inherited home; that makes sell-and-reinvest the fallback to test.</li></ul></section>
<p class="lead">A mixed path: after a hypothetical sale, temporarily ladder proceeds across short U.S. Treasury maturities, then move them into a diversified stock allocation over 24–36 months. Compare that with investing the lump sum immediately.</p>''' + callout(
        'The trade-off beside the headline',
        'Phasing can reduce the amount exposed to a sudden equity fall during the entry window, but it does not remove risk. It can lag a rising market, delays equity exposure, and exposes cash to reinvestment risk as each short Treasury matures. Treasury interest is federally taxable and generally exempt from state and local income tax. This tool is pretax for equities and uses a user-entered net Treasury yield; it is not a tax forecast.',
        'warning') + '''<div class="whatif" id="phase-tool">
<h2>What-if controls</h2><p>Illustration only: the default amount is a generic $1,000,000, not a sale-proceeds estimate. Controls run locally in this browser and are not saved or sent anywhere. Dollar outputs are nominal and pretax.</p>
<div class="control-grid">
<label>Crash lens<select id="phase-stress-preset"><option value="deep" selected>Depression-era-inspired deep/slow stress</option><option value="sharp">2008-crisis-inspired sharp stress</option><option value="custom">Custom assumptions below</option></select></label>
<label>Starting proceeds (illustrative)<input id="phase-principal" type="number" min="0" step="10000" value="1000000"></label>
<label>Phasing period<select id="phase-months"><option value="24">24 months</option><option value="30" selected>30 months</option><option value="36">36 months</option></select></label>
<label>Net annual Treasury yield assumption<input id="phase-treasury" type="number" min="0" max="10" step="0.25" value="3"></label>
<label>Annual equity return assumption<input id="phase-equity" type="number" min="-50" max="50" step="0.5" value="6"></label>
<label>Equity drawdown stress<input id="phase-drawdown" type="number" min="0" max="90" step="1" value="50"></label>
<label>Crash starts (months after investment begins)<input id="phase-crash-month" type="number" min="0" max="120" step="1" value="0"></label>
<label>Recovery duration assumption (months)<input id="phase-recovery" type="number" min="1" max="120" step="1" value="60"></label>
<label>Comparison horizon<select id="phase-horizon"><option value="120" selected>10 years</option><option value="240">20 years</option><option value="360">30 years</option></select></label>
</div>
<p class="toolbar"><button type="button" id="phase-reset">Reset illustrative defaults</button><span id="phase-status" aria-live="polite">Initial values shown below.</span></p>
<div class="table-scroll"><table id="phase-results"><caption class="sr-only">Immediate and phased investing comparison</caption><thead><tr><th>Strategy</th><th>Terminal value</th><th>Maximum modeled drawdown</th><th>Interpretation</th><th>Status and official source</th></tr></thead><tbody>
<tr data-path="immediate"><td>Invest the full amount immediately</td><td id="phase-immediate-value">$0</td><td id="phase-immediate-dd">0%</td><td>Full equity exposure from the start; highest early crash exposure in this stress setup.</td><td><span class="badge assumption">Synthetic Assumption</span> ''' + src + '''</td></tr>
<tr data-path="phased"><td>Hold short Treasuries, then phase monthly</td><td id="phase-phased-value">$0</td><td id="phase-phased-dd">0%</td><td>Lower initial stock exposure; the parked portion earns the net yield assumption while awaiting its scheduled purchase.</td><td><span class="badge assumption">Synthetic Assumption</span> ''' + src + '''</td></tr>
</tbody></table></div>
<p class="table-note">The model is a transparent illustration, not a historical replay. The two preset lenses are deliberately synthetic and inspired by, but do not reconstruct, the 1929–1930s or 2008–09 market episodes. Their drawdown/recovery values are editable assumptions, not historical returns. No verified full-period total-return stock series is used here. Treasury yields at a future inheritance date are unknown; today's short rates cannot be locked for decades. Principal protection assumes eligible Treasury securities are held to maturity; selling before maturity can produce a gain or loss.</p></div>''' + table(
        'Same assumptions, different crash timing',
        ['Crash timing', 'Strategy', 'Terminal value', 'Maximum modeled drawdown'], [
            (['At start of phasing', 'Immediate lump sum', f'${rounded(early["immediate_terminal"]):,}', f'{early["immediate_drawdown"]:.1f}%'], As, 'bills treasnotes stocks'),
            (['At start of phasing', '30-month phased entry', f'${rounded(early["phased_terminal"]):,}', f'{early["phased_drawdown"]:.1f}%'], As, 'bills treasnotes stocks'),
            (['36 months after investment begins (after phasing)', 'Immediate lump sum', f'${rounded(late["immediate_terminal"]):,}', f'{late["immediate_drawdown"]:.1f}%'], As, 'bills treasnotes stocks'),
            (['36 months after investment begins (after phasing)', '30-month phased entry', f'${rounded(late["phased_terminal"]):,}', f'{late["phased_drawdown"]:.1f}%'], As, 'bills treasnotes stocks'),
        ], note='Synthetic planning example only. Default assumptions: $1,000,000 starting value; 30-month phasing; 3% net Treasury yield; 6% annual equity return; 50% drawdown; 60-month recovery; 10-year horizon. The shock multiplier recovers linearly to its growth trend. No probability or actual historical return is implied. Values are generic, pretax and rounded to $10 for display.') + callout(
        'Decision use',
        'Ask the adviser to run the same comparison with the actual net proceeds, an approved asset allocation, a Treasury ladder and tax estimates. Compare several crash start dates, including a crash after the staging period. Do not treat “phased” as a guaranteed safer or higher-return strategy.',
        'info')
    html = html.replace('id="phase-immediate-value">$0', f'id="phase-immediate-value">${rounded(early["immediate_terminal"]):,}')
    html = html.replace('id="phase-phased-value">$0', f'id="phase-phased-value">${rounded(early["phased_terminal"]):,}')
    html = html.replace('id="phase-immediate-dd">0%', f'id="phase-immediate-dd">{early["immediate_drawdown"]:.1f}%')
    html = html.replace('id="phase-phased-dd">0%', f'id="phase-phased-dd">{early["phased_drawdown"]:.1f}%')
    return html


def page_attorney_brief():
    return '''<article class="attorney-brief" id="attorney-brief">
<div class="brief-top"><span class="eyebrow">CONFIDENTIAL WORKING CHECKLIST · PREPARED WITHOUT IDENTIFIERS</span><span>Print / Save as PDF</span></div>
<h1>Attorney &amp; CPA Briefing Sheet</h1>
<p class="brief-sub">Purpose: prepare a decision after an expected trust inheritance. Property A is the future inherited home; Property B is already owned by the inheritor and has existing rental activity. Do not treat A and B as one tax or cash-flow event.</p>
<div class="brief-alert"><b>No final recommendation is supportable yet.</b> The leading paths to test are (1) occupy A if the trust permits and Proposition 19 requirements are met, (2) sell A and reinvest after tax, including 24–36 months of Treasury parking/phased equity entry, or (3) rent A only if verified net rental cash flow beats the alternatives. Keep B as a separate baseline.</div>
<div class="brief-columns"><section><h2>Questions for counsel</h2><ol>
<li>Who is trustee; what powers, distribution terms, debts, title, co-beneficiaries or sale requirements apply?</li>
<li>What is the date-of-death value, basis, trust tax classification and distribution date?</li>
<li>Is the transferee eligible for the family-home exclusion, what occupancy and claim deadlines apply, and what happens if the home is later rented or vacated?</li>
<li>What recorded liens, leases, permits, unit legality, local rent controls, transfer taxes and required notices affect either property?</li>
<li>Which deadlines apply to notice, title, tax returns, change-in-ownership statements and exclusion claims?</li>
</ol></section><section><h2>Questions for the CPA</h2><ol>
<li>Estimate the complete gross estate, prior taxable gifts, marital deductions, portability and federal estate-tax exposure in the year of death; do not compare one house alone to the exclusion.</li>
<li>Confirm federal and California basis, depreciation, capital-gain, NIIT, rental-income and property-tax treatment for each path.</li>
<li>Compare occupancy, rent, immediate sale, and phased reinvestment after taxes with sensitivity ranges—not one point forecast.</li>
<li>For investing, model 3-month to 2-year Treasury reinvestment risk, tax on interest, stock drawdowns, staged-entry dates, liquidity and target allocation.</li>
</ol></section></div>
<div class="brief-bottom"><section><h2>Documents / facts still needed</h2><p>Trust and amendments; deed and title report; current tax bills and assessments; date-of-death appraisal; mortgage / lien payoff; insurance declarations and three quotes; utility and repair records; lease and rent roll; rental permits and notices; solar interconnection / tariff; full estate inventory and gift history; intended residence and liquidity plan.</p></section>
<section><h2>Current estate-tax benchmark &amp; statutory clocks</h2><p>Federal exclusion: $15,480,000 for 2027; California has no separate estate tax under current law. The 2040s amount and any law change are unknown. Verify trustee notice (60 days), change-in-ownership statement (150 days), Form 706 (generally 9 months), homeowners’ exemption and Prop 19 deadlines at transfer. ''' + refs(*'irs2027 rtc13301 prob16061 rtc480 form706 pub801'.split()) + '''</p></section></div>
<p class="brief-sources"><b>Primary-source starting points:</b> ''' + refs(*'prob16061 rtc480 form706 estate irs2027 pub19 pub801 lta26026 basis rental rtc11911 ab1482 sfrates treasnotes bills stocks'.split()) + '''</p>
<p class="brief-foot">For attorney and tax-adviser review only. Not legal, tax, insurance, appraisal or investment advice. All personal names, addresses, ZIP codes, account details and parcel identifiers are intentionally omitted. Verify every deadline and law at the date of transfer.</p>
</article>'''


def page_glossary():
    rows = [
        (['Basis at death', 'The tax basis generally resets to fair market value at death under current federal law; confirm trust-specific facts and future law.', 'Verified rule; facts missing'], 'basis'),
        (['Change in ownership', 'A transfer that can trigger reassessment under California property-tax rules; trust transfers have specific exceptions and forms.', 'Verified rule; apply to deed'], 'rtc480 pub29'),
        (['Proposition 13', 'Limits assessed-value growth under a formula; it does not cap the total property-tax bill at 2%.', 'Verified rule'], 'pub29 lta26002'),
        (['Proposition 19 family-home exclusion', 'A qualifying intergenerational transfer may preserve some assessed value if occupancy, relationship, value limit and filing rules are met.', 'Verified rule; eligibility missing'], 'pub19 pub801 lta26026'),
        (['Gross estate / exclusion', 'The federal estate tax is measured on the taxable estate, not on the value one heir receives. The exclusion is year-specific and may change.', 'Verified current rule; future unknown'], 'estate irs2027 form706'),
        (['Treasury bill / note ladder', 'A short-maturity sequence intended to spread maturity and reinvestment dates. Bills mature in up to one year; a two-year Treasury note sits at the edge of the proposed 3-month–2-year range.', 'Guidance; future yield unknown'], 'bills treasnotes'),
        (['Reinvestment risk', 'The risk that matured principal must be reinvested at a lower yield than the current one; a short ladder does not lock a long-term return.', 'Guidance'], 'bills treasnotes cbo'),
        (['Drawdown', 'A decline from a prior portfolio peak; a stress result depends on the assumed path and does not estimate its probability.', 'Definition used in synthetic tool'], 'stocks'),
        (['Phased entry', 'Moving a planned amount into stocks at scheduled dates rather than investing all at once. It may reduce the effect of an early crash, but can lag a rising market.', 'Strategy description, not a guarantee'], 'stocks'),
        (['Net operating income', 'Rental receipts less operating expenses before financing and income tax; gross rent is not profit.', 'Guidance'], 'rental'),
        (['Depreciation recapture', 'Tax treatment of prior depreciation deductions when rental property is sold; amount depends on actual records and tax law.', 'Verified rule; facts missing'], 'rental capgains'),
        (['NOI / net proceeds', 'Net proceeds are sale cash after debt, transaction costs and applicable taxes; those values are unknown until documents and quotes are reviewed.', 'Case-specific amount missing'], 'rtc11911 basis'),
    ]
    return callout('How to use this glossary', 'Definitions are decision aids, not determinations for a particular trust, property or taxpayer. Every rule must be checked again at the transfer date.', 'info') + table(
        'Terms used throughout the brief', ['Term', 'Plain-English meaning', 'Scope'],
        [([term, definition, scope], 'Guidance', source_ids) for (term, definition, scope), source_ids in rows])
