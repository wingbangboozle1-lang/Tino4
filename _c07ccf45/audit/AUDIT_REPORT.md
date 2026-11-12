# Session `s-c07ccf45` — Line-by-Line Repository Audit & Cross-Model Reconciliation (`C07C-T1`)

Audit date: `2026-11-12` (UTC)

## 1. Summary of Repository State on `main`

- **Root published site (`index.html`, `pages/*.html`, `assets/style.css`, `tools/build.py`, `tools/verify.py`)**: Integrated from `s179ec133/site/` via PR #28 (`f5705d45`) and PR #32 (`arena-62edb6b1`). Contains 14 pages, 584 source-linked table rows, 1,364 links, 1,909 dollar amounts, and passes `python3 tools/verify.py` with `0` failures.
- **Staged reference packages**: `s179ec133/` (excluded in `_config.yml`) and `_s9ad1da71/` (underscore-excluded by Jekyll and listed in `_config.yml`).

## 2. Line-by-Line Verification Against Official `.gov` Sources

| Topic / Statutory Item | Root Site (`s179ec133`) | `_s9ad1da71` Reference | Official `.gov` Source Checked (`2026-11-12`) | Audit Verdict |
| --- | --- | --- | --- | --- |
| 2026 Federal Estate Basic Exclusion | `$15,000,000` | `$15,000,000` | IRS Estate Tax & P.L. 119-21 §70106 (`S04`, `S05`, `S06`) | **CONFIRMED** |
| 2027 Federal Estate Basic Exclusion | `$15,480,000` | `$15,480,000` | IRS IR-2026-133 & Rev. Proc. 2026-35 (`S02`, `S03`) | **CONFIRMED** |
| 2027 Annual Gift Exclusion | `$20,000` | `$20,000` | IRS IR-2026-133 (`S02`) | **CONFIRMED** |
| CA State & Local Inheritance/Death Tax | `$0` (prohibited) | `$0` (prohibited) | CA RTC §§13301 & 13302 (`S13`, `S14`) | **CONFIRMED** |
| Federal & CA Stepped-Up Basis at Death | FMV at death | FMV at death | IRC §1014 (`S07`, `S08`) & CA RTC §18031 (`S15`) | **CONFIRMED** |
| CA U.S. Treasury Interest Exemption | 0% CA tax | 0% CA tax | CA FTB Pub. 1001 (`S18`) | **CONFIRMED** |
| Prop. 19 Allowance (`2025-02-16` to `2027-02-15`) | `$1,044,586` (`$1,044,590` rounded) | `$1,044,590` rounded | CA BOE NR 25-02 & LTA 2025/009 (`S23`) | **CONFIRMED** |
| Prop. 13 Annual Cap & Base Levy | `1%` + debt; `min(2%, CCPI)` | `1%` + debt; `min(2%, CCPI)` | CA BOE Pub. 29 (`S21`) & SCC Assessor Booklet (`S28`) | **CONFIRMED** |
| County Documentary Transfer Tax (Property A) | `$1.10 / $1,000` (`0.11%`) | `$0.55 / $500` (`0.11%`), `$0` city | SCC Clerk-Recorder Fee Schedule (`S29`) | **CONFIRMED** |
| Property B FY 2026–27 Secured Tax Rate | `1.18162182%` | `1.18162182%` | SF BOS File 260971 (`S30`) & FY25–26 File 250876 | **CONFIRMED** |
| Property B Rent Board Allowable Increase | `1.6%` (`3/1/26–2/28/27`) | `1.6%` (`3/1/26–2/28/27`) | SF Rent Board Current Rates (`S31`) | **CONFIRMED** |
| Empty Homes Tax (EHT) Status | Struck down; affirmed `2026-09-11` (`A172067`) | Suspended (`Ord. 41-25`) | SF Treasurer EHT Page & Controller Letter (`S32`) | **CONFIRMED** |
| CA Statewide Homeowner Insurance Avg. | `$1,571` (`~$1,570` rounded) | `~$1,570` rounded | CA DOI Sustainable Insurance Strategy (`S36`) | **CONFIRMED** |
| CPUC NEM Legacy Grandfathering Window | Noted in text, but **not** applied in `proj_a` | Applied (`<= 2043` sunset) | CPUC NEM/NBT Portal (`D.16-01-044` & `D.22-12-056`, `S33`) | **GAP IN `s179ec133` MODEL** |
| Multi-Unit Schedule E Expense Split (2/3 vs. 3/3) | Deducts `3/3` in `b_net` even while occupying Unit 3 | Properly applies `2/3` when occupying Unit 3 & `3/3` when renting all 3 | IRS Pub. 527 (`S12`) | **GAP IN `s179ec133` MODEL** |

## 3. Five Specific Enhancements Implemented in `_c07ccf45/` (`C07C-T2` & `C07C-T3`)

1. **CPUC 20-Year NEM Legacy Sunset (`<= 2044`)**: `s179ec133/_work/model/engine.py` projects Property A's `-$180/yr` (`-$15/mo`) solar credit growing with inflation all the way through 2076 (`-$550/yr` credit in year 50). Under CPUC Decision D.16-01-044 and D.22-12-056, retail-rate NEM 1.0/2.0 export credits expire 20 years after interconnection (`<= 2044` for systems installed before the April 2023 NBT transition), transitioning to avoided-cost export credits plus fixed monthly delivery charges and inverter replacement reserves. `_c07ccf45/model/engine.py` models the `-$180/yr` credit through the 20-year legacy window and transitions to post-NEM net electricity + inverter reserve thereafter.
2. **IRS Pub. 527 Schedule E 2/3 vs. 3/3 Expense Allocation & `$7,000` Homeowners' Exemption Shift**: When the owner lives in Unit 3 of the 3-unit Property B (Plans 1 & 3), only 2/3 of shared building expenses (property tax, insurance, water, common electric, maintenance) are deductible against rental income on Schedule E. When the owner moves to Property A and rents out Unit 3 of Property B (Plan 2B), 100% (3/3) of Property B operating expenses become deductible and the `$7,000` Homeowners' Exemption (`BOE Pub. 800-6`) shifts from Property B to Property A.
3. **Full 13-Year Property A (`2014–2026`) and 10-Year Property B (`2016–2025`) `$10`-Rounded History + BOE Factor Check**: Preserves all 23 historical rows supplied by the user, pre-rounded to the nearest `$10` before storage, and verifies every year-over-year assessment step against official California BOE CCPI inflation factors.
4. **Balanced `75/25` Equity / CA-Tax-Exempt U.S. Treasury Strategy (`Plan 1C`)**: Alongside 100% Equities (`Plan 1A`) and 100% CA-Tax-Exempt U.S. Treasuries (`Plan 1B`), `_c07ccf45/model/engine.py` evaluates a staged `75% Equity / 25% U.S. Treasury` portfolio (`Plan 1C`) that captures strong equity compounding while mitigating sequence-of-returns crash risk (`R3`) and California's `13.3%` tax on ordinary interest.
5. **Zero Geographic or ZIP Identifiers in Candidate HTML**: Removes all city names, neighborhood names, and `?zcta=` ZIP query parameters from `_c07ccf45/site/**` and `_c07ccf45/data/inputs.json`.
