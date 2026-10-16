# skill-mac-app-updates

> **For Claude and other AI agents:** read this entire README before you work in this repo for the first time, and whenever you are unfamiliar with it. Then read `CLAUDE.md`.

A Claude skill: one sentence on what it does and when Claude uses it.

## Install

Claude Code, from this repo's working clone:

```bash
ln -s "$PWD" ~/.claude/skills/skill-mac-app-updates
```

Claude.ai: upload `dist/skill-mac-app-updates.skill` from the latest GitHub Release under Settings → Capabilities → Skills.

## Use

What a user says to trigger it, and what they get back. Include the scripts' main commands here.

## Tests

`evals/trigger-evals.json` holds should- and shouldn't-trigger prompts. Check triggering against the installed skill, one prompt at a time: skill-creator's `run_eval` with `--num-workers 1`. Parallel workers install competing copies of the skill and report false failures.

## Versioning and releases

The version is in [`VERSION`](VERSION), and the history is in [`CHANGELOG.md`](CHANGELOG.md). Every change adds a line under `[Unreleased]`.

To release, run `scripts/release.py patch|minor|major` (add `--dry-run` to preview first). It does the following:
- bumps the version and dates the changelog
- commits, then rebuilds `dist/skill-mac-app-updates.skill` from that commit (`scripts/build-release.sh`)
- tags, pushes, and publishes a GitHub Release with the `.skill` attached

After releasing, move the [hub-claude-skills](https://github.com/jordanromines-jpg/hub-claude-skills) hub to point at the new version.

---
Created from [template-skill](https://github.com/jordanromines-jpg/template-skill).
