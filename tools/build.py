#!/usr/bin/env python3
"""Rebuild the integrated dashboard in this repository root.
Delegates to the pinned, deterministic generator kept with the session evidence:
  python3 s179ec133/_work/tools/build.py <output-dir>
then re-applies the integration notices that belong to the shared outputs
(session scope: tools/**, not the pinned generator). Idempotent.
Usage: python3 tools/build.py"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "s179ec133", "_work", "tools", "build.py")
if not os.path.isfile(GEN):
    sys.exit("pinned generator not found: %s" % GEN)
rc = subprocess.call([sys.executable, GEN, ROOT])
if rc:
    sys.exit(rc)

NOTICE = ('<div class="notice"><strong>Location wording.</strong> This site names the two cities involved only where an '
          'official source is county- or city-specific (tax rate books, assessor letters, rent boards). No name, street address, '
          'ZIP code, parcel number, or account detail is published anywhere. If full location anonymity is required, the owner '
          'can ask for the city wording to be removed as well.</div>')
TARGET = os.path.join(ROOT, "pages", "flagged-for-review.html")
text = open(TARGET, encoding="utf-8").read()
anchor = '<p class="lead">Unverified items, assumptions, irregularities and open questions — each with the official link to check it.</p>'
if NOTICE not in text:
    if anchor not in text:
        sys.exit("anchor not found in pages/flagged-for-review.html — generator changed; update tools/build.py")
    text = text.replace(anchor, anchor + "\n" + NOTICE, 1)
    open(TARGET, "w", encoding="utf-8").write(text)
print("integration notices applied")
