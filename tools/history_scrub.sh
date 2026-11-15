#!/usr/bin/env bash
# Owner-run helper: rewrite public history to replace pre-rounding case
# figures with their published rounded values. DESTRUCTIVE. Read
# tools/history_scrub_runbook.md in full before running. Requires git 2.x,
# Python 3, and git-filter-repo (pip install git-filter-repo).
set -euo pipefail

REPO_URL="${1:-git@github.com:wingbangboozle1-lang/Tino4.git}"
WORK="${2:-$HOME/tino4-history-scrub}"

if [[ -e "$WORK" ]]; then
  echo "Refusing to overwrite existing $WORK — choose a fresh directory." >&2
  exit 1
fi

echo "==> Cloning full history to $WORK"
git clone --mirror "$REPO_URL" "$WORK"
cd "$WORK"

echo "==> Building replace-text rules from the verified rounding map."
cat > /tmp/tino4-scrub-rules.txt <<'EOF'
# Extend this list with EVERY exact pre-rounding figure found in git log -p.
# Format (git-filter-repo replace-text): literal:OLD==>NEW
literal:550,537==>550,540
literal:539,743==>539,740
literal:529,156==>529,160
literal:518,785==>518,790
literal:508,608==>508,610
literal:498,638==>498,640
literal:493,526==>493,530
literal:483,848==>483,850
literal:474,370==>474,370
literal:465,066==>465,070
literal:455,952==>455,950
literal:449,106==>449,100
literal:440,305==>440,310
literal:7,207==>7,210
literal:6,917==>6,920
literal:6,758==>6,760
literal:6,658==>6,660
literal:6,566==>6,570
literal:6,378==>6,380
literal:6,412==>6,410
literal:6,131==>6,130
literal:5,965==>5,970
literal:114,248==>114,250
literal:112,010==>112,010
literal:109,810==>109,810
literal:107,660==>107,660
literal:105,600==>105,600
literal:104,510==>104,510
literal:102,470==>102,470
literal:100,460==>100,460
literal:98,490==>98,490
literal:96,557==>96,560
literal:2,439==>2,440
literal:2,315==>2,320
literal:2,181==>2,180
literal:2,110==>2,110
literal:2,066==>2,070
literal:2,204==>2,200
literal:2,127==>2,130
literal:2,056==>2,060
literal:1,736==>1,740
literal:1,675==>1,680
literal:7,150==>7,150
literal:3,080,000==>3,080,000
literal:1,780,000==>1,780,000
EOF

echo "==> Rewriting history (review /tmp/tino4-scrub-rules.txt first!)"
git filter-repo --replace-text /tmp/tino4-scrub-rules.txt

cat <<'MSG'

==> Rewrite complete. NEXT (manual, per the runbook):
   1. git push --force --all origin && git push --force --tags origin
   2. Contact GitHub Support to clear PR diffs and cached views.
   3. Tell fork owners to re-clone; verify raw URLs for old SHAs 404.
   4. Record the scrub in COORDINATION.md and update the privacy page.
MSG
