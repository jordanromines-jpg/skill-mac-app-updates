# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/).

- **MAJOR:** a breaking change to the skill's scripts (flags, outputs, exit codes, file formats) or its name.
- **MINOR:** a new capability, or a behaviour or trigger change users would notice.
- **PATCH:** bug fixes, or docs and description wording with no change in behaviour.

Every release is tagged `vX.Y.Z`, published as a GitHub Release with `dist/<name>.skill` attached, and cut with `scripts/release.py`.

## [Unreleased]

### Added
- Skill scaffold from [template-skill](https://github.com/jordanromines-jpg/template-skill).
- `SKILL.md` (when to use it, the two-keys model) and `references/sparkle-setup.md`: Sparkle 2.10.0 pinned exactly, `SUFeedURL`, `SUPublicEDKey`, `CFBundleVersion`, `generate_keys` with the private key only in the releasing Mac's keychain. Written from Sparkle's docs and source; untested until Tether's first release.
- `references/release-workflow.md` and `assets/release.yml`: a macOS runner builds, signs with the one stable self-signed identity (checked against `MAC_SIGNING_IDENTITY_SHA1`), zips with `ditto`, attests with `actions/attest@v4` and attaches the zip to a draft Release; the releasing Mac verifies the attestation and identity, runs `generate_appcast` with its keychain key, publishes the Release and uploads `appcast.xml` to the permanent `appcast` Release. The workflow holds no update key. Untested.
