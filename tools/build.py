#!/usr/bin/env python3
"""Build the published dashboard from the verified model (Python standard library only).

The model, evidence ledger, flag register and page generator for this publication
live in `_c07ccf45/` (underscore-prefixed, therefore never published by Jekyll):

  _c07ccf45/model/engine.py        deterministic, strictly $10-rounded household model
  _c07ccf45/evidence/sources_and_flags.py   47 official sources + 13 flag records
  _c07ccf45/tools/build_candidate.py         static HTML generator (15 pages)
  _c07ccf45/tools/verify_candidate.py        structural / sourcing / privacy verifier

This wrapper regenerates `data/summary.json` and then rebuilds the published site
into the repository root (index.html, pages/, assets/), so `python3 tools/build.py`
reproduces the live site byte-for-byte.

Usage: python3 tools/build.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "_c07ccf45"


def main() -> None:
    subprocess.run([sys.executable, str(PKG / "model" / "engine.py")], check=True)
    subprocess.run(
        [sys.executable, str(PKG / "tools" / "build_candidate.py"), "--out", str(ROOT)],
        check=True,
    )
    # The generator also writes a .nojekyll marker inside its own output tree;
    # Jekyll must process the published root instead, so the marker is removed.
    stray = ROOT / ".nojekyll"
    if stray.exists():
        stray.unlink()
    print("Built the public dashboard into the repository root")


if __name__ == "__main__":
    main()
