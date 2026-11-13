# Independent audit — `arena-95cf9249` (2026-11-13)

**Session:** `arena-95cf9249` · **Branch:** `arena/95cf9249-tino4` (platform-fixed; IR-001 applies)
**Audited trees:** `main` @ `c5dcb6b` (baseline) and `main` @ `42aa3bb` (includes PR #49, merged 2026-11-13T11:57:24Z while this audit was in progress; the merged tree was re-verified).
**Scope claim:** C95C-1…C95C-6 in `COORDINATION.md`. Read-only on all shared outputs; changes confined to `_s95cf9249/**`, one `_config.yml` exclude line, and this session's board section.

## 1. Conclusion

No defect was found in the published statutory amounts, owner-supplied rounded tables, status labels, or privacy boundary of the live site. Two **change requests** (not defects — coverage/clarification improvements) are logged to the shared-output owners, and one **PR-body typo** is noted (no content defect). The live deployment matches the verified build.

## 2. Baseline and merged-tree verification runs

| Tree | Build | Verifier | Unit tests | Reproducibility |
| --- | --- | --- | --- | --- |
| `main` @ `c5dcb6b` | 17 pages, 561 CSV rows, no household inputs | 21 HTML, 821 rows, 3,842 links, 66 blanks, **0 failures** | 14/14 OK | diff empty |
| `main` @ `42aa3bb` (rebased, incl. PR #49) | 17 pages, 561 CSV rows | 21 HTML, **869 rows, 3,905 links, 80 blanks, 0 failures** | 14/14 OK | diff empty |

## 3. Independent checks (own implementation, separate from `tools/verify.py`)

Script: `_s95cf9249/audit/check.py`; raw output: `_s95cf9249/audit/check-output.txt`.

- 21 published HTML files; **869/869 table-body rows carry at least one official-source link** (3,905 link instances) and a status badge.
- Status distribution: synthetic 617, verified 70, guidance 75, missing 69, assumption 37, owner-supplied 1.
- **0 visible dollar amounts ≥ $1,000 that are not multiples of $10** (site text and the 561-row synthetic CSV).
- Privacy patterns (ZIPs 95014/94122, "Cupertino", neighbourhood "Sunset", "San Francisco", email, phone, SSN, APN wording): **0 true hits**. Two regex false-positives on the word "sunset" refer to the 2026 TCJA *sunset* (tax law), not a neighbourhood. No city, ZIP, address, parcel, name or contact detail is published.

## 4. Direct official-source verification (fetched by this session, 2026-11-13)

Full matrix with quotes: `_s95cf9249/audit/evidence.md`.

| # | Official page (fetched directly) | Confirmed |
| --- | --- | --- |
| 1 | IRS — *What's new — Estate and gift tax* (irs.gov) | WFTC (P.L. 119-21, signed 2025-07-04) amends §2010(c)(3): basic exclusion **$15,000,000 for 2026** |
| 2 | IRS — Newsroom IR-2026-133 (2027 inflation adjustments, 2026-11-05) + Rev. Proc. 2026-35 | 2027 basic exclusion **$15,480,000** ("up from $15,000,000 for 2026"); annual gift exclusion **$20,000 for 2027**, "up from **$19,000 for calendar year 2026**" |
| 3 | Cal. RTC §63.2 (leginfo.legislature.ca.gov, chunks 0–1) | Operative parent-child exclusion statute (post-2021-02-16). (d): new taxable value = taxable value + max(0, FMV − [taxable value + $1,000,000 adjusted]); (a)(1)(A)–(C): principal-residence + homeowners'-exemption conditions and **enrollment of the DOC-date base (factored) when eligibility is later lost**; (e)(9): transfers through inter vivos or testamentary **trusts qualify**; (f): 3-year claim window |
| 4 | BOE — *Proposition 19 Fact Sheet* Pub 801 (boe.ca.gov) | Allowance window amounts: $1,000,000 (2021–23), $1,022,600 (2023–25), **$1,044,586 (2025-02-16 – 2027-02-15, LTA 2025/009)**; worked example: FBYV $300,000 + FMV $1,500,000 → excluded amount $1,300,000 → difference $200,000 → **new taxable value $500,000** (= max(FBYV, FMV − allowance)); BOE-19-P claim, 3-year filing, homeowners' exemption within one year |
| 5 | SF Gov — Rent Board current rates (sf.gov) | Allowable rent increase **1.6% for 2026-03-01 – 2027-02-28** (and history 1.4% / 1.7%); **File 261020** (10%/yr combined banked + capital-improvement cap) posted 2026-11-09 as **proposed, not enacted** |
| 6 | CPUC — Net Energy Metering and Net Billing (cpuc.ca.gov) | NBT since 2023-04-15 under D.22-12-056; export compensation "usually lower than the retail rate"; **nine-year legacy period** for original NBT customers; NEM tariffs closed to new enrollments; applies to PG&E/SCE/SDG&E territories only |
| 7 | Live site — `wingbangboozle1-lang.github.io/Tino4/pages/estate-thresholds.html` | Deployed page serves the merged content, incl. the 2026 gift-exclusion row ($19,000, Verified); synthetic 2040–2050 exclusion illustrations compound from the last official amount ($15,480,000 @ 2027) — arithmetic re-checked (e.g. 2045 @ 2.5% = $24,143,520 ✓, @ 4% = $31,359,640 ✓) |

Cross-checked arithmetic on PR #49's owner-supplied history and projection (rounded to $10 and compounded from rounded inputs): spot-checked A 2024/2025/2026 and all B rows, plus the 3%/2% projection column at 2026/2030/2035/2040/2045/2050/2076 — **all values reproduce** (e.g. A FMV 2045 = $3,100,000 × 1.03¹⁹ = $5,435,870 ✓; A FBYV 2045 = $550,540 × 1.02¹⁹ = $802,030 ✓; 2050 tax = 1% × $6,301,660 = $63,020 ✓).

## 5. Change requests (logged in `COORDINATION.md`; not edited by this session)

| ID | To | Request | Why (verified basis) |
| --- | --- | --- | --- |
| CR-C95C-01 | Shared-output owners | Add the **RTC §63.2 family-home exclusion path** next to the rental path in the illustrative forward projection on `pages/property-tax.html` (currently the projection models only full reassessment at transfer, labeled "rental path"). At the page's own 2045 assumption: FMV $5,435,870; taxable value $802,030; allowance $1,044,586 → family-home base = FMV − allowance ≈ **$4,391,290** (1% base levy ≈ $43,910/yr) vs rental base $5,435,870 (≈ $54,360/yr) — ≈ **$10,450/yr** difference, growing with the biennial allowance indexation. Also note §63.2(a)(1)(C): if the transferee later loses eligibility (e.g. converts to rental), the DOC-date base (factored) is enrolled — material to the live-then-rent comparison the owner's brief asks for. | RTC §63.2(d)(2)(A)-(B) + Pub 801 worked example, fetched 2026-11-13 (see evidence.md) |
| CR-C95C-02 | Shared-output owners | The projection uses the **1% base levy only**; the page's own owner-supplied A history implies an effective rate of ≈ 1.33–1.37% (tax ÷ assessment, 2014–2025). Add a disclosed effective-rate variant or note so decision totals are not understated ~25–33%. Pub 29 documents that the 1% general levy plus voter-approved debt and charges form the total bill. | Pub 29 (already cited on the page) + owner-supplied history ratios |
| CR-C95C-03 (note, no change) | — | PR #49's description text "2026 annual gift exclusion 9,000" is a **body typo only**; the published row says **$19,000 (Verified)** and is confirmed correct by IR-2026-133 fetched directly. The board log of `s-24be15f7` states $19,000. | IR-2026-133 (fetch #2 above) |

## 6. Acceptance notes on PR #49 (merged during this audit)

- Owner-supplied tax/assessment history and operating-cost figures are published **rounded to $10 with no identifier**: rows say "Property A"/"Property B" only — no ZIP, city, address, unit count tied to a location, name, or parcel (independently re-scanned, §3).
- The F17 reconciliation (verifier narrative checks relaxed where they conflicted with the owner brief's $10-rounding requirement; identifiers remain prohibited) is consistent with the owner's instructions and is documented on the Flagged for Review page.
- Known-since-IR-003 owner-data irregularities (missing A 2026 tax, repeated tax totals, tax growth ≠ assessment growth) remain disclosed on the page as items to reconcile against original county bills.

## 7. Limits

This audit verifies **published content against official sources and the owner brief's technical rules** (rounding, sourcing, privacy, reproducibility). It does not verify the owner's private facts (which remain unverified by design), does not appraise either property, and does not constitute tax, legal, insurance, appraisal or investment advice. The change requests are suggestions for the shared-output owners and the owner to review before implementation.
