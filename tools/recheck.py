#!/usr/bin/env python3
"""Rebuild the model and report whether the published recommendation moved.

The owner's standing instruction is that any input change must be followed by a
rebuild and an explicit check of whether the *answer* changed — not just whether
the build passes. This tool does exactly that, offline, with no network access
and no household data beyond the rounded figures already in the generator.

Usage:
    python3 tools/recheck.py            # compare against the committed snapshot
    python3 tools/recheck.py --update   # accept the current state as the baseline

Exit status: 0 unchanged, 1 moved (or no snapshot), 2 on a build failure.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "tools" / "recommendation-snapshot.json"
sys.path.insert(0, str(ROOT / "tools"))


def fingerprint() -> dict:
    """Every value the published recommendation actually rests on.

    If one of these moves, the ranking can move with it, so a reviewer must
    re-read the recommendation rather than trust the previous conclusion.
    """
    import sitebuild as sb

    return {
        "inherit_year": sb.INHERIT_YEAR,
        "transfer_tax_exclusion_branch": sb.money10(sb.a_tax_exclusion(sb.INHERIT_YEAR)),
        "transfer_tax_reassessed_branch": sb.money10(sb.a_tax_reassessed(sb.INHERIT_YEAR)),
        "annual_tax_delta": sb.money10(sb.DELTA_2045),
        "ten_year_tax_delta": sb.money10(sb.DELTA_10YR),
        "rent_hurdle_month": sb.money10(sb.RENT_HURDLE_MONTH),
        "net_sale_proceeds": sb.money10(sb.SELL_NET_2045),
        "prop19_allowance_at_transfer": sb.money10(sb.excl_amount(sb.INHERIT_YEAR)),
        "carryover_base_at_transfer": sb.money10(sb.a_assessed(sb.INHERIT_YEAR)),
        "estate_threshold_at_transfer": sb.money10(sb.estate_threshold(sb.INHERIT_YEAR)),
        "sf_transfer_tax_on_property_b": sb.money10(sb.sf_transfer_tax(sb.PROPERTY_B["value_2026"])[0]),
        "b_depreciation_low_share_annual": sb.money10(sb.b_depreciation(sb.BUILDING_SHARE_LOW)["annual"]),
        "b_recapture_low_share_10y": sb.money10(sb.b_depreciation(sb.BUILDING_SHARE_LOW)["fed_recapture"]),
        "section121_excess_after_10y": sb.money10(sb.live_then_sell_exclusion(10)["excess_single"]),
        "staging_winning_scenarios": [
            row["cells"][0] for row in sb.staging_table_rows()
            if not row["cells"][4].startswith("no gain")
        ],
        "distribution_median_real": sb.money10(sb.outcome_distribution()["real"][0.5]),
        "distribution_worst_real": sb.money10(sb.outcome_distribution()["real"][0.0]),
        "publish_assessment_levels": sb.PUBLISH_ASSESSMENT_LEVELS,
    }


def main(argv: list[str]) -> int:
    update = "--update" in argv
    build = subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=ROOT)
    if build.returncode != 0:
        print("recheck: the build failed; nothing was compared.")
        return 2
    verify = subprocess.run([sys.executable, str(ROOT / "tools" / "verify.py")], cwd=ROOT)
    if verify.returncode != 0:
        print("recheck: the verifier failed; fix it before reading the comparison.")
        return 2

    current = fingerprint()
    if update or not SNAPSHOT.is_file():
        SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"recheck: snapshot {'updated' if update else 'created'} at {SNAPSHOT.relative_to(ROOT)}")
        return 0

    previous = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    moved = {key: (previous.get(key), value) for key, value in current.items() if previous.get(key) != value}
    if not moved:
        print("recheck: UNCHANGED — every value the recommendation rests on matches the committed snapshot.")
        print("         The published recommendation does not need to be re-read after this input state.")
        return 0
    print(f"recheck: MOVED — {len(moved)} value(s) the recommendation depends on changed:")
    for key, (before, after) in sorted(moved.items()):
        print(f"  - {key}: {before!r} -> {after!r}")
    print("         Re-read the conditional best plan on index.html and the decision-log entry for each")
    print("         changed input before repeating the previous conclusion. Commit the snapshot with")
    print("         `python3 tools/recheck.py --update` once the reasoning has been reviewed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
