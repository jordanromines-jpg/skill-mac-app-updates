# Sparkle setup in the app

Sources: [Sparkle documentation](https://sparkle-project.org/documentation/),
[programmatic setup](https://sparkle-project.org/documentation/programmatic-setup/),
[publishing](https://sparkle-project.org/documentation/publishing/), and the tools' source at tag `2.10.0`
(`generate_keys/main.swift`, `sign_update/main.swift`, `generate_appcast/`). Checked 16 Oct 2026, when 2.10.0 was
the latest release.

## 1. Add Sparkle, pinned to one exact version

Sparkle 2 needs macOS 12 or later. Pin an exact version so a Sparkle release never changes the app (or its tools)
without a commit that says so. Update it deliberately, read Sparkle's changelog, and re-test an update.

**Swift package app** (`Package.swift`):

```swift
dependencies: [
    .package(url: "https://github.com/sparkle-project/Sparkle", exact: "2.10.0"),
],
targets: [
    .executableTarget(name: "MyApp", dependencies: [.product(name: "Sparkle", package: "Sparkle")]),
]
```

**Xcode project:** File › Add Package Dependencies…, `https://github.com/sparkle-project/Sparkle`, rule
**Exact Version** `2.10.0`. Xcode embeds and signs the framework itself.

### Swift package apps assembled by a script (untested)

`swift build` doesn't make a `.app`, so a build script assembles one. With Sparkle it must also:

1. Copy the framework into the bundle **with `ditto`**, which keeps the framework's symlinks (a copy that follows
   them breaks its signature):
   `ditto .build/release/Sparkle.framework MyApp.app/Contents/Frameworks/Sparkle.framework`
   (if it isn't there, `find .build -name Sparkle.framework -maxdepth 4`).
2. Let the executable find it: `install_name_tool -add_rpath @executable_path/../Frameworks MyApp.app/Contents/MacOS/MyApp`
   (Sparkle's manual-install docs give the equivalent linker flag, `-Wl,-rpath,@loader_path/../Frameworks`).
3. Sign the pieces inside out, never with `--deep` (Sparkle's sandboxing page). See
   [release-workflow.md](release-workflow.md#signing-order).

Sparkle's command-line tools come in the same download: with SwiftPM they're under
`.build/artifacts/sparkle/Sparkle/bin/` (`generate_keys`, `sign_update`, `generate_appcast`). If the path differs,
`find .build/artifacts -name generate_keys`. They also ship in `Sparkle-2.10.0.tar.xz` on Sparkle's GitHub Release.

## 2. Start the updater

SwiftUI (from Sparkle's programmatic-setup page; trimmed):

```swift
import SwiftUI
import Sparkle

final class CheckForUpdatesViewModel: ObservableObject {
    @Published var canCheckForUpdates = false
    init(updater: SPUUpdater) {
        updater.publisher(for: \.canCheckForUpdates).assign(to: &$canCheckForUpdates)
    }
}

struct CheckForUpdatesView: View {
    @ObservedObject private var model: CheckForUpdatesViewModel
    private let updater: SPUUpdater
    init(updater: SPUUpdater) {
        self.updater = updater
        self.model = CheckForUpdatesViewModel(updater: updater)
    }
    var body: some View {
        Button("Check for Updates…", action: updater.checkForUpdates)
            .disabled(!model.canCheckForUpdates)
    }
}

@main
struct MyApp: App {
    private let updaterController = SPUStandardUpdaterController(
        startingUpdater: true, updaterDelegate: nil, userDriverDelegate: nil)

    var body: some Scene {
        WindowGroup { ContentView() }
            .commands {
                CommandGroup(after: .appInfo) { CheckForUpdatesView(updater: updaterController.updater) }
            }
    }
}
```

AppKit: keep one `SPUStandardUpdaterController` alive for the app's lifetime (an object in `MainMenu.xib`, or a
property of the app delegate) and point a "Check for Updates…" menu item at its `checkForUpdates:` action. A
menu-bar-only app (`LSUIElement`) puts that item in its status menu. `SUUpdater` is Sparkle 1 and is a deprecated
stub in Sparkle 2.

Sparkle asks the user whether to check automatically on the **second** launch, not the first.

## 3. Info.plist keys

| Key | Value | Why |
|---|---|---|
| `SUFeedURL` | `https://github.com/OWNER/REPO/releases/download/appcast/appcast.xml` | Where the appcast is. HTTPS only. This skill keeps it on a permanent Release tagged `appcast` ([release-workflow.md](release-workflow.md)). Its file name (`appcast.xml`) is also the name `generate_appcast` writes. |
| `SUPublicEDKey` | the base64 string `generate_keys` prints | Sparkle installs only archives signed by the matching private key. |
| `CFBundleVersion` | a whole number that goes up every release, e.g. the CI run number | Sparkle compares this, not the short version. Not a git hash, not `git describe`. |
| `CFBundleShortVersionString` | `1.4.0` | What people see. |
| `CFBundleIdentifier` | e.g. `com.example.myapp` | Must never change: it is part of the app's identity for macOS permissions too. |

Optional, later: `SURequireSignedFeed` (Sparkle 2.9+, also needs `SUVerifyUpdateBeforeExtraction`) makes Sparkle
check a signature on the appcast itself, not just on each archive. It changes the publishing steps (the appcast
must be re-signed after every edit), so leave it off until the basic flow works.

## 4. Make the EdDSA update key, once, on the releasing Mac

```bash
.build/artifacts/sparkle/Sparkle/bin/generate_keys
```

- It stores the private key in **this Mac's login keychain** (item "Private key for signing Sparkle updates",
  account `ed25519` unless you pass `--account`) and prints the public key to put in `SUPublicEDKey`. Allow the
  keychain prompt.
- Run again, it prints the existing public key instead of making a new one. `generate_keys -p` prints just the
  public key, for scripts.
- One key can sign every app you ship (Sparkle's own help says so). Use `--account <name>` only to keep keys for
  different organisations apart, and then pass the same `--account` to `sign_update` and `generate_appcast`.

### Where the private key may and may not be

| Place | OK? |
|---|---|
| The releasing Mac's login keychain | Yes: the only working copy |
| An encrypted offline backup the person makes (`generate_keys -x file`, then store it in a password manager and delete `file`) | Yes, and do it: a lost key can't be recovered, and every installed copy would be stranded (key rotation needs a Developer ID-signed app) |
| GitHub Actions secrets, the repo, any CI log, a chat | **No** |
| Another Mac | Only by the person, deliberately (`generate_keys -f file`), when the releasing Mac changes |

`sign_update` and `generate_appcast` can also take the key on standard input (`--ed-key-file -`), which is how
other guides put it in CI. This skill doesn't: the key stays in the keychain, and signing happens on the Mac.

## 5. Check it

```bash
plutil -p MyApp.app/Contents/Info.plist | grep -E 'SUFeedURL|SUPublicEDKey|CFBundleVersion'
.build/artifacts/sparkle/Sparkle/bin/generate_keys -p      # must equal SUPublicEDKey
codesign --verify --deep --strict --verbose=2 MyApp.app      # checks only; never sign with --deep
```

To force a check while testing: `defaults delete <bundle-id> SULastCheckTime`, then relaunch. Sparkle logs to
Console.app.

## When Sparkle 3 comes out

The tools, keys or Info.plist keys may change. Re-read Sparkle's documentation and changelog before moving past
2.x, and update this page (risk R-2 in the hub plan).
