# Final privacy and evidence audit

**Audit date:** 2026-11-13 (UTC)
**Scope:** Final generated Pages candidate and its build/source boundary on this branch.
**Disposition:** Technical checks pass; repository-history privacy remains unresolved. The candidate has not been merged or deployed.

This report intentionally does not reproduce personal, household, location, or case-specific details from the public coordination board, pull requests, or repository history. No private records, addresses, or parcels were researched.

## Executive result

The branch-generated static Pages artifact now contains a generic comparison of inherited Property A and already-owned Property B, kept distinct. It publishes no household monetary projections, no winner or preferred financial path, and no model-generated projection CSV. The annual register keeps its year labels while every household amount cell is explicitly blank. Current-law amounts are limited to the reviewed allowlist and carry date/scope caveats.

This finding applies to the **candidate built from this branch**, not the presently served Pages deployment. GitHub reports the repository and Pages site as public, with Pages sourced from `main`; the branch has not been deployed. The Pages API status is asynchronous and does not verify the rendered content in a user's browser.

## Scope and evidence limits

Reviewed the public-content source, builder dependencies, generated HTML, verifier, regression tests, Jekyll exclusions, runtime assets, and the source ledger. The ledger contains 36 entries and five failed-retrieval records. Seven supplemental entries are dated 2026-11-13; earlier entries are dated 2026-11-12. The ledger records excerpts, retrieval chunks, scope limitations, and failed attempts.

The review is not a line-by-line audit of every page of every long publication, a complete survey of legislation, or legal, tax, appraisal, insurance, or financial advice. An official link supports only the stated source scope; it does not verify household facts or a future outcome. In particular, current-year legal amounts are not extended as future thresholds; introduced bills are not treated as law; and historical FHFA/CPI or shorter-horizon CBO material is not presented as a property or long-term portfolio forecast.

## Findings

### F-01 — Resolved in this candidate: unverified public projection outputs

- `tools/build.py` imports reviewed content and evidence only; it does not import the retired arithmetic model or read private inputs.
- The builder no longer creates the synthetic projection CSV. That tracked CSV is deleted, and the verifier fails if a copy is present.
- The former numerical comparison outputs have been replaced with blank household cells and formula/evidence requirements. The candidate’s annual register has 51 year rows; each row has five household monetary cells, all blank and explicitly marked as missing.
- Property A remains the inherited asset; Property B remains separately identified as already owned. The content does not assume that inheriting A automatically transfers or resets B. The decision pages state that evidence is insufficient to rank paths.
- The retired model and its arithmetic tests remain in the public source repository for legacy testing, but the builder does not use them and Pages does not publish them. Their test parameters are not verified or approved household assumptions. Jekyll exclusions do not hide these source files from Git users.

### F-02 — Critical, unresolved: public Git and historical disclosure boundary

The GitHub API reports the repository as public. The current coordination file and earlier Git objects, pull-request diffs, branches, forks, clones, archives, and caches may contain case-derived material. Jekyll exclusions and `noindex` affect neither Git access nor existing copies. This checkout is shallow, so it cannot establish that all historical objects or copies have been found.

No repository-visibility change, repository-wide history rewrite, public branch cleanup, fork removal, or cache/CDN purge was performed. The audit branch was rebased onto current `main`; that branch-level update does not remove prior public objects. A current-tree edit cannot guarantee removal of earlier disclosures. GitHub’s visibility guidance also warns that making a GitHub Free repository private can unpublish its Pages site and does not make existing public forks private. The repository owner must decide on any coordinated remediation and deployment plan. Until then, do not put private records in this repository or its public issues.

### F-03 — High, unresolved: isolated legacy model remains Git-visible

The legacy model and its arithmetic tests remain in the public repository even though they are excluded from Pages and disconnected from the builder. The candidate’s blank-value guarantee therefore applies to the Pages artifact, not to every historical or developer/test file in public Git. This audit does not represent those fixtures as household facts. If the publication rule is intended to cover every file visible in Git, the owner should remove or separately archive the legacy sandbox and decide whether a history remediation is warranted.

### F-04 — Medium, unresolved: substantive and deployment verification limits

The verifier checks structure, registered links, status labels, allowed current-law numeric displays, explicit blank projection cells, internal targets, privacy patterns, and publication exclusions. It cannot prove that every sentence follows from its cited source. No browser-based visual or interactive smoke test was run for this candidate. The latest GitHub Pages API check reported `building` from `main`, not this branch; a prior direct live-page request failed with a TLS/SSL EOF, so end-user live rendering remains unverified.

## Technical validation on this branch

Commands were run after rebuilding the generated pages:

```text
python3 tools/build.py
Built 17 public pages. No household inputs or monetary projections loaded.

python3 tools/verify.py
Checked 21 HTML files, 293 sourced/statused rows, 863 official links,
312 blank cells, and the blank 2026–2076 projection register.
0 technical failures. These checks do not certify legal or household financial accuracy.

python3 -m unittest discover -s tools -p 'test_*.py' -v
16 tests passed.

node --check assets/app.js
python3 -m py_compile _7eff7e24/content.py _7eff7e24/evidence.py _7eff7e24/model.py tools/build.py tools/verify.py tools/test_model.py
git diff --check
All passed.
```

The verifier also confirmed the old CSV is absent, all five monetary cells on each projection-year row are blank and explicitly labeled, the public source allowlists pass, and the private/retired-model build dependency checks pass. No `.nojekyll` bypass or outbound browser data call is present.

## Recommendation

The candidate is technically ready for owner review as a proposed Pages-content correction. Do not treat this report or a passing build as resolution of the public Git/history risk. Before merging, the owner should review the sanitized candidate, decide whether the public repository boundary is acceptable, and plan any visibility/history/copy remediation separately. If the change is merged, verify the resulting Pages deployment and rendered artifact afterward; do not claim this candidate is live until then.
