# Release workflow: GitHub builds and signs, the Mac approves

> **Untested** until Tether's first real release. Commands follow Sparkle 2.10.0's documentation and tool source,
> GitHub's `actions/attest` v4 and `gh attestation verify`. When a step fails in practice, fix it here.

| Who | Does | Holds |
|---|---|---|
| GitHub Actions ([assets/release.yml](../assets/release.yml)) | Builds, code-signs with the stable identity, zips, attests, attaches the zip to a **draft** Release | The code-signing identity (secrets) |
| The releasing Mac (a person runs it) | Downloads the zip, verifies its attestation and signature, signs it for Sparkle, publishes the Release and the appcast | The EdDSA update key (login keychain) |

## One-time setup

### 1. The stable code-signing identity

A self-signed certificate is free and gives the app a **stable** identity: macOS ties Screen Recording,
Accessibility and other permissions to it, so they survive updates
([first-install-and-permissions.md](first-install-and-permissions.md)). Make it **once** and keep it for the life of
the app. If the app already has one (Tether: `scripts/setup-signing.sh`), export that one instead of making a new
one, or every existing install loses its permissions.

To make one (the person runs this; it writes only to a temporary folder):

```bash
NAME="MyApp Signing"; T="$(mktemp -d)"; umask 077
cat > "$T/cert.cnf" <<CNF
[req]
distinguished_name = dn
x509_extensions = ext
prompt = no
[dn]
CN = $NAME
[ext]
basicConstraints = critical, CA:false
keyUsage = critical, digitalSignature
extendedKeyUsage = critical, codeSigning
CNF
openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -config "$T/cert.cnf" -keyout "$T/key.pem" -out "$T/cert.pem"
P12PW="$(openssl rand -hex 16)"
openssl pkcs12 -export -legacy -inkey "$T/key.pem" -in "$T/cert.pem" -name "$NAME" -out "$T/id.p12" -passout "pass:$P12PW"
```

`-legacy` makes a `.p12` that macOS's `security import` reads (OpenSSL 3's default encryption isn't). Then:

1. Store `id.p12` and `$P12PW` in the password manager: this is the only copy of the identity.
2. Add them as repository secrets:
   `base64 -i "$T/id.p12" | gh secret set MAC_SIGNING_P12_BASE64` and
   `printf '%s' "$P12PW" | gh secret set MAC_SIGNING_P12_PASSWORD`.
3. Record its SHA-1 as a repository variable, so the workflow refuses any other identity:
   `openssl x509 -in "$T/cert.pem" -noout -fingerprint -sha1 | cut -d= -f2 | tr -d : | gh variable set MAC_SIGNING_IDENTITY_SHA1`
4. `rm -rf "$T"`.

The certificate is valid ten years. Code already signed keeps working after it expires, but new builds can't be
signed with it; plan a deliberate identity change (and the permissions reset it causes) well before then.

### 2. The permanent appcast Release

```bash
gh release create appcast --title "Update feed" --latest=false \
  --notes "appcast.xml for Sparkle. Don't delete: every installed copy reads it."
```

The app's `SUFeedURL` is then `https://github.com/OWNER/REPO/releases/download/appcast/appcast.xml`. Never delete
or rename this Release or its tag. GitHub redirects that address to its download servers over HTTPS, which Sparkle
follows.

### 3. The workflow

Copy [assets/release.yml](../assets/release.yml) to `.github/workflows/release.yml` and set `APP_NAME` and
`BUILD_SCRIPT`. The build script must write `build/<APP_NAME>.app` with Sparkle in `Contents/Frameworks` and
`$BUILD_NUMBER` (the workflow's run number, which only goes up) as `CFBundleVersion`. Attestations are free on
public repositories; a private one needs GitHub Enterprise Cloud.

#### Signing order

Inside out, never `--deep` (Sparkle's sandboxing docs): `Installer.xpc`, `Downloader.xpc` (keeping its
entitlements), `Autoupdate`, `Updater.app`, then `Sparkle.framework`, then the app. The example leaves out the
hardened runtime (`-o runtime`): it is needed only for notarization, which needs a paid Developer ID, and its
library validation expects a Team ID that a self-signed identity doesn't have (Sparkle's docs report the same
problem with ad-hoc signatures). Untested: confirm on the first release that Sparkle loads and installs.

## Each release

1. **Tag and push** on a clean `main`: `git tag v1.4.0 && git push origin v1.4.0`. The workflow leaves a draft
   Release `v1.4.0` with `MyApp-1.4.0.zip`.
2. **On the releasing Mac**, the person runs (set the first three lines):

```bash
REPO=OWNER/REPO; APP=MyApp; TAG=v1.4.0
BIN=~/path/to/Sparkle/bin                           # generate_keys, sign_update, generate_appcast
EXPECTED_SHA1=$(gh variable get MAC_SIGNING_IDENTITY_SHA1 -R "$REPO")
W="$(mktemp -d)"
gh release download "$TAG" -R "$REPO" -p "$APP-*.zip" -D "$W"
ZIP="$(ls "$W"/*.zip)"

# 1. Built by this repo's release workflow, from this repo? (Sigstore-backed build provenance)
gh attestation verify "$ZIP" -R "$REPO" --signer-workflow "$REPO/.github/workflows/release.yml"

# 2. Signed with the one stable identity?
ditto -x -k "$ZIP" "$W/check"
codesign --verify --deep --strict "$W/check/$APP.app"
codesign -d --extract-certificates="$W/check/cert" "$W/check/$APP.app"
[ "$(shasum -a 1 "$W/check/cert0" | cut -d' ' -f1 | tr a-f A-F)" = "$EXPECTED_SHA1" ] && echo "identity OK"
rm -rf "$W/check"

# 3. Sign for Sparkle (EdDSA key from this Mac's keychain) and write appcast.xml
"$BIN/generate_appcast" --download-url-prefix "https://github.com/$REPO/releases/download/$TAG/" "$W"

# 4. Publish: the release first (so the zip's address works), then the feed
gh release edit "$TAG" -R "$REPO" --draft=false
gh release upload appcast "$W/appcast.xml" -R "$REPO" --clobber
```

Stop at the first check that fails, and don't publish: a failed attestation or a different identity means the zip
didn't come from the expected build.

3. **Check it live**: `curl -sL https://github.com/$REPO/releases/download/appcast/appcast.xml` shows the new
   `sparkle:version` and an `enclosure` with `sparkle:edSignature`; an installed older copy offers the update
   (force a check with `defaults delete <bundle-id> SULastCheckTime`).

### What generate_appcast does here

- Reads each archive's `Info.plist`; names the appcast after `SUFeedURL`'s file name (`appcast.xml`).
- Signs each archive with the EdDSA key from the login keychain (allow the keychain prompt; `--account` if the key
  was made with one). `sign_update <zip>` does the same signing alone and prints the `sparkle:edSignature` and
  `length` attributes, if you ever write the appcast by hand.
- Keeps only the versions whose archives are in the folder. With one zip per run, the appcast holds just the newest
  version. That is enough for Sparkle, which offers the newest version the Mac can run. No delta updates.
- Release notes: put `MyApp-1.4.0.md` next to the zip and add `--embed-release-notes` (Markdown needs Sparkle 2.9+
  and macOS 12+). Untested.

## Never

- Put the EdDSA private key, or `generate_keys -x` output, in a GitHub secret, the repo or a log. Signing for
  Sparkle happens only on the releasing Mac.
- Regenerate the code-signing identity or the EdDSA key to "fix" a failing release. Find out why it fails.
- Publish a release whose attestation or identity check failed.
