## What this does

Replaces the placeholder case content with the actual decision brief, built from an official-source ledger that this session read.

**The recommendation, on these rounded inputs:** plan to occupy Property A and keep Property B as it is; hold a signed sell-and-reinvest plan as the fallback. Renting A is not recommended, because it loses operating cash every year for twenty years and forgoes the tax base that the family-home exclusion preserves.

## Numbers that drive it

| Line | Value |
| --- | --- |
| Renting A, twenty-year after-tax total | $10,977,570 |
| Selling A at transfer and reinvesting, after tax | $14,568,100 |
| Rental operating cash over the twenty years | −$856,010 |
| Tax saved by occupying instead of renting | $883,660 |
| Assessment if occupied vs rented (2045) | $5,893,150 vs $9,705,070 |
| Deepest published California drawdown / recovery | −41.0% / 12.8 years |

The occupancy case survives because the tax saving exceeds the rental operating loss. If insurance clears roughly $12,000 a year, that advantage is erased, and the page says so.

## Site

15 pages plus 7 redirect stubs, a dashboard, a year-by-year CSV (204 rows, every value a multiple of $10), a 22-question register with discovery paths, 19 review-only proposals, 14 flagged items, and a source ledger. Every table row carries an official `.gov` link and a status badge; unsupported cells are blank and flagged rather than estimated.

## Verification

- `tools/build.py` runs self-checks then generates; `tools/verify.py` reports 22 HTML files, 426 sourced/statused rows, 897 official link instances, 24 blank-cell registers, 204 CSV rows, **0 failures**.
- `tools/test_case.py` has **29 regressions**, including a hard privacy gate and the statutory allowance indexation.
- CI runs the tests, rebuilds, verifies, and **fails if the committed output differs from a fresh build**.

## Defects found and fixed while reading the output

1. **Prop 19 allowance indexation was wrong.** The model grew the allowance at a 4% house assumption; RTC 63.2 and BOE LTA 2025/009 index the $1,000,000 base to the FHFA California index every second February 16. Fixed; the 2045 tax saving fell from $1,244,570 to $883,660, and the prose followed because it is computed.
2. All five invented shock paths printed the **same** ten-year value (a `**0` bug).
3. The decision page left **all seven** path results blank.
4. A black-swan row promised a fifty-year window table that was **never emitted**.
5. One **dead official link** (`pub801.pdf` → 404) repointed to the live page.
6. The rebase onto current `main` left **conflict markers inside eleven generated pages**; they were re-emitted from source.

## Privacy

No name, address, ZIP, parcel or account number appears on any page. The verifier enforces that, plus a check that the raw un-rounded owner figures are never published. F01 on the flagged page now states the concrete residual exposure: this **public repository's** `COORDINATION.md` still records both ZIPs, both counties and the exact federal rent benchmarks for those ZIPs, written by earlier sessions. It is excluded from the Pages artifact but is in the tree and the history. No history rewrite was attempted; that needs an owner decision.

## Answered change requests

- **CR-C95C-02** does not apply: the model never used a 1% levy. It applies the effective rate the owner's own bills imply (A 1.32–1.41%, B 1.74–2.14%), which is stated on the page.
- **CR-C95C-01**: the structural request was already met, and checking it surfaced defect 1 above.

Not legal, tax, insurance, appraisal or investment advice.
