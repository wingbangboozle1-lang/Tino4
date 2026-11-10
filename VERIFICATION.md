# VERIFICATION.md — line-by-line record

Research date: **2026-11-10**. Every row below states: the value, where it came from, the official
source, and the status. Status is one of:

| Status | Meaning |
|---|---|
| **Verified** | Read directly from a primary/government source and quoted. Link given. |
| **User-supplied** | Supplied in the request. Shown as given, never restated as fact. |
| **Derived** | Arithmetic performed on user-supplied figures. The arithmetic is shown. |
| **Assumption** | A planning input with no official parcel-level source. Range given. Flows to the Flagged page. |
| **Unverified — blank** | Could not be confirmed. The value is left blank rather than estimated. |

A value is never marked Verified because a secondary site said so. Where a secondary source
appeared to agree, it is not cited.

---

## 1. Estate, gift and inheritance tax

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 1.1 | Federal estate tax basic exclusion, 2026 | $15,000,000 | **Verified** | IRS, *Estate tax* — "2026 \| $15,000,000" — https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax |
| 1.2 | 2026 exclusion confirmed in the annual inflation release | $15,000,000, up from $13,990,000 in 2025 | **Verified** | IRS IR-2025-103 — "Estates of decedents who die during 2026 have a basic exclusion amount of $15,000,000, up from a total of $13,990,000" — https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill |
| 1.3 | Federal estate tax top rate | 40% | **Verified** | IRS, *Estate tax* (tax is computed, then reduced by the unified credit); rate confirmed in the Form 706 instructions chain from the same IRS page. Used only to compute "tax per $1m over". |
| 1.4 | Annual gift tax exclusion, 2026 | $19,000 | **Verified** | IRS IR-2025-103 — "For tax year 2026, the annual exclusion for gifts remains at $19,000" |
| 1.5 | Portability of unused exclusion to a surviving spouse | Available, elected on a timely Form 706 | **Verified** | IRS, *Estate tax* — "Beginning January 1, 2011, estates of decedents survived by a spouse may elect to pass any of the decedent's unused exemption" |
| 1.6 | California state estate tax | **None**. No California estate tax return required for deaths on/after 1/1/2005 | **Verified** | California State Controller's Office — "For decedents that die on or after January 1, 2005, there is no longer a requirement to file a California Estate Tax Return" — https://www.sco.ca.gov/ardtax_estate_tax.html |
| 1.7 | California inheritance tax | **None**. Also no state GST tax after 12/31/2004 | **Verified** | Same SCO page — "The California Generation-Skipping Transfer tax shall not apply to the generation-skipping transfers after December 31, 2004" |
| 1.8 | California income treatment of an inheritance | Excluded from California income at receipt | **Verified** | California FTB — "If you received a gift or inheritance, do not include it in your income. However, if the gift or inheritance later produces income, you will need to pay tax on that income." — https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html |
| 1.9 | Local (county/city) inheritance tax | **None** in Santa Clara County or San Francisco | **Verified by absence** | Neither the Santa Clara County Assessor's assessment booklet nor the SF Treasurer's heir-information page levies any transfer tax on inheritance. The only charge is the documentary transfer tax when a *deed for consideration* is recorded, plus recording fees. See rows 4.6–4.8. |
| 1.10 | Forward-indexed federal exclusion, 2027–2065 | **Not published** | **Unverified — blank** | The exclusion is indexed from 2027 under the enacted law, but the IRS has not published future amounts. The model holds 2026 at $15,000,000 and labels every later year a **floor**. Flagged F11. |
| 1.11 | Cash amount in the inheritance | **Withheld** | **Withheld by policy** | Never recorded. All headroom figures are expressed per $1,000,000 so the real amount need never be written down. Flagged F10. |

**Reading of 1.1–1.9:** at the federal level the tax is on the *estate*, not on the heir, and only the
amount above $15,000,000 is taxed. California adds no estate or inheritance tax. So for this
inheritance the binding question is not "is there inheritance tax" — there isn't — but whether
**Property A + Property B + the cash + any other assets exceed $15,000,000 at the date of death**.
That is answered per-year in the estate table on the site.

