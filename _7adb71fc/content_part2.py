"""Case content: pages 6-11."""
from html import escape as E
from case_data import A, B, A_HISTORY, B_HISTORY, A_MID, B_MID, P, assess_check
from case_model import (money as M, projection, path_comparison, sale_proceeds,
                        after_tax_reinvest, exclusion_projection, allowance)
from evidence import SOURCES, FAILED, DATE
from content_part1 import table, callout, cards, refs, pct, V, O, Pj, As, Ms


def page_cost():
    a26 = projection('A', transfer=2045)[0]
    b26 = projection('B')[0]
    rows = [
        ('Mortgage or secured debt', None, None,
         'Never modelled. Neither property is assumed debt free. Obtain the payoff statement for B and confirm whether any loan encumbers A at transfer.', Ms, 'estate'),
        ('Property tax, all-in', M(a26['bill_full']), M(b26['bill_full']),
         'Owner bills divided by owner assessments. Includes charges beyond the 1% levy; no bonds, direct assessments or exemptions have been verified.', O, 'pub29'),
        ('Of which the 1% constitutional levy', M(a26['levy_base']), M(b26['levy_base']),
         'The constitutional rate. The remainder is local debt and charges that are not capped at 2%.', V, 'pub29'),
        ('Of which everything else', M(a26['levy_other']), M(b26['levy_other']),
         'About a third of A\'s bill and half of B\'s. This share can rise by local vote.', O, 'pub29'),
        ('Home insurance, owner-occupied', M(1500) + ' assumed', None,
         'The owner estimate. No policy has been read. A landlord policy is a different product with different limits.', O, 'cdi'),
        ('Home insurance, rented out', None, M(1500) + ' assumed',
         'A tenant-occupied building usually needs a landlord or dwelling policy. The owner estimate was not stated as one.', Ms, 'cdi'),
        ('Earthquake coverage', None, None,
         'Not included anywhere in this brief. Standard policies exclude it and the state insurer of last resort has coverage gaps.', Ms, 'cdi'),
        ('Water and sewer', M(a26['water']) + ' assumed', M(b26['water']) + ' assumed',
         'A: midpoint of $100-$150 a month. B: midpoint of $330-$400 a month for three units. No utility bill has been read and no tariff verified.', O, 'cpucnem'),
        ('Electricity', M(a26['electric']) + ' assumed, a credit', M(b26['electric']) + ' assumed',
         'A: midpoint of a $10-$20 monthly credit, so negative. B: midpoint of $30-$70 a month. Solar export is a bill credit, not cash.', O, 'cpucnem eia'),
        ('Maintenance and repairs', M(a26['maintenance']) + ' modelled', M(b26['maintenance']) + ' modelled',
         'A: 1.0% of value. B: 1.5% of value. Both are assumptions, not invoices. Roof, sewer, seismic and solar replacement are separate.', As, 'rental'),
        ('Vacancy and management', None, M(b26['rent'] * (P['vacancy'] + P['management'])) + ' modelled',
         '5% vacancy and 8% management applied to B\'s gross rent. Neither figure has been quoted or observed.', As, 'ab1482'),
        ('Annual running cost, excluding debt', M(a26['cash_cost_owner']), M(b26['cash_cost_owner']),
        'The sum of the rows above at 2026 prices. It is the number a household budget has to carry.', Pj, 'cdi pub29'),
    ]
    return callout('No verified insurance premium exists for either property',
        'The California Department of Insurance publishes comparison tools, a list of carriers writing difference-in-conditions '
        'policies and the coverage gaps in the FAIR Plan. It publishes no premium for any address. The owner estimate of '
        + M(1500) + ' a year is carried as an owner figure everywhere it appears, never as a verified quote. For a rented A '
        'that same number is very likely too low, because a landlord policy on a high-value single-family home in this '
        'county is a different underwriting class from an owner-occupied policy.', 'warning') + table(
        'Running costs, both homes, 2026', ['Cost line', 'Property A', 'Property B', 'How the number was produced'], rows) + table(
        'Sensitivity: what a change in each cost does to the recommendation', ['If this cost moves', 'Effect on living in A versus renting it', 'Why'], [
        (['Insurance up 200%', 'Widens the gap in favour of selling.', 'Insurance is paid whether the home is occupied or rented, so it hits both, but occupancy also loses the rent that would have helped.'], As, 'cdi'),
        (['Insurance up 700% to ' + M(12000), 'Eats the entire occupancy tax advantage.', 'The occupancy gain is about ' + M(path_comparison(2045)['move_in_savings']/20) + ' a year. Above roughly twelve thousand a year the tax base no longer pays for itself.'], As, 'cdi pub801'),
        (['Electricity credit becomes a charge', 'Small. About ' + M(2160) + ' a year at worst.', 'Even losing the whole credit and paying retail is a rounding error next to the tax and the value.'], As, 'cpucnem eia'),
        (['Water doubles', 'Small on A, moderate on B.', 'A\'s water is under two thousand a year. B\'s is closer to four thousand.'], As, 'cpucnem'),
        (['Maintenance doubles', 'Narrows the case for holding A, but not by much.', 'A\'s modelled maintenance is 1% of a large value, so it already dominates the rent.'], As, 'rental'),
    ]) + table('Mixed-use accounting for Property B', ['Issue', 'Treatment that has to be verified', 'Why it is not obvious'], [
        (['How much of B is personal and how much is rented',
          'Allocate using a documented basis, such as floor area or rooms actually used, and keep the personal share out of the rental schedule.',
          'Three units do not mean two thirds, and the personal share of a shared utility is not deductible.'], Ms, 'rental'),
        (['Whether all three units are legal',
          'Check the certificate of occupancy and any permits for the third unit.',
          'An unpermitted unit changes the rent you can count and the insurance you can buy.'], Ms, 'rental'),
        (['Whether the tenancies are covered by the local ordinance',
          'Read the coverage test for the building\'s age and use, and the exemption notice rules.',
          'Insurance-company rent estimates and the lawful increase are different numbers.'], Ms, 'ab1482 sfrates'),
        (['Whether the vacant unit may lawfully be rented',
          'Confirm the legal unit count and any owner-move-in restriction.',
          'A vacant unit is not automatically rentable.'], Ms, 'sfrates'),
    ])


