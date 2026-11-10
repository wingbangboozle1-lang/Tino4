#!/usr/bin/env python3
"""Append verified-fact records to a data/facts/*.json file.

Usage: python3 tools/add_facts.py <category> < records.json
Each record needs: id, topic, value, quote, source_name, source_url, status.
'verified_on' defaults to today's date if omitted.
"""
import json, sys, datetime, pathlib

REQUIRED = ["id", "topic", "value", "source_name", "source_url", "status"]
ALLOWED_STATUS = {"verified", "unverified"}


def main():
    cat = sys.argv[1]
    path = pathlib.Path(__file__).resolve().parent.parent / "data" / "facts" / f"{cat}.json"
    existing = json.loads(path.read_text()) if path.exists() else []
    ids = {r["id"] for r in existing}
    new = json.load(sys.stdin)
    today = datetime.date.today().isoformat()
    for r in new:
        for k in REQUIRED:
            if k not in r:
                raise SystemExit(f"{r.get('id')}: missing field {k}")
        if r["status"] not in ALLOWED_STATUS:
            raise SystemExit(f"{r['id']}: bad status {r['status']}")
        if r["status"] == "verified" and not (r["value"] and r.get("quote")):
            raise SystemExit(f"{r['id']}: verified facts need a value and a supporting quote")
        if r["status"] == "unverified" and r["value"]:
            raise SystemExit(f"{r['id']}: unverified facts must have a blank value")
        if not r["source_url"].startswith("https://"):
            raise SystemExit(f"{r['id']}: source_url must be https")
        if r["id"] in ids:
            raise SystemExit(f"duplicate id {r['id']}")
        r.setdefault("quote", "")
        r.setdefault("verified_on", today)
        ids.add(r["id"])
        existing.append(r)
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
    print(f"{path.name}: {len(existing)} records ({len(new)} added)")


if __name__ == "__main__":
    main()
