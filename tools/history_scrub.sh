#!/usr/bin/env bash
# Deliberately non-destructive placeholder. History remediation requires an
# authorized repository administrator, a private encrypted archive, and
# GitHub Support coordination. See tools/history_scrub_runbook.md.
set -euo pipefail
cat >&2 <<'MSG'
This helper does not rewrite history. Do not force-push from this session.
A repository administrator must review the runbook, preserve a private archive,
coordinate collaborators, and follow current GitHub sensitive-data guidance.
MSG
exit 2
