"""Case content: pages 12-17."""
from html import escape as E
from case_data import A, B, P, A_MID, B_MID
from case_model import money as M, exclusion_projection, path_comparison, projection
from evidence import SOURCES, FAILED, DATE
from content_part1 import table, callout, cards, refs, pct, V, O, Pj, As, Ms


def page_estate():
    rows = []
    for y, amount in exclusion_projection((2040, 2050)):
        rows.append(([y, None, M(amount), M(amount - path_comparison(min(y, 2050))['sale_price'])], Pj, 'irs2027 form706'))
    return callout('There is no inheritance tax to plan around, and that is the good news',
        'California prohibits an inheritance or estate tax of its own, and the state controller confirms no California '
        'estate return is required for anyone dying after 2004. The federal estate tax is a tax on the estate above the '
        'exclusion for the year of death, not on what any one heir receives. On current law an estate well past '
        + M(P['exclusion_2027']) + ' is needed before any federal tax is due, and the money mentioned in the brief would have to be '
        'tested against the whole estate, which is not known.', 'warning') + table(
        'The thresholds that actually exist', ['Item', 'Amount or rule', 'What it does and does not mean'], [
        (['Federal basic exclusion, 2026', M(P['exclusion_2026']),
          'Set by Public Law 119-21 for deaths in 2026. An estate below this owes no federal estate tax.'], V, 'estate wfct'),
        (['Federal basic exclusion, 2027', M(P['exclusion_2027']),
          'Published 5 November 2026. Indexed each year after; the 2040s figure is not published and is not knowable.'], V, 'irs2027'),
        (['Federal annual gift exclusion, 2027', M(20_000),
          'Per recipient per year, before any lifetime gift tax return is needed. This is a separate allowance from the estate exclusion.'], V, 'irs2027'),
        (['Top federal estate rate', '40%',
          'A marginal rate on the taxable estate above the exclusion, after credits. It is not 40% of the whole estate.'], V, 'form706'),
        (['Filing deadline', '9 months after death, with a 6-month extension available',
          'The return is due whether or not tax is owed, if the threshold is passed.'], V, 'form706'),
        (['California estate or inheritance tax', 'None',
          'Prohibited by statute and confirmed by the state controller. The dormant pickup provision only applies if a federal state death tax credit returns.'], V, 'rtc13301 rtc13302 sco'),
        (['California fiduciary income tax', 'Trust income over $10,000 gross or $100 net may require a return',
          'This is income tax on the trust, not a transfer tax. It applies while the trust holds the house and collects rent.'], V, 'ftbtrust'),
        (['Portability', 'An election on a timely filed return',
          'A surviving spouse can inherit an unused exclusion, but only by electing. Do not assume double the exclusion without it.'], V, 'estate form706'),
        (['Stepped-up basis', 'Fair market value at death, generally',
          'The income-tax reset that makes an inherited home nearly tax free to sell immediately. It is a different benefit from the estate exclusion.'], V, 'basis'),
    ]) + table(
        'Projected exclusion and headroom, 2040 to 2050, using a stated assumption', ['Transfer year', 'Published figure for that year', 'Projected exclusion at ' + pct(P['estate_growth']*100) + ' a year', 'Headroom over a transfer-date sale value of A'], rows,
        'The middle column is empty on purpose: no official source publishes a 2040 exclusion. The right-hand columns are '
        'arithmetic on the published 2027 figure plus an assumed growth rate, and they are labelled Projection for that '
        'reason. They are not a threshold and they must not be used to size a gift.') + callout(
        'The real risk is legislative, not arithmetic',
        'A future Congress can lower the exclusion, and it has changed several times since 2001. The 2027 figure is '
        'indexed, so on unchanged law it rises above ' + M(P['exclusion_2027']) + '. The two things that would actually matter are a '
        'reduction in the exclusion and a repeal of the step-up in basis. Neither is enacted, and the one bill this '
        'session checked that would repeal the step-up was introduced and referred to committee, not passed.') + table(
        'What would have to be true for a federal tax to matter', ['Condition', 'Where it stands', 'What to do'], [
        (['A large total estate', 'Unknown. The homes alone are ' + M(A['value_2026'] + B['value_2026']) + ' at 2026 values; the additional money has not been disclosed or valued.',
          'Build one schedule with a CPA. Only the total matters.'], Ms, 'estate'),
        (['No prior taxable gifts', 'Unknown. Forms 709 may exist and have not been read.',
          'Obtain any filed 709s. Prior gifts reduce the exclusion.'], Ms, 'form706'),
        (['A lower exclusion in the year of death', 'Not enacted. Speculation only.',
          'Re-test annually, and prefer liquidity over illiquidity if the estate is close to the line.'], Ms, 'estate'),
        (['A repeal of the basis step-up', 'A bill was introduced in the 119th Congress and referred to committee. It did not become law.',
          'Do not plan on a repeal, but do not assume the step-up survives forever.'], V, 'basis'),
    ]) + table('Sample arithmetic, not a tax computation', ['Taxable estate', '2027 exclusion', 'Arithmetic on the excess at 40%', 'What it is not'], [
        ([M(v), M(P['exclusion_2027']), M(max(0, v - P['exclusion_2027']) * 0.40),
          'Not a Form 706. Ignores deductions, credit, portability, prior gifts and every asset other than the estate total.'], Pj, 'form706')
        for v in (15_000_000, 20_000_000, 30_000_000, 50_000_000)])