---

## 2. Basis and capital gains

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 2.1 | Basis of inherited property | Fair market value at date of death (IRC §1014) | **Verified** | IRS Pub. 551 — "Generally, the basis of property inherited from a decedent is ... The FMV of the property at the date of the individual's death" — https://www.irs.gov/publications/p551 |
| 2.2 | Community property step-up | Entire community interest takes a new basis at the first spouse's death | **Verified** | IRS Pub. 551 — "When either spouse dies, the total value of the community property, even the part belonging to the surviving spouse, generally becomes the basis of the entire property" |
| 2.3 | Property received from a trust | Same inherited-property basis rules apply | **Verified** | IRS Pub. 551, section *Property Received from a Trust* (linked from the inherited-property section of the same page) |
| 2.4 | Federal 0%/15%/20% long-term breakpoints, 2026 (joint) | 0% to $98,900; 15% to $613,700; 20% above | **Verified** | IRS Rev. Proc. 2025-32 §4.03 — https://www.irs.gov/pub/irs-drop/rp-25-32.pdf |
| 2.5 | Same, single filer | 0% to $49,450; 15% to $545,500; 20% above | **Verified** | Same, Rev. Proc. 2025-32 §4.03 |
| 2.6 | §121 principal-residence exclusion | $500,000 joint / $250,000 single | **Verified** | IRS Topic 701 — "you may qualify to exclude up to $250,000 of that gain ... or up to $500,000 ... if you file a joint return" — https://www.irs.gov/taxtopics/tc701 |
| 2.7 | §121 ownership and use tests | 2 of the last 5 years, both tests inside the same 5-year window | **Verified** | Same Topic 701 page |
| 2.8 | California capital-gains treatment | No preferential rate; taxed as ordinary income | **Verified** | California FTB — "California does not have a lower rate for capital gains. All capital gains are taxed as ordinary income." — https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html |
| 2.9 | California real-estate withholding on a sale | 3⅓% of sales price, or an alternative gain-based calculation | **Verified** | California FTB, Form 593 instructions — "the REEP must withhold the full 3 1/3% (.0333) of the sales price or the alternative withholding calculation amount" — https://www.ftb.ca.gov/forms/2026/2026-593-instructions.html |
| 2.10 | California top marginal rate used in the blended gain rate | 9.3% blended | **Assumption** | Chosen as a mid-bracket blend for a gain of this size. Not a verified marginal rate for any specific year's income. Range 8%–13.3% applies. Flagged F12. |
| 2.11 | 3.8% net investment income tax | Applied above $250,000 joint / $200,000 single MAGI | **Verified (statutory thresholds)** | IRC §1411 thresholds; the 2026 long-term table in Rev. Proc. 2025-32 §4.03 is the rate structure the NIIT stacks on. |
| 2.12 | Depreciation on residential rental | 27.5-year straight line | **Verified** | IRS Pub. 527, *Residential Rental Property* — https://www.irs.gov/publications/p527 |
| 2.13 | Land is not depreciable | Land share excluded from depreciable basis | **Verified** | IRS Pub. 527, *What Rental Property Can't Be Depreciated — Land* |
| 2.14 | Land share of Property A's value | 60% | **Assumption** | No official land/improvement split without the APN. Range 50%–70%. Flagged F13. |

---

