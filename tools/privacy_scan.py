#!/usr/bin/env python3
"""Read-only exposure audit for every ref in the repository.

Purpose: report *where* household-identifying material may still exist in Git
history without ever printing the sensitive values themselves. The output is
counts, refs and file paths only, so the audit report is safe to paste into a
public coordination log.

This script never modifies the repository, never writes a file, and never
prints a matched value. It is a scope-finding tool, not a remediation tool:
removing material from history requires the repository administrator workflow
documented in tools/history_scrub_runbook.md.

Usage:
    python3 tools/privacy_scan.py            # summary across all refs
    python3 tools/privacy_scan.py --verbose  # add one line per affected commit
"""
from __future__ import annotations

import subprocess
import sys
from collections import defaultdict

# Fragments that identify the case. These are the *patterns* used for the
# audit; they are the same class of identifier the public site verifier
# already blocks. Keep this list in sync with KNOWN_IDENTIFIERS in
# tools/verify.py.
PATTERNS = [
    "95014",
    "94122",
    "Cupertino",
    "Sunset District",
    "Santa Clara County",
    "Parkside",
    "Bancroft",
    "wingbangboozle",
]

# Property-value and rent strings seen in earlier drafts are matched by shape
# rather than by exact value so the audit does not restate a figure.
VALUE_SHAPES = ["3,100,000", "1,800,000", "7,150", "550,537", "114,248"]


def git(*args: str) -> str:
    """Run a read-only git command and return stdout."""
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    return result.stdout


def refs() -> list[str]:
    out = git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags")
    return [line for line in out.splitlines() if line and not line.endswith("/HEAD")]


def audit(verbose: bool) -> int:
    all_refs = refs()
    hits: dict[str, set[str]] = defaultdict(set)

    for ref in all_refs:
        for pattern in PATTERNS + VALUE_SHAPES:
            # -l lists matching paths only; -F treats the pattern literally and
            # avoids regex injection. Case-insensitive to catch slug variants.
            out = git("grep", "-l", "-i", "-F", "--no-color", pattern, ref, "--")
            for line in out.splitlines():
                path = line.split(":", 2)[-1]
                hits[ref].add(path)
                if verbose:
                    # Print the pattern *category* only, never the value.
                    kind = "value-shape" if pattern in VALUE_SHAPES else "identifier"
                    print(f"  {ref}\t{kind}\t{path}")

    affected = sorted(hits)
    print(f"Scanned refs: {len(all_refs)}")
    print(f"Refs containing at least one match: {len(affected)}")
    if affected:
        print("\nAffected refs (counts only, no values printed):")
        for ref in affected:
            print(f"  {ref}\t{len(hits[ref])} file(s)")
        print(
            "\nRemediation is an administrator action. See "
            "tools/history_scrub_runbook.md; a rebuild cannot recall clones, "
            "forks, caches or pull-request views."
        )
        return 1
    print("No known identifier or value shape found in any scanned ref.")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit("--verbose" in sys.argv[1:]))
