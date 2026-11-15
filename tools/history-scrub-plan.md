# Pre-rounding Git history: audit result and owner-executable scrub plan

**Status: NOT scrubbed.** This document records what the 2026-11-15 audit found
and how the repository owner can remove pre-rounding personal data from Git
history. Only the owner (or a repository admin) can execute the rewrite: the
session sandbox must never force-push or rewrite shared history.

**This file contains no figures on purpose.** A mapping from a published
rounded value back to its unrounded source value is more sensitive than either
value alone — it re-identifies exactly the record the rounding was designed to
hide. The same rule applies to every tracked file, and `tools/verify.py`
enforces it (see "Rounding-map ban" below).

## 1. Audit result (2026-11-15)

Method: `git log --all --oneline -S <pattern>` (pickaxe) over the fetched
history, plus a blob scan of `git rev-list --all --objects`. Patterns tested
were unrounded owner figures (assessment values, tax amounts, rent,
valuations) and place identifiers. **Counts only were recorded; no matched
value was ever printed, and none may be added to this file.**

| Pattern class | Commits containing it |
| --- | --- |
| Unrounded current-year assessment figure | 8 |
| Unrounded prior-year assessment figure | 8 |
| Postal-code identifier (San Francisco) | 36 |
| Postal-code identifier (Peninsula city) | 35 |
| Rent figure with unit marker | 16 |
| Property A valuation estimate | 29 |
| Property B valuation estimate | 28 |
| Property B assessment figure | 10 |

Interpretation:

- The **current tree** is the only part a session can fix. It is scanned on
  every build by `tools/verify.py`.
- The **reachable Git history** still contains pre-rounding personal data in
  roughly 195 commits and 252 historical paths (E428 audit, re-confirmed by
  the CC44 and 3D3 audits).
- **New finding (2026-11-15, session `arena/79e0fd5e-tino4`):** an earlier
  session stored the literal rounded/unrounded mapping inside
  `tools/history_scrub.sh` and named one unrounded assessment value in this
  plan. That made the reverse map publicly readable in the tree *and* added a
  new commit containing it — the opposite of the scrub's purpose. Both files
  are now figure-free and the verifier fails on any future mapping. The
  historical copies remain in the objects listed above and must be removed by
  the owner-run rewrite described here.
- PR diffs, forks, clones and GitHub caches derived from that history are
  outside the repository's control and must be treated as exposed regardless of
  any rewrite.

## 2. Why the site cannot fix this

A branch-level change (new commits) never removes old objects: the data stays
reachable via commit hashes, PR pages and `git log` on main. Only a history
rewrite plus coordination with GitHub Support can shrink exposure.

## 3. Owner-executable scrub plan

Prerequisites: repository admin rights; a fresh machine with full history;
`git filter-repo` installed; everyone informed that hashes will change and
clones must be re-cloned.

1. **Back up first.** `git clone --mirror` the repository to a private,
   encrypted location. Keep it until GitHub Support confirms cleanup.
2. **Build the rules file privately**, outside any clone, mode 600. One line
   per exact pre-rounding string, in git-filter-repo's replace-text format,
   mapping it to the rounded value already published. Never commit, paste or
   attach this file anywhere; `tools/verify.py` rejects a rules file inside the
   repository.
3. **Rewrite history.** Drop the retired case directories and apply the rules:

   ```bash
   git filter-repo --invert-paths \
     --path _7adb71fc/ --path _7eff7e24/ --path _1775f697/review/ \
     --path _a3de132b/audit/ --path _s8bb142d0/audit/ --path _s95cf9249/audit/ \
     --path content_part1.py --path content_part2.py --path content_part3.py \
     --path content_part4.py --path case_data.py --path case_model.py \
     --path case-projections.csv
   ```

   Then run `tools/history_scrub.sh`, which wraps
   `git filter-repo --replace-text <private rules file>` and refuses to run
   unless the rules file is outside a git working tree, owned by you and mode
   600.
4. **Force-push the rewritten history** (owner action) for every ref that
   should survive, then delete stale session branches — each surviving branch
   and open PR keeps the old objects reachable.
5. **Contact GitHub Support** to expire cached views and PR diff data for the
   removed commits and to run a GC, providing the list of removed hashes.
6. **Consider visibility.** Earlier API attempts to restrict visibility failed
   with HTTP 403 from the session token. Change visibility to private
   (Settings → Danger Zone) if the family prefers defence in depth, or accept
   the public posture knowingly.
7. **Rotate or restate anything that was exposed.** Treat the unrounded figures
   as known: they cannot be un-leaked. The value of the scrub is reducing
   *ongoing* discoverability — mainly by removing the reverse map — not undoing
   past exposure.
8. **Verify after the rewrite** with the same pickaxe patterns; all should
   return zero commits. Update COORDINATION.md and this file with the date.

## 4. What a session may do instead (and did, 2026-11-15)

- Keep the current tree clean; the verifier enforces $10 rounding on every
  published amount, bans comma-grouped unrounded numbers anywhere in the tree,
  and fails on a rounding map.
- Publish the rounded analysis with placeholders for place identifiers.
- Record this plan so the owner can act without the session's context.
- Offer a build-time switch (`PUBLISH_ASSESSMENT_LEVELS` in
  `tools/sitebuild.py`) that replaces absolute assessed values with an indexed
  series (2014 = 100), which removes the most re-identifiable published element
  while keeping every growth rate the decision actually depends on.
