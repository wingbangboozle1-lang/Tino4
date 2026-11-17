#!/usr/bin/env python3
"""Read-only exposure audit for every ref in the repository.

Purpose: report *where* household-identifying material may still exist in Git
history without printing the sensitive values, and without storing them in
plaintext inside this tracked file.

Design notes
------------
* The default pattern list is stored base64-encoded. Encoding is **not**
  security and is not relied on as such. Its only job is to keep the raw
  identifiers out of the tracked plaintext so the audit tool does not become
  a new search-indexable copy of the very material it is meant to find.
* The tool prints counts, refs and file paths only. It never prints a matched
  value, so its output is safe to paste into a public coordination log.
* Read-only: no checkout, no reset, no write to any ref. Removing material
  from history requires the administrator workflow in
  tools/history_scrub_runbook.md.

Usage
-----
    python3 tools/privacy_scan.py                 # summary across all refs
    python3 tools/privacy_scan.py --verbose       # one line per ref/kind/path
    python3 tools/privacy_scan.py --patterns FILE # extra patterns, one per line

--patterns files must live outside the tracked tree (for example
/private-work/identifiers.txt) and are never committed. Do not place the raw
identifiers in this repository.
"""
from __future__ import annotations

import base64
import subprocess
import sys
from collections import defaultdict

# base64 of the identifier fragments used for the audit. Decoded at runtime.
_ENCODED = [
    "OTUwMTQ=",
    "OTQxMjI=",
    "Q3VwZXJ0aW5v",
    "U3Vuc2V0IERpc3RyaWN0",
    "U2FudGEgQ2xhcmEgQ291bnR5",
    "UGFya3NpZGU=",
    "QmFuY3JvZnQ=",
]

# Property-value and rent strings seen in earlier drafts. Encoded for the same
# reason as the identifiers above, and deliberately NOT annotated with the
# decoded value: an earlier version carried the plain numbers in these trailing
# comments, which defeated the encoding entirely.
_ENCODED_SHAPES = [
    "MywxMDAsMDAw",
    "MSw4MDAsMDAw",
    "NywxNTA=",
    "NTUwLDUzNw==",
    "MTE0LDI0OA==",
]

ACCOUNT = base64.b64decode("d2luZ2JhbmcvYm9veg==").decode()


def _decode(items: list[str]) -> list[str]:
    return [base64.b64decode(item).decode() for item in items]


def git(*args: str) -> str:
    """Run a read-only git command and return stdout."""
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.stdout


def refs() -> list[str]:
    out = git(
        "for-each-ref",
        "--format=%(refname)",
        "refs/heads",
        "refs/remotes",
        "refs/tags",
    )
    return [line for line in out.splitlines() if line and not line.endswith("/HEAD")]


def load_extra_patterns(argv: list[str]) -> list[str]:
    if "--patterns" not in argv:
        return []
    path = argv[argv.index("--patterns") + 1]
    try:
        with open(path, encoding="utf-8") as handle:
            return [line.strip() for line in handle if line.strip()]
    except OSError as exc:
        print(f"Cannot read pattern file: {exc}")
        raise SystemExit(2)


def audit(verbose: bool, extra: list[str]) -> int:
    identifiers = _decode(_ENCODED) + extra + [ACCOUNT]
    shapes = _decode(_ENCODED_SHAPES)
    all_refs = refs()
    hits: dict[str, set[str]] = defaultdict(set)
    commits: dict[str, int] = defaultdict(int)

    for ref in all_refs:
        for pattern in identifiers + shapes:
            out = git("grep", "-l", "-i", "-F", "--no-color", pattern, ref, "--")
            for line in out.splitlines():
                path = line.split(":", 2)[-1]
                hits[ref].add(path)
                if verbose:
                    kind = "value-shape" if pattern in shapes else "identifier"
                    print(f"  {ref}\t{kind}\t{path}")
        # Count affected commits so the report can distinguish "a few recent
        # commits" from "present since the first import".
        for pattern in identifiers[:2]:
            log = git("log", "--oneline", "-i", "-F", f"-S{pattern}", ref, "--")
            commits[ref] = max(commits[ref], len(log.splitlines()))

    affected = sorted(hits)
    print(f"Scanned refs: {len(all_refs)}")
    print(f"Refs containing at least one match: {len(affected)}")
    if affected:
        print("\nAffected refs (counts only, no values printed):")
        for ref in affected:
            print(f"  {ref}\t{len(hits[ref])} file(s)")
        deepest = max(commits.values()) if commits else 0
        print(f"\nDeepest affected-commit count on any single ref: {deepest}")
        print(
            "\nRemediation is an administrator action. See "
            "tools/history_scrub_runbook.md; a rebuild cannot recall clones, "
            "forks, caches or pull-request views."
        )
        return 1
    print("No known identifier or value shape found in any scanned ref.")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit("--verbose" in sys.argv[1:], load_extra_patterns(sys.argv[1:])))
