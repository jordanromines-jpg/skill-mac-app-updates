---
name: skill-mac-app-updates
description: Ship a self-built Mac app as a download that updates itself with Sparkle 2, without a paid Apple Developer account. GitHub Actions builds and code-signs the app with one stable self-signed identity, the releasing Mac checks the build's attestation and signs the update with Sparkle's EdDSA key (which never goes to GitHub), and the appcast lives on a permanent GitHub Release. Use this whenever someone wants a Mac app to update itself, adds Sparkle or an appcast to an app, sets up SUFeedURL or SUPublicEDKey, runs generate_keys, sign_update or generate_appcast, writes a GitHub workflow that builds and signs a .app, or asks why macOS blocks their downloaded app or forgets its Screen Recording or Accessibility permission after an update. Also use it for "Open Anyway" first-install instructions and for choosing how a non-App-Store Mac app gets its updates.
---

# Mac App Updates

How to ship a Mac app you build yourself as a download that updates itself, using
[Sparkle 2](https://sparkle-project.org) (MIT licence), GitHub Actions and GitHub Releases, without paying Apple
for a Developer ID. Three references hold the detail; read the one for the step you're on:

| Step | Read |
|---|---|
| Put Sparkle in the app, make the update key | [references/sparkle-setup.md](references/sparkle-setup.md) |
| Build and sign on GitHub, approve and publish on the Mac | [references/release-workflow.md](references/release-workflow.md) and [assets/release.yml](assets/release.yml) |
| First install (Open Anyway) and keeping macOS permissions across updates | [references/first-install-and-permissions.md](references/first-install-and-permissions.md) |

> **Untested (v0.x):** this skill is written from Sparkle's documentation and source (2.10.0, checked 16 Oct 2026),
> not from a real release. The release-workflow and first-install pages are untested until Tether's first real
> release proves them. Where a step fails in practice, fix the skill and say so in its changelog.

## The shape

Two keys, two places. Keep them apart; that is the whole security model.

| Key | What it proves | Where it lives | Never |
|---|---|---|---|
| **Code-signing identity** (a self-signed certificate) | This is the same app as before, so macOS keeps its permissions | A GitHub Actions secret (a `.p12` and its password), used by the build | Changed or regenerated |
| **EdDSA update key** (Sparkle's `generate_keys`) | This update really came from you, so Sparkle installs it | The login keychain of the one Mac that approves releases | On GitHub, in a repo, a secret or a log |

1. A tag push makes GitHub's macOS runner build the app, sign it with the stable identity, zip it, attest it
   (record where it was built) and attach it to a GitHub Release.
2. On the releasing Mac, a person downloads that zip, checks the attestation with `gh attestation verify`, then runs
   Sparkle's `generate_appcast`, which signs the zip with the EdDSA key from the keychain and writes `appcast.xml`.
3. The Mac uploads `appcast.xml` to one permanent Release (tag `appcast`), whose download address is the app's
   `SUFeedURL`. Installed copies see the new item and update themselves.

If GitHub (or a stolen GitHub token) ever produces a bad build, it cannot ship it: Sparkle installs only archives
whose EdDSA signature matches the `SUPublicEDKey` built into the installed app, only the releasing Mac can make
that signature, and the Mac signs nothing whose attestation doesn't check out.

## Before acting

- **Never move the EdDSA private key to GitHub**, never print it, and never write it to a file in a repo. Moving it
  between Macs (`generate_keys -x` / `-f`) is for the person to do themselves; say so rather than doing it.
- Creating the signing certificate, adding GitHub secrets, and publishing a release are the person's calls: show
  the command and wait for a go.
- Check which Mac is the releasing Mac before running `generate_keys`: running it on a second Mac makes a
  **second, different key**, and updates signed with it fail on every installed copy.

## Workflow

1. Read [references/sparkle-setup.md](references/sparkle-setup.md): add Sparkle pinned to an exact 2.x version, set
   `SUFeedURL` and `SUPublicEDKey`, run `generate_keys` once on the releasing Mac.
2. Read [references/release-workflow.md](references/release-workflow.md): create the stable signing identity, add
   it as secrets, copy [assets/release.yml](assets/release.yml), create the permanent `appcast` Release.
3. Read [references/first-install-and-permissions.md](references/first-install-and-permissions.md) and put its
   Open Anyway steps on the download page.
4. Verify: install an older build, publish a newer one, and see the older one offer and install it with its
   permissions intact. Report what was observed, not what should happen.

## Gotchas (from the docs and source, not yet observed)

- `CFBundleVersion` must be a number that goes up every release (Sparkle compares it). A git hash or
  `git describe` output breaks update ordering.
- An update signed with a different code-signing identity still installs if its EdDSA signature is good, but
  macOS treats it as a new app: Screen Recording and Accessibility are lost. Sparkle won't warn you.
- Once a release is code-signed, an unsigned update is refused, and the EdDSA key and the signing identity can't
  both change in one update.
- `generate_appcast` keeps only the versions whose archives are in its folder. With one archive per run (this
  skill's way) the appcast always holds just the newest version, and there are no delta updates.
