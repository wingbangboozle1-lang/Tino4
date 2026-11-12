# Independent `.gov` / `.ca.gov` Source Verification & Privacy-First Audit (`s-8bb142d0`)

- **Audit date:** `2026-11-12` (UTC)
- **Session / Branch:** `s-8bb142d0` (`arena/8bb142d0-tino4`)
- **Privacy boundary:** Zero household dollar inputs, zero parcel/street/city/ZIP identifiers, and 100% `$10`-rounded numeric displays (`ROUND_HALF_UP`). Unverified household records remain intentionally blank on the public dashboard (`main` @ `92a0a8b`).

---

## 1. Directly Fetched Official `.gov` / `.ca.gov` Sources (`2026-11-12`)

Every official authority below was directly retrieved via `fetch_page` during this session and cross-checked against the published dashboard's legal claims and status badges (`Verified`, `Guidance`, `Missing`, `Synthetic`):

| Ref | Agency & Official Publication | Live `.gov` / `.ca.gov` URL | Directly Verified Rule / Statutory Figure (`$10`-rounded display) |
| --- | --- | --- | --- |
| `IRS-2027` | IRS News Release IR-2026-133 / Rev. Proc. 2026-35 (Nov. 5, 2026) | `https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts` | **2027** federal estate basic exclusion **`$15,480,000`** (`$15,000,000` in 2026 under P.L. 119-21); **2027** annual gift exclusion **`$20,000`** (`$19,000` in 2026); standard deduction **`$16,600`** single / **`$33,200`** joint. |
| `RTC-13301` | Cal. Revenue & Taxation Code § 13301 (read with § 13302 & State Controller guidance) | `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=13301.&lawCode=RTC` | Prohibits state and local gift, inheritance, succession, legacy, or estate transfer taxes (`$0` California estate return requirement for post-2004 deaths). Does not exempt ongoing property or income taxes. |
| `RTC-18031` | Cal. Revenue & Taxation Code § 18031 | `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=18031.&lawCode=RTC` | Incorporates IRC Subchapter O (including IRC § 1014 fair-market-value basis at death) into California personal income tax law unless modified by statute. |
| `RTC-480` | Cal. Revenue & Taxation Code § 480(b) | `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=480.&lawCode=RTC` | Trustee/transferee must file a Change in Ownership Statement within **150 days** after death for non-probate trust transfers (`$100` or `10%` statutory penalty mechanics if unfiled after 90-day written assessor request). |
| `PROB-16061.7` | Cal. Probate Code § 16061.7(f) | `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB` | Successor trustee notification must be served on beneficiaries and heirs within **60 days** after a revocable trust becomes irrevocable at death. |
| `BOE-NR-25-02` | California BOE News Release NR 25-02 / LTA 2025/009 & Pub. 801 | `https://www.boe.ca.gov/news/2025/nr-25-02.htm` | Prop. 19 principal-residence intergenerational exclusion cap for transfers **Feb. 16, 2025 – Feb. 15, 2027** is `FBYV + ~$1,044,590` (`$10`-rounded display; exact unrounded statutory figure governs assessor filings); requires principal-residence occupancy and exemption claim within **1 year** plus `BOE-19-P` filing within **3 years**. |
| `CIV-1947.12` | Cal. Civil Code § 1947.12 (AB 1482 Tenant Protection Act) | `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV` | Statewide annual rent-increase cap of `5% + regional CPI` or `10%` (whichever is lower) through statutory sunset **Jan. 1, 2030**, with mandatory written notice required for alienable-separate single-family exemption (`§ 1947.12(d)(5)`). |
| `LOCAL-RENT` | Local Rent Board — Current Rates & Legislative Notice (updated Nov. 9, 2026) | `https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit` | Annual allowable increase **`1.6%`** for **Mar. 1, 2026 – Feb. 28, 2027**; security deposit interest **`4.2%`**. Legislative File **261020** (`10%/yr` combined banked + capital-improvement cap) is **proposed, NOT enacted** as of Nov. 9, 2026. |
| `CPUC-NBT` | CPUC — Net Energy Metering & Net Billing Tariff (`D.22-12-056`) | `https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing` | Applications after Apr. 15, 2023 take avoided-cost export credits (`9-year` original-customer legacy); closed retail NEM 1.0/2.0 systems carry `20-year` interconnection legacy (`$0.02–$0.03/kWh` net surplus compensation). Credits are tariff-dependent, not guaranteed perpetual cash profit. |
| `CDI-SIS` | California Dept. of Insurance — Sustainable Insurance Strategy Snapshot (Oct. 27, 2026) | `https://www.insurance.ca.gov/01-consumers/180-climate-change/sustainable-insurance-strategy.Cfm` | **`8,300,730`** voluntary market residential policies vs. **`677,449`** FAIR Plan policies across **`662`** distressed ZIPs. Statewide NAIC homeowner averages are not quotes for high-value or mixed-use rental underwriting. |
| `CBO-62809` | Congressional Budget Office — Budget & Economic Outlook Update: 2026–2036 (Oct. 8, 2026) | `https://www.cbo.gov/publication/62809` | Baseline 10-year Treasury yield averages **`4.3%`** (`2026–2036`); federal debt held by the public rises from **`100.6%`** (`2026`) to **`120.2%`** (`2036`) of GDP. |
| `HR-5336` | Congress.gov — H.R. 5336 (*Equal Tax Act*, 119th Congress) | `https://www.congress.gov/bill/119th-congress/house-bill/5336/all-info` | Introduced `09/11/2025` (`17` cosponsors through `06/23/2026`, referred to House Ways & Means; companion `S. 4122` in Senate Finance `03/17/2026`). **Introduced only — NOT enacted law.** |
| `SFPUC-218` | SFPUC — FYE 2027 & FYE 2028 Proposition 218 Rate Notice (eff. July 1, 2026) | `https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice` | **`7.0%/yr`** water + **`15.0%`** (FY27) / **`14.5%`** (FY28) wastewater rate-revenue increases. Replaces dead legacy `/rate-changes` URL (`S35`). |