def page_process():
    steps = [
        ('Month 0', 'Death and the trust becomes irrevocable',
         'The trustee\'s duties begin. The instrument, not the deed date, determines what happens to the house.',
         'Confirm who the acting trustee is and get the original instrument.',
         'prob16061'),
        ('Day 0-60', 'Trustee notification to beneficiaries and heirs',
         'A trustee must serve a notification when a revocable trust becomes irrevocable, generally within 60 days.',
         'Diarise the date; a late notice is a personal liability for the trustee.',
         'prob16061'),
        ('Day 0-150', 'Death-transfer change of ownership statement',
         'The trustee files with the county recorder or assessor in each county where real property sits, within 150 days.',
         'This is how the county learns to reassess. It is required, not optional.',
         'rtc480'),
        ('Day 30-90', 'Obtain the appraisal date of death value',
         'The date of death fair market value is both the federal estate value and the inherited basis. One appraisal serves both.',
         'Do it early. A retroactive appraisal years later is expensive and weaker.',
         'basis'),
        ('Month 3-6', 'Decide the occupancy plan, and occupy if eligible',
         'To keep the family-home exclusion, an eligible child must use the home as a principal residence, with the exemption claim inside one year.',
         'This is the fork that determines the whole analysis. Do not rent it out while you decide.',
         'pub801 lta26026'),
        ('Month 0-12', 'File the homeowners exemption',
         'A claim inside one year gives the exclusion from the transfer date. Later claims start from the filing year.',
         'The one-year clock is the most expensive one to miss.',
         'pub801 homeex'),
        ('Month 0-9', 'Federal estate return, if the threshold is passed',
         'Due nine months after death, with a six-month extension available. Required even if no tax is due.',
         'Whether it is required depends on the whole estate, which is currently unknown.',
         'form706'),
        ('Year 1-3', 'File the intergenerational exclusion claim',
         'Form BOE-19-P to the assessor, within three years, and before any transfer to a third party.',
         'Filing late is better than not filing, but the benefit starts later.',
         'pub801'),
        ('Year 1', 'Insurance, utilities and the first full year of bills',
         'Open the policies, transfer the accounts, and collect twelve months of bills.',
         'This is when the cost estimates on this site can be replaced with facts.',
         'cdi cpucnem'),
        ('Year 1-3', 'If selling: list, sell and reinvest',
         'A sale soon after the appraisal minimises the taxable gain, because the basis is the date of death value.',
         'Selling later means the gain is measured from the death value, not from the sale date.',
         'basis capgains'),
        ('Year 3+', 'If holding: annual review',
         'Re-check the exclusion conditions, the rent ceiling, the insurance and the assessment.',
         'A move-out, a tenancy change or a law change can each undo the plan.',
         'lta26026 ab1482'),
        ('Year 10-20', 'If still holding: the reversal condition',
         'Re-run this analysis at each transfer-date anniversary against the written fallback plan.',
         'A plan without a review date is a hope.',
         'stocks'),
    ]
    return callout('This is the process, with the clocks that carry penalties',
        'Four statutory clocks matter and each one costs money if it is missed: 60 days for the trustee notification, '
        '150 days for the death-transfer statement, 9 months for a federal estate return, 1 year for the homeowners '
        'exemption and 3 years for the exclusion claim. Only the last two carry a benefit, and only if they are filed. '
        'Nothing in this table is legal advice for a particular trust; the trustee and a lawyer have to apply it.', 'warning') + table(
        'Inheritance, step by step', ['When', 'What happens', 'The rule', 'Why it matters'], [
        ([w, t, r, why], 'Guidance', src) for w, t, r, why, src in steps])


