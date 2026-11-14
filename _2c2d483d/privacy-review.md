# Privacy boundary review — 2026-11-14

## Executive finding

**The current public pages are generic after PR #58, but the public repository and historical refs are not yet proven privacy-safe.** The public HTML now omits household-specific values, locations, histories, and projections. A new scan of the checked-out tree found no supplied postal-code, street-address, or email-pattern hits in the rendered site or the current coordination file. However, legacy tracked source/model files still retain rounded owner-supplied financial inputs and derived model code; the repository is public. Earlier coordination/history and prior Git objects, pull-request diffs, branches, forks, clones, caches, or deployments may retain older case details. A clean current site is not a clean repository history.

This report deliberately does not repeat any location identifier or household amount.

## Checks performed

- Repository: `wingbangboozle1-lang/Tino4`; visibility checked with `gh api repos/wingbangboozle1-lang/Tino4` on 2026-11-14 — **public**.
- Public site after PR #58 and PR #59: `python3 tools/build.py` regenerates a generic site without reading household inputs; `python3 tools/verify.py` checks all eight public HTML files and finds no case-like values or projection CSV. The site's privacy page states the history caveat.
- Current rendered HTML and current coordination board were scanned for supplied postal codes, the two named localities/neighbourhood, street-address patterns, and email patterns. No such direct identifier pattern was found in those current outputs.
- The current tracked repository still contains legacy model/source modules with rounded owner-specific figures and derived values, even though the current builder does not import or publish them. These files remain accessible to anyone who can view the public repository.
- The current checkout is shallow and pinned to an Arena feature branch. It does not contain enough history for a complete object/ref audit or repository-wide history rewrite.
- Current-tree validation after the privacy remediation: `python3 tools/build.py`, `python3 tools/verify.py`, one privacy regression test, and `git diff --check` passed. These checks do **not** prove that legacy tracked files or old Git objects have been removed, that claims are all source-entailed, or that external copies are gone.

## Work completed in parallel

PR #57 added a case-labeled phased-investing stress tool, attorney/CPA print sheet, glossary, mixed-path navigation, and first-screen answer-changing factors. PR #58 then replaced household-specific public output with generic guidance and removed the case projection CSV; PR #59 corrected the phased-investing drawdown interpretation. The current public site is therefore a generic decision framework rather than a household-specific numerical recommendation. This is an intentional privacy-first boundary; the individual projections and dollar comparisons requested in the original brief are not currently published.

## Status and limits

- This session did not inspect private tax records, perform owner/address research, or add any personal data.
- This session did not rewrite Git history, force-push, change repository visibility, or delete another session's files.
- The public pages are generic, but the public Git working tree still contains legacy case-specific inputs in excluded/internal source modules. Excluding files from Jekyll only controls the site artifact; it does not make a public GitHub repository private.
- Old Git objects, PR diffs, refs, forks, clones, caches, and previous deployments are outside the reach of a normal PR. No history cleanup is claimed.

## Recommended remediation, in order

1. Treat previously public location and financial material as exposed. Do not add new documents, account details, exact values, parcel records, or identifying context to this public repository.
2. Have the repository owner/admin decide whether to make the repository private immediately. That can limit future access but cannot recall copies already made, and it is not a substitute for history cleanup.
3. After owner/admin authorization, remove obsolete case-specific inputs and derived models from the current public tree, preserving only a separately approved secure private copy where needed. Confirm the public builder still works without importing them.
4. With owner/admin authorization and a coordinated maintenance window, follow GitHub's sensitive-data removal procedure to rewrite affected history, force-update every relevant branch/tag/ref, address pull-request references, and request GitHub cache/support cleanup where available. Coordinate with collaborators to replace old clones. Verify forks and external copies separately; they cannot be erased by a normal merge.
5. Re-run a whole-tree and published-artifact privacy scan after remediation. A clean site build is not a clean Git history.

Official GitHub guidance: [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Release gate

**The public page output has been generalized, but repository-level privacy remediation remains `needs review`.** Do not describe the repository as fully anonymized or its pre-rounding history as scrubbed until owner-authorized current-tree and history/ref/cache reviews are completed and independently checked.
