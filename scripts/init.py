#!/usr/bin/env python3
"""One-time setup for a skill repo created from this template. Run right after "Use this template":

  scripts/init.py skill-<name> ["Skill Title"]

The name is lowercase-with-hyphens, starts with "skill-" and equals the repo name. The script fills the name into
SKILL.md, .release-assets and the README, writes a fresh CHANGELOG.md (starting at [Unreleased])
and VERSION 0.0.0 so the template's own history doesn't carry over, then deletes itself.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_LINK = "[template-skill](https://github.com/jordanromines-jpg/template-skill)"

README = """# {name}

> **For Claude and other AI agents:** read this entire README before you work in this repo for the first time, and whenever you are unfamiliar with it. Then read `CLAUDE.md`.

A Claude skill: one sentence on what it does and when Claude uses it.

## Install

Claude Code, from this repo's working clone:

```bash
ln -s "$PWD" ~/.claude/skills/{name}
```

Claude.ai: upload `dist/{name}.skill` from the latest GitHub Release under Settings → Capabilities → Skills.

## Use

What a user says to trigger it, and what they get back. Include the scripts' main commands here.

## Tests

`evals/trigger-evals.json` holds should- and shouldn't-trigger prompts. Check triggering against the installed skill, one prompt at a time: skill-creator's `run_eval` with `--num-workers 1`. Parallel workers install competing copies of the skill and report false failures.

## Versioning and releases

The version is in [`VERSION`](VERSION), and the history is in [`CHANGELOG.md`](CHANGELOG.md). Every change adds a line under `[Unreleased]`.

To release, run `scripts/release.py patch|minor|major` (add `--dry-run` to preview first). It does the following:
- bumps the version and dates the changelog
- commits, then rebuilds `dist/{name}.skill` from that commit (`scripts/build-release.sh`)
- tags, pushes, and publishes a GitHub Release with the `.skill` attached

After releasing, move the [hub-claude-skills](https://github.com/jordanromines-jpg/hub-claude-skills) hub to point at the new version.

---
Created from {template_link}.
"""

CHANGELOG = """# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/).

- **MAJOR:** a breaking change to the skill's scripts (flags, outputs, exit codes, file formats) or its name.
- **MINOR:** a new capability, or a behaviour or trigger change users would notice.
- **PATCH:** bug fixes, or docs and description wording with no change in behaviour.

Every release is tagged `vX.Y.Z`, published as a GitHub Release with `dist/<name>.skill` attached, and cut with `scripts/release.py`.

## [Unreleased]

### Added
- Skill scaffold from {template_link}.
"""


def main() -> None:
    if len(sys.argv) < 2 or not re.fullmatch(r"skill(-[a-z0-9]+)+", sys.argv[1]):
        sys.exit(__doc__ + "\nSkill repos and skills are named skill-<what-it-does>, e.g. skill-imgbb-upload.")
    name = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else name.removeprefix("skill-").replace("-", " ").capitalize()

    skill = (ROOT / "SKILL.md").read_text().replace("SKILL_NAME", name).replace("SKILL_TITLE", title)
    (ROOT / "SKILL.md").write_text(skill)
    example = ROOT / ".release-assets.example"
    (ROOT / ".release-assets").write_text(example.read_text().replace("SKILL_NAME", name))
    example.unlink()
    (ROOT / "README.md").write_text(README.format(name=name, template_link=TEMPLATE_LINK))
    (ROOT / "CHANGELOG.md").write_text(CHANGELOG.format(template_link=TEMPLATE_LINK))
    (ROOT / "VERSION").write_text("0.0.0\n")
    Path(__file__).unlink()
    print(f"Initialised skill {name!r}. Next: write SKILL.md (especially the description), "
          "add scripts/, fill evals/trigger-evals.json, commit, then `scripts/release.py minor`.")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)


if __name__ == "__main__":
    main()
