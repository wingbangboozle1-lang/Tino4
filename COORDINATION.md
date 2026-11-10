# COORDINATION.md — Shared Task Board

This file is the shared coordination board for all agent sessions working on this
repository. It lists each task, its status (`unclaimed`, `in progress`, `done`,
`needs review`), the owning session ID, and the files it touches.

**Read this file before starting work.** Claim a task by adding your session ID and
file scope to the table below, then **commit and push the claim immediately**.
Never start a task another session has claimed. Keep file scopes non-overlapping.
If you need a file owned by another session, log the request here instead of
editing it. Make small, frequent commits, and run `git pull --rebase` before every
push. Resolve merge conflicts without discarding another session's work and log
what happened. When a task is finished, record its sources, verification
performed, and irregularities here and mark it `done`. Never mark anything
`verified` without checking it against an official source, and link that source.
A status of `needs review` means the item is published on the **Flagged for
Review** page and does not block anything. If a session crashes or a claim is more
than 60 minutes old with no commits, another session may take over and note the
handoff in the log.

- **Repository:** `wingbangboozle1-lang/Tino4`
- **Integration/working branch:** `arena/0837be92-tino4` (platform-fixed branch; see
  IR-001)
- **Site published from:** `main` → `/docs` (GitHub Pages)
- **Board last updated:** 2026-11-10 (UTC)
- **Active session ID:** `s-0837be92`

## Platform constraint (IR-001)

This environment pins every session of this conversation to the single branch
`arena/0837be92-tino4` and forbids creating, switching to, or pushing any other
branch (including `session-<id>/<task>` branches or separate git worktrees).
Therefore the requested branch-per-session isolation is implemented instead by
**non-overlapping file scopes within the one branch**, recorded below. All claims
and commits below are made on `arena/0837be92-tino4`. The pull request is opened
from `arena/0837be92-tino4` → `main` and merged there. Logged as an irregularity
on the Flagged for Review page. This does not change the deliverable.

## Task board

| Task ID | Task | Status | Owner session | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| T1 | Repo scaffolding, coordination board, privacy/anonymization policy, README, `.gitignore`, Pages settings | in progress | `s-0837be92` | `COORDINATION.md`, `README.md`, `.gitignore` | 2026-11-10 |
| T2 | Research & official source register (federal/state/local tax law, thresholds, proposed law changes, insurance, utilities, inflation) | in progress | `s-0837be92` | `internal/research-notes.md`, `internal/source-register.md` | 2026-11-10 |
| T3 | Verified-facts table data (every row links an official source) | unclaimed | | `docs/data/facts.json` | |
| T4 | Projection & scenario model data (property tax, value, operating costs, inheritance thresholds, 2026–2055) | unclaimed | | `docs/data/projections.json`, `docs/data/model-inputs.json` | |
| T5 | Site pages: executive summary, property tax, operating costs, inheritance law, decision analysis, step-by-step process, sources, flagged for review, privacy | unclaimed | | `docs/*.html`, `docs/pages/*.html`, `docs/assets/**` (excluding shared index/nav) | |
| T6 | Line-by-line verification pass, link check, build check | unclaimed | | `internal/verification-log.md` | |
| T7 | Final integration: shared table data, `docs/index.html` + navigation, merge branches (n/a – single branch), re-verify combined data, build with no broken links, publish to GitHub Pages | unclaimed | | `docs/index.html`, `docs/data/**` (integration only) | |
| T8 | Pull request → `main`, merge, confirm GitHub Pages deployment, record PR link and merge result here | unclaimed | | `COORDINATION.md` (final log only) | |

## Session registry

| Session ID | Branch | Started (UTC) | Notes |
| --- | --- | --- | --- |
| `s-0837be92` | `arena/0837be92-tino4` | 2026-11-10 | First session. Repo contained only a 7-byte `README.md` at `f195ee6`. No other claims existed. Acting sequentially as task owner and final integration session; see IR-001. |

## Source register (populated as tasks finish)

| Source ID | Official source (URL) | Used for | Verified (UTC) |
| --- | --- | --- | --- |
| IRS-706 | https://www.irs.gov/pub/irs-pdf/i706.pdf | 2026 federal basic exclusion amount $15,000,000; Form 706 filing threshold; basic credit $5,945,800 | 2026-11-10 |
| IRS-IRM-263 | https://www.irs.gov/irm/part3/irm_03-012-263r | Estate/gift tax exemption amounts by year 2012–2026 | 2026-11-10 |
| FTB-GIFT | https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html | California: inheritance not included in income | 2026-11-10 |
| BOE-NR25-02 | https://www.boe.ca.gov/news/2025/nr-25-02.htm | Prop 19 exclusion cap = FBYV + $1,044,586 (2/16/2025–2/15/2027); 1-year homeowner exemption filing | 2026-11-10 |
| BOE-LTA25015 | https://www.boe.ca.gov/proptaxes/pdf/lta25015.pdf | Prop 19 conditions: transferor principal residence, transferee occupancy within 1 year, withdrawal consequences | 2026-11-10 |
| BOE-PUB29 | https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf | Prop 13: 1% rate + voter-approved bonds; 2% assessment cap | 2026-11-10 |
| SCC-ASSESS-2026 | https://files.santaclaracounty.gov/exjcpb1521/2026-04/assessment-information-2026-booklet-english-3-23-26-web.pdf | Santa Clara County: reassessment at date of death for living-trust property, PCOR, supplemental assessment, typical 1.1488% rate example | 2026-11-10 |

_(Register is extended as each task completes.)_

## Verification log

| Task | Verification performed | Result |
| --- | --- | --- |
| T2 (partial) | Fetched IRS Form 706 instructions (Rev. July 2026), IRS IRM 3.12.263, FTB gifts-and-inheritance page, BOE news release 25-02, BOE LTA 2025/015, Santa Clara County 2026 assessment booklet directly from official domains and read the relevant lines | Pass – 7 sources confirmed live |

## Irregularities log

| ID | Description | Status |
| --- | --- | --- |
| IR-001 | Platform pins this session to one branch; requested `session-<id>/<task>` branches and git worktrees cannot be created. Mitigated via exclusive file scopes. | needs review (published) |
| IR-002 | User-supplied San Francisco property-tax figures imply an effective rate of ~2.14% of the stated tax assessment, materially above the official FY 2025-26 secured rate of 1.18268325%; the tax figures also rise ~2.9–6.2%/yr while the stated assessment rises only 2%/yr. Cause cannot be confirmed from an official source. | needs review (published) |
| IR-003 | User-supplied utility, insurance, market-value, and rental-income figures have no official source; they are treated as unverified model inputs, not as sourced facts. | needs review (published) |

## Change log

- 2026-11-10 — `s-0837be92`: created board (repo had no board). Claimed T1 and T2 with exclusive scopes. Recorded IR-001/002/003. Committed and pushed claim.
