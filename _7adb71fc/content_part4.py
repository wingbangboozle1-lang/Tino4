"""Reference pages added 2026-11-14: Attorney & CPA briefing sheet, deadline timeline, glossary.

Every fact links to an official page through the evidence ledger (SOURCES). Owner-supplied values carry
status Owner and no link, because no official source states them. Figures are model output rounded to $10
by case_model.money. Personal identifiers are never written here: placeholders such as [Owner] and [Attorney]
stand in for names, and no address, ZIP code, parcel or neighbourhood appears.
"""
from html import escape as E
from case_data import A, B, P
from case_model import path_comparison, money as M
from content_part1 import refs as _refs, table, callout, pct, V, O, Pj, As, Ms, _flip, _gap_at


def refs(*keys):
    """Accept space-joined keys as well as separate keys; every key must exist in the ledger."""
    return _refs(*' '.join(keys).split())


def mini(headers, rows):
    """Compact table for the one-page sheet. Each row: (cells, status, source keys)."""
    out = ('<table class="mini"><thead><tr>' + ''.join(f'<th scope="col">{E(h)}</th>' for h in headers)
           + '<th scope="col">Status</th><th scope="col">Official source</th></tr></thead><tbody>')
    for cells, status, ids in rows:
        out += '<tr>' + ''.join(f'<td>{c}</td>' for c in cells)
        out += (f'<td><span class="badge {status.split()[0].lower()}">{E(status)}</span></td>'
                f'<td>{refs(*ids.split()) if ids else "None; owner input"}</td></tr>')
    return out + '</tbody></table>'


def page_brief():
    c = path_comparison(2045)
    flip = _flip(lambda v: _gap_at('equity', v), 0.0, 0.15)
    flip_txt = pct(flip * 100, 1) if flip is not None else 'not reached in 0% to 15%'
    out = ('<div class="brief-sheet">'
           '<div class="brief-head"><div><span class="eyebrow">ONE PAGE · PRINT OR SAVE AS PDF</span>'
           '<h2>Attorney &amp; CPA Briefing Sheet</h2></div>'
           '<p class="brief-meta">Prepared for [Attorney] and [CPA] by [Owner], 14 November 2026. '
           'Property A: a home to be inherited through a trust, expected 2040 to 2050. Property B: a three-unit building '
           'already owned. The two are analysed separately. Figures rounded to $10. Projections are model arithmetic, not forecasts.</p></div>'
           '<div class="brief-grid">')
    out += '<section><h3>1. Facts and figures</h3>' + mini(
        ['Item', 'Figure'], [
            (['Property A, assessed value, 2026 roll (estimate)', M(A['assessed_2026'])], Pj, 'lta26002'),
            (['Property B, assessed value, 2026 roll (estimate)', M(B['assessed_2026'])], Pj, 'lta26002 pub29'),
            (['Market value and 2025 tax bill, A and B (owner to supply)', ''], Ms, 'pub29'),
            (['Rent from two units in B, annual (owner to supply)', ''], Ms, 'ab1482'),
            (['Federal basic exclusion, deaths in 2026 / 2027', M(P['exclusion_2026']) + ' / ' + M(P['exclusion_2027'])], V, 'wfct irs2027'),
            (['Family-home allowance, to 15 Feb 2027', '$1,044,590 (rounded)'], V, 'pub801 rtc632'),
            (['Insurance, both properties', 'Not quoted'], Ms, 'cdi'),
        ]) + '</section>'
    out += ('<section><h3>2. Model result, transfer in 2045, 20-year horizon, after tax</h3>' + mini(
        ['Path', 'Result'], [
            (['Sell A, reinvest the net proceeds', M(c['reinvest_after_tax'])], Pj, 'capgains niit'),
            (['Rent A, then sell at year 20', M(c['rental_total'])], Pj, 'rental'),
            (['Tax saved by living in A, years 1 to 20', M(c['move_in_savings'])], Pj, 'pub29'),
        ]) +
        f'<p class="brief-note">Selling leads while the return on the proceeds stays above about {flip_txt} a year after tax. '
        f'The {pct(P["tax_div"] * 100, 1)} tax rate on dividends and gains is an assumption, not a verified rate.</p></section>')
    out += ('<section><h3>3. Questions for the attorney</h3><ol>'
            '<li>Is the trust revocable now, and when does it become irrevocable? Trustee notice is due within 60 days of that event. '
            + refs('prob16061') + '</li>'
            '<li>Who files the death-transfer statement, the trustee or the transferee? Due within 150 days after death. '
            + refs('rtc480') + '</li>'
            '<li>Can the heir meet the Proposition 19 tests: principal residence on both sides, an eligible relationship, and a claim within three years? '
            + refs('pub19') + '</li>'
            '<li>Will the estate need Form 706 (nine months after death, if required)? ' + refs('form706') + '</li>'
            '<li>Confirm the state position: California imposes no estate or inheritance tax of its own. '
            + refs('rtc13301 rtc13302') + '</li>'
            '</ol></section>')
    out += ('<section><h3>4. Questions for the CPA</h3><ol>'
            '<li>Basis: the inherited basis is generally fair market value on the date of death. ' + refs('basis') + '</li>'
            '<li>Depreciation recapture on B and on any rented A: unrecaptured section 1250 gain is taxed at a maximum 25%. '
            + refs('capgains rental') + '</li>'
            '<li>Net investment income tax on rents and gains, including the trust threshold. ' + refs('niit') + '</li>'
            '<li>Trust income tax filing (Form 541), if a filing test is met. ' + refs('ftbtrust') + '</li>'
            f'<li>Replace the model inputs: the {pct(P["tax_div"] * 100, 1)} tax rate, the {pct(P["equity"] * 100, 1)} equity return, '
            f'the {pct(P["home_growth_default"] * 100, 1)} home growth and the {pct(P["rent_yield_default"] * 100, 1)} gross rent yield.</li>'
            '<li>Solar export credits are usually lower than retail. ' + refs('cpucnem') + '</li>'
            '</ol></section>')
    out += ('<section class="brief-wide"><h3>5. Deadlines (full timeline on its own page)</h3><p>'
            '9 months after death: Form 706, if required. 150 days after death: death-transfer statement. '
            '60 days after the trust event: trustee notice. Within 3 years: Proposition 19 claim. '
            'Each 1 November: county tax bill. Each 15 February: homeowners\' exemption claim. '
            'Installment due dates and the Form 706 extension were not verified and are left blank. '
            + refs('form706 rtc480 prob16061 pub19 rtc2610 homeex') + '</p></section>')
    out += ('<section class="brief-wide"><h3>6. Missing</h3><p>'
            'Appraisal of A at transfer; title reports; any debt or lien; the trust instrument; insurance quotes including earthquake; '
            'a rent roll and leases for B; the 2026 assessment notice for A; the legal status of the rental units in B. See Flagged for review.</p></section>')
    out += '</div></div>'
    return out


