#!/usr/bin/env python3
"""s-179ec133 — build the dashboard.  Usage: python3 build.py [output directory]
Default output: ../../site (the candidate dashboard inside this session's own directory)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sitegen, pages_a, pages_b


def build(out):
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    os.makedirs(os.path.join(out, "pages"), exist_ok=True)
    open(os.path.join(out, "assets", "style.css"), "w", encoding="utf-8").write(sitegen.CSS.strip() + "\n")
    made = []
    for fn in (pages_a.p_index, pages_a.p_summary, pages_a.p_decision, pages_a.p_properties, pages_a.p_projections, pages_a.p_costs,
               pages_b.p_law, pages_b.p_estate, pages_b.p_process, pages_b.p_blackswan, pages_b.p_lawwatch, pages_b.p_flagged,
               pages_b.p_sources, pages_b.p_method):
        made.append(fn(out))
    return made


if __name__ == "__main__":
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "..", "..", "site"))
    files = build(out)
    print("built %d pages into %s" % (len(files), out))
