#!/usr/bin/env python3
"""Data gate: run before every build. Fails loudly rather than publishing a bad row."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OFFICIAL_DOMAINS = (
    "irs.gov", "uscode.house.gov", "leginfo.legislature.ca.gov", "boe.ca.gov",
    "asr.santaclaracounty.gov", "santaclaracounty.gov", "payments.sccgov.org",
    "sftreasurer.org", "sfassessor.org", "sf.gov", "sfpuc.gov", "pge.com",
    "insurance.ca.gov", "cfpnet.com", "huduser.gov", "census.gov", "ftb.ca.gov",
    "courts.ca.gov", "santaclara.courts.ca.gov", "cpuc.ca.gov", "sjwater.com",
)

errors, warnings = [], []


def load(p):
    with open(os.path.join(ROOT, "data", p)) as fh:
        return json.load(fh)


sources = load("sources.json")["sources"]
facts = load("facts.json")["facts"]
assumptions = load("assumptions.json")

ids = [s["id"] for s in sources]
if len(ids) != len(set(ids)):
    errors.append("duplicate source id")

for s in sources:
    if not s["url"].startswith("https://"):
        errors.append(f"{s['id']}: URL is not https")
    if not any(d in s["url"] for d in OFFICIAL_DOMAINS):
        errors.append(f"{s['id']}: domain not on the official-source allowlist -> {s['url']}")
    if not s.get("covers"):
        warnings.append(f"{s['id']}: no 'covers' note")

fids = [f["id"] for f in facts]
if len(fids) != len(set(fids)):
    errors.append("duplicate fact id")

for f in facts:
    if f["status"] not in ("verified", "reported", "flagged"):
        errors.append(f"{f['id']}: unknown status {f['status']}")
    if f["status"] == "verified":
        if not f.get("source"):
            errors.append(f"{f['id']}: marked verified with no source")
        elif f["source"] not in ids:
            errors.append(f"{f['id']}: source id not in registry ({f['source']})")
    if f["status"] in ("reported", "flagged") and f.get("source"):
        warnings.append(f"{f['id']}: {f['status']} but cites a source ({f['source']}) — check the badge is right")
    for bad in ("TBD", "TODO", "N/A", "unknown"):
        if bad.lower() in str(f["value"]).lower():
            warnings.append(f"{f['id']}: placeholder-looking value {f['value']!r}")

# no personal information patterns: street numbers, APNs, SSNs
pn = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{3}-\d{3}-\d{3}\b|\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Way|Boulevard|Blvd)\b")
for f in facts:
    if pn.search(str(f)):
        errors.append(f"{f['id']}: possible personal identifier")

# assumption completeness
for key in ("appreciation", "inflation", "investment", "property_tax", "capital_gains",
            "rental_income_tax", "estate_exclusion_2026", "prop19_cap_2026"):
    if key not in assumptions:
        errors.append(f"assumptions missing {key}")

print(f"Sources: {len(sources)}  Facts: {len(facts)}  "
      f"(verified {sum(1 for f in facts if f['status']=='verified')}, "
      f"reported {sum(1 for f in facts if f['status']=='reported')}, "
      f"flagged {sum(1 for f in facts if f['status']=='flagged')})")
for w in warnings:
    print("  warn:", w)
if errors:
    print("\nFAILED")
    for e in errors:
        print("  error:", e)
    sys.exit(1)
print("OK — data gate passed.")
