# template-skill

> **For Claude and other AI agents:** read this entire README before you work in this repo for the first time, and whenever you are unfamiliar with it. Then read `CLAUDE.md`.

A GitHub template for Claude skill repos. It's [template-repo](https://github.com/jordanromines-jpg/template-repo)'s versioning and releases, plus skill scaffolding.

| File | Purpose |
|---|---|
| `SKILL.md` | Skeleton with frontmatter (`name`, a pushy `description`) and sections for the before-acting check, the workflow and gotchas. |
| `scripts/` | The skill's own scripts go here. `release.py`, `init.py` and `build-release.sh` are repo tooling and are left out of the package. |
| `evals/trigger-evals.json` | Should- and shouldn't-trigger prompts for testing the description. |
| `scripts/build-release.sh` | Builds `dist/<name>.skill` from the last commit with `git archive`: SKILL.md plus scripts/, references/ and assets/. |
| `.release-assets.example` | `init.py` turns it into `.release-assets`, which attaches `dist/<name>.skill` to every GitHub Release. |
| `scripts/release.py` | Same as template-repo's: bump, date the changelog, commit, build the `.skill`, tag, push, release. |
| `scripts/init.py` | One-time setup: fills in the skill name, writes a fresh CHANGELOG, VERSION and README, then deletes itself. |
| `CLAUDE.md` | Changelog, release, trigger-eval and secrets conventions for Claude sessions. |

## Use

```bash
gh repo create skill-my-thing --private --template jordanromines-jpg/template-skill --clone
cd skill-my-thing
scripts/init.py skill-my-thing "My Thing"
git add -A && git commit -m "Initialise from template-skill" && git push
ln -s "$PWD" ~/.claude/skills/skill-my-thing
```

Next:
1. Write `SKILL.md` and the scripts, and fill in `evals/trigger-evals.json`.
2. Release v0.1.0 with `scripts/release.py minor`.
3. Add the repo to [hub-claude-skills](https://github.com/jordanromines-jpg/hub-claude-skills) as a submodule.

Name skill repos `skill-<what-it-does>`. The skill's `name:` is the repo name, and `init.py` refuses names without the `skill-` prefix. The full naming convention is in [template-repo](https://github.com/jordanromines-jpg/template-repo#naming).

## Versioning of this template

This repo versions itself with the same tools. `scripts/init.py` replaces this repo's own `CHANGELOG.md` in new repos.
