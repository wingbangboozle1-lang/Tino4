# Two-property decision brief

**Live:** https://wingbangboozle1-lang.github.io/Tino4/

A privacy-first static dashboard using a generic inherited-asset (**Property A**) versus
already-owned-property (**Property B**) scenario. Includes an executive summary,
live/rent/sell comparison, missing-evidence register, review-only suggestion queue, costs and
insurance, tax/process guidance, current-law watchlist, source ledger and flagged irregularities.

## Evidence and privacy boundary

* 29 official sources directly retrieved/read on **2026-11-12**. Short passages, retrieval chunks
  and exact verification scope are in `_7eff7e24/evidence.py` and the site's source ledger.
* Every published table body row links to an official source and carries a status:
  **Verified**, **Guidance**, **Missing**, or **Synthetic**. A contextual link is not verification
  of the row's recommendation, household applicability or invented model parameters.
* Unverified household numeric cells in the **generated Pages content** are **blank**, never zero
  or guessed. That site does not reproduce private tax history, rent, utility estimates, property
  values, addresses, ZIPs, parcels or individuals. Rounded numbers can still identify a property
  in combination. The synthetic layer uses fictional inputs. Separately, the case layer publishes owner-supplied figures only after rounding every dollar to $10, with an Owner-supplied status label; projection outputs are labeled assumptions, never forecasts.
* Synthetic examples: 2026–2076 (50 compounding years, 51 endpoints), all 11 illustrative transfer
  years 2040–2050, seven economic regimes, and a 20-/50-year simplified after-tax comparison.
  All displayed dollars round half-up to $10. They are not officially verified forecasts,
  insurance quotes, tax returns, backtests or recommendations to execute.
* **Public repository warning:** The GitHub repository is public. The current root
  `COORDINATION.md`, earlier Git history, PR diffs, other branches, deployment caches, forks and
  clones may contain case-derived detail. Jekyll exclusions keep coordination/work files out of
  the Pages artifact; they do not restrict access to the public Git repository. Obsolete
  case-derived packages were removed from the current build tree, but that is not deletion of
  earlier disclosures. Owner-coordinated visibility/history/cache review remains necessary. No
  history rewrite or repository-visibility change was performed automatically.

## Reproduce and test

Python 3, standard library only. No install or network needed.

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

`tools/build.py` uses only `_7eff7e24/{content,evidence,model}.py`. There are no private inputs.
It emits 17 pages, four legacy redirects, and `assets/projections.csv` (561 case rows, every dollar rounded to $10, each labeled CASE_PROJECTION_ASSUMPTIONS). Assets are local;
there are no analytics, remote fonts or browser API calls. Optional suggestion review choices
are saved only in local browser storage; they do not implement changes or constitute shared approval.

The verifier checks internal targets/anchors, every row's source/status, official URL allowlist,
missing cells, $10 dollar rounding, prohibited identifiers, row statuses and official links, CSV horizon, HTML structure,
publication exclusions, absence of `.nojekyll`, and private-package independence. Arithmetic
unit tests independently check the calculation rules and stress paths. These technical checks
are **not** a claim of comprehensive legal verification or financial accuracy for a household.

## Layout

```
index.html, pages/, assets/    public static product
_7eff7e24/evidence.py          source extracts and failed-retrieval register
_7eff7e24/content.py           reviewed public content
_7eff7e24/model.py             deterministic synthetic examples (no household inputs)
_7eff7e24/AUDIT.md             repository audit findings and limits
tools/                        builder, verifier, regression tests
COORDINATION.md               shared task board and deployment record (not site content)
```

## Decision boundary

The provisional research priority is to test retaining existing housing and selling A into a
risk-appropriate diversified portfolio, but **no household profit-maximizing winner is established**.
Trust terms, eligibility, estate size/gift history, debts, insurance, achievable rent, repairs,
actual tax rates and future law remain unverified. The questions page assigns discovery tasks to
trustee/advisers; they cannot be resolved by public research without private records and authority.
Never upload those records to this public repository or public issues.

Not tax, legal, investment, appraisal or insurance advice. No sale, move, rent increase, trust
distribution or investment is executed by this site.
