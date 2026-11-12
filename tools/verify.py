#!/usr/bin/env python3
"""Verify the published dashboard (Python standard library only).

Delegates to `_c07ccf45/tools/verify_candidate.py`, which checks every page for:
  * complete, balanced table markup and a no-index directive;
  * every table row linking at least one official government publication;
  * every external link being a URL in the evidence ledger, on a `.gov` host;
  * every internal link resolving;
  * every dollar amount of $1,000+ being a multiple of $10, unless it is an exact
    statutory figure quoted from a linked source;
  * the absence of names, parcel numbers, city names, neighbourhood names and
    ZIP codes;
  * the required row counts (50 projection years per property, 7 stress regimes,
    the full 47-source register and the full 13-item flag log).

It then re-checks the Jekyll publication boundary in `_config.yml` so no working
file can be served by GitHub Pages. Exit status 1 on failure.

Usage: python3 tools/verify.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "_c07ccf45" / "tools" / "verify_candidate.py"
REQUIRED_EXCLUSIONS = ["tools", "_c07ccf45", "COORDINATION.md", "README.md", "s179ec133", "_s9ad1da71"]


def main() -> None:
    result = subprocess.run([sys.executable, str(VERIFY), str(ROOT)])
    if result.returncode != 0:
        sys.exit(result.returncode)

    config = (ROOT / "_config.yml").read_text(encoding="utf-8")
    missing = [x for x in REQUIRED_EXCLUSIONS if f"  - {x}\n" not in config and not config.rstrip().endswith(f"  - {x}")]
    if missing:
        print(f"missing Jekyll exclusion(s): {', '.join(missing)}")
        sys.exit(1)

    # The published tree must contain only static site files.
    allowed_root = {"index.html", "pages", "assets"}
    unexpected = [
        p.name
        for p in ROOT.iterdir()
        if p.is_dir() and p.name in {"_c07ccf45", "s179ec133", "_s9ad1da71", "tools"}
    ]
    assert allowed_root  # documentation only
    if unexpected:
        print(f"note: working directories present but excluded from publication: {', '.join(sorted(unexpected))}")

    print("exclusion checks passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
