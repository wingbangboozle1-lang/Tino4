# R01 — California property tax & inheritance law (verified against official sources)

Verified 2026-11-10. Every row below was read on the linked official page. Anything I could not
confirm on an official page is marked **[UNVERIFIED]** and appears on the site's Flagged for Review page.

## 1. The two separate questions on an inherited California house

| Question | Answer | Official source |
|---|---|---|
| Does the heir owe an *inheritance / estate* tax at the state level? | No. California has no inheritance tax and no state estate tax; its old "pick‑up" tax equals a federal credit that was repealed, so it collects zero. | FTB bill analysis SB 378: https://www.ftb.ca.gov/tax-pros/law/legislation/2019-2020/SB378-032519.pdf |
| Does the *property tax* reset to market value? | Yes, unless the transfer qualifies for the Proposition 19 intergenerational exclusion. | RTC §63.2: https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2 |

## 2. Proposition 19 — the controlling statute (RTC §63.2)

Effective for transfers **on or after February 16, 2021**. It replaced the old Prop 58/193 exclusion.

| Rule | Detail | Source |
|---|---|---|
| Eligible property | Only (a) the transferor's **principal residence** that becomes the transferee's principal residence, or (b) a **family farm**. | RTC §63.2(a)(1)–(2) |
| Occupancy deadline | Transferee must occupy **within one year** of the transfer and **continually** thereafter. | RTC §63.2(a)(1)(A) |
| Claim deadline (exemption) | File for the homeowners' exemption (BOE‑266) **within 1 year** of transfer. | RTC §63.2(a)(1)(B) |
| Claim deadline (exclusion) | File BOE‑19‑P **within 3 years**, or before transfer to a third party, whichever is earlier. | BOE LTA 2026/026 |
| Value cap | New taxable value = FBYV + (FMV at transfer − (FBYV + $1M adjusted)). The $1M is **not** a flat exemption; it is a cushion above the existing taxable value. | RTC §63.2(d); BOE LTA 2026/026 |
| If the heir moves out | The exclusion is **removed**, and the market value established at the transfer date (factored forward) is enrolled on the next lien date. | RTC §63.2(a)(1)(B)–(C) |
| Rented units of a multi‑unit building | Only the unit occupied as the principal residence qualifies; the rest is reassessed at full cash value. | BOE LTA 2026/026, Q5 |
| Long‑term leases (35 yrs+) | Not eligible (rented property cannot take the homeowners' exemption). | BOE LTA 2026/026, Q31 |
| Legal entities / LLCs | **Not eligible** — the exclusion reaches real property, never entity interests. Moving the house into an LLC after claiming also kills the exclusion. | RTC §63.2(e)(8); BOE LTA 2026/026, Q32–Q35 |
| Transfers through a **trust** | **Eligible** — the trust is looked through to present beneficial ownership. | BOE LTA 2026/026, Q39 |
| Late filing | Prospective relief only (starts with the lien date of the year the claim is filed); no refund of prior years. | RTC §63.2(f)(3)(A); BOE LTA 2026/026, Q23 |

**The $1M cushion, as officially adjusted:**

| Transfer date window | Applies $ | Source |
|---|---|---|
| 2021‑02‑16 → 2023‑02‑15 | $1,000,000 | BOE LTA 2025/009 |
| 2023‑02‑16 → 2025‑02‑15 | $1,022,600 | BOE LTA 2025/009 |
| 2025‑02‑16 → 2027‑02‑15 | **$1,044,586** | BOE LTA 2025/009 — https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf |
| Next adjustment | February 2027, then every other February 16, indexed to the FHFA California HPI | RTC §63.2 / Cal. Const. art. XIII A §2.1(c)(4) |

## 3. Proposition 13 — the arithmetic behind every projection

| Element | Value | Source |
|---|---|---|
| General levy | 1% of taxable value, plus voter‑approved bond debt | Cal. Const. art. XIII A §1; BOE |
| Annual inflation factor cap | 2% (the lower of CCPI change or 2%) | RTC §51(a)(1) |
| 2026‑27 factor | **1.02** (CCPI +3.307%, capped at 2%) | BOE LTA 2026/002 — https://www.boe.ca.gov/proptaxes/pdf/lta26002.pdf |
| Homeowners' exemption | $7,000 off the assessed value, owner‑occupied only, **not** for rented/vacant property | RTC §218 |
| Typical Santa Clara County ad valorem rate | ≈1.193% (1% + bond debt); varies by Tax Rate Area | SCC Assessor Annual Report 2025‑26; SCC Controller Tax Rate Book FY2025‑26 — https://controller.santaclaracounty.gov/property-tax-distribution/property-tax-rate-book |
| San Francisco secured rate FY2025‑26 | **1.18268325 per $100** of assessed value | SF Board of Supervisors file 25‑0876 (Controller) — https://sfgov.legistar.com/View.ashx?GUID=AC93184C-32A4-4DA1-887D-09FC319785E7&ID=14779286&M=F |

> Note: the county **rate book** (not a blog) is the authoritative source for a parcel's TRA rate.
> A parcel's exact rate cannot be resolved here because no APN was provided (privacy — we do not
> want it). The model therefore uses the county‑typical rate and shows the +/-0.1% sensitivity.