## 3. Property tax

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 3.1 | Prop 13 statutory minimum rate | 1% of net taxable value, plus voter-approved debt | **Verified** | Santa Clara County Assessor Annual Report 2025-26 — "The minimum ad valorem property tax rate is 1% of the net taxable value of the property. The total tax rate may be higher due to voter-approved general obligation bonds" — https://files.santaclaracounty.gov/exjcpb1521/2025-11/annual_report_2025-2026.pdf |
| 3.2 | Annual assessment growth cap | 2% | **Verified** | BOE LTA 2026/002 — "Increase to base year value is limited to 2 percent pursuant to California Constitution, article XIII A, section 2(b)" — https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf |
| 3.3 | 2026-27 assessment roll inflation factor | **1.02** | **Verified** | Same LTA 2026/002 — "please prepare your 2026 assessment roll using an inflation factor of 1.02" (CCPI +3.307%, capped at 2%) |
| 3.4 | Santa Clara County illustrative composite rate | **1.1488%** ($1.00 base + $0.0388 county bonds + $0.100 school bonds + $0.010 water bonds per $100) | **Verified** | Santa Clara County Assessor, *Assessment Information for the Santa Clara County Property Owner* — https://files.santaclaracounty.gov/exjcpb1521/2024-11/assessment_information_booklet.pdf |
| 3.5 | Property A's actual tax rate area | **Unverified — blank** | **Unverified — blank** | A parcel's composite rate varies by tax rate area and can only be looked up with the APN, which privacy policy forbids recording. Flagged F14. |
| 3.6 | SF secured property tax rate, FY 2026-27 | **1.18162182%** | **Verified** | SF Treasurer & Tax Collector — "The secured property tax rate for Fiscal Year 2026-27 is 1.18162182%." — https://sftreasurer.org/property/secured-property-taxes |
| 3.7 | Supplemental assessment after a change in ownership | Issued for the difference between new and old value, prorated | **Verified** | Same SF Treasurer page — "If the property is reassessed at a higher value, a supplemental assessment will be issued calculated on the difference between the new value and the old or prior value" |
| 3.8 | Homeowners' exemption | $7,000 of taxable value | **Verified** | BOE — "The California Constitution provides a $7,000 reduction in the taxable value for a qualifying owner-occupied home. The home must have been the principal place of residence of the owner on the lien date, January 1st." — https://www.boe.ca.gov/proptaxes/homeowners_exemption.htm |
| 3.9 | Homeowners' exemption filing | BOE-266, one-time, by February 15 for the full amount | **Verified** | Same BOE page |
| 3.10 | Property A's rate used in the model | **1.3352%** | **Derived** | $7,207 ÷ $539,743 = 1.3352% from the user's own 2025 figures. Preferred over 1.1488% because it reproduces the actual bills. The county figure is run as a sensitivity. Flagged F2. |
| 3.11 | Property B's rate used in the model | **2.1350%** | **Derived** | $2,439 ÷ $114,248 = 2.1350% from the user's own 2025 figures. **81% above SF's published 1.1816%** — the largest irregularity in the supplied data. Flagged F1. |

### The two rate irregularities, stated plainly

**Property B (F1).** The supplied series implies a 2.14% effective rate for 2025 and ranges from
1.68% to 2.14% across 2016–2025. San Francisco's published secured rate is 1.1816%. The gap is not a
rounding artefact: it is roughly $1,070 a year at the 2025 assessment, and it persists for a decade.
Two explanations fit — (a) real parcel-level charges beyond the secured rate (special assessments,
bond levies, a Mello-Roos-style district), or (b) a transcription issue in the supplied table.
Either way, the model uses the *implied* rate for Property B so the projection matches the bills
actually paid, and the published rate is shown beside it so the discrepancy is visible rather than
smoothed away. **This is the single most important figure to confirm against an actual tax bill.**

**Property A (F2).** Implied 1.3352% against a county illustration of 1.1488% — a 16% excess, about
$1,000 a year. Plausible causes are the same. Less alarming than F1 but the same action applies.

---