def page_tax():
    rows = []
    for y, t, a in A_HISTORY:
        rows.append((['A', str(y), M(t), M(a), pct((t / a * 100) if t else 0, 2) if t else None], O, 'pub29 lta26002'))
    for y, t, a in B_HISTORY:
        rows.append((['B', str(y), M(t), M(a), pct(t / a * 100, 2)], O, 'pub29 lta26002'))
    checks = []
    for label, hist, rate in (('A', A_HISTORY, A_MID['tax_rate']), ('B', B_HISTORY, B_MID['tax_rate'])):
        for year, step, implied, supplied in assess_check(hist, rate):
            checks.append(([label, year, pct(step * 100, 2), M(implied), M(supplied)], O,
                           'lta26002 pub29'))
    return callout('Three different numbers are called "value" and they are not interchangeable',
        'Market value is what a buyer would pay. Assessed value is the Prop 13 base that the bill is calculated on. Tax '
        'basis is what the income tax is calculated on when you sell. A federal step-up resets the third and does nothing '
        'to the second. The Proposition 19 exclusion resets the second and does nothing to the third. Confusing them is the '
        'single most expensive mistake available in this decision.', 'warning') + table(
        'The supplied history, rounded to $10', ['Property', 'Year', 'Property tax paid', 'Assessed value', 'Implied rate'], rows,
        'These are your figures, rounded before publication. They are internally consistent with each other, which is a '
        'useful check, but no county roll or bill has been read by this session.') + table(
        'Does the history match Prop 13? Every year-to-year step, re-derived', ['Property', 'Year', 'Assessment step', 'Tax implied by the assessment', 'Tax you supplied'], checks,
        'The implied column multiplies the rounded assessment by the effective rate your own bills support. Where it and '
        'the supplied tax differ, the difference is consistent with the deduction of the $7,000 homeowners exemption from '
        'the assessed value before the rate is applied, which is what the constitution provides.') + table(
        'The rules that govern the bill', ['Rule', 'What the official source says', 'What it means here'], [
        (['The 1% levy', 'One percent of assessed value plus the rate needed for voter-approved bonded debt.', 'A\'s effective rate is ' + pct(A_MID['tax_rate']*100, 2) + ' of assessed value and B\'s is ' + pct(B_MID['tax_rate']*100, 2) + '. Neither is 1%.'], V, 'pub29'),
        (['The 2% cap', 'Annual increases in the base year value are limited to no more than 2%.', 'Applied every year in every projection on this site, including in the crash years, because that is what the cap does.'], V, 'pub29'),
        (['The cap is not a ceiling on the bill', 'The limit applies to the base year value, not to charges and direct assessments.', 'A new bond or a new direct assessment can raise the bill by more than 2% in a single year.'], V, 'pub29'),
        (['Reassessment on transfer', 'Property is reassessed to market value on a change in ownership.', 'Renting A triggers this at the transfer date. Occupying it does not, if the family-home exclusion applies.'], V, 'pub29 pub19'),
        (['The family-home exclusion', 'The base may carry over, up to the factored base plus the biennially adjusted allowance, if an eligible child occupies the home as a principal residence.', 'This is the mechanism that creates almost all of the occupancy advantage.'], V, 'pub801 lta26026'),
        (['Continual use', 'If the home stops being the transferee\'s principal residence, the exclusion is removed.', 'Move out later and the reassessment arrives then, computed from the transfer date.'], V, 'lta26026'),
        (['Filing windows', 'Claim the exclusion within three years, and file the homeowners exemption within one year to get the exclusion from the transfer date.', 'Miss the one-year window and the benefit starts when you file, not when you inherited.'], V, 'pub801'),
        (['The homeowners exemption', 'A $7,000 reduction in taxable value for a qualifying owner-occupied home.', 'Worth about ' + M(7000 * A_MID['tax_rate']) + ' a year on A. One such home per claimant.'], V, 'homeex'),
        (['The death-transfer statement', 'The trustee or transferee files within 150 days after the date of death.', 'Not optional, and it is how the county learns to reassess.'], V, 'rtc480'),
        (['Documentary transfer tax', 'Fifty-five cents per $500 in the county, plus any city tax.', 'Paid on a sale, not on an inheritance that stays in the trust.'], V, 'rtc11911'),
    ]) + callout('Why the allowance is the number most people get wrong',
        'The statute does not freeze one million dollars, and it does not index the allowance to the value of the house. '
        'Revenue and Taxation Code 63.2 sets a one million dollar base and directs that it be adjusted every second '
        'February 16 to the prior calendar year percentage change in the federal House Price Index for California. The published '
        'figure for transfers between 16 February 2025 and 15 February 2027 is $1,044,590, shown rounded like every other '
        'dollar on this site. This site replays the measured index rate of 6.35% a year, from the same official series used '
        'on the black-swan page, and re-sets the figure in two-year steps. That is why the allowance on a 2045 transfer is '
        'about $3,163,890 rather than $1,044,590. It is a replay of a published series, not a forecast, and it is '
        'deliberately not tied to the 4% house-growth assumption.', 'info') + callout('What the history does not tell you',
        'No county roll, bill or exemption record has been read. A supplied total that repeats in consecutive years, a '
        'year with no bill, and a missing current-year bill for B are all recorded as gaps rather than explained. They may '
        'be perfectly ordinary: fiscal-year labelling, a supplemental assessment, a refund or a payment timing difference '
        'would all produce the same appearance. The correct next step is to pull the original bills and the assessor\'s '
        'value notice for each year, which is question Q3 and Q4 on the questions page.')


