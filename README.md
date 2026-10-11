# Deckystation

Use a Steam Deck as a handheld terminal for local work and remote Herdr sessions.

Includes a Steam Input layout, Herdr Gaming Mode setup, local dictation settings,
Parakeet Vulkan tests, and SSH tools for operating the Deck from another machine.
This is configuration and glue around upstream tools, not a fork of SteamOS or Herdr.

## Controller layout

Open **Herdr** from Steam's Non-Steam library. The layout applies to Herdr only.

| Control | Action |
|---|---|
| Right trackpad | Mouse pointer |
| Right trackpad press | Left click |
| Right stick | Mouse pointer |
| Right stick press | Zoom/unzoom focused pane |
| Left trackpad swipe | Scroll vertically |
| Left trackpad press | Show/hide sidebar |
| R2 / L2 | Left / right mouse button; hold R2 to drag/select |
| D-pad up/down | Scroll; hold to repeat |
| D-pad left/right | Focus pane left/right |
| Left stick | Arrow keys |
| Left stick press | New tab |
| A / B | Enter / Escape |
| X | Steam keyboard |
| Y | Tab |
| Menu (three lines) | Command palette |
| View (two rectangles) | Workspace picker |
| L4 / R4 | Previous / next tab |
| L5 / R5 | Copy / paste |
| Hold L1 + R1 | Record dictation; release to transcribe |

Herdr uses Super (Windows key) for its native Linux shortcuts. The profile sends
these chords directly. Copy requires a text selection. There is no easy-button
binding for close, quit, or interrupt. A is a real Enter key and can submit text.
Steam and Quick Access keep their system behavior.

## Install the controller profile

Requires Python 3.11+ and `vdf==3.4`. Run on the Deck, in Desktop Mode, with Steam
fully exited. The installer refuses to run while Steam is active.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# Find the numeric account folder; do not use your public Steam profile ID.
ls "$HOME/.local/share/Steam/steamapps/common/Steam Controller Configs"
.venv/bin/python scripts/install_controller.py --user-id YOUR_NUMERIC_ACCOUNT_ID
```

The installer backs up Herdr's old profile and the controller config index. Other
games are preserved. Start Steam, return to Gaming Mode, and launch Herdr.
The profile is called **Deckystation - Herdr**. For an existing custom Herdr keymap,
merge [these native shortcuts](config/herdr-gpui-controller.toml) into your local
GPUI configuration; do not replace your theme/layout settings.

To restore, exit Steam and copy the matching `.backup-*` files over
`herdr/controller_neptune.vdf` and `configset_controller_neptune.vdf` in that same
account directory. Restart Steam. Backups contain private account data: keep them local.

## Complete setup

See [setup](docs/setup.md) for Tailscale, SSH, pacman repair, Herdr, the Steam
shortcut, Codex, CUA, dictation, and local models. Pinned download URLs and SHA-256
values are in [artifacts.json](config/artifacts.json). Credentials are created on
each device and never copied into this repository.

```sh
# Run from the controlling Mac, using an existing SSH alias named steamdeck.
python3 deckctl.py status
python3 deckctl.py launch
python3 deckctl.py capture
python3 deckctl.py exec uname -a
```

`capture` uses Gamescope's screenshot signal, SCP, and macOS `sips`. It captures
Vulkan windows that X11 screenshots may show as black. Screenshots may contain
private terminal content and are excluded from Git. `cua` forwards JSON to an
installed `cua-driver`; it needs the driver's server/session running on the Deck.
The CLI's mouse/input guard limitations under Gamescope remain upstream limitations.

## Dictation and local inference

```text
L1 + R1 -> Deck microphone -> local Whisper Vulkan -> clipboard paste
                                                    |
                            Herdr: Super+V <--------+
                       Other apps: Ctrl+V <---------+
```

Decktation is enabled in Generic mode. It does not open chat or press Enter.
Diagnostics sharing is off. The [version-specific paste patch](decktation-herdr-paste.patch)
fixes Herdr's different paste shortcut. Backups are made before applying it.

Parakeet v3 and 110M are installed/tested as separate CLI engines. **They are not
wired into Decktation.** See [measured results and limits](docs/validation.md).
No model, recording, runtime binary, account ID, SSH key, or login file is shipped.

## Development

```sh
.venv/bin/python scripts/build_layout.py
.venv/bin/python -m unittest discover -s tests
python3 deckctl.py self-test
```

`build_layout.py` is the source of the committed controller VDF. Tests cover its
repeated-key format, shortcut preservation, backups, reruns, and checksum failures.
Steam Input uses repeated `group` and `binding` keys: do not parse these profiles
with a normal dictionary or with duplicate-key merging enabled.

## Upstream projects

- [Herdr](https://herdr.dev/) and [Herdr GPUI](https://github.com/penso/herdr-gpui)
- [deck-tailscale](https://github.com/tailscale-dev/deck-tailscale)
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader)
- [Decktation](https://github.com/silverfoxy/decktation)
- [parakeet.cpp](https://github.com/mudler/parakeet.cpp)
- [CUA](https://github.com/trycua/cua)
- [Steam Input source modes](https://partner.steamgames.com/doc/features/steam_controller/input_source_modes)

MIT for this repository's original code. The Decktation patch includes MIT-licensed
upstream context; its notice is in [licenses](licenses/Decktation-MIT.txt).
Upstream binaries and models retain their own licenses.