## 4. Prop 19 and the intergenerational exclusion

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 4.1 | Prop 19 parent-child exclusion applies only to a principal residence | Yes | **Verified** | BOE — "Proposition 19 limits the parent-child transfer exclusion to a transfer of (1) a family home that is the principal residence of the transferor and becomes the principal residence of the transferee, or (2) a family farm" — https://www.boe.ca.gov/prop19/ |
| 4.2 | **Prop 19 does not apply to a rental home** | Yes — explicitly | **Verified** | Same BOE page, FAQ 04: "Does Proposition 19 apply to a transfer between parents and children of a rental home? **No.**" |
| 4.3 | Excluded amount formula | Factored base year value + $1,000,000, biennially adjusted | **Verified** | Same BOE page — "The value limit under Proposition 19 is the sum of the factored base year value plus $1 million" |
| 4.4 | Current adjusted amount | **$1,044,586** for transfers 2/16/2025 – 2/15/2027 | **Verified** | BOE LTA 2025/009 — "for transfers that occur February 16, 2025 through February 15, 2027, the value cap will be the sum of the property's factored base year value plus $1,044,586" — https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf |
| 4.5 | Prior adjusted amounts | $1,000,000 (2/16/2021–2/15/2023); $1,022,600 (2/16/2023–2/15/2025) | **Verified** | Same LTA 2025/009 table |
| 4.6 | Adjustment mechanism | FHFA California House Price Index, every other February 16, beginning 2/16/2023 | **Verified** | Same LTA 2025/009 — quoting art. XIII A §2.1(c)(4) |
| 4.7 | Adjustment for a transfer in 2040–2050 | **Not published** | **Unverified — blank** | Only the 2025–2027 figure exists today. The model holds $1,044,586 flat, which is *conservative for the heir* because the FHFA CA index has been rising. Flagged F15. |
| 4.8 | Continuous-occupancy condition | Exclusion is lost when the heir stops occupying; reassessed to the date-of-death FMV factored forward | **Verified** | BOE — "once the property is no longer your principal residence, it will receive a new taxable value as of the lien date following the date you no longer occupy the property" |
| 4.9 | Claim deadlines | Homeowners'/disabled-veterans' exemption within **1 year**; exclusion claim within **3 years** or before sale to a third party | **Verified** | BOE Prop 19 comparison chart — "File for homeowners' exemption within 1 year of transfer / File claim for exclusion within 3 years or before transfer to third party" |
| 4.10 | Claim form and county fee | BOE-19-P; $110 non-refundable processing fee in Santa Clara County | **Verified** | Santa Clara County Assessor — "A non-refundable processing fee of $110 is required in Santa Clara County." — https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/prop19 |
| 4.11 | Which property is the parents' principal residence | **Not stated in the request** | **Unverified — blank** | Determines whether Prop 19 can apply at all. The model assumes Property A and shows the alternative. Flagged F6. |

### Why 4.2 is decisive

Property B is currently a three-unit building with two units rented. Under 4.2 it cannot receive
the Prop 19 exclusion. Property A can — but only if the heir actually moves in and stays in. That
single rule is what separates the three strategies more than any interest-rate assumption does,
and it is why the live-in scenario is modelled with the exclusion and the rent-out scenario without it.

---