def page_questions():
    q = [
        ('Q1', 'Highest', 'What exactly does the trust say about the real property?',
         'Who is the trustee, who is the beneficiary of the home, is there a specific devise, a requirement to sell, or a power to retain. Nothing about the property is known beyond that it is held in trust.',
         'The trustee, and a lawyer who reads the instrument.',
         'Every other question depends on this. A direction to sell ends the analysis.', 'Missing', 'prob16061 pub19'),
        ('Q2', 'Highest', 'Will the family-home exclusion actually be available?',
         'Whether you are an eligible child, whether the transferor used it as a principal residence, whether you will occupy it within one year, and whether the value exceeds the allowance.',
         'The county assessor in the county where the property sits, using form BOE-19-P.',
         'It is the difference between a bill based on ' + M(2_918_180) + ' and one based on ' + M(6_531_230) + ' in 2045. It is the largest single number in the decision.', 'Missing', 'pub801 lta26026'),
        ('Q3', 'Highest', 'What does the current assessment roll and bill say for each property?',
         'The assessed value, the 1% levy, every direct assessment, any bond, and any exemption applied. Only the owner totals are known here.',
         'The county assessor and tax collector, by parcel, in writing.',
         'It separates the part of the bill that is capped at 2% from the part that is not.', 'Missing', 'pub29'),
        ('Q4', 'High', 'Why does the supplied history differ from the implied tax in some years?',
         'A repeated total, a missing year and a missing current-year bill for the second property are visible in the data. No cause is inferred.',
         'The original bills and the assessor\'s annual value notices.',
         'If a supplemental assessment or a refund is in the history, a future projection should not simply trend the total.', 'Missing', 'lta26002'),
        ('Q5', 'Highest', 'What insurance is actually available, and at what price?',
         'Owner-occupied, tenant-occupied and mixed-use are three different products. Earthquake is excluded from standard policies and the state insurer of last resort does not cover liability or theft.',
         'Three licensed brokers, each asked for the same reconstruction limit and deductible.',
         'Above roughly ' + M(12000) + ' a year the occupancy advantage disappears. Below it, occupancy wins on cost alone.', 'Missing', 'cdi'),
        ('Q6', 'High', 'What rent could Property A actually achieve?',
         'No listing, appraisal or rent survey has been read. The assumption used is a ' + pct(P['rent_yield_default']*100) + ' gross yield.',
         'Three written rental opinions for comparable homes, plus the tenancy rules that apply.',
         'Renting only competes if collected rent clears about ' + M(path_comparison(2045)['horizon_row']['cash_cost_rental']/0.95) + ' a year in the transfer year, before management and any mortgage.', 'Missing', 'rental ab1482'),
        ('Q7', 'High', 'Is the third unit at Property B legal and rentable?',
         'A vacant unit is not automatically a lawful unit. The certificate of occupancy and the permits have not been seen.',
         'The local building department, and any rent board registration record.',
         'Adding lawful rent changes B\'s cash flow, and B is the asset you keep in the recommended path.', 'Missing', 'sfrates rental'),
        ('Q8', 'High', 'What is the total estate, not just these two homes?',
         'The brief mentions a considerable amount of money in addition to the homes. The amount, the form and the beneficiary structure are all unknown.',
         'The trustee, with a CPA, on a single schedule of every asset and debt.',
         'The federal exclusion is tested against the whole estate. ' + M(P['exclusion_2027']) + ' in 2027 is generous, but a large estate changes the answer completely.', 'Missing', 'estate form706'),
        ('Q9', 'High', 'What is the combined income tax position in the transfer year?',
         'Filing status, other income, and whether the seller is the trust or the beneficiary all change the marginal rate.',
         'A CPA, using a year-specific projection for both the federal and California returns.',
         'The difference between a trust sale and a beneficiary sale is not modelled here and can be significant.', 'Missing', 'capgains niit ftbgains'),
        ('Q10', 'Medium', 'Are there any encumbrances on either property?',
         'No mortgage, lien, reverse mortgage or HELOC has been confirmed on either property. Every projection here is debt free by omission, not by evidence.',
         'A title report for each property.',
         'A reverse mortgage or a lien would change the net proceeds and could force a sale.', 'Missing', 'estate'),
        ('Q11', 'Medium', 'What condition is Property A in, and what is due to fail?',
         'No inspection has been performed. Roof, sewer, electrical, foundation and the age of the solar system are unknown.',
         'A licensed inspector, plus the solar installer\'s interconnection and warranty file.',
         'A single major repair in the first two years changes the ranking of the paths.', 'Missing', 'rental'),
        ('Q12', 'Medium', 'Which electricity tariff is the solar system on?',
         'Systems interconnected before April 2023 sit on a different export tariff from newer ones, and the credit value differs.',
         'The utility, with the interconnection date and the annual true-up statement.',
         'The owner reports a small credit. That is plausible, but the tariff determines whether it survives a change of occupant or ownership.', 'Missing', 'cpucnem'),
        ('Q13', 'Medium', 'How is the estate to be distributed, and on what timetable?',
         'The brief says 2040 to 2050 with no fixed date. The trustee may have discretion.',
         'The trustee and the instrument.',
         'The transfer year moves the numbers substantially: the sale value in 2040 and 2050 differs by about ' + M(path_comparison(2050)['sale_price']-path_comparison(2040)['sale_price']) + '.', 'Missing', 'prob16061'),
        ('Q14', 'Medium', 'What are the actual selling costs?',
         'A 6% assumption covering commission, escrow, title and concessions. No net sheet has been read.',
         'A title company and two brokers, each producing a written seller net sheet for the property.',
         'One percent of a ' + M(6_500_000) + ' home is ' + M(65_000) + '. This assumption is worth real money.', 'Assumption', 'rtc11911'),
        ('Q15', 'Medium', 'What return should the invested proceeds realistically target?',
         'A ' + pct(P['equity']*100) + ' total return is assumed. The securities regulator publishes risk warnings and no expected return.',
         'An adviser, producing a written investment policy statement with a stated risk tolerance.',
         'If the realistic return is 4% rather than 6%, the case for selling narrows sharply.', 'Assumption', 'stocks cbo'),
        ('Q16', 'Medium', 'Will the family-home exclusion still exist in 2045?',
         'It is a constitutional provision that replaced a previous one in 2021. No official source forecasts its survival.',
         'The Secretary of State\'s ballot measures and the Legislature\'s bill list, checked annually.',
         'A repeal would remove almost the entire occupancy advantage and reduce the decision to a comparison of cash flows.', 'Missing', 'pub19 sos2026'),
        ('Q17', 'Medium', 'What does the statewide rent ceiling do after 2030?',
         'The current statute expires on 1 January 2030. What replaces it is not law yet.',
         'The Legislature, and the local rent board annually.',
         'If rent control tightens, renting A becomes worse, not better.', 'Missing', 'ab1482'),
        ('Q18', 'Low', 'Is there any unclaimed property in the estate?',
         'The state holds unclaimed property, including unredeemed savings bonds, and publishes a free search.',
         'The state controller\'s unclaimed property search, and TreasuryDirect for savings bonds.',
         'A small, inexpensive check that occasionally finds real money.', 'Missing', 'sco'),
        ('Q19', 'Highest', 'What cash reserve exists for a forced-sale scenario?',
         'No reserve, income, debt or spending figure is known. The stress page shows a 41% drawdown and a 12.8-year recovery.',
         'The household, producing a simple statement of liquid reserves and annual commitments.',
         'Without a reserve, a market decline turns a paper loss into a realised one, which is the largest avoidable risk here.', 'Missing', 'fhfa bills'),
        ('Q20', 'Low', 'What are the actual water, sewer and electricity bills?',
         'The owner gave monthly ranges. No bill, meter or tariff has been read.',
         'Twelve months of bills for each property, plus the water district\'s published tariff.',
         'Small in the model, but it is the only cost where a verified number is a phone call away.', 'Missing', 'cpucnem eia'),
        ('Q21', 'Low', 'Do the properties sit in a fire or flood hazard zone?',
         'No hazard disclosure has been read. This affects both insurability and price.',
         'The state hazard maps and the seller or trustee disclosure package.',
         'A high hazard score can make a property uninsurable at any price, which ends the occupancy plan.', 'Missing', 'cdi'),
        ('Q22', 'Low', 'What did the properties sell for, and when?',
         'Only assessed values are known. The transfer history would show whether a base year value is unusually low.',
         'The county recorder, by document search.',
         'Useful context for how much Proposition 13 protection is embedded, but not decisive.', 'Missing', 'pub29'),
    ]
    return callout('Answer these in order, and do not decide before Q1 to Q6 are closed',
        'The questions are ordered by what unlocks the most. The first six determine whether occupancy is even available, '
        'what the two bills really are, and what the property would rent for. Until those are answered on paper from an '
        'authorised source, any recommendation including the one on this site is conditional. The discovery suggestions '
        'exist so that an answer, when it arrives, is a document rather than an assumption.', 'warning') + table(
        'Questions, who can answer them, and what each one unlocks', ['ID', 'Priority', 'Question', 'What is missing today', 'Who or what can answer it', 'What it unlocks'], [
        ([i, pr, t, m, w, u], s, src) for i, pr, t, m, w, u, s, src in q])


