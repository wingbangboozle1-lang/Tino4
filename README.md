# Two-property decision brief

**Live:** https://wingbangboozle1-lang.github.io/Tino4/

A privacy-first static dashboard using a generic inherited-asset (**Property A**) versus
already-owned-property (**Property B**) scenario. Includes an executive summary,
live/rent/sell comparison, missing-evidence register, review-only suggestion queue, costs and
insurance, tax/process guidance, current-law watchlist, source ledger and flagged irregularities.

## Evidence and privacy boundary

* 36 official-source entries: 29 sources were directly read on **2026-11-12** and 7 additional
  sources on **2026-11-13**. Short passages, per-source retrieval dates/chunks and verification
  limits are in `_7eff7e24/evidence.py` and the site's source ledger.
* Every published table body row links to an official source and carries a status:
  **Verified**, **Guidance**, or **Missing**. A contextual link is not verification of a row's
  recommendation, household applicability or future outcome.
* Unverified household amounts and future projections in the **generated Pages content** are
  **blank**, never zero or guessed. The site does not publish invented model-dollar examples,
  private tax history, rent, utility estimates, property values, addresses, ZIPs, parcels or
  individuals. The 2026–2076 register shows annual rows with all household monetary cells
  intentionally blank; it is a template, not a forecast.
* Public monetary figures are limited to directly sourced current-law amounts and are rounded
  half-up to the nearest $10 for display. Exact statutory figures control filings. Historical
  economic observations and current statutory rates are not projected through 2040–2050.
* **Public repository warning:** The GitHub repository is public. The current root
  `COORDINATION.md`, earlier Git history, PR diffs, other branches, deployment caches, forks and
  clones may contain case-derived detail. Jekyll exclusions keep coordination/work files out of
  the Pages artifact; they do not restrict access to the public Git repository. Obsolete
  case-derived packages were removed from the current build tree, but that is not deletion of
  earlier disclosures. Owner-coordinated visibility/history/cache review remains necessary. No
  repository-wide history rewrite or repository-visibility change was performed.

## Reproduce and test

Python 3, standard library only. No install or network needed.

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

`tools/build.py` uses only `_7eff7e24/{content,evidence}.py`. It does not import the legacy
synthetic sandbox model or read private inputs. It emits 17 public HTML pages and four legacy
redirects; no monetary projection CSV is generated. Assets are local; there are no analytics,
remote fonts or outbound network/API calls. `app.js` uses local storage only for optional review
choices and the browser print dialog; choices do not implement changes or constitute shared
approval. The retired model and arithmetic tests remain in the public repository as isolated test
fixtures, but are not imported by the builder or shipped in Pages. Their parameters are not
verified or approved household assumptions; Jekyll exclusions do not hide them from Git users.

The verifier checks internal targets/anchors, every row's source/status, the official-source
allowlist, blank projection cells, current-law monetary and percentage allowlists, nearest-$10
displays, prohibited identifiers, HTML structure, publication exclusions, absence of `.nojekyll`,
and independence from private packages and the retired model. Unit tests exercise the isolated
legacy arithmetic, but those values do not feed public pages. These technical checks are **not**
comprehensive legal verification or a household financial result.

## Layout

```
index.html, pages/, assets/    public static product
_7eff7e24/evidence.py          source extracts and failed-retrieval register
_7eff7e24/content.py           reviewed public content
_7eff7e24/model.py             retired isolated arithmetic sandbox; not in public build
_7eff7e24/AUDIT.md             repository audit findings and limits
tools/                        builder, verifier, regression tests
COORDINATION.md               shared task board and deployment record (not site content)
```

## Decision boundary

**No household profit-maximizing winner or preferred path is established.** The site compares
living in, renting or selling A while keeping B separate, but leaves all household amounts blank.
Trust terms, eligibility, estate size/gift history, debts, insurance, achievable rent, repairs,
actual tax rates and future law remain unverified. The questions page assigns discovery tasks to
trustee/advisers; they cannot be resolved by public research without private records and authority.
Never upload those records to this public repository or public issues.

Not tax, legal, investment, appraisal or insurance advice. No sale, move, rent increase, trust
distribution or investment is executed by this site.
