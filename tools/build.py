#!/usr/bin/env python3
"""Build the public dashboard from the verified model. Standard library only.

The model, evidence ledger and page generator live in s179ec133/_work/.
This wrapper runs the engine and then builds into the repository root
(index.html, pages/, assets/), so `python3 tools/build.py` reproduces
the published site deterministically. Usage: python3 tools/build.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "s179ec133" / "_work"


def main():
    subprocess.run(
        [sys.executable, str(WORK / "model" / "engine.py")],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(WORK / "tools" / "build.py"), str(ROOT)],
        check=True,
    )
    print("Built public dashboard into repository root")


if __name__ == "__main__":
    main()