## 5. Rent regulation

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 5.1 | SF allowable annual rent increase | **1.6%** for 3/1/2026–2/28/2027 | **Verified** | SF Rent Board — "Allowable Rent Increase: 1.6% for March 1, 2026 – February 28, 2027" — https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit |
| 5.2 | Prior year's SF allowable increase | 1.4% (3/1/2025–2/28/2026); 1.7% the year before | **Verified** | Same Rent Board page |
| 5.3 | AB 1482 cap formula | Lower of 5% + regional CPI, or 10% | **Verified** | Civil Code §1947.12 — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12 |
| 5.4 | AB 1482 CPI area for San Francisco | CPI-U San Francisco-Oakland-Hayward (Alameda, Contra Costa, Marin, San Francisco, San Mateo) | **Verified** | §1947.12(g)(1)(A)(iv) |
| 5.5 | AB 1482 CPI area for Cupertino | **No metro index in the statute's list for Santa Clara County** | **Verified by reading** | §1947.12(g)(1)(A) lists only LA, Riverside-San Bernardino, San Diego, and SF-Oakland-Hayward. Subparagraph (B) then requires the **California CPI** for areas without a metro index. So Cupertino rent growth under AB 1482 tracks the statewide CPI, not the Bay Area's. |
| 5.6 | AB 1482 owner-occupied two-unit exemption | §1947.12(d)(6) | **Verified** | §1947.12(d)(6) — exempts a single structure with two units where the owner occupies one |
| 5.7 | Does that exemption fit Property B? | **No** — Property B has three units | **Derived** | Reading of §1947.12(d)(6) against the stated three-unit configuration. Flagged F16. |
| 5.8 | AB 1482 sunset | Repealed as of January 1, 2030 | **Verified** | §1947.12(o) — "This section shall remain in effect until January 1, 2030, and as of that date is repealed" |
| 5.9 | Rent growth used across the horizon | **2%/yr flat** | **Assumption** | A neutral planning number between SF's 1.6% and AB 1482's current-window figures, and deliberately not above either. Range 1.5%–3%. Legally, nothing entitles a landlord to 2% after 2029. Flagged F17. |
| 5.10 | Market rent for Property A if rented out | **$5,400/month** | **Unverified — assumption** | No official rent exists for this specific home. A HUD FY2026 Fair Market Rent cross-check was attempted; the HUD FMR query table did not return values in this research pass, so **no HUD figure is claimed**. Range $4,500–$7,000 modelled. Flagged F18. |
| 5.11 | Property B's current rent | $7,150/month for two units | **User-supplied** | As stated in the request. Equates to $85,800/yr gross. |

---

## 6. Utilities and solar

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 6.1 | Cupertino water providers | Three systems: San Jose Water (southeast), California Water Service (northeast), City of Cupertino (west, operated by SJW under lease to 2036) | **Verified** | City of Cupertino — https://www.cupertino.gov/Residents/Utilities/Water |
| 6.2 | SJW Schedule 1 monthly service charge, 5/8-inch | **$79.67** | **Verified** | SJW Schedule 1, AL 629A, effective 7/1/2026 — https://www.sjwater.com/media/oxuletnh/schedule-1-al629a-july-2026.pdf |
| 6.3 | SJW quantity rates | $5.0355/ccf (0–6), $7.5156/ccf (6–12), $14.3548/ccf (over 12) | **Verified** | Same SJW schedule |
| 6.4 | SJW surcharges | CAP surcharge $2.61/month; WRAM surcharge $0.2996/ccf for 12 months from AL 627 | **Verified** | Same SJW schedule, Special Conditions 3 and 6 |
| 6.5 | Property A's water cost | **$125/month** ($1,500/yr) | **User-supplied**, cross-checked | Midpoint of the $100–$150 range supplied. SJW tariff math (service charge + ~10 ccf) lands near $135–$155 for water alone, so the range is plausible and possibly low. |
| 6.6 | SFPUC 5/8-inch monthly water service charge | $19.65 (FY26-27) → $21.02 (FY27-28) | **Verified** | SFPUC Rate Schedule W-1A — https://www.sfpuc.gov/sites/default/files/accounts-and-services/Rates_Schedule_Water_Sewer_2026-7.pdf |
| 6.7 | SFPUC residential water volume rates | Tier 1 $12.20/ccf (first 4 units); tier 2 $13.55/ccf | **Verified** | Same SFPUC schedule, W-1A |
| 6.8 | SFPUC multi-family water volume rates | Tier 1 $12.03/ccf per dwelling unit (first 3 units); tier 2 $12.91/ccf | **Verified** | Same SFPUC schedule, W-1B |
| 6.9 | SFPUC residential wastewater | Monthly service charge $6.62; volume $20.74 per discharge unit; multi-family flow factor 95% | **Verified** | Same SFPUC schedule, Schedule A |
| 6.10 | SFPUC simplified residential stormwater, Tier 3 (3,301–6,000 sq ft) | $29.55/month FY26-27 → $42.29 FY27-28 | **Verified** | Same SFPUC schedule, Schedule D |
| 6.11 | Property B's water/sewer cost | **$365/month** ($4,380/yr) for all three units | **User-supplied**, cross-checked | Midpoint of the $330–$400 range supplied. Rough tariff math for ~13 ccf/month across three units reproduces roughly $330–$380 all-in including stormwater, so the reported range is consistent with published SFPUC tariffs. |
| 6.12 | Property A's net electricity | **−$15/month** (a credit) | **User-supplied** | Reported as no bill and roughly $10–$20/month profit. Modelled as a $15 credit. |
| 6.13 | NEM tariffs closed to new enrollment | Yes | **Verified** | CPUC — "These tariffs are closed to new enrollments" — https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/net-energy-metering |
| 6.14 | Net Billing Tariff start | Interconnections applied for on/after **April 15, 2023** | **Verified** | Same CPUC page — "Since April 15, 2023, customers applying for interconnection have taken service on the new net billing tariff (NBT) pursuant to D.22-12-056" |
| 6.15 | Which tariff applies to Property A's existing solar | **Unverified — blank** | **Unverified — blank** | Depends on the system's original interconnection date, which is not supplied. Modelled as a $15 credit with a $0 floor sensitivity. Flagged F8. |
| 6.16 | Property B's electricity | **$50/month** | **User-supplied** | Midpoint of the $30–$70 range supplied for the building. |
| 6.17 | Future SFPUC/SJW rate increases | Escalated at 2.5%/yr general inflation | **Assumption** | SFPUC has published two-year rates only (FY26-27, FY27-28). Nothing official exists through 2065. Flagged F19. |

