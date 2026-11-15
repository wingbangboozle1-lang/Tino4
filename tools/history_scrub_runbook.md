# Repository history privacy runbook

**Status: owner/admin follow-up required.** Current-site cleanup cannot erase earlier commits, pull-request diffs, forks, caches, downloads or clones. Treat anything previously public as potentially retained.

## Before a history change

- Preserve an encrypted private archive outside GitHub.
- Coordinate with repository collaborators and stop concurrent pushes.
- Review GitHub's current sensitive-data removal documentation and contact GitHub Support about pull-request diffs and cached views.
- Identify all affected refs and clones without copying sensitive content into public notes.
- Decide whether public Pages and repository visibility remain appropriate; test the impact before changing settings.

## If an administrator authorizes a rewrite

Use a fresh, full-history mirror and a reviewed, access-controlled remediation plan. Remove or redact affected objects across every ref, not only the default branch. Verify the rewrite in a fresh clone, coordinate collaborator re-clones, and ask GitHub Support about server-side cached content. Do not force-push until the archive and recovery plan have been approved.

No command or branch-level site update can recall copies already downloaded or retained by third parties. Record only high-level completion status and date here; do not add the affected values, identities or locations.