def page_law():
    return table('Current law, and what is only proposed', ['Topic', 'Status today', 'What is proposed or pending', 'Effect on this decision'], [
        (['Statewide rent ceiling',
          'Five percent plus the change in the cost of living, capped at ten percent. The statute expires on 1 January 2030.',
          'No replacement is law. Local ordinances continue and some are tighter.',
          'Renting A gets worse if a tighter cap replaces it, so this does not change the recommendation.'], V, 'ab1482'),
        (['Local rent increase, current period',
          '1.6% for 1 March 2026 to 28 February 2027 for covered units, with security deposit interest at 4.2%.',
          'A board of supervisors file would cap combined banked and capital improvement increases at ten percent a year. It is expressly not enacted.',
          'Caps the upside of renting B, and of renting A if covered.'], V, 'sfrates'),
        (['Family-home transfer exclusion',
          'Available to an eligible child who occupies the home, with a value allowance adjusted every second February.',
          'No repeal is pending. The provision replaced an earlier one in 2021, so it has changed before.',
          'This is the benefit that makes occupancy the recommendation.'], V, 'pub19 pub801 lta25009'),
        (['Federal estate exclusion',
          M(P['exclusion_2027']) + ' for deaths in 2027, indexed annually.',
          'Indexed by formula. A reduction would require legislation.',
          'Determines whether the estate has a federal problem at all.'], V, 'irs2027'),
        (['Step-up in basis at death',
          'Generally fair market value at death becomes the heir\'s basis.',
          'A repeal bill was introduced in the 119th Congress and referred to committee. It is not law.',
          'If repealed, an immediate sale would no longer be almost tax free.'], V, 'basis'),
        (['State personal property taxes',
          'Proposition 42 led 51.4% to 48.6% in the unofficial count as of 12 November 2026, to be certified by 11 December 2026.',
          'It constrains new state taxes on personal property such as financial assets. It does not touch real property tax.',
          'Relevant to the invested-proceeds path only in the very long run, and not yet certified.'], V, 'sos2026'),
        (['Solar export compensation',
          'Systems interconnected from 15 April 2023 take net billing, where export credits are usually below retail.',
          'Ongoing regulatory proceedings, and a nine-year legacy period for original customers.',
          'A small credit today is not a fifty-year credit. Do not capitalise it.'], V, 'cpucnem'),
        (['Insurance market',
          'The state insurer of last resort covers fire, lightning, explosion and smoke, with additional perils by endorsement, and does not cover liability or theft.',
          'Ongoing regulatory action on rates and coverage. No premium is published for any address.',
          'The single largest unpriced risk, and the one most likely to change the answer.'], V, 'cdi'),
        (['Long-run interest rates',
          'The official ten-year projection averages 4.3% for 2026 to 2036, with stress cases at 4.8% and 5.8%.',
          'No official fifty-year projection exists.',
          'Sets the bar the invested-proceeds path must clear, and the risk that it clears it by less than assumed.'], V, 'cbo'),
    ]) + callout('How to keep this page honest',
        'Check the primary source, not the summary, and check it on a date. A rule that was current when this page was '
        'built can change. The two items most likely to move are the rent ceiling, whose current statute expires in 2030, '
        'and the family-home exclusion, which has already been rewritten once. Neither is a reason to delay the decision; '
        'both are reasons to avoid a plan that only works under today\'s statute.')


