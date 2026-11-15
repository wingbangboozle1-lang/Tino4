#!/usr/bin/env bash
# Owner-run helper: rewrite public history so pre-rounding case figures are
# replaced by their published rounded values. DESTRUCTIVE.
#
# Read tools/history_scrub_runbook.md in full before running this.
#
# PRIVACY RULE FOR THIS REPOSITORY: this script deliberately contains NO
# numbers at all. A file that maps a rounded figure back to its unrounded source
# value is more sensitive than either value alone, because it re-identifies the
# record the rounding was meant to hide. The mapping is supplied at run time
# from a private file that must never be committed, cloned or pasted into an
# issue, PR or this repository.
#
# Usage:
#   tools/history_scrub.sh <clone-url> <work-dir> <private-rules-file>
#
# <private-rules-file> is a git-filter-repo replace-text file kept outside the
# repository. Each line replaces one exact pre-rounding string with its rounded
# published form; build it locally from your own private records. It must live
# outside every clone of this repository (the script refuses to run otherwise).
set -euo pipefail

REPO_URL="${1:-}"
WORK="${2:-}"
RULES="${3:-}"

die() { echo "ERROR: $*" >&2; exit 2; }

[[ -n "$REPO_URL" && -n "$WORK" && -n "$RULES" ]] || \
  die "usage: $0 <clone-url> <work-dir> <private-rules-file> (see the runbook)"
[[ -e "$WORK" ]] && die "refusing to overwrite existing $WORK — choose a fresh directory"
[[ -f "$RULES" ]] || die "rules file not found: $RULES (create it privately, outside any clone)"
command -v git >/dev/null || die "git is required"
git --version >/dev/null
command -v git-filter-repo >/dev/null || die "install git-filter-repo first (pip install git-filter-repo)"

# Guard 1: the rules file must not be inside a git working tree of this project.
if git -C "$(dirname "$RULES")" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  die "the rules file is inside a git working tree — move it somewhere untracked and outside every clone"
fi
# Guard 2: refuse a rules file that is itself world-readable or tracked.
[[ -O "$RULES" ]] || die "the rules file must be owned by you"
perms="$(stat -c '%a' "$RULES" 2>/dev/null || stat -f '%Lp' "$RULES")"
[[ "$perms" == "600" || "$perms" == "400" ]] || die "set the rules file to mode 600 first (chmod 600 '$RULES')"

echo "==> Cloning full history to $WORK"
git clone --mirror "$REPO_URL" "$WORK"
cd "$WORK"

echo "==> Rewriting history with the private rules file (this is irreversible)."
echo "    Review every line of $RULES first: it is the only copy."
read -r -p "    Type SCRUB to continue: " confirm
[[ "$confirm" == "SCRUB" ]] || die "aborted by operator; nothing was rewritten"
git filter-repo --replace-text "$RULES"

cat <<'MSG'

==> Rewrite complete. NEXT (manual, per the runbook):
   1. git push --force --mirror so every ref carries the rewritten history.
   2. Contact GitHub Support to clear cached PR diffs and run a GC; provide the
      list of removed commit hashes.
   3. Tell fork/clone owners to re-clone; confirm old raw URLs return 404.
   4. Delete stale session branches that still reference pre-rewrite objects.
   5. Shred or encrypt the private rules file, then update COORDINATION.md and
      the site's Privacy page with the date the scrub was completed.
MSG
