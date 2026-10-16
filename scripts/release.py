#!/usr/bin/env python3
"""Cut a release: bump VERSION, move CHANGELOG [Unreleased] into a dated section, tag, push,
and publish a GitHub Release whose notes are that section.

  scripts/release.py patch|minor|major|X.Y.Z [--dry-run] [--trailer "Co-Authored-By: ..."]

Steps, in order:
  1. Checks: on the default branch, clean tree, in sync with origin, [Unreleased] has entries.
  2. Writes VERSION and CHANGELOG.md (new dated section, empty [Unreleased], compare links).
  3. Commits "Release vX.Y.Z".
  4. If scripts/build-release.sh (or tools/build-release.sh) exists, runs it; anything it changes is committed as
     "Build artifacts for vX.Y.Z" (e.g. a packaged .skill file built from the release commit).
  5. Tags vX.Y.Z, pushes, and runs `gh release create` with the section as notes. Files listed
     in .release-assets (one path per line) are attached.

Python 3.9+ standard library, git and gh. See CHANGELOG.md for what counts as major/minor/patch.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def run(*cmd: str, capture: bool = True) -> str:
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture)
    if r.returncode != 0:
        sys.exit(f"failed: {' '.join(cmd)}\n{(r.stderr or r.stdout or '').strip()}")
    return (r.stdout or "").strip()


def bump(current: str, how: str) -> str:
    if SEMVER.match(how):
        return how
    m = SEMVER.match(current)
    if not m:
        sys.exit(f"VERSION is not X.Y.Z: {current!r}")
    major, minor, patch = map(int, m.groups())
    if how == "major":
        return f"{major + 1}.0.0"
    if how == "minor":
        return f"{major}.{minor + 1}.0"
    if how == "patch":
        return f"{major}.{minor}.{patch + 1}"
    sys.exit(f"expected patch, minor, major or X.Y.Z, got {how!r}")


def repo_url() -> str:
    return run("gh", "repo", "view", "--json", "url", "-q", ".url")


def rewrite_changelog(text: str, old: str, new: str, url: str) -> tuple[str, str]:
    """Return (new changelog text, release notes for `new`)."""
    m = re.search(r"^## \[Unreleased\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]: |\Z)", text, re.S | re.M)
    if not m:
        sys.exit("CHANGELOG.md has no '## [Unreleased]' section")
    notes = m.group(1).strip()
    if not notes:
        sys.exit("[Unreleased] is empty: add entries describing this release first")
    section = f"## [Unreleased]\n\n## [{new}] - {date.today().isoformat()}\n\n{notes}\n\n"
    text = text[:m.start()] + section + text[m.end():]

    # Compare links at the bottom: point [Unreleased] at the new tag, add a link for the new version.
    unreleased_link = f"[Unreleased]: {url}/compare/v{new}...HEAD"
    new_link = (f"[{new}]: {url}/compare/v{old}...v{new}" if run("git", "tag", "-l", f"v{old}")
                else f"[{new}]: {url}/releases/tag/v{new}")
    if re.search(r"^\[Unreleased\]: .*$", text, re.M):
        text = re.sub(r"^\[Unreleased\]: .*$", f"{unreleased_link}\n{new_link}", text, count=1, flags=re.M)
    else:
        text = text.rstrip() + f"\n\n{unreleased_link}\n{new_link}\n"
    return text, notes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bump", help="patch | minor | major | X.Y.Z")
    ap.add_argument("--dry-run", action="store_true", help="show the result without changing anything")
    ap.add_argument("--trailer", action="append", default=[],
                    help='commit trailer to add, e.g. "Co-Authored-By: Name <email>" (repeatable)')
    a = ap.parse_args()

    branch = run("git", "rev-parse", "--abbrev-ref", "HEAD")
    default = run("gh", "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name")
    if branch != default:
        sys.exit(f"on {branch!r}; releases are cut from {default!r}")
    if run("git", "status", "--porcelain"):
        sys.exit("working tree has uncommitted changes; commit them first")
    run("git", "fetch", "-q", "origin", default)
    if run("git", "rev-parse", "HEAD") != run("git", "rev-parse", f"origin/{default}"):
        sys.exit(f"local {default} differs from origin/{default}; pull or push first")

    old = (ROOT / "VERSION").read_text().strip()
    new = bump(old, a.bump)
    if run("git", "tag", "-l", f"v{new}"):
        sys.exit(f"tag v{new} already exists")
    url = repo_url()
    changelog, notes = rewrite_changelog((ROOT / "CHANGELOG.md").read_text(), old, new, url)
    assets = [l.strip() for l in (ROOT / ".release-assets").read_text().splitlines()
              if l.strip() and not l.startswith("#")] if (ROOT / ".release-assets").exists() else []

    print(f"{old} -> {new}\n\n--- release notes ---\n{notes}\n---------------------")
    if assets:
        print("assets:", ", ".join(assets))
    if a.dry_run:
        print("dry run: nothing changed")
        return

    (ROOT / "VERSION").write_text(new + "\n")
    (ROOT / "CHANGELOG.md").write_text(changelog)
    run("git", "add", "VERSION", "CHANGELOG.md")
    trailers = "".join(f"\n\n{t}" if i == 0 else f"\n{t}" for i, t in enumerate(a.trailer))
    run("git", "commit", "-q", "-m", f"Release v{new}{trailers}")

    build = next((b for b in (ROOT / "scripts" / "build-release.sh", ROOT / "tools" / "build-release.sh") if b.exists()), None)
    if build:
        run("sh", str(build), capture=False)
        if run("git", "status", "--porcelain"):
            run("git", "add", "-A")
            run("git", "commit", "-q", "-m", f"Build artifacts for v{new}{trailers}")

    for path in assets:
        if not (ROOT / path).exists():
            sys.exit(f".release-assets lists {path}, which does not exist (nothing pushed yet; "
                     f"undo with: git reset --hard origin/{default})")

    run("git", "tag", "-a", f"v{new}", "-m", f"v{new}")
    run("git", "push", "-q", "origin", default)
    run("git", "push", "-q", "origin", f"v{new}")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(notes + "\n")
    run("gh", "release", "create", f"v{new}", "--title", f"v{new}", "--notes-file", f.name,
        "--verify-tag", "--latest", *[str(ROOT / p) for p in assets])
    print(f"released v{new}: {url}/releases/tag/v{new}")


if __name__ == "__main__":
    main()