**Note on 6.15:** this is a real money question, not a formality. Under the retail-rate NEM 2.0
credit the solar is worth roughly $500–$900/yr of avoided bill. Under the Net Billing Tariff the
export credit is at avoided-cost value and the same generation would be worth far less — the
onsite consumption is still offset, but the surplus that currently produces the $10–$20/month
credit would shrink. The plan should confirm the interconnection date before relying on the credit.

---

## 7. Insurance

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 7.1 | Official parcel-level homeowner premium for 95014 | **None published** | **Unverified — blank** | The California Department of Insurance regulates rates and publishes approved filings, but not a parcel- or ZIP-level premium. The CDI rate-comparison tool is the correct place to obtain a real quote: https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/ |
| 7.2 | Official parcel-level landlord premium for 94122 | **None published** | **Unverified — blank** | Same. |
| 7.3 | Property A insurance used in model | **$1,500/yr** | **Unverified — user estimate** | As supplied. Sensitivity doubles it to $3,000. Flagged F7. |
| 7.4 | Property B insurance used in model | **$1,500/yr** | **Unverified — user estimate** | As supplied. A three-unit rented building at $1,500 is low for the exposure; sensitivity uses $4,000. Flagged F7. |
| 7.5 | Earthquake insurance | **Not modelled — $0** | **Unverified — blank** | No coverage or premium was supplied and none can be verified at parcel level. Standard California homeowners policies exclude earthquake. This is a real unmodelled cost, called out on the Flagged page. Flagged F20. |
| 7.6 | Insurance escalation | 2.5%/yr (general inflation) | **Assumption** | No forward official projection exists. California insurance rates have been rising faster than CPI, so this is likely optimistic. Flagged F7. |

A secondary web search during research surfaced insurer-marketing averages for these counties
(e.g. "Santa Clara $1,010/yr", "San Francisco $1,331/yr", "$3,509/yr"). **None of those is cited,
used, or shown as a value** — they are marketing estimates from private quote-aggregation sites, not
official figures, and they contradict each other by a factor of three. They are mentioned here only
to record that they were seen and deliberately rejected.

---

