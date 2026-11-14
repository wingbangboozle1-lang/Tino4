"""Privacy-first public site builder. Never consumes household inputs or case projections."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    "index.html": ("Decision workspace", "A private planning framework for an anticipated inheritance and a separately owned rental property. No household-specific values, locations, histories, or projections are published here.", [
        ("Start with the decision gates", "Confirm the trust terms, transfer date, beneficiaries, tax basis, occupancy intent, debts, leases, and insurance before comparing live, rent, or sell paths."),
        ("Keep the properties separate", "Distinguish the anticipated inheritance from the separately owned property. Verify title, tax assessment, rental status, and applicable rules for each property independently."),
        ("Test mixed paths", "Compare occupancy, partial rental where lawful, sale, and a staged investment plan. Model cash reserves and reinvestment risk alongside returns."),
        ("Do not treat a forecast as a fact", "A transfer expected decades from now depends on future law, markets, costs, trust language, and the property's condition. Refresh all inputs with qualified advisers near the event."),
    ]),
    "pages/attorney-cpa-brief.html": ("Attorney & CPA briefing sheet", "Printable checklist for adviser meetings. No personal or property-specific data is included.", [
        ("Trust and title", "Obtain the executed trust and amendments, deed, trustee authority, beneficiary terms, debt and liens, and distribution or sale requirements."),
        ("Tax", "Determine date-of-death valuation and basis records; federal estate-tax filing and payment deadlines; California property-tax change-in-ownership reporting; and eligibility and deadlines for any applicable parent-child property-tax exclusion."),
        ("Operations", "Confirm legal unit status, leases, deposits, rent-control coverage, insurance availability, rebuilding limits, utilities, maintenance history, and solar/export-credit agreements."),
        ("Decision model", "Request side-by-side after-tax cash flows for occupy, rent, sell, mixed use, and phased investing, including fees, vacancy, capital repairs, inflation, and adverse market entry scenarios."),
    ]),
    "pages/phased-investing.html": ("Phased investing & reinvestment risk", "A general scenario framework for comparing immediate investment with a 24–36 month Treasury staging period; no return is guaranteed.", [
        ("Sequence-risk question", "If sale proceeds are invested shortly before a major equity decline, an investor may experience a large early loss. A Treasury holding period changes exposure during that interval but creates reinvestment risk if yields fall before reinvestment."),
        ("Compare the pathways", "Model immediate diversified investment; staged short-duration Treasury holdings followed by scheduled equity purchases over 24–36 months; and a blended allocation with a retained liquidity reserve."),
        ("Stress-test", "Use multiple historical crash-entry dates and inflation regimes, including the Great Depression and global financial crisis, as historical illustrations rather than forecasts. Compare ending wealth, drawdown, purchasing power, income, and liquidity."),
        ("Required inputs", "At decision time obtain the actual distributable amount, taxes and costs, current Treasury yields, tax status, portfolio allocation, risk tolerance, liquidity needs, and adviser-approved investment policy."),
    ]),
    "pages/glossary.html": ("Glossary", "Plain-language definitions for the decision framework.", [
        ("Assessment / tax basis", "Assessment is the value used by a property-tax authority to calculate property tax. Income-tax basis is a separate concept used to determine taxable gain; confirm the applicable basis with a tax professional."),
        ("Reinvestment risk", "The risk that proceeds from a maturing investment must be reinvested at a lower yield."),
        ("Sequence risk", "The effect of the timing of returns, especially losses early in a withdrawal or investment period."),
        ("Mixed path", "A combination of choices, such as occupying part of a property, renting another lawful unit, retaining a separate property, or investing sale proceeds in stages."),
    ]),
    "pages/suggestions.html": ("Suggestions for review", "Review these improvements before adopting any change; this site does not apply recommendations automatically.", [
        ("Create a verified document vault", "Store deeds, trust documents, leases, tax bills, insurance policies, utility statements, and repair records in an access-controlled private location; publish only anonymized conclusions."),
        ("Compare mixed choices", "Model occupying one unit while renting others where lawful, retaining one property while selling another, and staged investment rather than limiting comparison to pure choices."),
        ("Put reversal conditions first", "List the facts that could change the preferred path—trust restrictions, occupancy, tax treatment, insurance availability, net rent, and liquidity—and document how each would be verified."),
        ("Stress sequence risk", "Compare immediate investment with 24–36 months in short-duration U.S. Treasury securities followed by phased equity purchases; include reinvestment and inflation risk, not just crash protection."),
        ("Update on decision dates", "Re-check official rules, professional quotes, property condition, market values, and investment assumptions when the transfer becomes imminent."),
    ]),
    "pages/what-we-need.html": ("Questions & missing evidence", "Collect documents rather than guessing. Blank facts are intentionally not estimated.", [
        ("Trustee / attorney", "What transfers, when, to whom, with what restrictions, debts, and distribution deadlines? Is continued occupancy allowed?"),
        ("CPA / tax attorney", "What are the estate's total taxable assets and deductions? What basis and valuation method apply? Which returns and payments are required, and when?"),
        ("Assessor / tax adviser", "What is the current assessed value, applicable tax rate and direct assessments, and which exclusion or reassessment rules apply to the actual transfer?"),
        ("Insurers / contractors", "Obtain written primary, landlord, fire, earthquake, and liability quotes; replacement-cost estimates; inspection findings; and multi-year repair plans."),
        ("Property manager / rent counsel", "Verify lawful unit count, permitted use, lease terms, rent limitations, tenant protections, and net achievable rent using current documents."),
        ("Investment adviser", "Compare immediate investment with 24–36 month Treasury staging and phased stock purchases; show liquidity, after-tax yields, inflation, and historical crash-entry stress tests."),
    ]),
    "pages/privacy.html": ("Privacy and limitations", "No personal or household-specific information is intentionally included in the public pages.", [
        ("Public-output boundary", "The published pages contain generic process guidance only. No names, addresses, postal codes, property valuations, rents, expense histories, or individualized recommendations are included."),
        ("History caveat", "Previously pushed Git objects, pull requests, forks, caches, and clones may retain older material even after the current site is cleaned. A history rewrite cannot recall copies already made."),
    ]),
    "pages/flagged-for-review.html": ("Flagged for review", "No household-specific figures are verified for public release. Resolve these evidence gaps before relying on a recommendation.", [
        ("Private input removal", "Earlier repository material may contain case-derived figures and location details. This public site intentionally omits them. Historical commits, forks, pull-request diffs, caches, and clones may still retain prior content."),
        ("History cleanup", "A full Git history rewrite requires repository-owner coordination and cannot erase copies already made elsewhere. Review repository visibility and coordinate a force-push only after preserving a secure private archive."),
        ("Insurance premiums", "No property-specific insurance price is published because premiums depend on underwriting and written quotes. Obtain insurer quotes near the decision date."),
        ("Future law and projections", "The anticipated transfer is decades away. Current law is not a forecast; validate statutes and thresholds again immediately before action."),
    ]),
}
STYLE = '''body{margin:0;background:#f5f7f8;color:#182a32;font:16px/1.6 system-ui,sans-serif}header,main,footer{max-width:980px;margin:auto;padding:24px}header{border-bottom:1px solid #d5dfe2}h1{font-size:2.3rem;line-height:1.15}h2{font-size:1.15rem;margin:0 0 8px}article{background:white;border:1px solid #dce5e7;border-radius:12px;padding:20px;margin:14px 0}a{color:#126a64}nav{display:flex;gap:16px;flex-wrap:wrap}footer{color:#52636a;font-size:.9rem}@media print{body{background:white}nav,footer{display:none}article{break-inside:avoid}}'''

def build():
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets' / 'style.css').write_text(STYLE, encoding='utf-8')
    (ROOT / 'pages').mkdir(exist_ok=True)
    for name,(title,intro,items) in PAGES.items():
        nav = ''.join(f'<a href="{("../" if name != "index.html" else "")}{("index.html" if dest == "index.html" else dest)}">{escape(label)}</a>' for dest,(label,_,__) in PAGES.items())
        parts = ''.join(f'<article><h2>{escape(head)}</h2><p>{escape(body)}</p></article>' for head,body in items)
        html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer"><title>{escape(title)} · Private decision framework</title><link rel="stylesheet" href="{'assets/style.css' if name == 'index.html' else '../assets/style.css'}"></head><body><header><nav>{nav}</nav><h1>{escape(title)}</h1><p>{escape(intro)}</p><button onclick="window.print()">Print this page</button></header><main>{parts}</main><footer>Planning framework only; not legal, tax, insurance, appraisal, or investment advice. No household-specific inputs are published.<p>Primary-source starting points: <a href="https://www.boe.ca.gov/prop19/">California Board of Equalization Proposition 19</a> · <a href="https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax">IRS estate tax</a> · <a href="https://www.irs.gov/forms-pubs/about-form-706">IRS Form 706</a> · <a href="https://www.treasurydirect.gov/marketable-securities/treasury-bills/">Treasury bills</a></p></footer></body></html>'''
        (ROOT / name).write_text(html, encoding='utf-8')
    # Remove old generated tables and aliases from the public output. Never publish projections.
    for p in (ROOT / 'pages').glob('*.html'):
        if p.name not in {"attorney-cpa-brief.html", "what-we-need.html", "flagged-for-review.html", "privacy.html", "suggestions.html", "phased-investing.html", "glossary.html"}:
            p.unlink()
    csv_path = ROOT / 'assets' / 'case-projections.csv'
    if csv_path.exists():
        csv_path.unlink()
    print('Built privacy-safe generic site; no household inputs or case projections were read.')

if __name__ == '__main__':
    build()
