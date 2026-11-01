#!/usr/bin/env python3
"""Check a creator-owned Artilect production without running its upstream code."""
import configparser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

def require(ok, message):
    if not ok:
        ERRORS.append(message)

def valid_public_url(s):
    try:
        u = urlparse(s)
        return (u.scheme == "https" and bool(u.netloc)
                and not u.username and not u.password)
    except ValueError:
        return False

# An untouched scaffold is not yet a submitted production. Keep initial forks green;
# as soon as the creator edits the recipe or adds technologies, enforce every check.
starter = ROOT / "artilect.json"
if starter.is_file() and not (ROOT / ".gitmodules").exists():
    try:
        data = json.loads(starter.read_text(encoding="utf-8"))
        if (data.get("title") == "TODO: Name your production"
                and data.get("summary") == "TODO: One sentence about what I made"):
            print("✓ Blank Artilect starter ready. Add technologies and create real media before submitting.")
            sys.exit(0)
    except (ValueError, OSError):
        pass

metadata = ROOT / "artilect.json"
if not metadata.exists():
    ERRORS.append("Missing artilect.json")
    obj = {}
else:
    try:
        obj = json.loads(metadata.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        ERRORS.append("artilect.json must be valid JSON")
        obj = {}
require(obj.get("schema") == 1, "artilect.json schema must be 1")
for field in ("title", "summary", "reproduce", "rights_notes"):
    v = obj.get(field, "")
    require(isinstance(v, str) and bool(v.strip()) and "TODO" not in v,
            "Set a real " + field + " in artilect.json")
media_url = obj.get("media_url") or ""
media_path = obj.get("media_path") or ""
require(bool(media_url or media_path), "Provide media_url or media_path to a real creative output")
if media_url:
    require(valid_public_url(media_url), "media_url must use HTTPS")
if media_path:
    path = (ROOT / media_path).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(),
            "media_path must name a file inside this repository")

for path in ("README.md", "AGENTS.md", "production/README.md"):
    require((ROOT / path).is_file(), "Missing " + path)

if (ROOT / "README.md").is_file():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("example.com/replace-this" not in readme,
            "Replace the starter watch link with your real media link")
    require("Replace this sentence" not in readme,
            "Describe the actual creative work in README.md")

mods = ROOT / ".gitmodules"
entries = {}
if not mods.exists():
    ERRORS.append("Missing .gitmodules: use git submodule add for at least two technologies")
else:
    cp = configparser.ConfigParser(interpolation=None)
    try:
        cp.read(mods, encoding="utf-8")
        for name in cp.sections():
            path = cp.get(name, "path", fallback="")
            url = cp.get(name, "url", fallback="")
            require(bool(re.fullmatch(r"technologies/[A-Za-z0-9_.-]+", path)),
                    "Submodule must be directly inside technologies/: " + path)
            require(bool(re.fullmatch(r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+(?:\.git)?", url)),
                    "Use a public HTTPS GitHub upstream URL: " + url)
            require(path not in entries, "Duplicate technology path: " + path)
            entries[path] = url
    except (ValueError, configparser.Error) as exc:
        ERRORS.append("Invalid .gitmodules: " + str(exc))
require(len(entries) >= 2, "Include at least two independently developed upstream technologies")
try:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--stage"],
        check=True, capture_output=True, text=True
    )
    links = {line.split("\t", 1)[1] for line in result.stdout.splitlines()
             if line.startswith("160000 ")}
    for path in entries:
        require(path in links, path + " is not a tracked Git submodule (mode 160000)")
except (OSError, subprocess.CalledProcessError):
    ERRORS.append("Could not inspect Git index; run inside a Git repository")

if ERRORS:
    for error in ERRORS:
        print("✗", error, file=sys.stderr)
    sys.exit(1)
print("✓ Artilect production contract valid; upstream code was not executed.")
