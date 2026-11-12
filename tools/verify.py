#!/usr/bin/env python3
"""Verify the public dashboard. Standard library only.

Delegates to the model verifier in s179ec133/_work/tools/verify.py,
which checks for every page: every table row links to an official
source and carries a status label; every external link is a URL in
the evidence ledger; every internal link and anchor resolves; every
dollar amount of $1,000 or more is a multiple of $10 unless it is an
exact figure quoted from an official source; no ZIP code,
neighbourhood name, e-mail address or parcel wording appears; every
page asks search engines not to index it. Also checks that the
legacy candidate directory stays excluded from the Pages build
(PR #27 regression guard). Exit status 1 on failure.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "s179ec133" / "_work" / "tools" / "verify.py"


def main():
    result = subprocess.run(
        [sys.executable, str(VERIFY), str(ROOT)],
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
    config = (ROOT / "_config.yml").read_text()
    for x in ["tools", "s179ec133", "COORDINATION.md", "README.md"]:
        if f"  - {x}" not in config:
            print(f"missing exclusion: {x}")
            sys.exit(1)
    print("exclusion checks passed")


if __name__ == "__main__":
    main()
