# COORDINATION.md — Shared Task Board

This is the shared task board for all agent sessions working on `wingbangboozle1-lang/Tino4`.
It records each task, its status (`unclaimed` / `in progress` / `done` / `needs review`), the
owning session ID, and the files it touches. **Read this before starting work.** Claim a task by
writing your session ID and file scope here, commit and push the claim immediately, and never
start a task another session has claimed. Keep file scopes non-overlapping; if you need a file
owned by another session, log the request here instead of editing it. Make small, frequent
commits and run `git pull --rebase` before every push. On a merge conflict, stop, resolve without
discarding another session's work, and log it. When a task finishes, record its sources,
verification performed, and irregularities here and mark it `done`. Never mark anything
`verified` without checking it against an official source and linking that source. A status of
`needs review` means the item is published on the **Flagged for Review** page and does not block
anything. A claim older than 60 minutes with no commits may be taken over; note the handoff.

- **Repository:** `wingbangboozle1-lang/Tino4`
- **Working / integration branch:** `arena/ef28fa90-tino4` (platform-fixed; see IR-001)
- **Live site:** https://wingbangboozle1-lang.github.io/Tino4/ (GitHub Pages, `main`, root)
- **Board last updated:** 2026-11-11 (UTC)
- **Final integration session:** `s-0837be92` (2026-11-10); follow-up session `s-accb6bba` (2026-11-11); audit session `arena-ef28fa90` (2026-11-11)

## Platform constraint (IR-001)

Arena pins every session of this conversation to the single branch `arena/0837be92-tino4` and
forbids creating, switching to, or pushing any other branch (including `session-<id>/<task>`
branches or separate git worktrees). Isolation was therefore implemented by **non-overlapping
file scopes** within the one branch, recorded below. The pull request is opened from
`arena/0837be92-tino4` → `main`. Published on Flagged for Review as IR-001; does not affect the
analysis.

## Task board

| Task ID | Task | Status | Owner session | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| T1 | Repo scaffolding, coordination board, privacy/anonymization policy, README, `.gitignore`, Pages settings | done | `s-0837be92` | `COORDINATION.md`, `README.md`, `.gitignore` | 2026-11-10 |
| T2 | Research & official source register (federal/state/local tax law, thresholds, proposed changes, insurance, utilities, inflation) | done | `s-0837be92` | `internal/research-notes.md`, `internal/source-register.md` | 2026-11-10 |
| T3 | Verified-facts table data, every row linked to an official source | done | `s-0837be92` | `docs/data/facts.json`, `docs/data/sources.json` | 2026-11-10 |
| T4 | Projection & scenario model data 2026–2055 and deterministic generator | done | `s-0837be92` | `tools/*.py`, `docs/data/projections.json`, `docs/data/model-inputs.json`, `docs/data/decisions.json` | 2026-11-10 |
| T5 | Site pages: executive summary, property tax, projections, operating costs, inheritance law, thresholds, decision analysis, process, watchlist, methodology, sources, flagged, privacy | done | `s-0837be92` | `docs/pages/*.html`, `docs/assets/**` | 2026-11-10 |
| T6 | Line-by-line verification pass, link check, privacy scan, build check | done | `s-0837be92` | `internal/verification-log.md`, `tools/verify.py` | 2026-11-10 |
| T7 | Final integration: shared table data, `docs/index.html` + navigation, root mirror, merge branches, re-verify combined data, no broken links, publish to GitHub Pages | done | `s-0837be92` | `docs/index.html`, `docs/data/**`, root mirror | 2026-11-10 |
| T8 | Pull request → `main`, merge, confirm GitHub Pages deployment, record PR link and merge result here | done | `s-0837be92` | `COORDINATION.md` (final log only) | 2026-11-10 |
| T9 | Black-swan / 50-year stress-scenario section: historical episodes from official sources + modelled stress paths, new subpage, nav, index link | done | `s-accb6bba` | `tools/sources.py`, `tools/build.py`, `docs/data/black-swan.json`, `docs/pages/black-swan-scenarios.html`, `pages/black-swan-scenarios.html`, `docs/index.html`, `index.html` | 2026-11-11 |
| T10 | Re-verify line by line after T9 (source links, column counts, privacy, root mirror), fix failures | done | `s-accb6bba` | `tools/verify.py`, `internal/verification-log.md` | 2026-11-11 |
| T11 | Pull request → `main`, merge, confirm GitHub Pages deployment, record PR link and merge result here | done | `s-accb6bba` | `COORDINATION.md` (final log only) | 2026-11-11 |
| T12 | Independent audit & line-by-line re-verification: build reproducibility, `verify.py`, HTTP 200 sweep, privacy scan, root-mirror check, live-site check | in progress | `arena-ef28fa90` | `COORDINATION.md`, `internal/verification-log.md` | 2026-11-11 |
| T13 | Official-source freshness spot-check: re-fetch key statutory values (IRS, BOE, county, CBO, CDI, FTB) and record unchanged/changed | in progress | `arena-ef28fa90` | `internal/research-notes.md` (addendum only), `COORDINATION.md` | 2026-11-11 |
| T14 | Pull request → `main`, merge, confirm GitHub Pages deployment, record PR link and merge result here | unclaimed | `arena-ef28fa90` | `COORDINATION.md` (final log only) | 2026-11-11 |

