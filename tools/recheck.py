#!/usr/bin/env python3
"""Rebuild, verify, and report whether the published framework actually moved.

The owner's standing instruction is that any input change must be followed by a
rebuild *and* an explicit statement of whether the answer changed — not merely
whether the build passed. Under the containment policy the public site publishes
rules and evidence state, so this tool fingerprints that layer: pages built, the
source register, and which rows are verified, missing or unverified. A household
model is optional and always private: point --private-model at a JSON file
OUTSIDE this repository and it diffs the ranking in that file too, printing only
whether the order changed, never the figures.

    python3 tools/recheck.py
    python3 tools/recheck.py --private-model ../tino-private/model.json
    python3 tools/recheck.py --update          # accept current state as baseline

Exit status: 0 unchanged, 1 moved (or no snapshot yet), 2 on a build failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "tools" / "framework-snapshot.json"
sys.path.insert(0, str(ROOT / "tools"))


def framework_fingerprint() -> dict:
    """Evidence state of the published site: counts and hashes, no figures."""
    import sitebuild as sb

    manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
    statuses: dict[str, int] = {}
    rows = 0
    for page in manifest:
        text = (ROOT / page).read_text(encoding="utf-8")
        rows += text.count("<tr>") - text.count("<thead>")
        for label in sb.STATUS.values():
            statuses[label] = statuses.get(label, 0) + text.count(f'class="badge {label.lower().replace(" ", "-")}">')
    source_keys = sorted(sb.SOURCES)
    return {
        "page_count": len(manifest),
        "data_rows": rows,
        "badge_counts": dict(sorted(statuses.items())),
        "source_keys": source_keys,
        "source_hash": hashlib.sha256("\n".join(sorted(sb.SOURCES)).encode("utf-8")).hexdigest()[:16],
        "official_hosts": sorted(__import__("verify").OFFICIAL_HOSTS),
        "site_hash": hashlib.sha256(
            "".join((ROOT / p).read_text(encoding="utf-8") for p in manifest).encode("utf-8")
        ).hexdigest()[:16],
    }


def private_model_ranking(path: Path) -> list[str] | None:
    """Read a private model's ranking, if the owner keeps one outside the repository.

    Only the ordering is ever printed. The file is never copied, hashed or committed.
    """
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    ranking = data.get("ranking") or data.get("paths") or []
    return [str(item) for item in ranking] or None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="accept the current state as the baseline")
    parser.add_argument("--private-model", default=None, help="path to a private model JSON outside this repository")
    args = parser.parse_args(argv)

    for script in ("tools/build.py", "tools/verify.py"):
        result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT)
        if result.returncode != 0:
            print(f"recheck: {script} failed; fix that before reading this comparison.")
            return 2

    current = framework_fingerprint()
    model_path = Path(args.private_model).expanduser() if args.private_model else None
    if model_path is not None and ROOT in model_path.resolve().parents:
        print("recheck: --private-model must point outside the repository so nothing case-specific is tracked.")
        return 2
    if model_path is not None:
        ranking = private_model_ranking(model_path)
        if ranking is None:
            print(f"recheck: private model not readable at {model_path}; skipping the ranking diff.")
        else:
            current["private_ranking_hash"] = hashlib.sha256("|".join(ranking).encode("utf-8")).hexdigest()[:12]
            print("recheck: private ranking order recorded as a hash only; the figures stayed on disk.")

    if args.update or not SNAPSHOT.is_file():
        SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"recheck: snapshot {'updated' if args.update else 'created'} at {SNAPSHOT.relative_to(ROOT)}")
        return 0

    previous = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    moved = {k: (previous.get(k), v) for k, v in current.items() if previous.get(k) != v}
    if not moved:
        print("recheck: UNCHANGED — the published evidence layer matches the committed snapshot.")
        return 0
    print(f"recheck: MOVED — {len(moved)} aspect(s) of the published framework changed:")
    for key, (before, after) in sorted(moved.items()):
        if isinstance(before, list) or isinstance(after, list):
            summary = "added: " + ", ".join(set(map(str, after or [])) - set(map(str, before or [])) or {"none"})
            summary += " | removed: " + ", ".join(set(map(str, before or [])) - set(map(str, after or [])) or {"none"})
            print(f"  - {key}: {summary}")
        else:
            print(f"  - {key}: {before!r} -> {after!r}")
    print("         Re-read the affected pages before repeating an earlier conclusion; then accept the")
    print("         state with `python3 tools/recheck.py --update`.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
