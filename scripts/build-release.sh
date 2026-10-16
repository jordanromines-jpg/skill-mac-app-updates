#!/bin/sh
# Build dist/<name>.skill (zip installable on Claude.ai) from the last commit.
# release.py runs this after its release commit; you can also run it by hand after committing.
# Packages SKILL.md plus scripts/, references/ and assets/ (whichever exist), leaving out repo tooling.
set -eu
cd "$(dirname "$0")/.."
name=$(sed -n 's/^name: *//p' SKILL.md | head -1)
[ -n "$name" ] || { echo "SKILL.md has no 'name:'" >&2; exit 1; }
if [ "$name" = "SKILL_NAME" ]; then echo "SKILL.md name is still the template placeholder; nothing to package"; exit 0; fi
paths="SKILL.md"
for d in scripts references assets; do [ -d "$d" ] && paths="$paths $d"; done
mkdir -p dist
# shellcheck disable=SC2086
git archive --format=zip --prefix="$name/" -o "dist/$name.skill" HEAD $paths \
  ':(exclude)scripts/release.py' ':(exclude)scripts/init.py' ':(exclude)scripts/build-release.sh'
unzip -l "dist/$name.skill"
