# First install and permissions

> **Untested** until Tether's first real release. Sources: Apple's Mac User Guide page
> [Open a Mac app from an unknown developer](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac),
> Apple's [TN3127: Inside Code Signing: Requirements](https://developer.apple.com/documentation/technotes/tn3127-inside-code-signing-requirements),
> and Sparkle 2.10.0's source (`SUPlainInstaller.m`, `SPUUpdateDriver.m`, `SUUpdateValidator.m`).

## Why macOS blocks the first open

A browser marks a downloaded file as quarantined. When the app is first opened, Gatekeeper checks it. An app that
isn't notarized by Apple (notarizing needs a paid Developer ID) is blocked with a message that Apple couldn't
verify it. This happens **once**, on the first install. Sparkle's updates don't trigger it again: Sparkle releases
the new copy from quarantine itself when it installs an update.

On macOS 15 (Sequoia) and later, Control-click › Open no longer gets past this. The only way through in the
interface is **Open Anyway** in System Settings.

## Steps to put on the download page

Write them for someone who has never done it. Adjust the app name.

1. Download `MyApp-1.4.0.zip` and double-click it to unzip.
2. Drag **MyApp** into your **Applications** folder. Open it from there, not from Downloads.
3. Double-click MyApp. macOS says it can't verify it. Click **Done** (not Move to Trash).
4. Open **System Settings › Privacy & Security** and scroll down to **Security**. Next to the message about MyApp,
   click **Open Anyway**. The button is there for about an hour after step 3; if it's gone, repeat step 3.
5. Enter your Mac login password and click **OK**, then **Open Anyway** again if asked.

After that, MyApp opens normally and updates itself.

Why step 2 matters: an app opened from where it was downloaded runs from a temporary read-only location
("App Translocation"). Sparkle refuses to update it there and tells the user to move it to Applications and relaunch.

For people comfortable with Terminal there is an alternative to steps 3–5:
`xattr -d com.apple.quarantine /Applications/MyApp.app`. Don't make it the main path, and never suggest turning off
Gatekeeper for the whole Mac.

## Why the signing identity must never change

macOS remembers privacy permissions (Screen Recording, Accessibility, Microphone, Files and Folders…) against the
app's **designated requirement**: a rule, built into its code signature, that says which code counts as this app.
Each time the app uses a protected resource, macOS checks that this version still satisfies the rule it stored
when the person said yes (TN3127).

| How the app is signed | Its designated requirement | Permissions after an update |
|---|---|---|
| Not signed | None | Not reliably remembered |
| Ad-hoc ("Sign to Run Locally") | Tied to that exact build's code hash | **Lost on every update**: the person is asked again, or the app silently stops working |
| One stable self-signed identity (this skill) | The bundle identifier plus that certificate | **Kept**, as long as the certificate and bundle identifier never change |
| Developer ID (paid) | The bundle identifier plus your Apple Team ID | Kept, even across certificate renewals |

Check what an app's requirement is with `codesign -d -r- MyApp.app`. With a self-signed identity it names the
identifier and pins the certificate (expect a `certificate leaf = H"…"` clause); confirm that on the first real
build and note the result here.

So:
- Make the identity once and store it safely ([release-workflow.md](release-workflow.md#1-the-stable-code-signing-identity)).
  The workflow refuses to sign with any other one.
- Never change `CFBundleIdentifier`.
- Sparkle won't stop an identity change: if the EdDSA signature is good, an update signed with a different identity
  still installs (`SUUpdateValidator.m` accepts either check passing, to allow key rotation). The first sign of the
  mistake is people losing permissions.
- If the identity ever must change (lost, or about to expire), say so in the release notes and tell people which
  permissions to grant again in System Settings › Privacy & Security.

## Testing permissions across an update

1. Install the previous release, grant its permissions, and confirm they work.
2. Let Sparkle install the new release.
3. Confirm the app still has them without being asked again. `tccutil reset ScreenCapture <bundle-id>` (or
   `Accessibility`) resets a test Mac to start over.
