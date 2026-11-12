# Independent Line-by-Line Verification & Repository Audit (`s-09b3ffa0`)

**Audit Date:** `2026-11-12` (UTC)  
**Scope:** Independent primary `.gov` / `.ca.gov` verification of all statutory, tax, utility, insurance, housing, and macroeconomic inputs (`_s09b3ffa0/evidence/official_ledger.json`) and technical review of the landed `main` candidate (`s179ec133`) and secondary reference (`_s9ad1da71`).  
**Privacy Standard:** Strict placeholder anonymization (`[Property A]` / `[Property B]`, `[Jurisdiction A]` / `[Jurisdiction B]`) and strict `$10` pre-rounding on all owner-supplied and modeled figures.

---

## 1. Executive Audit Verdict

1. **Directional Strategic Agreement Confirmed:** Independent modeling from `$10`-pre-rounded inputs confirms the core conclusion across prior sessions: **selling `[Property A]` upon trust inheritance (capturing the IRC §1014 / CA RTC §18031 date-of-death fair-market-value basis step-up), retaining `[Property B]` (living in Unit 3 while keeping Units 1–2 rented), and reinvesting net sale proceeds into a diversified low-cost equity index (or 60/40 equity + CA-tax-exempt U.S. Treasury glidepath)** dominates both **Renting `[Property A]`** and **Living in `[Property A]`** across all 11 transfer years (`2040–2050`), across `98.0%` (`49/50`) of rolling historical cohorts (`1976–2025`), and across `81.6%` of 500 de-meaned block-bootstrap 50-year stress paths.
2. **Five Material Technical & Privacy Improvements Implemented in `_s09b3ffa0/`:**
   - **Finding A-1 — Published Location Wording Narrowing (`HIGH — Privacy`):** The landed root pages (`pages/operating-costs.html`, `pages/properties.html`, `pages/sources.html`) explicitly paired municipal and school-bond names with the 13-year `$10`-rounded assessment series (`$440,310`–`$550,540`). `_s09b3ffa0/site/` removes all city, neighborhood, school-district, ZIP, and parcel identifiers while retaining direct links to every official county/state/federal source.
   - **Finding A-2 — Strict `$10` Rounding Without Carveouts (`MEDIUM — Privacy/Compliance`):** `s179ec133`'s verifier exempted `OFFICIAL_NUMBERS`, leaving 17 unrounded dollar amounts (`>= $100`) across 7 pages. `_s09b3ffa0/site/` enforces `amount % 10 == 0` on **100% of dollar figures `>= $100`** across all 15 pages (`0` exceptions).
   - **Finding A-3 — CPUC 20-Year Solar NEM Legacy Sunset (`D.14-03-041` & `D.22-12-056`) (`MEDIUM — Model Validity`):** `s179ec133` projected `[Property A]`'s solar net credit (`-$180/yr`) as an inflation-indexed cash profit forever through `2076` (`-$570/yr`). Official CPUC rules cap NEM 1.0/2.0 retail export credits at **20 years from interconnection** (`<= 2046` for an already-installed 2026 system), after which systems transition to the Net Billing Tariff (`D.22-12-056`) with avoided-cost export credits plus inverter replacement cycles.
   - **Finding A-4 — IRC §280A / IRS Pub. 527 Mixed-Use 2/3 Expense Allocation, `$7,000` Homeowners' Exemption Shift, & Unit-3 Leasing Option (`MEDIUM — Tax Accuracy`):**
     - Forensic BOE Prop. 13 roll arithmetic (`(AV_{t-1} + $7,000) × factor - $7,000`) proves with `$0`–`$10` residual across `2018–2025` that `[Property B]` currently carries the `$7,000` Homeowners' Exemption (`Gross FBYV = $121,250` in 2025; `Net Taxable = $114,250`), whereas `[Property A]` (`$550,540` in 2026) matches `1.02 × $539,740` with zero `$7,000` subtraction.
     - Under IRS Pub. 527, when the inheritor resides in Unit 3 of `[Property B]`, only **2/3** of shared building expenses are deductible against rental income on Schedule E (`1/3` is personal). Conversely, if the inheritor moves into `[Property A]`, the `$7,000` Homeowners' Exemption shifts from `[Property B]` to `[Property A]`, and leasing `[Property B]` Unit 3 (`Plan L2`) adds `+$664,620` real 2026$ over leaving Unit 3 vacant (`Plan L1`).
   - **Finding A-5 — Closure of Official Source Blanks (`F-22` & `F-23` Verified Directly on `.gov`):**
     - Verified official tiered Real Property Transfer Tax rates (`0.50%` to `6.00%`, including `0.75%` for `$1M–<$5M` and `2.25%` for `$5M–<$10M`) directly from `sf.gov` (`Assessor-Recorder Fee & Transfer Tax Schedule`) and `0.11%` county-only transfer tax (`$0` city conveyance tax in non-charter cities) from `clerkrecorder.santaclaracounty.gov`.
     - Verified official FY 2026–27 (`12.6%`) and FY 2027–28 (`12.5%`) combined water/sewer rate increases directly from `sfpuc.gov` (`Proposition 218 Notice`) and regulated Class A water attrition increases (`3.99%` in 2026; `4.49%` in 2027) from `cpuc.ca.gov` (`D.24-12-077`).
     - Verified Oct. 27, 2026 statewide California average admitted homeowner premium (`$1,570` `$10`-rounded from official `$1,571`) on `insurance.ca.gov` while keeping parcel-specific high-value/habitational carrier quotes **blank and flagged** per strict anti-hallucination rules.

---

## 2. Summary Comparison: Baseline 2045 Inheritance (20-Year Horizon to 2065, Constant 2026$)

| Strategy (All Plans Retain `[Property B]`) | Terminal Wealth Ex-`[Property B]` (2026$) | Total Wealth Incl. `[Property B]` (2026$) | Cumulative 20-Yr Net Cash Flow (2026$) | Win Share (50 Hist. Cohorts) | Win Share (500 Bootstrap Paths) |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Plan S1: Sell `[Property A]` → 100% Equity Index** | **$7,031,710** | **$9,661,220** | +$1,602,080 | **98.0%** (49/50) | **81.6%** |
| **Plan S2: Sell `[Property A]` → 60/40 Stocks + U.S. Treasuries** | **$5,989,000** | **$8,618,510** | +$1,897,690 | 0.0% (2nd in crashes) | 1.2% |
| **Plan R: Keep & Rent Out `[Property A]`** | **$4,671,930** | **$7,301,440** | +$763,720 | 2.0% (1/50) | 16.0% |
| **Plan S3: Sell `[Property A]` → 100% CA-Exempt U.S. Treasuries** | **$4,151,520** | **$6,781,030** | +$2,266,230 | 0.0% | 1.0% |
| **Plan L2: Live in `[Property A]` + Lease `[Property B]` Unit 3** | **$3,905,480** | **$6,534,990** | -$276,850 | — (variant) | — (variant) |
| **Plan L1: Live in `[Property A]` (Keep Unit 3 Unrented)** | **$3,240,860** | **$5,870,370** | -$1,103,570 | 0.0% | 0.2% |
