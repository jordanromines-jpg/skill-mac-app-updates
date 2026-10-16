# skill-mac-app-updates

> **For Claude and other AI agents:** read this entire README before you work in this repo for the first time, and whenever you are unfamiliar with it. Then read `CLAUDE.md`.

A Claude skill for shipping a self-built Mac app as a download that updates itself with [Sparkle 2](https://sparkle-project.org), without a paid Apple Developer account: GitHub Actions builds and signs the app with one stable identity, and the releasing Mac checks the build's attestation and signs the update with Sparkle's EdDSA key, which never goes to GitHub.

**Status: 0.x, untested.** Written from Sparkle's documentation and source; the release and first-install steps are proved only once Tether ships its first release with them.

## Install

Claude Code, from this repo's working clone:

```bash
ln -s "$PWD" ~/.claude/skills/skill-mac-app-updates
```

Claude.ai: upload `dist/skill-mac-app-updates.skill` from the latest GitHub Release under Settings → Capabilities → Skills.

## Use

Ask Claude to make a Mac app update itself, add Sparkle or an appcast, write the GitHub workflow that builds and signs a `.app`, or explain why macOS blocks a downloaded app or forgets its permissions after an update. Claude reads `SKILL.md`, then the reference for the step at hand:

- `references/sparkle-setup.md`: Sparkle in the app, `SUFeedURL`, `SUPublicEDKey`, `generate_keys`
- `references/release-workflow.md` and `assets/release.yml`: GitHub builds and signs, the Mac verifies and publishes the appcast
- `references/first-install-and-permissions.md`: Open Anyway, and keeping Screen Recording and Accessibility across updates

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
