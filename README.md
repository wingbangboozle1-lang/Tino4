# Tino4 — Inheritance Decision Dashboard

A static, privacy-first decision dashboard for a planned **2040–2050 trust inheritance** of
a residential property (`Property A — Cupertino 95014`), with a second property
(`Property B — San Francisco Outer Sunset 94122`) held as the household's residence and
rental-income context.

**Live site:** https://wingbangboozle1-lang.github.io/Tino4/

## Privacy rule (highest priority)

No personal information appears anywhere in this repository or on the website. All
personally identifying details are replaced with placeholders (`[DECEDENT]`,
`[BENEFICIARY]`, `[TRUST]`, `[TRUSTEE]`, `[CASH AMOUNT]`). Properties are referred to only
by placeholder label and ZIP code — no street addresses, parcel/APN numbers, account
numbers, trustee names, or household composition. Figures supplied in the request are
treated as **unverified user-provided inputs** and are published only on the
**Flagged for Review** page as placeholders/model inputs, never as verified facts.

## Contents

| Path | Purpose |
| --- | --- |
| `COORDINATION.md` | Shared task board: claims, statuses, sources, verification, irregularities, PR log |
| `docs/` | Canonical GitHub Pages site (landing dashboard + category subpages) |
| `index.html`, `pages/`, `assets/`, `data/` | Byte-identical root mirror, because this repository's Pages source is `main` `/` and the Pages admin API was not reachable (IR-017) |
| `.nojekyll` / `_config.yml` | Root `.nojekyll` keeps the legacy Pages build a pure static copy; `_config.yml` is a fallback exclusion list if Jekyll is re-enabled. Internal notes are never linked from the site and contain no personal information. |
| `archive-v2/` | Prior session's merged site, preserved intact during final integration |
| `internal/prior-sessions/` | Trees of the other parallel-session branches, preserved intact during final integration |
| `docs/data/` | Machine-readable facts, model inputs, projections, decision outputs, source register |
| `tools/build.py` | Deterministic generator: builds all JSON and all static HTML from verified sources |
| `tools/verify.py` | Line-by-line verification: source links per row, internal links, privacy scan |
| `internal/` | Internal-only working notes (not published by GitHub Pages) |

## Method

- Only official sources (`.gov` and state/local government domains) are used as facts.
  Every table row carries a link to the official source.
- Where a value cannot be confirmed from an official source, the **Official value** cell is
  left blank and the item is flagged as `UNVERIFIED` on the Flagged for Review page.
- Model projections are explicitly labelled as model outputs (not facts); each row cites the
  official rule used in the derivation. All currency is rounded to the nearest **$10**.
- Reproduce with `python3 tools/build.py && python3 tools/verify.py`. No manual input is
  required.

> This is an informational analysis, not legal or tax advice. Confirm all parcel-specific
> facts with the county assessor and a licensed tax professional before acting.
