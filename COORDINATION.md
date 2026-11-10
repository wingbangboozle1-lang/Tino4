# Coordination board

Integration session: `session-9dcf1e9f`; branch: `arena/9dcf1e9f-tino4` (session branch fixed by workspace). Single integration session; no overlapping claims known. A new session must read this board before claiming files. Date: 2026-11-10.

| Task | Status | Owner | File scope |
| --- | --- | --- | --- |
| Source research and verification | done | session-9dcf1e9f | sources.html, taxes.html |
| Property and cost analysis | needs review | session-9dcf1e9f | properties.html, costs.html |
| Projection and decision analysis | needs review | session-9dcf1e9f | projections.html, decisions.html |
| Inheritance workflow | done | session-9dcf1e9f | process.html |
| Integration, privacy, navigation and review list | done | session-9dcf1e9f | index.html, flagged.html, assets/style.css, COORDINATION.md |
| Link validation, PR, merge and Pages confirmation | done | session-9dcf1e9f | tests/validate.py, COORDINATION.md |

`needs review` denotes unverified inputs and is published on Flagged for Review. No other session's edits were overwritten or conflicts encountered.

## Source review and irregularities

* Verified [BOE Prop 19](https://www.boe.ca.gov/prop19/) and [BOE parent-child guidance](https://www.boe.ca.gov/pdf/pub800-1.pdf): principal-residence requirements, filing, the adjusted limit, and partial reassessment. The old base does **not** necessarily remain unchanged.
* Verified [BOE assessment guidance](https://boe.ca.gov/pdf/pub800-10.pdf): growth limit and exceptions.
* Verified [IRS estate tax](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax) and [2026 adjustments](https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill): exclusion, filing threshold and portability; [IRS basis](https://www.irs.gov/pub/irs-pdf/p551.pdf) for general inherited basis and exceptions.
* Verified [FTB](https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html): inheritance income treatment. [California estate tax statute](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=13302) describes the link to federal state-death-tax credit; future treatment needs review.
* Verified [SF Rent Board](https://www.sf.gov/news--annual-rent-increase-3126-22827-announced), [California rental statute](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12.), [SF 2025–26 tax rate resolution](https://sfbos.archive.sf.gov/sites/default/files/r0447-25.pdf), [insurance comparison guidance](https://www.insurance.ca.gov/0400-news/0100-press-releases/2018/release138-18.cfm), and [CPUC solar report](https://www.cpuc.ca.gov/-/media/cpuc-website/divisions/office-of-governmental-affairs-division/reports/2025/2025-sb-695-report_093025.pdf).
* Parcel values, historical assessments and costs, rent, trust details, basis, allocation, insurance and future returns are not independently verifiable; withheld rather than asserted. Actual assessments, exemption eligibility, and mixed-use allocation need review. No numerical winner or estate headroom can be certified.
* The first claim commit contained user-supplied financial estimates in this public repository's Git history, although no names, addresses or APNs were included. They have been removed from the current board and site, and this session's branch history was replaced before merging. GitHub may retain the original commit by its ID or in caches; repository history rewrite cannot guarantee complete removal.
* Prior draft incorrectly assumed complete Prop 19 base preservation and categorically disqualified the mixed-use property; corrected before integration.

## Integration status

* Pull request: https://github.com/wingbangboozle1-lang/Tino4/pull/1 merged successfully on 2026-11-10 (merge commit `678e4a060bd2c391b397740d7029493003cc0584`).
* `python3 tests/validate.py` passed for all local links and the official-source link in every data row; `git diff --check` passed. Static HTML/CSS requires no build step. Official research links were fetched or reviewed; no automated guarantee of future external availability.
* Pages configured to publish from `main` root. The deployment for merge `678e4a060bd2c391b397740d7029493003cc0584` succeeded: https://github.com/wingbangboozle1-lang/Tino4/actions/runs/42796366372 . The public landing page and tax page were fetched and confirmed. Live site: https://wingbangboozle1-lang.github.io/Tino4/ . GitHub issued non-fatal runner/action deprecation notices.
