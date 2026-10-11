# Setup notes

Tested on SteamOS 3.8.28, x86-64, with an AMD VANGOGH GPU. These are the actual
setup steps and custom configuration used by Deckystation. Authentication and
machine addresses are deliberately device-specific. Run commands on the Deck
unless a section says otherwise. Keep SteamOS's read-only root enabled afterward.

## 1. Remote access

Install [deck-tailscale](https://github.com/tailscale-dev/deck-tailscale) using its
README. The tested checkout was `4691bb20d492ae9b2f5121c3eaf6e2dc1950e73f`.
Complete Tailscale login in your own browser. Do not embed a reusable auth key in
scripts. Verify `tailscaled` is enabled and active and that tailnet DNS works.

```sh
systemctl is-enabled tailscaled
systemctl is-active tailscaled
/opt/tailscale/tailscale status
getent hosts YOUR_OTHER_TAILNET_HOST
```

On the tested Deck, `/etc/resolv.conf` was stale. Only if that is also true on your
machine, and systemd-resolved is active, back it up and restore the stub link:

```sh
sudo cp -a /etc/resolv.conf /etc/resolv.conf.before-deckystation
sudo ln -sfn /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
sudo systemctl restart systemd-resolved tailscaled
```

For normal OpenSSH over Tailscale, enable `sshd`, generate a separate Ed25519 key
on each machine, and append only the other machines' **public** keys to
`~/.ssh/authorized_keys`. Preserve existing entries. Use mode 700 for `.ssh` and
600 for private keys/authorized_keys. Verify each host key through a trusted
connection. Never copy private keys between devices.

Example controller-machine SSH stanza (replace paths/user as needed):

```sshconfig
Host steamdeck
    HostName YOUR_DECK_TAILNET_NAME
    User deck
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ProxyCommand /ABSOLUTE/PATH/TO/tailscale nc %h %p
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

The Deck's Tailscale executable is `/opt/tailscale/tailscale`. Macs can use
`/usr/local/bin/tailscale` or `/opt/homebrew/bin/tailscale`; use the real installed
path, since noninteractive SSH does not necessarily have Homebrew in PATH.
After key login works in a second connection, enable OpenSSH at boot and disable
password login via an sshd drop-in. Run `sshd -t` before reloading. If switching
from Tailscale SSH, disable that interception from a working LAN/OpenSSH session
with `sudo /opt/tailscale/tailscale set --ssh=false`.

Tailscale runs in Desktop and Gaming Mode and starts after reboot. Sleeping or
powered-off hardware is not reachable. SteamOS updates may require checking the
upstream deck-tailscale update procedure again.

## 2. Pacman repair, only when needed

Use the repositories shipped for your exact SteamOS release. Do not replace them
with generic Arch repositories or run a broad `pacman -Syu` to install one tool.
For an uninitialized keyring, the tested repair was:

```sh
sudo pacman-key --init
sudo pacman-key --populate archlinux holo
sudo steamos-readonly disable
# Refresh only in preparation for a specific package from matching SteamOS repos.
sudo pacman -Sy
sudo pacman -S --needed inetutils
sudo steamos-readonly enable
pacman -Dk
```

`inetutils` supplied the missing `hostname` command. A refresh is not an OS upgrade.
Always restore read-only mode, including after a failed package command. Use the
SteamOS updater for the operating system.

## 3. Herdr daemon and native client

Fetch the pinned, verified artifacts from this repo:

```sh
python3 scripts/fetch_artifact.py herdr /tmp/herdr-deckystation
python3 scripts/fetch_artifact.py herdr-gpui /tmp/Herdr-deckystation.tar.gz
```

Install the daemon as `~/.local/bin/herdr`. Extract the client archive into a
staging directory. Its top-level directory contains `bin/herdr-gpui` and `share`.
Install the real GUI binary at `~/.local/lib/herdr-gpui/herdr-gpui`, copy the icon,
desktop file and licenses under `~/.local/share`, and install [the scale wrapper](../config/herdr-gpui)
as `~/.local/bin/herdr-gpui` (mode 755). Update the desktop entry's `Exec` to that
absolute wrapper path. Back up existing files before replacement.

```sh
mkdir -p "$HOME/hub" "$HOME/.config/systemd/user"
cp config/herdr.service "$HOME/.config/systemd/user/herdr.service"
systemctl --user daemon-reload
systemctl --user enable --now herdr
sudo loginctl enable-linger "$USER"
```

Put `~/.local/bin` on the shell PATH. With the GUI closed, back up
`~/.local/state/herdr/gpui/window-state.json` and set its window to 1280 x 800:

```json
[{"x":0.0,"y":0.0,"width":1280.0,"height":800.0,"display":"00000000-0000-0000-0000-000000000000"}]
```

Both scale factor 1 and a full-size window are needed. A 640 x 400 saved window is
magnified by Gamescope even when GPUI's scale factor is correct. The tested local
appearance was `layout = "comfortable"`, `theme = "Follow Herdr"`; keep existing
appearance preferences. Closing the GUI must not stop the Herdr daemon.

Add remote machines using `herdr machine add SSH_ALIAS --label LABEL`. Verify
remote `herdr status client --json` compatibility first. One older embedded Mac
server reported no detached-daemon support despite a compatible protocol. The
workaround was a backed-up SSH endpoint entry in
`~/.local/state/herdr/client/endpoints.json`, retaining version 1 and existing
entries. Do not replace this file with another person's endpoints or restart
an active remote daemon just to add a client.

## 4. Steam shortcut and controller

With Steam fully exited in Desktop Mode:

```sh
.venv/bin/python scripts/install_shortcut.py --user-id YOUR_NUMERIC_ACCOUNT_ID
.venv/bin/python scripts/install_controller.py --user-id YOUR_NUMERIC_ACCOUNT_ID
```

The shortcut uses `/usr/bin/env`, launch options
`-u LD_PRELOAD -u WAYLAND_DISPLAY /home/deck/.local/bin/herdr-gpui`, the Herdr icon,
and a `~/hub` start directory. Steam Overlay is disabled. The script generates
paths from the current home directory, preserves other shortcuts and leaves any
existing Herdr shortcut unchanged. Name `Herdr` plus quoted executable
`"/usr/bin/env"` produces unsigned app ID `2380454464`, not a private account ID.

Return with `steamos-session-select gamescope`. Herdr appears under Non-Steam.
The controller layout is app-specific. Restore instructions are in the README.

## 5. Codex and CUA

Install the full official Codex package from
[OpenAI's installer](https://chatgpt.com/codex/install.sh), not just the main
binary: the package includes the code-mode host. Tested version: 0.162.1.
Use `codex login --device-auth` and your own browser login. Then run
`herdr integration install codex`. Preserve existing Codex settings and auth.
Model preferences belong to the user; this repository does not force a model.

Install CUA with [its official installer](https://cua.ai/driver/install.sh).
Tested driver: 0.34.0. For a Deck Codex process controlling Herdr in Gaming Mode:

```sh
codex mcp add cua-driver --env DISPLAY=:1 --env XDG_SESSION_TYPE=x11 \
  --env XDG_RUNTIME_DIR=/run/user/1000 \
  --env DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  -- "$HOME/.local/bin/cua-driver" mcp
```

Use the actual UID if it differs from 1000. Gaming Mode uses X11 display `:0` for
Steam and `:1` for the game app. CUA window enumeration worked, but its foreground
mouse guard and virtual input did not reliably work under Gamescope. Do not
claim that installation alone proves all control methods work. `deckctl.py`
provides the tested SSH and compositor-capture path.

## 6. Dictation

Install [Decktation 0.3.18](https://github.com/silverfoxy/decktation/releases/tag/v0.3.18)
through Decky Loader's plugin installer. Do not merely unzip it into plugins:
use Decky's dependency/install flow. Decky 3.2.1 was already installed on the
tested device; preserve other plugins. [config/decktation.json](../config/decktation.json)
contains the chosen preferences. Apply them through the plugin UI/API, or merge
them into its `button_config.json` with Decky stopped. Do not overwrite unrelated
preferences. Keep diagnostics off unless you choose otherwise.

L1+R1 records audio. Generic mode pastes into the focused field and sends no
Enter. Its resident whisper.cpp worker automatically selects Vulkan and downloads
`ggml-base.bin` to `~/.cache/decktation/whisper.cpp` on first use.

For the verified Herdr paste fix, with Decky stopped:

```sh
sudo systemctl stop plugin_loader
sudo python3 scripts/apply_dictation_patch.py \
  --plugin-dir "$HOME/homebrew/plugins/decktation" --app-id 2380454464
sudo systemctl start plugin_loader
```

The patch reads Gamescope's focused app as the desktop user. Only Herdr gets
Super+V; other apps get Ctrl+V. Supply your actual shortcut ID if it differs.
It refuses other Decktation versions and backs up both files. A plugin update
can replace it. Restore the two files from the printed backup directory while
Decky is stopped, then restart Decky. The patch uses X11/Gamescope focus;
Desktop Mode is not covered by this app-specific adjustment.

## 7. Parakeet Vulkan

```sh
python3 scripts/fetch_artifact.py parakeet-vulkan /tmp/parakeet-vulkan.tar.gz
python3 scripts/fetch_artifact.py parakeet-v3-q4 "$HOME/.cache/parakeet/tdt-0.6b-v3-q4_k.gguf"
mkdir -p "$HOME/.local/lib/parakeet" "$HOME/.local/bin"
tar xzf /tmp/parakeet-vulkan.tar.gz -C "$HOME/.local/lib/parakeet" --strip-components=1
ln -sfn ../lib/parakeet/parakeet-cli "$HOME/.local/bin/parakeet-cli"
ln -sfn ../lib/parakeet/parakeet-server "$HOME/.local/bin/parakeet-server"
PARAKEET_DEVICE=Vulkan0 "$HOME/.local/bin/parakeet-cli" transcribe \
  --model "$HOME/.cache/parakeet/tdt-0.6b-v3-q4_k.gguf" --input speech.wav --threads 4
```

Use a local WAV file or the upstream test fixture. CPU comparison uses
`PARAKEET_DEVICE=cpu`. Confirm `using device: Vulkan0` in logs and sample
`/sys/class/drm/card0/device/gpu_busy_percent` during inference. No CUDA, ROCm,
Docker, model server, or network transcription service is needed. This does not
replace Decktation's Whisper engine.

## 8. Reboot check

Reboot once after setup. Confirm a new boot ID, enabled/active tailscaled and
sshd, active user Herdr service, Decky restored preferences, retained Codex login,
and SSH in both directions. Launch Herdr through Steam and check actual remote
sessions and 1280 x 800 rendering. Reboot terminates local pane processes; do not
mistake persistent layouts for live processes surviving a reboot.
