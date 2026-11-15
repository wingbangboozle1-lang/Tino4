# Pre-rounding Git history: audit result and owner-executable scrub plan

**Status: NOT scrubbed.** This document records what the 2026-11-15 audit found
and exactly how the repository owner can remove pre-rounding personal data from
Git history. Only the owner (or a repository admin) can execute the rewrite:
the session sandbox must never force-push or rewrite shared history.

## 1. Audit result (2026-11-15)

Method: `git log --all --oneline -S <pattern>` (pickaxe) over the fetched
history (about 249 commits after fetching origin/main). Patterns tested were
unrounded owner figures (assessment values, tax amounts, rent, valuations) and
place identifiers. Counts only were recorded; no matched values were printed.

| Pattern class | Commits containing it |
| --- | --- |
| Unrounded 2026 assessment figure | 8 |
| Unrounded prior-year assessment figure | 8 |
| Postal-code identifier (SF district) | 36 |
| Postal-code identifier (Cupertino) | 35 |
| Rent figure with unit marker | 16 |
| Property A valuation estimate | 29 |
| Property B valuation estimate | 28 |
| Property B assessment figure | 10 |

Interpretation:

- The **current tree** (HEAD, and current origin/main) is clean: pattern scans
  of every tracked file found no unrounded figures or place identifiers.
- The **reachable Git history** still contains the pre-rounding personal data
  in roughly 195 commits and 252 historical paths (confirmed by the earlier
  E428 audit and re-confirmed here for the specific figures above).
- PR diffs, forks, clones, and GitHub caches derived from that history are
  outside the repository's control and must be treated as exposed regardless
  of any rewrite.

## 2. Why the site cannot fix this

A branch-level change (new commits) never removes old objects: the data stays
reachable via commit hashes, PR pages, and `git log` on main. Only a history
rewrite plus coordination with GitHub Support can shrink exposure.

## 3. Owner-executable scrub plan (run locally on a machine with full history)

Prerequisites: repository admin rights; a fresh clone with full history;
`git filter-repo` installed (`pip install git-filter-repo`); everyone informed
that hashes will change and clones must be re-cloned.

1. **Back up first.** `git clone --mirror` the repository to a private,
   encrypted location. Keep it until GitHub Support confirms all cleanup.
2. **Rewrite history** to drop the pre-rounding paths and redact patterns:

   ```bash
   git filter-repo --invert-paths \
     --path _7adb71fc/ --path _7eff7e24/ --path _1775f697/review/ \
     --path _a3de132b/audit/ --path _s8bb142d0/audit/ --path _s95cf9249/audit/ \
     --path content_part1.py --path content_part2.py --path content_part3.py \
     --path content_part4.py --path case_data.py --path case_model.py \
     --path case-projections.csv
   ```

   Then, for any remaining file that contained unrounded figures in history
   (the pickaxe list above names the commits), run a content replace pass:

   ```bash
   # inspect first, then replace each exact unrounded string with its $10-rounded form
   git filter-repo --replace-text expressions.txt
   # expressions.txt lines look like:  550537==>550540
   ```

3. **Force-push the rewritten history** (owner action): `git push --force
   origin main` and re-push any branches that should survive. Delete stale
   branches that still reference old objects.
4. **Contact GitHub Support** to (a) expire cached views and PR diff data for
   removed commits, and (b) run a GC on the repository so unreferenced objects
   are purged. Provide the list of removed commit hashes.
5. **Consider visibility.** The earlier API attempt to restrict visibility
   failed (HTTP 403 from the integration token). Change visibility to private
   (Settings → Danger Zone) if the family prefers defense in depth, or accept
   the public posture knowingly.
6. **Rotate anything that was exposed.** Treat the unrounded figures as
   known: they cannot be un-leaked. The value of the scrub is reducing
   *ongoing* discoverability, not undoing past exposure.
7. **Verify after the rewrite** with the same pickaxe patterns; all should
   return zero commits. Update COORDINATION.md and this file with the date.

## 4. What this session did instead

- Kept the current tree clean (automated verifier enforces rounding, no
  addresses/postal codes, no unrounded figures anywhere in tracked text).
- Published the rounded analysis on the site with placeholders only.
- Recorded this plan so the owner can act without needing the session's
  context.