## 4. Step‑by‑step: what inheriting through a trust actually looks like

Order of operations, each step tied to its official requirement:

| # | Step | Who / form | Timing | Source |
|---|---|---|---|---|
| 1 | Death certificate; trustee confirms the trust becomes irrevocable and identifies the successor trustee | Trustee | Days | Probate Code (trust admin) |
| 2 | Inventory & date‑of‑death appraisal of both properties and all accounts (this value becomes the heir's **income‑tax basis**) | Trustee / appraiser / probate referee | Weeks | IRC §1014 — https://www.law.cornell.edu/uscode/text/26/1014 |
| 3 | Determine **which house was the parents' principal residence** — this decides which property can qualify for Prop 19 | Trustee + county assessor records | Immediate | RTC §63.2(e)(5); BOE LTA 2026/026 Q1 |
| 4 | Decide who occupies which house (occupancy is a hard condition, one year, no exceptions) | Heirs | Before distribution | RTC §63.2(a)(1)(A); LTA 2026/026 Q7 ("There are no exceptions to this rule") |
| 5 | Record the deed / trustee's deed distributing the real property out of the trust | Trustee → County Recorder | Days–weeks | RTC §63.2; LTA 2026/026 Q39 (trust look‑through) |
| 6 | File **BOE‑266** homeowners' exemption for the occupied home | Heir → County Assessor | **≤1 year** from death/transfer | RTC §63.2(a)(1)(B) |
| 7 | File **BOE‑19‑P** parent‑child exclusion | Heir → County Assessor | **≤3 years**, before any third‑party sale | BOE LTA 2026/026 |
| 8 | Pay the **supplemental** tax bill on any reassessed portion (e.g., the rented units) | Heir | Two installments after the supplemental notice | RTC §75 et seq. |
| 9 | If the estate is large enough, file **Form 706** federal estate return (asset values roll up; portability election requires a timely 706) | Executor/trustee | 9 months (+6 extension) | IRS Estate tax page — https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax |
| 10 | Keep both houses out of an LLC; keep records of every capital improvement (adds to basis) | Heir | Ongoing | LTA 2026/026 Q32–Q35 |
| 11 | Annual: claim/maintain the homeowners' exemption; re‑verify every lien date that the occupant still lives there | Heir | Every Jan 1 | RTC §63.2(a)(1)(B)–(C) |

**Failure modes that cost real money** (all sourced above): not occupying within 12 months; putting the
house in an LLC; renting the whole property out; letting the occupying heir move out (the whole
exclusion unwinds and the *market value at the transfer date, factored forward*, is enrolled).

## 5. What the user‑supplied tables imply (arithmetic check, no official source needed)

Implied effective rate = property tax ÷ tax assessment, from the supplied rows:

| Property | Implied range | Official county rate | Read |
|---|---|---|---|
| Cupertino 95014 | 1.33% – 1.41% (2014–2025) | ≈1.193% | ~0.14–0.22 pts unexplained → likely fixed direct assessments or a different value column **[FLAGGED I1b]** |
| San Francisco 94122 | 1.96% – 2.13% (2016–2025) | 1.1827% | ~2× the official rate → second parcel, direct charges, or transcription **[FLAGGED I1]** |

Both are flagged, not "corrected": the supplied figures are reproduced verbatim and the model uses
the official rate.
