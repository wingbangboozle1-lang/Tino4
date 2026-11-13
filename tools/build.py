#!/usr/bin/env python3
"""Build the published site.

Runs the historical replay checks, the case model self-tests, then emits pages.
Standard library only. No network, no private inputs, no external package.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    ('historical replay and case model checks', [sys.executable, str(ROOT / '_7adb71fc/selftest.py')]),
    ('site generation', [sys.executable, str(ROOT / '_7adb71fc/sitebuild.py')]),
]

if __name__ == '__main__':
    for name, cmd in STEPS:
        print(f'-- {name}')
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode:
            sys.exit(result.returncode)
    print('Build complete. Nothing private was read.')
