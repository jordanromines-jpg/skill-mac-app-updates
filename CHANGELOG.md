# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/).

These versions cover the template itself.
- **MAJOR:** a breaking change to `release.py`, `init.py` or `build-release.sh` usage, or to the layout skill repos rely on.
- **MINOR:** a new scaffold file or script capability.
- **PATCH:** fixes and wording.

Releases are cut with `scripts/release.py`. Without a real skill name, `build-release.sh` refuses to package, so this repo's own releases carry no `.skill`.

## [Unreleased]

## [2.1.0] - 2026-10-15

### Added
- `plans/` (plangraph scaffold) and `.claude/settings.json` enabling the plangraph plugin, so plans are kept as a plangraph graph here.
- `CLAUDE.md` (which new skill repos inherit) and the README `scripts/init.py` writes tell Claude and other AI agents to read the entire README before they work in the repo for the first time, and whenever they are unfamiliar with it. This repo's own README says so too.

## [2.0.1] - 2026-10-10

### Changed
- `scripts/release.py` synced with template-repo 1.2.1, which also looks for `tools/build-release.sh`.

## [2.0.0] - 2026-10-10

### Changed
- **Breaking:** `scripts/init.py` requires names of the form `skill-<name>`. The skill's `name:` equals the repo name, and the default title drops the prefix.
- The repo is renamed `skill-template` → `template-skill`. Docs and examples use the new names. GitHub redirects the old URLs.

## [1.0.0] - 2026-10-10

### Added
- `SKILL.md` skeleton, `evals/trigger-evals.json`, `scripts/build-release.sh` (`.skill` packaging from the last commit, leaving out repo tooling) and `.release-assets.example`, which `init.py` activates.
- `scripts/release.py` from repo-template 1.0.0, plus `--trailer`.
- `scripts/init.py` for skills: fills the name into SKILL.md, `.release-assets` and the README, writes a fresh CHANGELOG and VERSION 0.0.0, then deletes itself.
- `CLAUDE.md`, including the rule that changing the description means re-running the trigger evals.

[Unreleased]: https://github.com/jordanromines-jpg/template-skill/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/jordanromines-jpg/template-skill/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/jordanromines-jpg/template-skill/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/jordanromines-jpg/template-skill/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/jordanromines-jpg/template-skill/releases/tag/v1.0.0
