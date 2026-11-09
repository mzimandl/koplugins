#!/usr/bin/env python3
"""Bring the package versions in manifest.json up to date.

- `source_type: "source"` packages (installed from a branch zip): copy the
  version from the branch's _meta.lua. ZenPM reads the installed plugin's
  version from `version = "..."` in _meta.lua and offers an update when the
  manifest's `version` is greater.
- `source_type: "release"` packages (installed from GitHub release assets):
  write versions/<id>.json (every release with its `source_asset`, ZenPM's
  versions_url format) and set `version` to the newest release and
  `prerelease_version` to the newest pre-release, which ZenPM offers only with
  Beta updates on.

GITHUB_TOKEN (optional) raises the GitHub API rate limit.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
# Same pattern ZenPM uses (internal/pkg/koreader_scan.go).
META_VERSION = re.compile(r"""\bversion\s*=\s*["']([^"']+)["']""")
SOURCE_URL = re.compile(r"^https://codeload\.github\.com/([^/]+/[^/]+)/zip/refs/heads/(.+)$")
GITHUB_REPO = re.compile(r"^https://github\.com/([^/]+/[^/]+?)/?$")


def fetch(url, api=False):
    request = urllib.request.Request(url)
    if api:
        request.add_header("Accept", "application/vnd.github+json")
        if os.environ.get("GITHUB_TOKEN"):
            request.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def meta_version(source_url):
    match = SOURCE_URL.match(source_url)
    if not match:
        return None
    repo, branch = match.groups()
    found = META_VERSION.search(fetch(f"https://raw.githubusercontent.com/{repo}/{branch}/_meta.lua"))
    return found.group(1) if found else None


def release_versions(package):
    """versions.json content, newest stable and newest pre-release version."""
    match = GITHUB_REPO.match(package.get("source", ""))
    if not match:
        return None
    data = json.loads(fetch(f"https://api.github.com/repos/{match.group(1)}/releases?per_page=100", api=True))
    releases, stable, pre = [], None, None
    for release in data:  # newest first
        if release.get("draft"):
            continue
        assets = [
            {key: asset[key] for key in ("name", "browser_download_url", "size", "digest") if asset.get(key)}
            for asset in release.get("assets", [])
            if asset.get("name") == package.get("source_asset")
        ]
        if not assets:
            continue
        for asset in assets:
            asset["url"] = asset.pop("browser_download_url")
        tag = release["tag_name"]
        entry = {"tag_name": tag, "name": release.get("name") or tag, "assets": assets}
        if release.get("prerelease"):
            entry["prerelease"] = True
            pre = pre or tag.lstrip("v")
        else:
            stable = stable or tag.lstrip("v")
        releases.append(entry)
    return {"releases": releases}, stable, pre


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = False
    for package in manifest["packages"]:
        fields = {}
        if package.get("source_type") == "source":
            version = meta_version(package.get("source_url", ""))
            if version:
                fields["version"] = version
        elif package.get("source_type") == "release":
            found = release_versions(package)
            if not found:
                continue
            versions, stable, pre = found
            path = ROOT / "versions" / f"{package['id']}.json"
            text = json.dumps(versions, indent=2, ensure_ascii=False) + "\n"
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                path.parent.mkdir(exist_ok=True)
                path.write_text(text, encoding="utf-8")
                print(f"{package['id']}: {path.relative_to(ROOT)} updated")
            fields["versions_url"] = f"versions/{package['id']}.json"
            if stable:
                fields["version"] = stable
            fields["prerelease_version"] = pre
        for key, value in fields.items():
            if package.get(key) != value:
                print(f"{package['id']}: {key} {package.get(key)} -> {value}")
                if value is None:
                    package.pop(key, None)
                else:
                    package[key] = value
                changed = True
    if changed:
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
