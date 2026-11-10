# VERIFICATION.md — audit trail

Prepared 2026-11-10. Every row below was checked against the page linked in it. Nothing was inferred to
fill a gap: where no official source exists, the value is carried as owner-reported or flagged and is
published on `pages/flagged.html`.

## A. Sources opened and read

| ID | Source | What was read | Result |
|---|---|---|---|
| IRS-ESTATE | https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax | Filing threshold table by year of death | 2025 = $13,990,000; **2026 = $15,000,000** |
| IRS-RP2532 | https://www.irs.gov/pub/irs-drop/rp-25-32.pdf | §2.14 (exclusion), §4.01 (rate tables), §4.03 (capital gain breakpoints) | $15,000,000; 0%/15% breakpoints $98,900 and $613,700 MFJ |
| IRS-IR25103 | https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill | 2026 headline figures | Estate credit $15,000,000; marginal rates unchanged |
| IRS-I706 | https://www.irs.gov/instructions/i706 | "What's new", line 9a | Basic exclusion amount $15,000,000 |
| IRS-706-FILING | https://www.irs.gov/businesses/small-businesses-self-employed/filing-estate-and-gift-tax-returns | "When to file" | Form 706 due 9 months after death; 6-month extension |
| IRS-P551 | https://www.irs.gov/publications/p551 | Basis other than cost | Inherited property basis = FMV at date of death |
| IRS-NIIT | https://www.irs.gov/individuals/net-investment-income-tax | Thresholds | 3.8%; $250,000 MFJ / $200,000 single |
| IRS-1031 | https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips | Real-property scope | §1031 limited to real property after 2017 |
| IRS-P527 / P523 / P559 | https://www.irs.gov/publications/p527 · /p523 · /p559 | Rental depreciation, sale of home, fiduciaries | 27.5-year life; §121 $250k/$500k |
| CA-XIIIA | https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=CONS&article=XIII%20A | Art. XIII A §1, §2 | 1% cap plus voter-approved debt; 2% value cap |
| RTC-51 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=51 | Inflation factor | CPI-based, capped at 2% |
| RTC-63.2 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2 | (a)(1)(A)-(C), (b), (d), (f) | Occupancy within 1 year; exemption within 1 year; claim required; removal on move-out |
| BOE-LTA25015 | https://boe.ca.gov/proptaxes/pdf/lta25015.pdf | Publication 800-1 | "$1 million amount is adjusted to $1,044,586" as of February 2025 |
| BOE-LTA26002 | https://boe.ca.gov/proptaxes/pdf/lta26002.pdf | Full letter | 2026-27 inflation factor **1.02**; CCPI +3.307% (Aug 2024–Aug 2025) |
| SCC-PROP19 | https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2 | Eligibility, forms, claim window | Parent **and** child principal-residence rule; BOE-19-P; 3-year claim |
| SCC-PROP13 | https://asr.santaclaracounty.gov/faq/understanding-proposition-13 | Levy and cap | 1% plus voter-approved taxes; 2% maximum increase |
| SCC-HOE | https://asr.santaclaracounty.gov/tax-savings/exemptions/homeowners | Exemption amount and deadlines | $7,000; full if filed by Feb 15, 80% afterwards |
| SCC-FAQ | https://asr.santaclaracounty.gov/faq/general-questions | Rate guidance | "Generally, using a rate of 1.2% will give a conservative estimate" |
| SF-TREAS | https://sftreasurer.org/property/secured-property-taxes | Opening paragraph | Secured rate FY 2026-27 **1.18162182%**; penalty dates |
| SF-ASSESSOR-TT | https://www.sfassessor.org/recorder-information/recording-document/transfer-tax | Rate table | $3.75 per $500 for $1M–$5M (0.75%) |
| CIV-1947.12 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12 | (a)(1) | 5% + cost-of-living change, max 10% |
| CIV-1954.52 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1954.52 | (a) | Vacancy decontrol |
| SF-RENT | https://www.sf.gov/learn-about-rent-increases-san-francisco | Current allowance | **1.6%** for Mar 1, 2026 – Feb 28, 2027 |
| RTC-17043 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17043 | 1% surtax | Applies above $1,000,000 taxable income |
| SCC-COURTS-PROBATE | https://santaclara.courts.ca.gov/self-help/self-help-topics/self-help-probate/self-help-probate-property-transfers/administering-probate-estate-after-appointment | Probate checklist, taxes | "California does not have an inheritance tax"; BOE-19-P in the checklist |
| SFPUC-RATES | https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice | Volumetric rates, average bill | $11.40/unit FY 2025-26 → $12.20 proposed; ~$171/month average single family |
| PG&E-E1 | https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-1.pdf | Total bundled rates | Tier 1 $0.32561/kWh; Tier 2 $0.40702/kWh; base charge $0.79343/day |
| CDI-HOME | https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/ | Index page | Guides plus a Homeowners Premium Survey tool; no parcel-level premium |
| CDI-SURVEY | https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20 | Landing page | Official premium comparison tool |
| FAIR-PLAN | https://www.cfpnet.com/ | Home page | Insurer of last resort; dwelling-fire base policy; DIC needed for HO-3 equivalent |
| LEG-SB974 | https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SB974 | Status | Chaptered 09/27/2026, Chapter 665, Statutes of 2026 |
| FTB-INHERIT | https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html | "Gifts and inheritance" | "do not include it in your income"; later income is taxable |
| RTC-13302 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=13302 | §13302 and Part 8 heading | "Prohibition of Gift and Death Taxes"; state tax limited to the federal state-death-tax credit |
| BOE-PROP19 | https://www.boe.ca.gov/prop19/ | Prop 19 comparison charts | "Principal residence of transferor and transferee"; value limit = taxable value + $1,000,000; exemption 1 yr / claim 3 yrs |
| CA-PROBATE-CODE | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16000 | Trustee duties | §16000 duty of loyalty/prudence |

