#!/usr/bin/env python3
"""Copy each source package's version from its _meta.lua into manifest.json.

ZenPM reads the installed plugin's version from `version = "..."` in _meta.lua
and offers an update when the manifest's `version` is greater.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "manifest.json"
# Same pattern ZenPM uses (internal/pkg/koreader_scan.go).
META_VERSION = re.compile(r"""\bversion\s*=\s*["']([^"']+)["']""")
SOURCE_URL = re.compile(r"^https://codeload\.github\.com/([^/]+/[^/]+)/zip/refs/heads/(.+)$")


def meta_version(source_url):
    match = SOURCE_URL.match(source_url)
    if not match:
        return None
    repo, branch = match.groups()
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/_meta.lua"
    with urllib.request.urlopen(url, timeout=30) as response:
        found = META_VERSION.search(response.read().decode("utf-8"))
    return found.group(1) if found else None


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = False
    for package in manifest["packages"]:
        if package.get("source_type") != "source":
            continue
        version = meta_version(package.get("source_url", ""))
        if version and version != package.get("version"):
            print(f"{package['id']}: {package.get('version')} -> {version}")
            package["version"] = version
            changed = True
    if changed:
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