TIMELINE = [
    ('At death, or when a revocable trust becomes irrevocable', 'Day 0',
     'Starts the trustee-notice clock and the change-in-ownership clock. The inherited basis is generally fair market value on the date of death.',
     'Verified', 'prob16061 basis'),
    ('Within 60 days of that event', 'Day 60',
     'The trustee serves notice on the beneficiaries.',
     'Verified', 'prob16061'),
    ('Within 150 days after death', 'Day 150',
     'Change-in-ownership statement for property held in a trust. Filed by the trustee, or by the transferee if the trust does not file it.',
     'Verified', 'rtc480'),
    ('Nine months after death, if a return is required', 'Month 9',
     'Form 706, the federal estate and GST tax return. The federal basic exclusion is $15,000,000 for deaths in 2026 and $15,480,000 for deaths in 2027.',
     'Verified', 'form706 irs2027 wfct'),
    ('Within three years of the transfer', 'Year 3',
     'The Proposition 19 claim must be filed within three years. Confirm the principal-residence tests before the distribution date.',
     'Verified', 'pub19'),
    ('Each year, on or before 1 November', 'Annual',
     'County tax bill mailed. Installment due and delinquency dates are not confirmed and are left blank.',
     'Verified', 'rtc2610'),
    ('Each year, by 15 February', 'Annual',
     'Homeowners\' exemption claim for an owner-occupied home. The exemption reduces taxable value by $7,000.',
     'Verified', 'homeex'),
    ('Every second year, on 16 February', 'Biennial',
     'The family-home allowance is re-indexed. The current statutory figure, $1,044,586 (quoted verbatim), applies from 16 February 2025 to 15 February 2027.',
     'Verified', 'rtc632 pub801'),
    ('5 November 2026, published', 'Published',
     'IRS 2027 inflation adjustments (IR-2026-133), published 5 November 2026: basic exclusion $15,480,000 for deaths in 2027, and a $20,000 annual gift exclusion.',
     'Verified', 'irs2027'),
    ('1 January 2030', 'Law date',
     'The statewide rent ceiling in Civil Code 1947.12 expires. Whether it is extended is not known.',
     'Verified', 'ab1482'),
    ('2040 to 2050', 'Window',
     'Expected transfer window for Property A, from the owner brief. This is a planning window, not a legal date.',
     'Owner', ''),
]


def page_deadlines():
    out = callout('How to read this timeline',
        'Clocks start at different events, so the list is ordered by trigger, not by calendar year. Each deadline names the '
        'rule it rests on. Where an official source did not confirm a date, the date is left blank and marked Missing '
        'rather than estimated.', 'info')
    out += '<ol class="timeline">'
    for when, tag, what, status, ids in TIMELINE:
        out += (f'<li class="tl-item"><div class="tl-when"><span class="tl-tag">{E(tag)}</span>'
                f'<strong>{E(when)}</strong></div><div class="tl-body"><p>{E(what)}</p>'
                f'<span class="badge {status.lower()}">{E(status)}</span> '
                f'{refs(*ids.split()) if ids else "Owner planning window; no legal source"}</div></li>')
    out += '</ol>'
    out += table('Dates that are still missing', ['Deadline', 'Why it is not listed as a date'], [
        (['Installment due dates for the secured property tax bill',
          'Not confirmed from an official source in this session. Check the county tax collector before relying on a date.'], Ms, 'rtc2610'),
        (['Form 706 extension', 'Not confirmed. Check the IRS Form 706 instructions before relying on an extension.'], Ms, 'form706'),
        (['Trust income tax return (Form 541) due date', 'Filing tests are on the FTB page; the due date was not confirmed here.'], Ms, 'ftbtrust'),
    ], note='These rows exist so that a missing date is visible. None of them is filled in by estimate.')
    return out


