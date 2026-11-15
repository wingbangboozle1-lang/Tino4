# Git history remediation runbook (repository owner action required)

Status as of 2026-11-15: **NOT DONE.** The current tree and generated site are
anonymized and $10-rounded, but the public Git history of
`wingbangboozle1-lang/Tino4` still contains pre-rounding case material from
earlier revisions. Until the steps below are completed by the repository
owner/admin, **treat all historic values as exposed.**

Why this was not done from the working session: history rewrites require
force-pushing refs other than the session's feature branch, which the session
is forbidden to touch, and they must be coordinated across open PRs and
concurrent sessions. GitHub documents history rewrites as disruptive and
notes that pull requests, forks, caches and clones may retain copies
(https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Before anything else

1. Preserve a **private, encrypted archive** of the current repository
   (including history) somewhere other than GitHub. The scrub destroys
   pre-scrub objects; you cannot retrieve them after a GC.
2. Close or merge all open PRs and coordinate with any concurrent sessions so
   no branch is mid-push during the rewrite.
3. Identify the material to remove: pre-rounding property values, exact tax
   and assessed-value figures, rent amounts, and any postal-code/parcel/name
   fragments that ever appeared in any commit.

## Option A — GitHub Support (recommended for this repo)

Ask GitHub Support to remove the sensitive objects from pull-request diffs and
cached views. This is the only route that reaches PR diffs and GitHub's caches.
Follow the current instructions in the GitHub docs link above (the support
form references specific commit/object identifiers).

## Option B — local rewrite with git-filter-repo

The helper `tools/history_scrub.sh` wraps the standard procedure:

1. Fresh clone + private backup.
2. `git filter-repo` (installed via pip) with replace-text expressions that map
   each pre-rounding figure to its published rounded value, plus removal of any
   file path that only ever held private inputs.
3. Force-push every ref: `git push --force --all origin &&
   git push --force --tags origin`.
4. Coordinate with GitHub Support about PR diffs/caches (Option A still needed).
5. Ask any fork owners to re-clone or hard-reset; delete and recreate forks if
   simpler.
6. Verify from a clean browser/incognito: raw.githubusercontent URLs for old
   commit SHAs must 404 after GC.

Review the replace-text rules in the script and extend them with every exact
value found by `git log -p` before running. A rule missed is a value that stays.

## After the scrub

- Re-run `python3 tools/build.py && python3 tools/verify.py` and the test suite.
- Update the privacy page and the COORDINATION.md record: change the
  "history is not scrubbed" state to the scrub date, method and verification
  result. Keep this runbook until GitHub Support confirms PR/caches are clean.
- Announce to collaborators: old clones are unsafe; everyone re-clones.
