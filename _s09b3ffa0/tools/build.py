#!/usr/bin/env python3
"""Deterministic builder for the 15-page candidate dashboard in _s09b3ffa0/site/."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
BASE_DIR = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

from pages_core import (  # noqa: E402
    build_black_swan,
    build_decision_analysis,
    build_executive_summary,
    build_index,
    build_inheritance_law,
    build_operating_costs,
    build_projections,
    build_properties,
)
from pages_policy import (  # noqa: E402
    build_audit_reconciliation,
    build_estate_thresholds,
    build_flagged,
    build_inheritance_process,
    build_law_watchlist,
    build_methodology,
    build_sources,
)
from style_and_layout import SITE_CSS, load_ledger_map  # noqa: E402


def build_all(out_dir: Path | None = None) -> None:
    target = out_dir or (BASE_DIR / "site")
    subprocess.run([sys.executable, str(BASE_DIR / "model" / "engine.py")], check=True)

    inputs = json.loads((BASE_DIR / "data" / "inputs_rounded.json").read_text(encoding="utf-8"))
    results = json.loads((BASE_DIR / "data" / "model_results.json").read_text(encoding="utf-8"))
    ledger = load_ledger_map()

    (target / "pages").mkdir(parents=True, exist_ok=True)
    (target / "assets").mkdir(parents=True, exist_ok=True)
    (target / "assets" / "style.css").write_text(SITE_CSS, encoding="utf-8")

    pages = {
        "index.html": build_index(inputs, results, ledger),
        "pages/executive-summary.html": build_executive_summary(inputs, results, ledger),
        "pages/decision-analysis.html": build_decision_analysis(inputs, results, ledger),
        "pages/properties.html": build_properties(inputs, results, ledger),
        "pages/operating-costs.html": build_operating_costs(inputs, results, ledger),
        "pages/projections.html": build_projections(inputs, results, ledger),
        "pages/black-swan-scenarios.html": build_black_swan(inputs, results, ledger),
        "pages/inheritance-law.html": build_inheritance_law(inputs, results, ledger),
        "pages/estate-thresholds.html": build_estate_thresholds(inputs, results, ledger),
        "pages/inheritance-process.html": build_inheritance_process(inputs, results, ledger),
        "pages/law-watchlist.html": build_law_watchlist(inputs, results, ledger),
        "pages/flagged-for-review.html": build_flagged(inputs, results, ledger),
        "pages/audit-reconciliation.html": build_audit_reconciliation(inputs, results, ledger),
        "pages/methodology.html": build_methodology(inputs, results, ledger),
        "pages/sources.html": build_sources(inputs, results, ledger),
    }

    for rel, content in pages.items():
        (target / rel).write_text(content, encoding="utf-8")

    print(f"Built {len(pages)} pages + CSS into {target}")


if __name__ == "__main__":
    out_arg = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    build_all(out_arg)