GLOSSARY = [
    ('Assessed value', 'The value on the county roll that property tax is calculated on. It is not the market price.', 'Property tax', 'pub29'),
    ('Base-year value', 'The assessed value set at the last change in ownership. Proposition 13 then limits its growth.', 'Property tax', 'pub29'),
    ('Change in ownership', 'A transfer that resets the assessed value to market value, unless an exclusion applies.', 'Inheritance steps', 'pub29'),
    ('Proposition 19 (family-home transfer)', 'Lets an eligible heir keep a lower assessed value on a family home when the heir uses it as a principal residence and files a claim within three years.', 'Brief, timeline, decision', 'pub19'),
    ('Family-home allowance', 'The amount by which market value may exceed the carried base value and still transfer under the exclusion. Re-indexed every second 16 February.', 'Property tax', 'rtc632 pub801'),
    ('Principal residence', 'The home the owner actually lives in as the main home. Required on both sides of a Proposition 19 transfer.', 'Live, rent or sell', 'pub19'),
    ('Change-in-ownership statement (death transfer)', 'Filed within 150 days after death when property passes through a trust, by the trustee or the transferee.', 'Timeline', 'rtc480'),
    ('Trustee notification', 'The trustee must serve notice within 60 days of the event that requires it, such as a revocable trust becoming irrevocable.', 'Timeline', 'prob16061'),
    ('Small-estate affidavit', 'A simpler transfer procedure for estates below the state ceiling of $166,250.', 'Inheritance steps', 'prob13100'),
    ('Stepped-up basis', 'The inherited property\'s tax basis is generally its fair market value on the date of death. Selling above that basis still produces taxable gain.', 'Attorney and CPA sheet', 'basis'),
    ('Form 706', 'The federal estate and GST tax return. It is due nine months after death when a return is required.', 'Estate tax', 'form706'),
    ('Basic exclusion amount', 'The federal amount an estate can pass free of estate tax: $15,000,000 for deaths in 2026, $15,480,000 for deaths in 2027.', 'Estate tax', 'irs2027 wfct'),
    ('Annual gift exclusion', 'The amount that can be given to one recipient each year without a gift-tax return. $20,000 for 2027.', 'Estate tax', 'irs2027'),
    ('California estate or inheritance tax', 'California imposes none of its own. A dormant pickup provision applies only if a federal state-death-tax credit is reinstated.', 'Estate tax', 'rtc13301 rtc13302'),
    ('Unrecaptured section 1250 gain', 'The part of a gain on depreciated real estate that is taxed at a maximum 25% rate.', 'Attorney and CPA sheet', 'capgains'),
    ('Depreciation on rental property', 'The annual deduction for a rental building over its recovery period. It is recaptured on sale.', 'Costs', 'rental'),
    ('Net investment income tax', 'A tax on investment income, including rents and gains, above income thresholds. The rate and thresholds are on the linked IRS page.', 'Attorney and CPA sheet', 'niit'),
    ('Homeowners\' exemption', 'A $7,000 reduction in taxable value for an owner-occupied home, claimed by 15 February.', 'Costs', 'homeex'),
    ('Inflation factor for assessments', 'The BOE factor applied to the assessed value each year. The 2026 factor is 1.02, the 2% cap.', 'Property tax', 'lta26002'),
    ('Treasury bill', 'Short-term US government debt of 4 to 52 weeks. Its interest is subject to federal tax and not to state or local tax.', 'Black-swan page', 'bills'),
    ('Rent ceiling (Civil Code 1947.12)', 'Caps yearly rent increases at 5% plus the cost-of-living change, or 10%, whichever is lower. The statute expires on 1 January 2030.', 'Costs', 'ab1482'),
    ('FAIR Plan', 'The California property insurance plan for properties that standard insurers will not cover. Coverage is limited.', 'Costs', 'cdi'),
    ('Export credit (solar)', 'Under net energy metering, exported power earns bill credits. Their value is usually lower than the retail rate.', 'Costs', 'cpucnem'),
]


def page_glossary():
    out = callout('Terms with no legal definition',
        'Black swan and phased investing are not legal or tax terms. They are defined on the black-swan page, where the '
        'method is stated. Every other term below is linked to the official page that states the rule.', 'info')
    out += table('Glossary', ['Term', 'Plain meaning', 'Where it is used'],
                 [([t, m, w], V, ids) for t, m, w, ids in GLOSSARY],
                 note='Each meaning is a plain-language summary of the linked official page. Read the page itself before relying on a figure.')
    return out
