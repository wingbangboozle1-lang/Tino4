#!/usr/bin/env python3
"""Verify the published site.

Checks structure, source coverage, rounding, privacy tokens and links. It does
not certify that a sentence is entailed by its source, and it is not legal or
financial advice.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7adb71fc'))

from verify import verify

if __name__ == '__main__':
    sys.exit(1 if verify() else 0)
