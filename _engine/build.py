#!/usr/bin/env python3
"""Build the public site.  Usage: python3 _engine/build.py [output_dir]  (default: repository root)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render, pages  # noqa: E402

REDIRECTS = {"decisions": "decision-analysis", "costs": "operating-costs", "flagged": "flagged-for-review"}


def main(out=None):
    out = os.path.abspath(out or os.path.join(HERE, ".."))
    os.makedirs(os.path.join(out, "pages"), exist_ok=True)
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    with open(os.path.join(out, "assets", "style.css"), "w", encoding="utf-8") as fh:
        fh.write(render.CSS.strip() + "\n")
    C = pages.context()
    for fn in pages.ALL_PAGES:
        fn(C, out)
    for old, new in REDIRECTS.items():
        with open(os.path.join(out, "pages", old + ".html"), "w", encoding="utf-8") as fh:
            fh.write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
                     f'<meta http-equiv="refresh" content="0; url={new}.html"><title>Page moved</title></head>'
                     f'<body><a href="{new}.html">Continue to the current page</a></body></html>\n')
    print(f"built {len(pages.ALL_PAGES)} pages, {render.Counter.tables} tables, {render.Counter.rows} source-linked rows -> {out}")
    print(f"central case {C.T}+{C.H}y: best = {C.best}; " + ", ".join(f"{k} {render.money(C.d['options'][k]['liq_real'])}" for k in C.ranked))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
