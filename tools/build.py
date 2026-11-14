#!/usr/bin/env python3
"""Build public pages without importing or reading private case inputs."""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if __name__ == '__main__':
    result = subprocess.run([sys.executable, str(ROOT / '_7adb71fc/sitebuild.py')], cwd=ROOT)
    sys.exit(result.returncode)