def page_flagged():
    findings = [
        ('F01', 'Critical', 'The coordination file in this public repository already contains the two ZIP codes',
         'The published site contains no ZIP, city, street or parcel. The repository does not have that guarantee. '
         'The coordination log, which is a working document shared between sessions and is excluded from the published '
         'site, records both ZIP codes, the county where each property sits, and the exact federal rent benchmarks for '
         'those ZIPs. Those lines were written by earlier sessions as research notes. They are in the current tree and '
         'in the commit history, so deleting them now would not remove them from earlier commits, forks or caches.',
         'Decide the repository audience first. If it must stay public, stop writing geography into the coordination log, '
         'and treat every figure already there as disclosed. Removing it from history is a force-push that rewrites shared '
         'commits, so it needs the owner decision and the other sessions agreement, not a unilateral edit.',
         'Missing', 'sco'),
        ('F02', 'Critical', 'Rounding to ten dollars is not anonymisation',
         'A property value, an assessed value and a tax bill published together can fingerprint a specific parcel even '
         'when each figure is rounded. Nothing published here includes a name, street address, ZIP code, parcel number, '
         'account number or permit number, but the combination of figures is still identifying to someone who already '
         'has a candidate list.',
         'If the combination matters, publish ranges or index values instead of dollars. This was offered as a choice, not '
         'imposed, because the brief asked for clear numbers.',
         'Guidance', 'pub29'),
        ('F03', 'High', 'The 2026 assessed value for Property B is inferred, not supplied',
         'The owner supplied history stops at 2025. The 2026 figure shown on this site is the 2025 figure times the 1.02 '
         'cap, rounded. It is a projection and is labelled as one wherever it appears.',
         'Replace it with the actual 2026 roll value when it arrives.',
         'Projection', 'lta26002'),
        ('F04', 'High', 'Property A has no tax bill for 2026 in the supplied data',
         'The history shows an assessment but no bill for the current year. No figure was invented to fill it.',
         'Obtain the current bill. The gap is visible on the property tax page rather than hidden.',
         'Missing', 'pub29'),
        ('F05', 'High', 'No insurance premium has been verified for either property',
         'The owner estimate of $1,500 a year appears throughout the brief as an owner figure. No policy, quote or '
         'declaration page has been read by this session, and the state regulator publishes no premium.',
         'Obtain three quotes per intended use. Above about $12,000 a year the recommendation changes.',
         'Missing', 'cdi'),
        ('F06', 'High', 'The rent assumption for Property A is an invention',
         'A gross yield assumption is not a rent. No listing, appraisal or rent survey was read. The rent that would make '
         'renting competitive is well above the assumption, and whether that rent is achievable is unknown.',
         'Obtain three written rental opinions before treating the rental path as closed.',
         'Assumption', 'rental ab1482'),
        ('F07', 'Medium', 'A 41% decline and a 12.8-year recovery appear on the stress page',
         'These are measured from the official California index, which is a state average, not this or any parcel. A '
         'single home can fall further or recover faster.',
         'Read them as a scale of risk, not as a forecast for this property.',
         'Verified', 'fhfa'),
        ('F08', 'Medium', 'The family-home allowance after 2027 is assumed, not published',
         'The statute adjusts the allowance every second February 16 to the federal California house price index. The '
         'published amount covers transfers to 15 February 2027. Projections after that multiply it by an assumed growth rate.',
         'Re-read the published amount before relying on any post-2027 figure, and never use the rounded display on a form.',
         'Assumption', 'lta25009 pub801'),
        ('F09', 'Medium', 'The 2026 statewide ballot measure results are unofficial',
         'The Secretary of State reports results as of 12 November 2026, with certification due by 11 December 2026. Any '
         'measure described as passed could still change in the count.',
         'Re-check after certification before relying on the outcome.',
         'Guidance', 'sos2026'),
        ('F10', 'Medium', 'Three official sources could not be read and are not cited numerically',
         'The federal housing rent summary rendered empty, the Census rent query needed a key, and a state insurance guide '
         'returned a not-found page. None was replaced with a secondary source.',
         'The affected cells are blank. See the failed-retrieval list on the sources page.',
         'Missing', 'fhfa cdi'),
        ('F11', 'Medium', 'Every projection is debt free because no debt is known',
         'A mortgage, reverse mortgage or lien on either property would change the proceeds and could force a sale. None '
         'has been ruled out.',
         'Obtain a title report for each property.',
         'Missing', 'estate'),
        ('F12', 'Low', 'The recommendations are conditional on a household risk preference that is not known',
         'A higher risk tolerance favours investing the proceeds; a lower one favours occupancy and a reserve. The brief '
         'states a goal of maximising profit and lowering costs, which is not the same as a stated tolerance for loss.',
         'Write the tolerance down before choosing, because it is the one input that cannot be researched.',
         'Missing', 'stocks'),
        ('F13', 'Low', 'Two rounding conventions are used deliberately',
         'All display money rounds half up to ten dollars. Percentages are shown to one or two decimals and are not '
         'rounded to ten. Internal arithmetic keeps full precision, so totals can differ from the sum of rounded lines by '
         'one line.',
         'Read a total from its own cell, not by adding a column by hand.',
         'Guidance', 'pub29'),
        ('F14', 'Low', 'The property tax rate used is your own effective rate, not a statutory rate',
         'The 1% levy is a statutory rate. The remainder, about a third of A\'s bill and half of B\'s, is local debt and '
         'direct assessments that can change by local vote.',
         'Re-derive the rate from the actual bill each year.',
         'Owner', 'pub29'),
    ]
    return callout('This page is the honest inventory of what is weak in this brief',
        'Nothing below blocks the recommendation, because the recommendation does not depend on the items that are '
        'missing. It does depend on the trust allowing occupancy, on insurance being available at a sane price and on the '
        'family-home exclusion surviving. If any of those three fails, read the executive summary again: the fallback is '
        'a sale, not a rental.', 'warning') + table(
        'Flagged for review', ['ID', 'Severity', 'Finding', 'What it means', 'What to do about it'], [
        ([i, s, t, m, w], st, src) for i, s, t, m, w, st, src in findings])