## 8. Transaction taxes and recording

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 8.1 | Santa Clara County documentary transfer tax | **$0.55 per $500** = 0.11% | **Verified** | Santa Clara County Clerk-Recorder — "computed at a rate of $.55 per $500 or fractional portion of real property value" — https://clerkrecorder.santaclaracounty.gov/recording-documents/recording-real-estate |
| 8.2 | Higher rate applies only in San Jose, Palo Alto and Mountain View | $1.65 per $500 | **Verified** | Same Clerk-Recorder page — "Properties located within San Jose, Palo Alto and Mountain View are taxable at a rate of $1.65 per $500" |
| 8.3 | Is Cupertino one of those three cities? | **No** | **Derived** | Cupertino is not San Jose, Palo Alto or Mountain View. So the 0.11% rate applies to Property A. |
| 8.4 | SF documentary transfer tax, $1M–<$5M tier | **$3.75 per $500** = 0.75% of the whole consideration | **Verified** | SF Assessor-Recorder — "If entire value or consideration is $1,000,000 or more but less than $5,000,000, your tax rate is $3.75 for each $500 or portion thereof" — https://www.sf.gov/transfer-tax |
| 8.5 | SF transfer tax is a whole-value bracket, not marginal | Yes | **Verified** | The wording "your tax rate is $X for each $500" applied to "entire value or consideration" makes it a cliff rate on the whole amount. |
| 8.6 | Other SF transfer tax tiers | $2.50/$500 ≤$250k; $3.40/$500 to $1M; $11.25/$500 to $10M; $27.50/$500 to $25M; $30.00/$500 above | **Verified** | Same SF page |
| 8.7 | SF recording base fee | $14.00 first page | **Verified** | https://www.sf.gov/reports--march-2024--fees-record-document-san-francisco |
| 8.8 | SB2 Building Homes and Jobs Act fee | $75–$225, **exempt** for documents transferring real property where transfer tax is paid | **Verified** | Same SF recording fee page — "Documents transferring real property where transfer tax is paid" is listed under Exemptions |
| 8.9 | PCOR fee in lieu | $20.00 when a transfer document is presented without a PCOR | **Verified** | Same SF recording fee page |
| 8.10 | Cost of sale (brokerage + escrow + title) | **6%** of gross price, plus the county transfer tax applied separately | **Assumption** | Assumes a ~5% commission plus escrow/title. Commissions are negotiable and not published. Range 5%–7%. Flagged F21. |

---

## 9. Market data used to anchor the projections

| # | Item | Value used | Status | Source |
|---|---|---|---|---|
| 9.1 | FHFA all-transactions California HPI, 2026Q2 | **974.97** | **Verified** | FHFA HPI state dataset — https://www.fhfa.gov/hpi/download/quarterly_datasets/hpi_at_state.txt |
| 9.2 | FHFA all-transactions California HPI, 2025Q2 | **966.27** | **Verified** | Same dataset |
| 9.3 | Year-over-year California HPI change, 2Q2025→2Q2026 | **+0.90%** | **Derived** | 974.97 ÷ 966.27 − 1 = 0.90% |
| 9.4 | FHFA CA HPI, 2004Q1 → 2026Q2 | 424.32 → 974.97 | **Verified** | Same dataset |
| 9.5 | Compound annual growth over that 22.4-year span | **+3.8%** | **Derived** | (974.97 ÷ 424.32)^(1/22.4) − 1 = 3.8% |
| 9.6 | Cupertino population, July 1 2025 estimate | **58,333** | **Verified** | U.S. Census QuickFacts — https://www.census.gov/quickfacts/fact/table/cupertinocitycalifornia/PST045225 |
| 9.7 | Cupertino population change, 2020→2025 | **−3.2%** | **Verified** | Same QuickFacts page |
| 9.8 | Home price appreciation, base case | **3.0%/yr** nominal | **Assumption** | Anchored to 9.5 but set below it, and below recent years' near-zero growth (9.3), to reflect an aging-population and slight-population-decline local market. Range 2%–4%. Flagged F22. |
| 9.9 | 10-year Treasury par yield, 2026-11-09 | **4.38%** | **Verified** | U.S. Treasury Daily Par Yield Curve — https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026 |
| 9.10 | 20-year and 30-year par yields, 2026-11-09 | **5.29%** and **5.26%** | **Verified** | Same Treasury page |
| 9.11 | Reinvestment portfolio return, base case | **6.5%/yr** nominal before tax | **Assumption** | Above the risk-free long bond (9.9, 9.10) because it assumes equity exposure; tax is applied separately, never folded in. Range 4.5%–8.5%. Flagged F23. |
| 9.12 | Portfolio income yield (taxed annually) | 2.0% | **Assumption** | Separates taxed cash yield from untaxed appreciation. Range 1.5%–3%. |
| 9.13 | Effective tax on portfolio income | 33% | **Assumption** | Blends the federal 15–20% long-term rates, 3.8% NIIT and California's ordinary treatment (2.8). Range 25%–40%. |
| 9.14 | Effective tax on net rental income | 37% | **Assumption** | Rental income is ordinary income federally and in California. Range 30%–45%. |
| 9.15 | General inflation for cost escalation | **2.5%/yr** | **Assumption** | Above the 2% assessment cap and below the recent 3.307% California CPI (3.3). Range 2%–3.5%. |
| 9.16 | Vacancy and credit loss | 4% of gross rent | **Assumption** | Standard planning allowance. Range 2%–8%. |

