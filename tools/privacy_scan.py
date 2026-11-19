#!/usr/bin/env python3
"""Read-only scan of accessible Git history for common direct identifiers.

This generic scan contains no household-specific values or identifiers. It checks
reachable commits for email, phone and street-address-shaped text, and prints
only ref/path counts. It is deliberately incomplete: it cannot find every form
of personal or property data, and a shallow checkout cannot inspect missing
history. It cannot establish that copies outside the scanned Git objects were
erased. Use the administrator runbook for a complete history-remediation plan.
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict

PATTERNS = {
    "email": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"),
    "street-address": re.compile(r"(?i)\b\d{1,6}\s+(?:[A-Za-z0-9.'-]+\s+){1,4}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Court|Ct)\b"),
}


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.stdout


def is_shallow_repository() -> bool:
    """Whether this checkout omits commits before the fetched boundary."""
    return git("rev-parse", "--is-shallow-repository").strip() == "true"


def refs() -> list[str]:
    out = git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags")
    return [line for line in out.splitlines() if line and not line.endswith("/HEAD")]


def audit(verbose: bool = False, _extra: list[str] | None = None) -> int:
    """Scan available commits. `_extra` is accepted for compatibility, not decoded or used."""
    matches: dict[str, set[str]] = defaultdict(set)
    scanned_refs = refs()
    accessible_commits = 0
    shallow = is_shallow_repository()
    for ref in scanned_refs:
        commits = git("rev-list", ref).splitlines()
        accessible_commits += len(commits)
        for commit in commits:
            paths = git("ls-tree", "-r", "--name-only", commit).splitlines()
            for path in paths:
                content = git("show", f"{commit}:{path}").encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
                for kind, pattern in PATTERNS.items():
                    if pattern.search(content):
                        matches[ref].add(path)
                        if verbose:
                            print(f"{ref}\t{kind}\t{path}")
    affected = sorted(matches)
    print(f"Scanned refs: {len(scanned_refs)}")
    print(f"Accessible ref/commit pairs checked: {accessible_commits}")
    print(f"Refs with common direct-identifier-shaped matches: {len(affected)}")
    if affected:
        print("Affected refs (counts and paths only; no matched values printed):")
        for ref in affected:
            print(f"  {ref}\t{len(matches[ref])} file(s)")
    if shallow:
        print("History completeness: shallow clone; earlier commits are not audited.")
    else:
        print("History completeness: full local history for the scanned refs was available.")
    if affected:
        print("This generic scan is incomplete and cannot verify external copies. See the administrator runbook.")
        return 1
    print("No common direct-identifier pattern found in the accessible commits; this is not proof that all data is safe or erased.")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit("--verbose" in sys.argv[1:]))
