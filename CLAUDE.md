# Conventions for Claude sessions in this skill repo

- **Read the README first.** Read the entire `README.md` before you work in this repo for the first time, and again whenever you are unfamiliar with it: it holds rules and context this file does not repeat.
- **Changelog:** every change that affects users or the repo gets a line under `## [Unreleased]` in `CHANGELOG.md`, in the same commit. Use the Keep a Changelog headings.
- **Version:** never edit `VERSION`, tags or releases by hand. Use `scripts/release.py patch|minor|major` and choose the level from the definitions at the top of `CHANGELOG.md`. Release only when the user asks, and run `--dry-run` first. The release rebuilds `dist/<name>.skill` and attaches it.
- **Description:** changing the `description` in `SKILL.md` changes when the skill triggers. Re-run the trigger evals (README, Tests) and record the result in the changelog.
- **Scripts:** put the skill's own scripts in `scripts/`. `release.py`, `init.py` and `build-release.sh` are repo tooling, and the package leaves them out.
- **Secrets:** they come from environment variables or the keychain, never from files in this repo.
