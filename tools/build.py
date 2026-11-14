#!/usr/bin/env python3
"""Build the generic public site without reading private case inputs."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    result = subprocess.run([sys.executable, str(ROOT / "tools/sitebuild.py")], cwd=ROOT)
    sys.exit(result.returncode)