## B. Values that could NOT be verified (published on Flagged for Review)

| Item | Why not | Treatment in the model |
|---|---|---|
| Insurance premiums, both properties | No agency publishes a parcel-level premium; CDI only offers a survey tool | $1,500/yr each, flagged; 5%/yr growth assumed |
| Cupertino water tariff | San Jose Water tariff page not retrievable in this window | $100–$150/mo owner-reported, $1,500/yr used |
| Cupertino market rent | No official rent series at house level; HUD FMR is metro/zip-wide and covers assisted housing, not this property | $6,000/mo assumption with a sensitivity table |
| SF third-unit market rent | Vacant unit; no rent in the owner's data | $3,600/mo assumption |
| Split of the tax bill between ad valorem tax and direct charges | Requires the annual bill itself | Residual carried as a CPI-grown charge line (Cupertino ~$730, SF ~$1,089) |
| Future Prop 19 cap indexation | BOE re-indexes every two years; nothing published for the 2040s | 2.5%/yr assumption |
| Future federal exclusion | Statute indexes it; 2027+ figures not yet published | 2.5%/yr from the verified 2026 figure |
| Cash inheritance amount | Not supplied — privacy | `[AMOUNT REDACTED]`; estate-tax tables show tax by estate size instead |
| Cupertino county transfer tax (0.11%) | Not re-verified this window | Used in the sale scenarios, disclosed on the Sources page |

## C. Arithmetic that was checked independently

| Check | Computation | Result |
|---|---|---|
| Cupertino effective rate, 2025 | ~$7,200 ÷ ~$540,000 (rounded) | ≈1.33% — stable across 2014–2025 |
| SF effective rate, 2025 | ~$2,400 ÷ ~$114,000 (rounded) | ≈2.11% vs. published secured rate 1.18162182% |
| Cupertino 2026 tax | 1.20% × $551,000 + $720 | $7,330 (projected; the 2026 bill does not exist yet) |
| SF 2026 assessed value | $114,000 × 1.02 | $116,280 |
| SF 2026 tax | 1.18162182% × $116,280 + $1,050 | $2,420 |
| Prop 19 at 2045 | $551,000 × 1.02¹⁹ = $802,700; value $3.1M × 1.035¹⁹ = $5,959,750; cap $1,044,586 × 1.025¹⁹ = $1,669,930 | Excluded ceiling ≈$2,472,600; taxable if claimed ≈$4,290,000 vs $5,959,750 if not |
| SF water sanity check | SFPUC average single-family ≈$171/mo × 3 units | ≈$513/mo vs owner's $330–$400 — owner figure is not implausible once sewer is included |

## D. Irregularities that remain open

1. SF effective rate ≈2.1% vs 1.18% published — unexplained ~96 bp residual.
2. Cupertino effective rate ≈1.33% vs 1.2% county planning guidance — the split is unknown.
3. SF 2018 tax +18.4% on +2% assessed value.
4. Cupertino 2017 tax −0.5% on +2% assessed value.
5. Which property is the parents' principal residence — determines whether Prop 19 relief exists at all.
6. Insurance and Cupertino water are owner estimates only.

All six are published on `pages/flagged.html` with the action needed to close them.

## D2. Privacy handling of the parcel figures

The series is published at reduced precision: assessed values to the nearest $1,000, tax bills to the nearest
$100. The exact figures supplied by the owner are **not** stored in this repository. This was a deliberate
change after the parallel session (`9dcf1e9f`) flagged that exact assessed values plus a ZIP code can be
re-identified against a county's public roll. Residual re-identification risk is disclosed on
`pages/properties.html`; the recommended fix if that matters is a private repository.

## E. Site integrity checks run before publish

```
python3 tools/validate_data.py   -> 39 sources, 42 facts (37 verified, 2 reported, 3 flagged); OK
python3 tools/build.py           -> 9 pages, no unresolved template placeholders
python3 tools/check_links.py     -> 18 HTML files (9 current + 9 archived), 47 external URLs; all internal links and anchors resolve
```

External URLs could not be probed from the build sandbox (outbound access is restricted), so each one was
opened and read with the research tool during this session; section A is the record of that reading.