---

## 2. Independent Verification of Defects Resolved Across the Repository

Prior to PR #45's privacy-first rebuild (`92a0a8b`), our line-by-line audit of the legacy `_c07ccf45` / `_s09b3ffa0` build identified seven concrete defects:

1. **Legacy `decision-analysis.html` table bug:** Column `Property A value (Plan 3)` referenced `a["cup_val"]` (sold) instead of `b2["cup_val"]` (retained), printing `sold` on all 20 rows. **Current status on `main`:** Superseded and resolved by PR #45's clean synthetic regime comparator (`tools/test_model.py` + `pages/decision-analysis.html`).
2. **Legacy `black-swan-scenarios.html` header/value mismatch:** Acute crash table columns 4–5 displayed Treasury (`1B`) and Rent (`3`) values under `3 · rent A out` and `2B · live in A` headers. **Current status on `main`:** Superseded and resolved by PR #45's 7-regime after-tax synthetic stress table (`Baseline`, `Inflation surge`, `Housing slump`, `Equity crash`, `Lost decade`, `Insurance and repairs`, `Compound shock`).
3. **Legacy `PLACE_GEO` text-scrubber corruption:** Replacing the capitalized word `"Sunset"` corrupted statutory sunset text (`"the coastal district Jan. 1, 2030"`). **Current status on `main`:** Resolved — `tools/verify.py` scans for prohibited district names without mutating statutory `"sunset"` prose.
4. **Dead `S35` SFPUC `/rate-changes` URL:** Directly verified dead on `2026-11-12`. **Current status:** Replaced on `main` with live CPUC/official links and recorded in `_s8bb142d0/audit/supplemental_evidence.py` (`sfpuc218`) with the live FYE 2027–2028 Prop. 218 Notice URL.
5. **Misclassified owner-supplied provenance (`IR-019`):** Legacy `open-questions.html` marked owner-supplied utility estimates as `"Have"` alongside CPUC links. **Current status on `main`:** Resolved (`F16` + intentionally blank cells with `aria-label="Not verified; intentionally blank"`).
6. **Public Git-history / private-workspace governance (`IR-018` / `F01`):** Public repository history cannot be erased by `_config.yml` or `noindex`. **Current status on `main`:** Tracked as `F01 · Highest` on `flagged-for-review.html` and `S01 · P0` on `suggestions.html`.
7. **Zero-carveout `$10` rounding:** Every dollar token on `main` is now a strict multiple of `$10` (`$1,044,590` `$10`-rounded display with explicit filing caveat), verified with zero statutory carveouts by `tools/verify.py`.

---

## 3. Targeted Non-Destructive Enhancements Ready for Public Integration

Cross-checking `main` (`92a0a8b`) against our `2026-11-12` `.gov` fetches identified four high-value factual additions that strengthen the privacy-first dashboard without introducing any household figures:

1. **Direct Congress.gov verification of pending step-up repeal bills (`hr5336`):** On `pages/law-watchlist.html`, upgrade `"Basis repeal / reduced estate exemption"` from `"no specific repeal bill status verified in this audit"` to directly verified `119th Congress` bill tracking (`H.R. 5336`, *Equal Tax Act*, introduced `09/11/2025`, 17 cosponsors in House Ways & Means; companion `S. 4122` in Senate Finance — **Introduced, NOT enacted**).
2. **California income-tax basis conformity (`rtc18031`) & statewide AB 1482 rent cap (`ab1482`):** Add `Cal. RTC § 18031` (confirming California conformity to IRC § 1014 death-date FMV basis) to `inheritance-law.html` and `Cal. Civ. Code § 1947.12` (statewide `5% + CPI` / `10%` rent cap + Jan. 1, 2030 statutory sunset + SFR exemption notice rule) to `law-watchlist.html`.
3. **CBO Oct. 2026 Treasury baseline (`cbo2026`) & CDI Oct. 27, 2026 market snapshot (`cdimarket`):** Add directly verified federal macro context (`4.3%` 10-yr Treasury 2026–2036 baseline; `100.6% → 120.2%` debt/GDP) and CDI voluntary (`8,300,730`) vs. FAIR Plan (`677,449`) policy counts to `sources.html`, `operating-costs.html`, and `law-watchlist.html`.
4. **Explicit `_s8bb142d0` exclusion in `_config.yml` & `verify.py`:** Ensure `_s8bb142d0` is listed alongside `_7eff7e24` and `_1775f697` in `_config.yml` and checked by `tools/verify.py`.
