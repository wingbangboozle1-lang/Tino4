# Anonymized inheritance decision workspace

This repository builds a static, source-linked decision framework for a
Cupertino-area home expected to transfer through a family trust around
2040-2050 ("Property A") and an already-owned San Francisco Outer Sunset
triplex ("Property B"). The analysis ranks live / rent / sell / mixed paths,
stresses the reinvestment of any sale proceeds against real 1928-2025 annual
returns, and prints the deadlines that decide the money.

## Privacy policy (highest-urgency constraint)

- **Placeholders only.** Property A / Property B / Heir / Trustor replace all
  identifying labels. No addresses, parcel numbers, personal names, postal
  codes, emails or phone numbers appear anywhere in the generated site.
- **Everything is rounded to the nearest $10** (owner anti-tracing rule), so
  rounded tables cannot be matched to a single parcel online. The one
  exception is the statutory Proposition 19 exclusion amount $1,044,586.
- **Owner-provided figures are marked** with an `owner` badge and remain
  unverified by definition; unknown values are left blank and flagged.
- **Automated enforcement.** `tools/verify.py` rejects any currency amount
  that is not a multiple of $10 (except the whitelisted statutory figure),
  any address/postal-code/email/phone pattern, any non-official external
  link, and any remote resource. This applies to every tracked text file.
- **Git history is not clean.** Pre-rounding figures remain in roughly 195
  historical commits; see `tools/history-scrub-plan.md` for the owner
  executable remediation steps. The current tree is clean; the history is not.

## Site contents

- `index.html` — what would change the answer, headline numbers, ranked answer.
- `pages/executive-summary.html` — the compressed ranking with risks attached.
- `pages/decision-analysis.html` — path matrix, cash flows, wealth horizons and
  local-only what-if controls.
- `pages/questions.html` — 24 questions with discovery steps and impact ratings.
- `pages/decision-log.html` — twelve decision-quality suggestions with a local-only review queue.
- `pages/suggestions.html` — reviewable suggestion queue (choices stay local).
- `pages/projections.html` — year-by-year value, tax and cash-flow projections.
- `pages/property-tax.html` — Prop 13/19 rules plus rounded assessment histories.
- `pages/operating-costs.html` — water, solar, insurance, maintenance lines.
- `pages/black-swan.html` — verified crash history, a regime map with CBO
  2036/2055 official baselines, and a real-data stress table for five entry
  strategies including 24-36 month Treasury parking.
- `pages/phased-investing.html` — the Treasury staging plan mechanics, a ladder
  reinvestment-risk panel and a synthetic-path simulator.
- `pages/estate-thresholds.html` — 2026/2027 federal amounts and California status.
- `pages/inheritance-process.html` — deadline timeline from death to filings.
- `pages/law-watchlist.html` — current law vs live proposals.
- `pages/attorney-cpa-brief.html` — one-page printable adviser brief.
- `pages/flagged-for-review.html`, `pages/glossary.html`, `pages/sources.html`,
  `pages/privacy.html` — review queue, definitions, source register, privacy rules.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The site uses no remote scripts, fonts, images, APIs, analytics or form
submission; a restrictive CSP enforces `connect-src 'none'`. The what-if tools
recompute locally and store nothing. The stress tools use the transcribed
1928-2025 annual-return series (NYU Stern compilation, flagged secondary) and a
clearly-labeled synthetic drawdown simulator; neither is a forecast or a
personal investment recommendation.

## Evidence and limitations

- Every data-table row carries a source link and an evidence badge
  (`verified`, `owner`, `derived`, `model`, `assumption`, `secondary`,
  `missing`, `guidance`). A source supports only its stated scope.
- Primary law: California Revenue and Taxation Code §§63.2, 480, 218, 18662,
  Probate Code §16061.7, BOE Publication 801 and Letter to Assessors
  2025/009, Public Law 119-21 §70106, IRS estate/gift pages, Publications
  551/523/527/559, Santa Clara County Tax Rate Book 2025-2026, SF Treasurer,
  Federal Reserve History, TreasuryDirect, HUD, BLS, CBO, FHFA, SEC, CDI,
  CPUC, CSLB, California Secretary of State.
- Insurance premiums and a few parcel-specific facts remain blank until
  written quotes and private records exist; the flagged page lists each one.
- Re-verify law, deadlines and market inputs with qualified advisers at the
  actual transfer date.