## Session registry

| Session ID | Branch | Role | Status |
| --- | --- | --- | --- |
| `s-0837be92` | `arena/0837be92-tino4` | Full research → build → verification → final integration → PR → merge → deploy | done (merged) |
| `s-accb6bba` | `arena/accb6bba-tino4` | Follow-up: black-swan / 50-year stress scenarios, re-verify, PR → merge → deploy | done (merged, PR #9) |
| `arena-ef28fa90` | `arena/ef28fa90-tino4` | Independent audit, source freshness spot-check, PR → merge → deploy | active |
| `session-9dcf1e9f` | `arena/9dcf1e9f-tino4` | First rules-only dashboard; PR #1 and #2 merged to `main`; preserved as `archive-v1/` | done (merged) |
| `arena-5e491e8f` | `arena/5e491e8f-tino4` | Quantified 9-page dashboard, model, PR #3 merged to `main`; preserved as `archive-v2/` | done (merged) |
| `arena-6acab13a` | `arena/6acab13a-tino4` | Source registry + projection engine; preserved in `internal/prior-sessions/arena-6acab13a/` | merged at integration |
| `arena-ce2391b3` | `arena/ce2391b3-tino4` | 12-page site + verification log; preserved in `internal/prior-sessions/arena-ce2391b3/` | merged at integration |
| `arena-fd984e93` | `arena/fd984e93-tino4` | Source-linked dashboard; preserved in `internal/prior-sessions/arena-fd984e93/` | merged at integration |

## Parallel-session audit and merge resolution

At 10:06 UTC, `git ls-remote --heads origin` showed five other session branches. Each was
fetched and inspected with `git ls-tree -r --name-only`; several boards claimed work "done" while
their branches contained only `COORDINATION.md` + `README.md`, so the >60-minute stale-claim
handoff rule was applied and the full build proceeded. Nothing was copied from those boards as
fact; their useful *flagged-irregularity* ideas were independently re-derived from official
sources.

While this session was building, `main` advanced to `0bce61b` (PR #3 from `arena-5e491e8f`,
which had already archived the `session-9dcf1e9f` site as `archive-v1/`). As the final
integration session:

1. `git merge -s ours --no-ff refs/remotes/origin/main` recorded the merged work in history
   without overwriting this session's integrated tree.
2. The **entire** `main` tree (41 files) was preserved byte-for-byte in `archive-v2/`, so the
   prior session's site remains functional at `/archive-v2/`.
3. The three unmerged branches (`arena-6acab13a`, `arena-ce2391b3`, `arena-fd984e93`) were each
   merged with `-s ours` and their complete trees archived under
   `internal/prior-sessions/arena-<id>/` (9 / 26 / 13 files).
4. `arena-5e491e8f` and `arena-9dcf1e9f` were already ancestors of `main`, so their work is in
   `archive-v2/` / `archive-v1/` and no second merge was needed.
5. All archived trees were scanned for personal information (emails, phones, street addresses,
   SSNs, APNs): **none found**. No other session's work was discarded; every branch remains on
   the remote.
6. Combined data re-verified line by line after the merges: `python3 tools/build.py` and
   `python3 tools/verify.py` re-run on the merged tree.

The root mirror exists because the repository's Pages site is `build_type=legacy`,
`source=main:/` and the Pages administration API returned 403 `Resource not accessible by
integration` for this session's token (IR-017). `docs/` remains canonical; the root copy is
byte-identical, verified by `tools/verify.py`.

## Complete source register (official only)

Every URL below was fetched and read line by line on 2026-11-10. Full machine-readable copy:
`docs/data/sources.json` and `internal/source-register.md`. Site page: `pages/sources.html`.

| ID | Agency | Official document | URL | Verified (UTC) |
| --- | --- | --- | --- | --- |
| S01 | IRS | IRS — Instructions for Form 706 (Rev. July 2026) | https://www.irs.gov/pub/irs-pdf/i706.pdf | 2026-11-10 |
| S02 | IRS | IRS — Internal Revenue Manual 3.12.263, Estate and Gift Tax Returns | https://www.irs.gov/irm/part3/irm_03-012-263r | 2026-11-10 |
| S03 | IRS | IRS — Revenue Procedure 2025-32 (2026 inflation adjustments) | https://www.irs.gov/pub/irs-drop/rp-25-32.pdf | 2026-11-10 |
| S04 | IRS | IRS — 2026 Instructions for Form 709 (early-release draft) | https://www.irs.gov/pub/irs-dft/i709--dft.pdf | 2026-11-10 |
| S05 | IRS | IRS — Publication 551 (12/2025), Basis of Assets | https://www.irs.gov/publications/p551 | 2026-11-10 |
| S06 | IRS | IRS — Topic no. 701, Sale of Your Home | https://www.irs.gov/taxtopics/tc701 | 2026-11-10 |
| S07 | IRS | IRS — Topic no. 409, Capital Gains and Losses | https://www.irs.gov/taxtopics/tc409 | 2026-11-10 |
| S08 | IRS | IRS — Topic no. 559, Net Investment Income Tax | https://www.irs.gov/taxtopics/tc559 | 2026-11-10 |
| S09 | IRS | IRS — Publication 527 (2025), Residential Rental Property | https://www.irs.gov/publications/p527 | 2026-11-10 |
| S10 | U.S. Congress | Congress.gov — Public Law 119-21 (H.R.1), §70106, 07/04/2025 | https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf | 2026-11-10 |
| S11 | U.S. Congress | Congress.gov — H.R.1 (119th Congress), all information | https://www.congress.gov/bill/119th-congress/house-bill/1/all-info | 2026-11-10 |
| S12 | U.S. Congress | Congress.gov — H.R.5336, Equal Tax Act (introduced 09/11/2025), text | https://www.congress.gov/bill/119th-congress/house-bill/5336/text | 2026-11-10 |
| S13 | U.S. Congress | Congress.gov — H.Res.206, stepped-up basis resolution | https://www.congress.gov/bill/119th-congress/house-resolution/206/all-info | 2026-11-10 |
| S14 | U.S. Congress / CRS | Congress.gov — CRS IF12846, The Estate and Gift Tax | https://www.congress.gov/crs_external_products/IF/HTML/IF12846.html | 2026-11-10 |
| S15 | CA FTB | California FTB — Gifts and inheritance | https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html | 2026-11-10 |
| S16 | CA FTB | California FTB — Capital gains and losses | https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html | 2026-11-10 |
| S17 | CA FTB | California FTB — Analysis of SB 726 (03/23/2017): estate pick-up tax is zero | https://www.ftb.ca.gov/tax-pros/law/legislation/2017-2018/sb726-032317.pdf | 2026-11-10 |
| S18 | CA FTB | California FTB — Estates and trusts (Form 541) | https://www.ftb.ca.gov/file/personal/filing-situations/estates-and-trusts/index.html | 2026-11-10 |
| S19 | CA FTB | California FTB — 2025 Form 541 Fiduciary Income booklet | https://www.ftb.ca.gov/forms/2025/2025-541-booklet.html | 2026-11-10 |
| S20 | CA BOE | California BOE — Publication 29, California Property Tax: An Overview (March 2025) | https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf | 2026-11-10 |
| S21 | CA BOE | California BOE — LTA 2025/015, Proposition 19 information sheets | https://www.boe.ca.gov/proptaxes/pdf/lta25015.pdf | 2026-11-10 |
| S22 | CA BOE | California BOE — News Release 25-02, Prop 19 $1,044,586 exclusion adjustment | https://www.boe.ca.gov/news/2025/nr-25-02.htm | 2026-11-10 |
| S23 | CA BOE | California BOE — Introduction to Proposition 19 (April 2023) | https://www.boe.ca.gov/pdf/Introduction-to-Prop-19-042023.pdf | 2026-11-10 |
| S24 | CA BOE | California BOE — Sample BOE-19-P, parent-child reassessment exclusion claim | https://www.boe.ca.gov/proptaxes/pdf/sample-boe19p.pdf | 2026-11-10 |
| S25 | CA BOE | California BOE — Publication 800-6, Homeowners' Exemption | https://www.boe.ca.gov/pdf/pub800-6.pdf | 2026-11-10 |
| S26 | CA BOE | California BOE — Sample BOE-502-AH, Change of Ownership Statement | https://www.boe.ca.gov/proptaxes/pdf/sample-boe502ah.pdf | 2026-11-10 |
| S27 | CA BOE | California BOE — Board Meeting May 2026, Property Tax Forms (R&T §480(b)) | https://www.boe.ca.gov/meetings/pdf/2026/202605-PT-Forms.pdf | 2026-11-10 |
| S28 | CA BOE | California BOE — Property Tax Annotation 220.0760, Trusts (R&T §62(d)) | https://www.boe.ca.gov/lawguides/property/current/ptlg/annt/220-0760.html | 2026-11-10 |
| S29 | CA BOE | California BOE — Publication 800-10, How Property Is Assessed (2% cap) | https://boe.ca.gov/pdf/pub800-10.pdf | 2026-11-10 |
| S30 | Santa Clara County | Santa Clara County Assessor — Assessment Information 2026 booklet | https://files.santaclaracounty.gov/exjcpb1521/2026-04/assessment-information-2026-booklet-english-3-23-26-web.pdf | 2026-11-10 |
| S31 | City & County of SF | San Francisco Board of Supervisors — File 250876, FY2025-26 tax rate resolution | https://sfbos.archive.sf.gov/sites/default/files/r0447-25.pdf | 2026-11-10 |
| S32 | CA Legislature | California Probate Code §16061.7 — Notification by trustee (60 days) | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB | 2026-11-10 |
| S33 | CA Legislature | California AB 1482 — Tenant Protection Act of 2019 (rent cap through 01/01/2030) | https://www.leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201920200AB1482 | 2026-11-10 |
| S34 | City & County of SF | SF.gov — Rent Board Current Rates (1.6% for 3/1/26–2/28/27; File 261020 notice) | https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit | 2026-11-10 |
| S35 | CA Legislature | California SB 293 (2025–2026) — generational transfer exclusions | https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260SB293 | 2026-11-10 |
| S36 | CA Legislature | California AB 1516 (Chapter 72, 2025) — three-year claim filing, operative 01/01/2027 | https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260AB1516 | 2026-11-10 |
| S37 | CA SOS | California Secretary of State — PR26-85, 2026 wealth-tax initiative eligible | https://www.sos.ca.gov/administration/news-releases-and-advisories/2026-news-releases-and-advisories/california-secretary-state-shirley-n-weber-phd-announces-new-measure-eligible-november-2026-general-election-ballot-imposes-one | 2026-11-10 |
| S38 | CA SOS | California Secretary of State — Official Voter Information Guide, Proposition 40 | https://voterguide.sos.ca.gov/propositions/40/ | 2026-11-10 |
| S39 | CA SOS | California Secretary of State — 2026 General Election results (unofficial; certified by 12/11/2026) | https://electionresults.sos.ca.gov/ | 2026-11-10 |
| S40 | CA SOS | California Secretary of State — Qualified statewide ballot measures, 11/03/2026 | https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures | 2026-11-10 |
| S41 | CA PUC | CPUC — Net Energy Metering and Net Billing (NBT / D.22-12-056) | https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing | 2026-11-10 |
| S42 | CA PUC | CPUC — Decision 22-12-056, Net Billing Tariff | https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M500/K043/500043682.PDF | 2026-11-10 |
| S43 | CA PUC | CPUC — Decision 24-12-027, San Jose Water Company 2025–2027 GRC | https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M551/K128/551128522.PDF | 2026-11-10 |
| S44 | SFPUC | SFPUC — Proposition 218 notice, proposed FY2027–FY2028 water/sewer rates | https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposition-218-notice-proposed-water-and-sewer-rates | 2026-11-10 |
| S45 | SFPUC | SFPUC — Power Rates 2025-26 (Hetch Hetchy Power +10%) | https://sfpuc.org/accounts-services/water-power-sewer-rates/proposed-power-rates-2024 | 2026-11-10 |
| S46 | CA DOI | California Department of Insurance — Sustainable Insurance Strategy (avg premium $1,571) | https://www.insurance.ca.gov/01-consumers/180-climate-change/sustainable-insurance-strategy.Cfm | 2026-11-10 |
| S47 | CA DOI | California Department of Insurance — Residential Property Insurance Report (ZIP-level data) | https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/ | 2026-11-10 |
| S48 | HUD | HUD — FY2026 Small Area Fair Market Rent Schedule | https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY2026_Small_Area_FMR_Schedule.pdf | 2026-11-10 |
| S49 | HUD | HUD — Small Area Fair Market Rents data page | https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html | 2026-11-10 |
| S50 | CBO | CBO — Testimony on The Budget and Economic Outlook: 2026 to 2036 (03/11/2026) | https://www.cbo.gov/publication/62207 | 2026-11-10 |
| S51 | CBO | CBO — The Budget and Economic Outlook: 2026 to 2036 (02/11/2026) | https://www.cbo.gov/publication/62105 | 2026-11-10 |
| S52 | CBO | CBO — Projections of Deficits and Debt Under Two Scenarios With Higher Interest Rates (10/08/2026) | https://www.cbo.gov/publication/62809 | 2026-11-10 |
| S53 | CBO | CBO — The Budget and Economic Outlook: 2026 to 2036, Executive Summary (PDF) | https://www.cbo.gov/system/files/2026-02/61882-Executive-Summary.pdf | 2026-11-10 |
| S54 | CA BOE | California BOE — LTA 2025/023, assessed value / 2% annual cap | https://boe.ca.gov/proptaxes/pdf/lta25023.pdf | 2026-11-10 |
| S55 | CA SOS | California Secretary of State — 2026 General Election Official Voter Information Guide | https://vig.cdn.sos.ca.gov/2026/general/pdf/complete-vig.pdf | 2026-11-10 |
| S56 | City & County of SF | SF.gov — Annual Rent Increase for 3/1/26–2/28/27 Announced (1.6%) | https://www.sf.gov/news--annual-rent-increase-3126-22827-announced | 2026-11-10 |
| S57 | U.S. Bureau of Labor Statistics | BLS — Historical CPI-U, U.S. city average, all items (2024 archive) | https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202402.pdf | 2026-11-11 |
| S58 | Federal Reserve Board | Federal Reserve — Evidence from the Survey of Consumer Finances: 2007–09 recession | https://www.federalreserve.gov/pubs/feds/2010/201006/201006pap.pdf | 2026-11-11 |
| S59 | Federal Housing Finance Agency | FHFA — House Price Index: scope, repeat-sales method, and datasets | https://www.fhfa.gov/data/hpi | 2026-11-11 |
| S60 | Congressional Budget Office | CBO — The Long-Term Budget Outlook: 2024 to 2054 | https://www.cbo.gov/publication/59711 | 2026-11-11 |
| S61 | U.S. Bureau of Labor Statistics | BLS — CPI-U June 2022: 9.1% 12-month increase | https://www.bls.gov/news.release/archives/cpi_07132022.htm | 2026-11-11 |
| S62 | Congressional Budget Office | CBO — The Long-Term Budget Outlook: 2025 to 2055 | https://www.cbo.gov/publication/61187 | 2026-11-11 |

**Total: 62 official sources.** No commercial or third-party source is used as a fact.
Every table row on the site links to one or more of these IDs.

### T9 source findings and modeling boundaries (2026-11-11)

- S57 BLS historical CPI-U monthly archive supports the qualitative fact that inflation moves unevenly over time; the scenario does not claim a precise 1970s replay.
- S58 Federal Reserve Board staff working paper (explicitly preliminary; authors' views): estimates household home values fell 22% and corporate-equity values in household balance sheets fell 37% from December 2007 to June 2009. The page accurately labels these as the study's estimates, not official market-index returns.
- S59 FHFA defines its HPI as a weighted repeat-sales measure of single-family house-price movement; it is not a property-specific forecast.
- S60/S62 CBO long-term outlooks (2024 and 2025 editions) project inflation consistent with the Fed's 2% goal over 2026–2054 and 2027–2055, respectively; the 2075 endpoint is outside their horizon.
- S61 BLS June 2022 release: CPI-U increased 9.1% over the 12 months ending June 2022.
- The 2026–2075 annual path is explicitly synthetic: 3% home growth / 2.2% CPI / 7% equity is the smooth comparator; the stress years and returns are chosen stress inputs, not official data or a prediction. The 2045 assessment reset is a simplified assumption; Prop 19, future levies, and parcel charges are excluded. The page discloses that investor taxes/fees/withdrawals are excluded from its isolated portfolio path.

## Verification performed (line by line)

| Check | Method | Result |
| --- | --- | --- |
| Official source verification | Each of the 62 URLs fetched from the official domain and read; verified quotes recorded in `internal/research-notes.md` and this follow-up entry | PASS |
| Every table row has an official source link | `tools/verify.py` parses every `<tr>` in every `<tbody>` and requires `>=1` `<a class="src" href="http...">` | PASS — 984 / 984 rows across 30 HTML files |
| Source URLs are official | Every source link must be in the registry and on a government domain | PASS |
| No broken internal links | Every relative href resolved against the published tree; plus HTTP 200 check of 33 paths with a local static server | PASS — 0 failures |
| Navigation consistency | All 15 nav entries present on all 15 canonical pages | PASS |
| Unverified values left blank | `blank()` renders an empty official-value cell; `UNVERIFIED` status; published on Flagged for Review | PASS |
| Privacy scan | Regex scan of all published HTML for emails, phone numbers, street addresses, APN/parcel IDs, SSNs; placeholders used for all persons and the cash amount | PASS — 0 matches |
| Model integrity | 30 projection years; every money value divisible by $10; scenario/snapshot year keys match; exemption and thresholds consistent | PASS |
| Root mirror | Byte-identical comparison of root vs `docs/` for index, 14 pages, 2 assets, 7 JSON files | PASS |
| Prior-session work preserved | `archive-v2/` and three `internal/prior-sessions/` trees present | PASS |
| Table column integrity | Every `<tbody>` row has exactly as many `<td>` as the table has `<th>` (Status/Source columns included) | PASS |
| Black-swan model integrity | `tools/verify.py` validates 50 consecutive years, all scenario source IDs, $10-rounded money, 2045 investment start, and variable paths | PASS |
| Overall | `python3 tools/verify.py` after the black-swan addition | **10,031 checks, 0 failures** |

Full machine-readable log: `internal/verification-log.md`.

## Irregularities (all published on Flagged for Review)

| ID | Summary | Status |
| --- | --- | --- |
| IR-001 | Platform pins one branch; session branches/worktrees unavailable | needs review |
| IR-002 | SF supplied tax implies ~2.13% effective rate vs official 1.18268325% | needs review |
| IR-003 | Cupertino tax series inconsistencies; 2026 tax blank | needs review |
| IR-004 | User-supplied values unverifiable from official sources (privacy, no APN) | needs review |
| IR-005 | Decedent's principal residence unknown (Prop 19 eligibility) | needs review |
| IR-006 | Solar interconnection / NEM status and monthly profit unverified | needs review |
| IR-007 | Parcel-level insurance premiums unverified; CDI statewide average only | needs review |
| IR-008 | Future county rates and Prop 19 biennial cap unknown | needs review |
| IR-009 | Model assumptions are not official facts | needs review |
| IR-010 | CA conformity to federal step-up basis not separately confirmed | needs review |
| IR-011 | 2026 CA Proposition 40 outcome not certified until 12/11/2026 | needs review |
| IR-012 | No local inheritance/estate tax source found (blank, not asserted zero) | needs review |
| IR-013 | Draft IRS Form 709 instructions and BOE sample forms used | needs review |
| IR-014 | SF File 261020 banked-rent-increase proposal not enacted | needs review |
| IR-015 | SFPUC water/sewer increases proposed, not confirmed adopted | needs review |
| IR-016 | Rental income tax and depreciation recapture not fully modelled | needs review |
| IR-017 | Pages admin API inaccessible; root mirror used | needs review |

Site page: `pages/flagged-for-review.html` (each flag links its official sources).
`needs review` does not block the merge.

## Deployment log

| Item | Result |
| --- | --- |
| Pull request #6 | https://github.com/wingbangboozle1-lang/Tino4/pull/6 — "Integrate anonymized, source-verified inheritance decision dashboard (2040–2050 trust)" |
| Merge result | `gh pr merge 6 --merge` → **MERGED**, merge commit `f936c6c780139e72a311e9d2516d8a5f2c17ea50` at 2026-11-10T10:31:20Z |
| GitHub Pages build (PR #6) | `built` at 2026-11-10T10:32:37Z, no error, https://wingbangboozle1-lang.github.io/Tino4/ |
| Live-site spot check | `pages/executive-summary.html` served the new dashboard; a rendering-column defect was found in the generated tables, fixed, and redeployed via the follow-up PR recorded below |
| Follow-up fix | Table-structure fix (nested/duplicated `<td>`) + column-count verification; see the final Change log entry and the follow-up PR link below |
| Follow-up PR | https://github.com/wingbangboozle1-lang/Tino4/pull/7 — "Fix table column structure and add column-count verification (follow-up to #6)" |
| Follow-up merge result | `gh pr merge 7 --merge` → **MERGED**, merge commit `bf5bc946a6e8d137cef665d2ccc937c23d1d8d2e` at 2026-11-10T10:37:31Z |
| Final Pages deployment | Build `built` at 2026-11-10T10:37:53Z with no error; live root dashboard and `pages/executive-summary.html` fetched from https://wingbangboozle1-lang.github.io/Tino4/ and verified: correct content, aligned table columns, official source links present |
| Final verification (previous deployment) | `python3 tools/verify.py` on the regenerated tree: 5,958 checks, 0 failures; 750/750 table rows source-linked; column counts consistent |

## Change log

- 2026-11-10 — `s-0837be92`: created board; claimed T1/T2; recorded IR-001/002/003. Pushed claim.
- 2026-11-10 — `s-0837be92`: T1/T2 done; 50+ official URLs fetched and read; audited all five
  other session branches; claimed T3–T5.
- 2026-11-10 — `s-0837be92`: T3/T4/T5 done — deterministic generator (`tools/build.py`),
  56-source registry, 33 verified facts, 30-year projections 2026–2055, three-option decision
  model, 14-page dashboard, 17 flags. Every table row source-linked.
- 2026-11-10 — `s-0837be92`: T6 done — `tools/verify.py` 5,208 checks, 0 failures; privacy scan
  clean; local HTTP check 33/33 paths 200.
- 2026-11-10 — `s-0837be92`: T7 done — root mirror added (IR-017), `main` and three other
  session branches merged without discarding their work, prior sites archived, combined data
  re-verified line by line.
- 2026-11-10 — `s-0837be92`: T8 done — PR #6 opened, merged without approval, GitHub Pages build
  confirmed `built`. Live-site check found a table column defect; `tools/build.py` and
  `tools/verify.py` were fixed (column-count check added) and the site regenerated with
  5,958 checks / 0 failures. Follow-up PR recorded in Deployment log.

- 2026-11-10 — `s-0837be92`: follow-up PR #7 merged at `bf5bc94`; GitHub Pages build confirmed
  `built` with no error; live dashboard and executive-summary page fetched and verified. All
  tasks T1–T8 done. Final live site: https://wingbangboozle1-lang.github.io/Tino4/
- 2026-11-11 — `s-accb6bba`: audited merged site on `arena/accb6bba-tino4` (branched from `c4dbf8c`,
  PR #8 merge); `tools/verify.py` passes (5,958 checks, 0 failures). Claimed T9–T11: add the
  requested separate black-swan / 50-year stress-scenario section (historical episodes from
  official sources + modelled stress paths), re-verify, PR → merge → deploy. No file scope
  overlaps with any other active session.
- 2026-11-11 — `s-accb6bba`: T9/T10 complete. Added S57–S62 (BLS historical CPI and 2022 CPI release;
  Federal Reserve staff paper on 2008–09; FHFA HPI; CBO 2024/2025 long-term outlooks), an
  anonymized 2026–2075 stress model (baseline/stress home values, assessments, property tax,
  carrying-cost proxy, CPI index, and a 2045 sell-and-reinvest illustration), a historical
  evidence/assumptions section and dedicated subpage. Stress years are explicitly scenario
  choices, not forecasts. `python3 tools/build.py && python3 tools/verify.py`: 10,031 checks,
  0 failures; 984/984 table rows source-linked; 30 HTML files; privacy and mirror checks pass.
  Local `git diff --check` passes. No new personal data or unverified official values were added.
