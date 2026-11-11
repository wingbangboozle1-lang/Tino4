#!/usr/bin/env python3
"""s-179ec133 — checks of the tax arithmetic against the official tables, and of the model's hand-checkable figures.
Run: python3 test_engine.py   (exit status 1 on any failure)"""
import sys
import engine as E

fails = []


def near(name, got, want, tol=0.01):
    ok = abs(got - want) <= tol
    print(("ok   " if ok else "FAIL ") + "%s: got %.2f, expected %.2f" % (name, got, want))
    if not ok:
        fails.append(name)


def split(status, **kw):
    full = E.total_tax(status, 1.0, 1.0, **kw)
    C = E.CAL[status]
    inc = kw.get("wages", 0) + kw.get("ord_nii", 0) + kw.get("pref", 0) + kw.get("recapture", 0)
    ti = max(0, inc - C["sd"])
    ca = E.bracket_tax(ti, C["br"], 1.0) + 0.01 * max(0, ti - 1_000_000)
    return full - ca, ca


# Federal, Rev. Proc. 2026-35 Table 1: "$11,974.00 plus 22% of the excess over $104,050"
near("federal joint, taxable $200,000", split("mfj", wages=233200)[0], 11974 + 0.22 * 95950)
# Federal, Table 3: "$60,349.00 plus 35% of the excess over $264,550"
near("federal single, taxable $300,000", split("single", wages=316600)[0], 60349 + 0.35 * 35450)
# California 2025 Schedule Y: "6,403.94 + 9.30% of the amount over 145,448"
near("California joint, taxable $200,000", split("mfj", wages=211412)[1], 6403.94 + 0.093 * 54552)
near("California joint tax at $82,904 (published 2,044.02)", E.bracket_tax(82904, E.CAL["mfj"]["br"], 1.0), 2044.02)
near("California joint tax at $742,958 (published 61,972.37)", E.bracket_tax(742958, E.CAL["mfj"]["br"], 1.0), 61972.37)
# Long-term gain stacked on ordinary income: 0% to $102,100, 15% to $633,600, then 20%; 3.8% on income over $250,000
want = (2560 + 0.12 * (100000 - 25600)) + 0.15 * (633600 - 102100) + 0.20 * (700000 - 633600) + 0.038 * (733200 - 250000)
near("federal joint, $100,000 ordinary + $600,000 long-term gain", split("mfj", wages=133200, pref=600000)[0], want)
# Proposition 19 arithmetic (BOE Letter 2026/026): base 400,000, market 1,800,000, allowance 1,044,586 -> 755,414
near("Proposition 19 new taxable value", E.prop19_value(400000, 1800000, 1044586), 755414)
# Hand-checkable baseline levels
L = E.levels(E.baseline_path())
near("Property A value 2045 = 3,100,000 x 1.03^19", L["VA"][2045], 3100000 * 1.03 ** 19, 1)
near("Parents' taxable value 2045 = 550,540 x 1.02^19", L["AVAp"][2045], 550540 * 1.02 ** 19, 1)
near("Proposition 19 allowance 2045 = 1,044,586 x 1.022^10", L["X19"][2045], 1044586 * 1.022 ** 10, 1)
near("2027 exclusion as published", L["EX"][2027], 15480000)
sys.exit(1 if fails else 0)
