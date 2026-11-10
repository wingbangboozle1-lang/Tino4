# R02 — Federal & California estate, inheritance and capital‑gains tax

Verified 2026-11-10 against IRS, FTB and California statute pages.

## 1. The headline answer on "how much can be inherited tax‑free"

| Layer | Threshold | Tax above it | Official source |
|---|---|---|---|
| Federal **estate** tax | **$15,000,000** per person for deaths in 2026 (basic exclusion, made permanent and inflation‑indexed from 2027 by P.L. 119‑21) | 40% top rate | IRS "Estate tax" filing‑threshold table — https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax |
| Federal estate tax, married couple | $30,000,000 with a **portability election filed on a timely Form 706** | 40% | Same page + IRS estate/gift "what's new" — https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax |
| California **estate** tax | none | 0% | FTB SB 378 analysis (pick‑up tax = $0) |
| California **inheritance** tax | none | 0% | Same |
| Annual **gift** exclusion (lifetime planning tool) | $19,000 per recipient in 2026 ($194,000 to a non‑citizen spouse) | — | IRS Rev. Proc. 2025‑32 §4.42 — https://www.irs.gov/pub/irs-drop/rp-25-32.pdf |
| Special‑use valuation cap (§2032A) | $1,460,000 reduction, 2026 deaths | — | Rev. Proc. 2025‑32 §4.41 |

**So the "threshold" that matters for this family is the federal $15M per person (2026 dollars).**
There is no state‑level number to cross.

**Projection of the threshold** (labelled arithmetic, not official): the statute indexes the $15M from
2027. If it grows with inflation at an assumed 2.5%/yr, the per‑person exclusion reaches roughly
**$24M by 2045** and **$27M by 2050**. At 3.0%/yr: ≈$26M by 2045, ≈$30M by 2050. These are
projections from a stated assumption, not published figures.

## 2. Basis: why the income‑tax side is usually the bigger number

| Rule | Effect | Source |
|---|---|---|
| IRC §1014 stepped‑up basis | Inherited property takes a basis equal to fair market value at death. Appreciation during the parents' lifetime is **never** taxed as income to the heir. | https://www.law.cornell.edu/uscode/text/26/1014 |
| Post‑death appreciation | Taxable to the heir at sale: 20% federal LTCG + 3.8% NIIT + 9.3% California (≈33.1% combined at the top) | IRC §1(h), §1411; CA RTC §17041 |
| IRC §121 home‑sale exclusion | $250,000 / $500,000 of gain on a **principal residence** excludable if the 2‑of‑5‑year ownership and use tests are met | IRS Topic 701 — https://www.irs.gov/taxtopics/tc701 |
| Rental depreciation | Depreciation taken (or allowable) after the inheritance reduces basis and is recaptured at 25% on sale | IRC §1250; IRS Pub 527 — https://www.irs.gov/publications/p527 |
| No step‑up on gifts | Gifting before death carries over the parents' low basis — the opposite of inheriting | IRC §1015 |

**Practical consequence:** the tax‑efficient order is *inherit, then decide* — not *gift, then inherit*.
Selling immediately after death produces ≈zero federal/California capital gain (basis = date‑of‑death
value). Every extra year of holding adds gain at ~33.1% up to the §121 cap.

## 3. California‑specific transaction taxes

| Item | Rate | Source |
|---|---|---|
| Documentary transfer tax (county) | $0.55 per $500 = **0.11%** of price | RTC §11911 — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11911 |
| San Francisco combined city‑county transfer tax, $1M–$5M tier | $3.75 per $500 = **0.75%** (tiers up to 6% above $25M) | SF Business & Tax Regs Code art. 12‑C; SF Assessor "Pay transfer tax" — https://www.sf.gov/pay-transfer-tax |
| California real‑estate withholding at closing | 3⅓% of gross sales price unless an exemption box is certified on **Form 593** (principal residence, zero gain, 1031 exchange) | Form 593 (2025) — https://www.ftb.ca.gov/forms/2025/2025-593.pdf |
| Gift transfers | Generally no transfer tax when the transfer is a bona fide gift | SF Assessor‑Recorder, "Pay transfer tax" |
| 1031 exchange out of state | California tracks the deferred gain annually on **Form FTB 3840** until recognized or death (clawback); the step‑up at death ends the tracking | Form FTB 3840 — https://www.ftb.ca.gov/forms/2024/2024-3840.pdf |

## 4. Retirement assets (if part of the "considerable money")

| Rule | Effect | Source |
|---|---|---|
| RMD age 73 | Traditional IRA/401(k) owner must start withdrawals at 73 | IRS — https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-required-minimum-distributions-rmds |
| Non‑spouse beneficiaries | 10‑year distribution window; distributions are ordinary income (federal + CA) — **no step‑up** | IRS Pub 590‑B; SECURE Act |

Inherited IRAs are the one asset class where the "tax‑free inheritance" story does *not* hold; they
should be modelled as ordinary income at the heir's marginal rate.

## 5. Law‑change watch on the federal side

| Proposal | Status | Source |
|---|---|---|
| Repeal of step‑up basis / tax unrealized gains at death (STEP Act) | Introduced in earlier Congresses; **not enacted** | Senate announcement (2021) — https://www.booker.senate.gov/news/press/booker-van-hollen-and-colleagues-announce-new-legislation-to-close-the-stepped-up-basis-tax-loophole |
| Estate‑tax repeal ("Death Tax Repeal Act") | Would reduce estate tax but **preserve** step‑up; not enacted as of this review | CRS overview — https://www.congress.gov/crs-product/R47113 |
| California wealth‑tax proposals (AB 259, 2023) | **Died in committee** — 01/31/24 | leginfo bill status — https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202320240AB259 |
| California estate tax referendum proposals (SB 378, SB 726) | Never enacted | FTB analyses (above) |

The model keeps current law as the base case and quantifies the step‑up‑repeal scenario separately
(see the Legislation page) because that single change is worth more than every other item combined.
