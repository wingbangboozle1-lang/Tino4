# Independent audit — privacy-first two-property decision brief

**Audit date:** 2026-11-12 (UTC)
**Published baseline:** `main` at `a67bebd` (PR #47), after privacy-first PRs #45–#46
**Audit branch:** `arena/a3de132b-tino4`
**Purpose:** independently compare the published product with the owner's stated requirements; re-check official-source claims and calculations; inspect privacy and publication boundaries; record evidence-backed gaps. This report does not reproduce household amounts or identifiers.

## Executive result

The deployed **Pages product** has been substantially corrected by PR #45: the public generator no longer reads the old private-input packages; numerical examples are clearly synthetic; unsupported household cells are blank; recommendations are conditional; source/status coverage, a question register and a review-only suggestions workflow are present. I re-fetched all 29 URLs in the product's registered source ledger, checking the relevant chunks for long IRS/BOE materials. The consequential current-law amounts and deadlines sampled below matched their cited official scopes. The build, link/status, privacy-token and arithmetic checks pass on this audit branch.

**Critical residual:** the GitHub repository is public (`isPrivate: false`). Jekyll excludes `COORDINATION.md` from the Pages artifact, but the current public `COORDINATION.md` itself contains case-derived financial/property detail; the older public commit/tree and PR history also retain removed case-derived packages. Thus “not in the Pages site” is not the same as “not published in the public repository.” Neither deletion from the current build tree nor `noindex` removes that exposure. No other session's board text was edited, no history was rewritten, and no visibility change was made. This needs an owner-coordinated privacy decision.

**Brief-completion gap:** actual household costs, values, tax history and a household-specific best-profit plan are not supplied by this version. The site intentionally shows a synthetic model and blank household results rather than treating owner-specific estimates as official or verified. It therefore demonstrates the requested calculations but does not answer “what is the best plan?” for this household; that answer remains blocked on verified private evidence and an authorized secure workflow.

## Scope and method

- Read the current README, `_config.yml`, PR #45 integration audit, source ledger and current generator/model; parsed the generated pages and table rows rather than relying on the earlier PR summary alone.
- Compared content with the owner-brief requirements recorded in `COORDINATION.md`: executive summary and decision rationale; quantified costs/projections and nearest-$10 displays; house/assessment/tax projections; live/rent/sell strategies; black-swan treatment; an information/answers/missing-evidence register; suggestions gated before implementation; source-linked claims; and privacy boundaries.
- Re-fetched all 29 official-source URLs listed in `_7eff7e24/evidence.py` on the audit date. For long sources, checked the claim-relevant chunks (including Form 706, Pub. 527 and BOE Proposition 19 material). This is not a line-by-line audit of every page of those publications or a legal opinion.
- Inspected GitHub repository visibility, the current `main` tree/configuration, prior tree history, PR #45's deletion diff, GitHub Actions verification and the Pages build API. Pages API reports commit `a67bebd` as `built` with no error. This turn did not make a separate live-browser fetch of the deployed URL.
- Built the privacy-genericized content on this branch and ran the builder, semantic/technical verifier, arithmetic/content tests, JavaScript syntax check and whitespace check. Browser dependencies are not present in this checkout; the content-only edits did not receive a second Chromium run. PR #46's preceding 17-page desktop/mobile smoke test is recorded in the board.

## Requirements trace

| Owner requirement | Current product | Audit result |
| --- | --- | --- |
| Executive summary and why a decision matters | Executive summary plus a conditional, non-execution warning | **Covered**, with an explicit limitation: no household winner is claimed. |
| Compare live, rent and sell/invest alternatives | Decision-analysis page and six conditional financial suggestions | **Covered as decision paths**, not quantified household outcomes. The synthetic columns are not evidence of actual returns. |
| Clear numerical projections for home value, assessed value and property tax | 2026–2076 fictional projections; 11 illustrative transfer years; separate market/assessed/tax columns | **Partially covered.** These are synthetic only. Annual tax is the illustrative 1% base levy, not a total bill; future allowance and law are not forecast. Actual A/B history and bills are blank. |
| Costs and dollar amounts rounded to $10 | Synthetic examples and official amounts displayed at $10 granularity; explicit warning about rounding | **Covered for displayed numbers.** Rounding is not anonymization and does not verify an input. |
| “Best plan and why” | Provisional research priority plus evidence needed to change direction | **Not resolved for the household.** A conditional test of “retain current housing; compare selling A” is not a profit-maximizing recommendation. Actual taxes, proceeds, rents, costs, risk tolerance and objective are unknown. |
| Long-horizon / black-swan reasoning | Seven synthetic regimes and 50-year illustrative projections; no historical replay, probability or success rate claimed | **Mechanics covered, forecast not covered.** No local verified return series or official 50-year forecast supports a household result. |
| Questions, known/unknown information and discovery steps | 16 prioritized evidence questions with missing answers and accountable roles | **Covered as a discovery register.** These are not verified household facts. |
| Suggestions before implementation | Separate financial/product queues, default “Not reviewed,” browser-local choices only | **Covered.** The UI does not execute financial or site changes and is not a shared approval record. |
| Official-source support and status labels | 29-source ledger; table rows carry a status and official context link | **Structurally covered; claim scope is limited.** A linked source does not independently prove a household fact, invented assumption or recommendation. |
| Privacy and publication boundaries | Synthetic-only Pages build, blank household cells, local-only review preferences, no external runtime calls; source jurisdictions disclosed | **Pages boundary substantially covered; public Git boundary fails**, as detailed in F01 below. |

## Findings

### F01 — Critical: public Git still exposes case-derived information

**Evidence:** `gh repo view` reports the repository is public. The current `main` version of the root `COORDINATION.md` contains case-derived property and financial detail in prior session records. `_config.yml` excludes that file from Jekyll, which keeps it out of the Pages artifact but does not restrict browsing/cloning from GitHub. The current `main` tree no longer contains `_c07ccf45/` or `_s09b3ffa0/`, but the earlier public tree/history and PR #45 deletion diff still contain those packages. The board itself also records that history/PR/cache/fork exposure may persist. This report deliberately does **not** repeat the underlying values.

**Impact:** a claim that “the public site has no household values” can be accurate while a broader claim that the public repository contains none is not. Exact historic details may be discoverable from the public repository even if they are absent from the Pages site and excluded from search indexing.

**Response in this branch:** clarified the site Privacy page and README to say that the *Pages artifact* is synthetic-only while the current public Git tree/history may retain case-derived detail. The report points out the boundary without copying values. No other session's board records, public history, repository visibility or remote branches were changed.

**Owner decision needed:** decide whether to change repository visibility and/or commission a coordinated history/cache/PR remediation, considering forks, clones, archives and collaborator disruption. A current-tree edit alone cannot guarantee erasure. Until decided, do not put further private records or amounts in this repository or its issues.

### F02 — High: household-specific result requested by the brief remains unavailable

The public site correctly marks actual household costs, property amounts, tax bills, rent, insurance, debt, repairs, tax allocation and result cells as missing. The calculator's $1 million example, $200,000 old assessment, costs, rent, rates and returns are invented model parameters. The illustrative 2040–2050 exclusion growth paths are not law. They explain arithmetic only. Therefore the page cannot establish the best household path or supply verified actual household projections. This is an intentional, privacy-safe boundary—not a finding that the synthetic model is a household forecast. A genuinely private, authorized evidence workflow and adviser-verified inputs would be prerequisites to closing it.

### F03 — Medium: source/status tests are not substantive legal verification

The verifier proves that rows have registered official links and statuses, links are on the allowlist, internal targets resolve and display rules pass. It cannot determine whether every sentence is entailed by its linked source. The methodology and audit flags disclose this limitation. My direct re-fetch of the 29 registered URLs found the key claims below consistent with their stated scopes; that does not certify every legacy claim, every exception or future-law application.

### F04 — Low: model is intentionally simplified and some “cost” columns are not all-in costs

The decision model applies invented effective rates and a simplified depreciation/sale treatment. It omits real tax brackets/stacking, debt, fees, estate allocation, passive-loss limits, local closing charges, withdrawals and actual underwriting. The property projection's 1% levy excludes bonds, direct charges, exemptions and supplemental timing. These are disclosed in Methodology/Flagged for Review; the scenarios must not be read as after-tax household forecasts.

### F05 — Resolved in this branch: case-specific narrative remnants on Pages

The Questions and related copy still presented several scenario attributes as facts, and the property-tax page exposed a property-by-year history outline even though its values were blank. The wording and historical outline have been generalized, while preserving the A/B distinction, conditional rental/personal-use paths, the full Missing register and legal rules. A regression guard now checks the generated public copy for case-specific narrative patterns, an explicit fractional unit-cost allocation, and property-specific historical year rows. This does not scrub the public Git board/history described in F01.

## Official-source spot-check results

The currently cited consequential source scopes matched the re-fetched official pages, with the following limits kept explicit in the product:

- IRS estate materials: the 2026 filing threshold is $15,000,000; filing tests consider the gross estate plus adjusted taxable gifts/specific exemption; portability is an election. IRS 2027 release states the 2027 basic exclusion of $15,480,000 and annual gift exclusion of $20,000. Form 706 instructions provide the 9-month filing deadline, possible 6-month filing extension, and 40% top marginal bracket.
- Inherited property: IRS FAQ says basis is generally death-date FMV or a properly elected alternate value, and selling above basis creates taxable gain. This supports the conditional language, not a tax-free-sale claim.
- California property tax: BOE Prop. 19 fact sheet gives the exact $1,044,586 allowance for transfers Feb. 16, 2025–Feb. 15, 2027, the residence/relationship conditions and claim timing. The site’s $1,044,590 display is a nearest-$10 display, not a filing amount. BOE Publication 29 supports the 1% base levy plus voter-approved debt and generally capped 2% annual factored-base growth; it does not support treating an all-in bill or 2% whole-bill increase as universal.
- Trust and death-transfer timing: Probate Code §16061.7 contains a generally 60-day notification rule with event, later-discovered-recipient and vacancy clocks; RTC §480(b) provides 150 days for nonprobate death transfers, including trust transfers, while probate timing differs.
- California transfer-at-death taxes: RTC §§13301–13302 must be read together; the Controller reports no California estate-return requirement for deaths after 2004 because the federal state-death-tax credit was eliminated. This does not exempt later property or income taxes.
- Rental/income and investments: IRS Pub. 527 confirms personal-use rental expenses require allocation and are not automatically deductible by unit count; IRS capital-gains/NIIT pages support the limited statutory descriptions; SEC, Treasury and FDIC sources support risk, bill-tax and deposit-coverage caveats, not model returns.
- Local and operating costs: the Rent Board’s 1.6% rate is only for Mar. 1, 2026–Feb. 28, 2027 and its Nov. 9 combined-cap proposal is expressly not enacted. CDI shopping material does not give a property-specific quote; CPUC solar/water pages provide tariff/regulatory context, not a household bill. Those values remain blank.

## Calculation, labels and publication checks

- The synthetic model uses one fictional $1,000,000 starting asset, a fictional $200,000 old assessment and an explicit 2026–2076 horizon (51 annual endpoints, 50 growth steps). Transfer-year examples switch between 2040–2050; the future Prop. 19 allowance is held at an invented constant for illustration and labelled Synthetic.
- I independently checked one-year mechanics: the equity path applies its invented total return, dividend tax, reinvested after-tax dividend basis and terminal-gain tax; the bill path applies the stated after-tax yield; rental first-year cash includes vacancy, the base levy, operating costs, management and no tax benefit from a modelled loss. The outputs matched the generator to the displayed $10 rounding. This validates arithmetic under the given assumptions only.
- All seven stress scenarios and numeric regime rows are labelled **Synthetic**. Missing household results are blank and statused **Missing**; contextual source links do not promote those values to Verified. Guidance rows do not present legal mandates as household outcomes.
- Jekyll excludes the work/coordination files from Pages; the public-site verifier found no `.nojekyll` bypass, prohibited location tokens, ZIP-like display or broken internal targets. GitHub repository visibility remains public, so this is not a repository confidentiality control.

## Changes and verification on this branch

A3DE-2 made only generic-copy/privacy-boundary edits and semantic checks; no financial parameters or legal-source claims changed. The historical property-tax year outline was reduced to two blank, non-dated A/B register rows. The current branch rebuild produces:

```text
Built 17 public pages and 561 synthetic CSV rows. No household inputs loaded.
Checked 21 HTML files, 821 sourced/statused rows, 3,842 official links,
66 blank cells, 561 synthetic CSV rows.
0 technical failures. These checks do not certify legal or household financial accuracy.
```

`python3 -m unittest discover -s tools -p 'test_*.py' -v`: 14 tests passed (including the new generic-copy regression and an explicit Jekyll exclusion for this audit directory). `node --check assets/app.js` and `git diff --check` passed. No browser test was run on these text-only edits because Chromium/Playwright dependencies are absent locally; the previous merged PR #46 recorded desktop/mobile smoke checks.

## Conclusion

The **Pages content proposed in this branch** communicates its synthetic-only scope more accurately and provides a useful, auditable planning framework. It does not supply the owner's actual-number/best-plan answer. More urgently, the **public Git repository is still not private**: the current coordination file and earlier public history contain case-derived material that Pages exclusions cannot hide. The owner must decide on repository/history remediation; this session intentionally did not rewrite history or alter other sessions' coordination records.
