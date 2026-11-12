"""Build the public dashboard from the verified model. Standard library only.

The model, evidence ledger and page generator live in s179ec133/_work/.
This wrapper runs the engine and then builds into the repository root
(index.html, pages/, assets/), so `python3 tools/build.py` reproduces
the published site deterministically. Two integration notices that belong
to the shared outputs are re-applied after the generator runs (idempotent;
generator files are not edited):
  1. pages/flagged-for-review.html gains a location-wording notice
     (city names appear only where official sources are county-/city-specific).
Usage: python3 tools/build.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "s179ec133" / "_work"

NOTICE = ('<div class="notice"><strong>Location wording.</strong> This site names the two cities involved only where an '
          'official source is county- or city-specific (tax rate books, assessor letters, rent boards). No name, street address, '
          'ZIP code, parcel number, or account detail is published anywhere. If full location anonymity is required, the owner '
          'can ask for the city wording to be removed as well.</div>')
ANCHOR = '<p class="lead">Unverified items, assumptions, irregularities and open questions — each with the official link to check it.</p>'


def main():
    subprocess.run(
        [sys.executable, str(WORK / "model" / "engine.py")],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(WORK / "tools" / "build.py"), str(ROOT)],
        check=True,
    )
    target = ROOT / "pages" / "flagged-for-review.html"
    text = target.read_text(encoding="utf-8")
    if NOTICE not in text:
        if ANCHOR not in text:
            sys.exit("anchor not found in pages/flagged-for-review.html — generator changed; update tools/build.py")
        text = text.replace(ANCHOR, ANCHOR + "\n" + NOTICE, 1)
        target.write_text(text, encoding="utf-8")
    print("Built public dashboard into repository root")


if __name__ == "__main__":
    main()
