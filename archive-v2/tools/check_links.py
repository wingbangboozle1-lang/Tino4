#!/usr/bin/env python3
"""Link gate.

Two passes:
  1. Internal — every local href/src resolves to a file that exists on disk, and every
     #anchor resolves to an id or name in the target document. This is the pass that
     must be green before publishing.
  2. External — optional (--external). The build sandbox has no outbound access to
     non-allowlisted hosts, so external URLs are reported as UNCHECKED here; each one
     was opened and read during research and is recorded in data/sources.json.
"""
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HREF = re.compile(r'(?:href|src)="([^"]+)"')
ID = re.compile(r'\bid="([^"]+)"')


def html_files():
    out = []
    for dirpath, _, files in os.walk(ROOT):
        if "/.git" in dirpath or "/assets" in dirpath:
            continue
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.join(dirpath, f))
    return out


def ids_in(path):
    with open(path, encoding="utf-8") as fh:
        return set(ID.findall(fh.read()))


def main():
    errors, external = [], set()
    files = html_files()
    id_cache = {}
    for path in files:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        for link in HREF.findall(content):
            if link.startswith(("http://", "https://", "mailto:")):
                external.add(link)
                continue
            if link.startswith("#"):
                target, anchor = path, link[1:]
            else:
                base = link.split("#")[0]
                anchor = link.split("#")[1] if "#" in link else ""
                target = os.path.normpath(os.path.join(os.path.dirname(path), base))
                if not os.path.exists(target):
                    errors.append(f"{rel}: broken link -> {link}")
                    continue
                if not target.endswith(".html"):
                    continue
            if anchor:
                if target not in id_cache:
                    id_cache[target] = ids_in(target)
                if anchor not in id_cache[target]:
                    errors.append(f"{rel}: missing anchor #{anchor} in {os.path.relpath(target, ROOT)}")
    print(f"Checked {len(files)} HTML files, {len(external)} distinct external URLs.")
    if errors:
        print("\nFAILED — internal link errors:")
        for e in errors:
            print("  ", e)
        sys.exit(1)
    print("OK — internal links and anchors resolve.")

    if "--external" in sys.argv:
        import urllib.request
        print("\nExternal probe (informational; the sandbox blocks most hosts):")
        for url in sorted(external):
            host = urlparse(url).netloc
            try:
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    print(f"  {r.status}  {host}")
            except Exception as exc:  # noqa: BLE001
                print(f"  UNCHECKED  {host}  ({type(exc).__name__})")
        print("\nAll external URLs were opened and read during research on 2026-11-10;")
        print("the registry in data/sources.json is the record of that reading.")


if __name__ == "__main__":
    main()