def page_sources():
    rows = []
    for key, (label, url, passage, scope, chunk) in SOURCES.items():
        rows.append(([f'<a href="{E(url, quote=True)}" rel="noopener noreferrer">{E(label)}</a>',
                      f'<span class="quote">{E(passage[:160])}{"..." if len(passage) > 160 else ""}</span>',
                      E(scope), chunk], 'Verified', key))
    out = callout('Every source below was fetched and read by this session on ' + DATE,
        'The quoted passage is what the page actually said, trimmed for length. The scope column states what the source '
        'does and does not establish, which is the part that prevents a link from being mistaken for a fact. Where a page '
        'could not be read, it is listed as a failed retrieval instead of being cited.', 'info')
    out += table('Official source ledger', ['Source', 'Passage as published', 'What it establishes and what it does not', 'Chunk'], rows,
                 'All sources are on official domains. A link verifies the rule, never a private fact about these properties.')
    out += table('Failed retrievals, recorded rather than substituted', ['Attempt', 'What happened'], [
        ([a, b], 'Missing', 'fhfa cdi') for a, b in FAILED])
    return out


def page_privacy():
    return callout('What was done to protect identity, and what was not',
        'No person, street address, ZIP code, parcel number, account number or permit number appears anywhere in this '
        'site. No private lookup was performed: this session did not search for an owner, an address or a parcel record. '
        'Every dollar figure is rounded half-up to the nearest ten dollars before it is used in any calculation, so a '
        'published number cannot be worked back to an exact bill. Property names are labels, A and B. That is the whole '
        'of the protection, and it should be understood for exactly what it is.', 'warning') + table(
        'Privacy safeguards and the limits of each', ['Area', 'What is protected', 'What is still exposed'], [
        (['Identity', 'No name, address, ZIP or parcel identifier, account or permit number is published. Properties are called A and B.',
          'A reader who already knows the household can infer which properties these are. Anonymisation protects against strangers, not against people who know you.'], V, 'sco'),
        (['Amounts', 'Every dollar figure rounded to ten dollars before use, in both directions and in every projection.',
          'Rounding is not anonymisation. A value, an assessment and a bill together can fingerprint a parcel.'], V, 'pub29'),
        (['Combinations', 'The brief avoids publishing a full tax history in one place where it could be matched to a public roll.',
          'The property tax page does show year-by-year assessed values. That is a deliberate trade-off of clarity for exposure.'], O, 'pub29'),
        (['Repository', 'The published site is generated from the rounded figures only.',
          'The repository holding this site is public. Earlier commits, pull request diffs, forks and caches can retain anything that was ever committed.'], Ms, 'sco'),
        (['Browser', 'No analytics, no third-party fonts, no remote scripts, no network calls, no cookies set by the application.',
          'The hosting provider may log requests. Review preferences are stored only in this browser and are never transmitted.'], V, 'stocks'),
        (['Documents', 'No document was requested, uploaded or committed.',
          'Deeds, trust instruments, bills, appraisals and statements should never be committed to this repository, not even temporarily.'], Ms, 'sco'),
    ]) + callout('The remediation that only the owner can authorise',
        'If the exposure of earlier commits matters, the options are: make the repository private, rewrite history and '
        'force-push, or start a clean repository and archive the old one. Each has a cost. A history rewrite invalidates '
        'every clone, every fork and every open pull request, and it cannot reach copies that have already been made. '
        'This session did none of those things, because they are not reversible and they affect other work.') + table(
        'The numbers that are rounded, and how', ['Convention', 'Rule', 'Where it shows'], [
        (['Display money', 'Half-up to the nearest ten dollars, so 125 becomes 130 and 124.99 becomes 120.', 'Every dollar cell on every page and in the CSV.'], V, 'pub29'),
        (['Inputs', 'The owner figures were rounded before any arithmetic was run, not after.', 'The projection engine reads only the rounded values.'], V, 'pub29'),
        (['Official amounts', 'Statutory figures are shown rounded for display and quoted exactly in the scope column.', 'The $1,044,586 allowance appears as $1,044,590 with the exact figure stated.'], V, 'lta25009'),
        (['Percentages', 'Shown to one or two decimals and not rounded to ten.', 'Rates, growth and impliede returns.'], V, 'pub29'),
        (['Totals', 'Computed from full precision, then rounded, so a column may not add exactly by hand.', 'Every total row.'], V, 'pub29'),
    ])