def page_suggestions():
    sug = [
        ('SUG-01', 'P0', 'Occupancy', 'Settle the trust question before anything else',
         'Get a written opinion on whether the trust permits, requires or forbids occupancy, and on who the trustee will be at the time.',
         'Every financial comparison on this site is downstream of it. If the instrument directs a sale, the analysis is over.',
         'prob16061 pub19'),
        ('SUG-02', 'P0', 'Tax', 'File the family-home exclusion claim in the first year',
         'Diarise the claim within twelve months of the transfer, and the homeowners exemption at the same time.',
         'The three-year claim window gives relief from the transfer date; the one-year exemption window does not. Missing the second loses years of benefit.',
         'pub801 lta26026 homeex'),
        ('SUG-03', 'P0', 'Privacy', 'Keep every private document out of this repository',
         'Deeds, trust instruments, bills, appraisals, insurance policies and account statements belong in an encrypted store outside this public repository.',
         'This repository is public. Deletion from the current build tree does not remove it from history, forks or caches.',
         'sco'),
        ('SUG-04', 'P1', 'Decision', 'Get three insurance quotes for each intended use',
         'Obtain owner-occupied, tenant-occupied and mixed-use quotes with the same reconstruction limit and deductible, and quote earthquake separately.',
         'Insurance is the one cost that can flip the recommendation, and it is one of the few that a phone call resolves.',
         'cdi'),
        ('SUG-05', 'P1', 'Decision', 'Test the rent assumption before testing the market',
         'Get three written rental opinions. Use the lowest, not the average.',
         'The case against renting is strong only if rent is near the assumed ' + pct(P['rent_yield_default']*100) + ' yield. Prove it or disprove it quickly.',
         'rental ab1482'),
        ('SUG-06', 'P1', 'Decision', 'Write the sell-and-reinvest plan down now, as a standing instruction',
         'Agree in advance the sale triggers, the investment allocation, the staging of entry into the market and the reserve to be held back.',
         'The recommendation is occupancy with sale as the fallback. A fallback that is improvised during a stress event is not a fallback.',
         'stocks bills'),
        ('SUG-07', 'P1', 'Tax', 'Model the whole estate, not the two homes',
         'Build one schedule of every asset, every debt and every beneficiary, then test it against the exclusion in the likely transfer year.',
         'The federal tax is on the estate. A large cash inheritance changes the answer for the houses completely.',
         'estate form706 irs2027'),
        ('SUG-08', 'P1', 'Cost', 'Pull twelve months of utility bills and the water tariff',
         'Verify water, sewer and electricity for both properties, and confirm which solar tariff applies.',
         'It is cheap evidence, and it replaces two ranges with two numbers.',
         'cpucnem eia'),
        ('SUG-09', 'P1', 'Risk', 'Set a reserve equal to two years of both properties\' costs',
         'Hold it in insured deposits or Treasury bills, sized to two years of bills, insurance and maintenance on both homes.',
         'The published state index fell 41% and took 12.8 years to recover. A reserve is what stops that becoming a forced sale.',
         'bills fhfa'),
        ('SUG-10', 'P2', 'Decision', 'Compare the occupancy case against the real alternative, not against zero',
         'If you do not move to A, you stay in B and keep its rent and its own tax base. Price the housing you actually give up.',
         'The comparison in this brief excludes B on purpose. A household decision has to include what happens to the home you already have.',
         'rental pub29'),
        ('SUG-11', 'P2', 'Tax', 'Check whether selling inside the trust or outside it is cheaper',
         'Ask a CPA to model both, including the fiduciary filing rules and the marginal rate of each seller.',
         'Not modelled here. The difference can be large and it is entirely a tax question.',
         'ftbtrust capgains'),
        ('SUG-12', 'P2', 'Cost', 'Obtain one inspection before the transfer date, not after',
         'A pre-transfer inspection turns an unknown repair bill into a known one and gives time to plan the cash.',
         'A single roof or sewer project early in the hold changes the ranking of the paths.',
         'rental'),
        ('SUG-13', 'P2', 'Process', 'Build a dated deadline calendar for the first 36 months',
         'Sixty days for the trustee notice, 150 days for the death-transfer statement, nine months for a federal estate return, twelve months for the exemption, three years for the exclusion claim.',
         'Every one of these has a statutory clock and a penalty or a lost benefit if it is missed.',
         'prob16061 rtc480 form706 pub801'),
        ('S01', 'P1', 'Site', 'Add a printable one-page decision sheet',
         'A single page carrying the recommendation, the three numbers that decide it and the six questions that are still open.',
         'It is what you would actually take to a trustee or an adviser meeting. It should contain no private data.',
         'estate'),
        ('S02', 'P1', 'Site', 'Add a what-if calculator with explicit sliders',
         'Let the reader move the rent yield, the insurance premium, the return and the transfer year and watch the ranking change.',
         'The recommendation depends on four assumptions. Showing that dependency is more honest than a single answer.',
         'stocks cdi'),
        ('S03', 'P2', 'Site', 'Put the evidence grade next to every number',
         'A visible marker distinguishing a verified statutory figure from an owner figure from an invention, on every page.',
         'Currently the status column does this but it is easy to miss. The distinction is the whole point of the brief.',
         'pub29'),
        ('S04', 'P2', 'Site', 'Publish the failed retrievals, not only the successes',
         'A short public list of sources that could not be read and why.',
         'It tells a reviewer exactly where the analysis is thin, which is more useful than a longer list of links.',
         'fhfa'),
        ('S05', 'P2', 'Site', 'Link each open question to the document that would close it',
         'Next to Q1 to Q22, name the specific form or record rather than the institution.',
         'It converts a research task into a checklist.',
         'rtc480 pub801'),
        ('S06', 'P2', 'Site', 'Keep a dated law-change log on this site',
         'A one-line entry each time a cited rule changes, with the date and the source.',
         'The rent ceiling expires in 2030 and the exclusion has been rewritten once already. A static brief ages badly.',
         'ab1482 pub19'),
    ]
    out = callout('Review first. Nothing here is implemented or recommended for immediate execution.',
        'This is a proposal queue, not a change engine. Selecting a preference below records it only in this browser. It '
        'does not change any projection, any tax rule, any file in this repository or any investment. Every item starts at '
        '"Not reviewed".', 'warning')
    out += '<div class="toolbar"><button id="reset-reviews" type="button">Reset local review choices</button><span id="review-summary" aria-live="polite">No review choices recorded.</span></div>'
    out += ('<section class="table-section"><h2>Proposals, financial and editorial</h2>'
            '<p class="table-note">Grouped by theme. Priority P0 is a prerequisite, P1 changes the recommendation, P2 '
            'improves the product. The trade-off column states what the proposal costs as well as what it buys.</p>'
            '<div class="table-scroll" tabindex="0" aria-label="Suggestion review queue"><table><thead><tr>'
            + ''.join(f'<th scope="col">{h}</th>' for h in ['ID / priority', 'Theme', 'Proposal', 'What it involves',
                                                            'Benefit and trade-off', 'Review preference', 'Status', 'Official context'])
            + '</tr></thead><tbody>')
    for ident, pri, theme, title, what, benefit, src in sug:
        out += (f'<tr><td>{ident} &middot; {pri}</td><td>{E(theme)}</td><td>{E(title)}</td><td>{E(what)}</td>'
                f'<td>{E(benefit)}</td><td><select class="review-choice" data-id="{ident}" '
                f'aria-label="Review preference for {ident}">'
                + ''.join(f'<option value="{v}">{v}</option>' for v in ['Not reviewed', 'Investigate', 'Preferred path', 'Defer'])
                + f'</select></td><td><span class="badge guidance">Guidance</span></td><td>{refs(*src.split())}</td></tr>')
    out += '</tbody></table></div></section>'
    out += table('Suggested approval sequence', ['Gate', 'Acceptance criterion', 'Why it comes in this order'], [
        (['1 - Privacy', 'No private document or amount in this repository, and a working encrypted store exists elsewhere.', 'Everything else assumes documents will exist somewhere safe.'], As, 'sco'),
        (['2 - Trust', 'A written answer on occupancy and on the trustee\'s authority.', 'It determines whether the other gates are even needed.'], As, 'prob16061'),
        (['3 - Evidence', 'Every owner figure replaced or confirmed by a bill, roll, quote or appraisal.', 'A rounded owner figure is a lead, not a fact.'], As, 'pub29 cdi'),
        (['4 - Tax', 'The whole estate and both filing positions modelled by a CPA.', 'The exclusion is tested on the estate, not on one asset.'], As, 'estate'),
        (['5 - Risk', 'A reserve is funded and the fallback plan is written down.', 'The largest avoidable loss is a forced sale.'], As, 'fhfa'),
        (['6 - Decision', 'One path chosen, with the trigger that would reverse it recorded.', 'A decision without a reversal condition is not reversible.'], As, 'stocks'),
    ])
    return out
