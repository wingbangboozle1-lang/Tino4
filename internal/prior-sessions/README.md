# Archived prior-session trees

These directories are the complete trees of earlier parallel-session branches, preserved by the
2026-11-10 integration so that no session's work was discarded. They are **superseded** by the
canonical site and are not linked from it.

## Privacy remediation — 2026-11-11 (session `s-356f911b`, task T13)

GitHub Pages serves this repository from `main` at the root with `.nojekyll`, so every path in the
repository is a public web page, including this directory. Two archived trees
(`arena-6acab13a/`, `arena-ce2391b3/`) still carried user-supplied assessment and tax figures that
were **not rounded to the nearest $10**, contrary to the project's privacy rule.

What was changed, in place, so the archives stay intact:

| Change | Scope |
| --- | --- |
| Every user-supplied assessed value and tax amount rounded to the nearest $10 (half-up) | 19 files, 248 replacements |
| Ratios that had been computed from the unrounded pair (implied effective tax rates) recomputed from the rounded pair, because a 4-decimal ratio can otherwise pin the unrounded numerator | same files |
| Statements that the tables were reproduced "verbatim" corrected | `arena-6acab13a/data/property-tax-history.json`, `arena-6acab13a/research/r01-property-tax-inheritance.md` |

What was **not** changed: model outputs in these archives were not regenerated. They were already
rounded to $10 and were computed from the original inputs, so they can differ from a fresh run by
a few dollars. `arena-fd984e93/` and `archive-v2/` were scanned and needed no change.

What this does **not** fix (owner action required): earlier commits and the original session
branches on the remote still contain the unrounded figures. See IR-019 on the coordination board.