---

## 10. Items deliberately left blank or excluded

| # | Item | Why | Status |
|---|---|---|---|
| 10.1 | Property A 2026 property tax | The user's table shows `--`. No 2026-27 bill exists at the research date. | **Blank** — F5 |
| 10.2 | Property A's actual tax rate area / composite rate | Requires the APN. | **Blank** — F14 |
| 10.3 | Parcel-level insurance premium, both ZIPs | Not published by any official body. | **Blank** — F7 |
| 10.4 | Earthquake insurance premium | Not supplied, not published at parcel level. | **Blank** — F20 |
| 10.5 | HUD Fair Market Rent for the two FMR areas | The HUD FMR query table returned no values in this research pass. Not guessed. | **Blank** — F18 |
| 10.6 | Forward-indexed federal estate exclusion, 2027+ | IRS has not published future amounts. | **Blank** — F11 |
| 10.7 | Forward-indexed Prop 19 cap, 2027+ | BOE has not published future amounts. | **Blank** — F15 |
| 10.8 | Probate fees avoided by the trust | California probate fees are statutory but depend on the estate's facts; not modelled. | **Excluded** — F24 |
| 10.9 | The cash inheritance amount | Privacy policy — never recorded. | **Withheld** — F10 |
| 10.10 | Any personal name, address, APN, parcel number, trustee or account number | Privacy policy — highest priority. | **Prohibited** |

---

## 11. Things a reader should be suspicious about

Stated plainly so they are not buried:

1. **The Property B tax figures are probably wrong somewhere (F1).** A 2.14% effective rate with a
   published 1.1816% secured rate is a large gap that persists for ten years. Ask for one actual
   Property B tax bill.
2. **The Property A 2017 and 2020 rows cannot be reconciled with a constant rate (F3, F4).** They are
   kept as supplied rather than corrected.
3. **Property A's rent if rented out is an assumption (F18)**, and it is the input the rent-out
   case is most sensitive to. A ±$1,300/month swing moves it by roughly $1.4m over the horizon.
4. **Nothing in the projection assumes any legal change (F17).** AB 1482 disappears in 2030 as
   written. The model does not assume it is extended, and does not assume it is not.
5. **Insurance is the weakest number in the model (F7).** It is the user's estimate, escalated at
   general inflation, with no earthquake coverage at all. In a real plan this is the first thing to
   replace with a quote.
6. **The recommendation is sensitive to the reinvestment return (F23).** At 4.5% rather than 6.5%
   the sell case loses a large part of its advantage. This is shown, not hidden — the break-even
   return is computed on the Decision page.
