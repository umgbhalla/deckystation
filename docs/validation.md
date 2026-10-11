# Validation

Test machine: Steam Deck, SteamOS 3.8.28, AMD Custom GPU 0932 / RADV VANGOGH.
Date: 2026-10-11. Results describe this device and these pinned versions.

## Controller and application

- Controller profile installed for Herdr only, with the previous profile and
  config index backed up. Steam restarted in Gaming Mode and loaded the mapping.
- Steam's controller log reports the Herdr mapping uses keyboard/mouse, not XInput.
- The owner physically tested pointer movement, scrolling and L4/R4 tab switching
  and reported that they work well. The other button assignments are configured
  but have not each received a separate physical test.
- Herdr rendered at 1280 x 800 with GPUI scale 1. Both remote machines' sessions
  appeared in the GUI. No changes were made to the remote application code.
- A real reboot changed the boot ID. Tailscale, sshd, Decky and the user Herdr
  daemon started. All six SSH directions between the three machines worked.
- Codex remained logged in. A real Codex shell request succeeded after installing
  its complete package, including code-mode host.

## Local speech inference

The same upstream 7.435-second `tests/fixtures/speech.wav` from parakeet.cpp
v0.6.1 was used. Four threads were specified for Parakeet. These are single
measurements, not a statistical benchmark or a guarantee for other speech.

| Engine | CPU seconds | Vulkan seconds | Timing boundary |
|---|---:|---:|---|
| Whisper base | 2.452 | 0.557 | Request only; resident model |
| Parakeet 110M Q8 | 0.405 | 1.004 | Whole CLI process, including startup |
| Parakeet v3 0.6B Q4_K | 1.359 | 0.943 | Whole CLI process, including startup |

Parakeet produced the expected words on both backends. The Vulkan logs selected
the Deck's AMD GPU. GPU busy samples peaked at 99-100%; CPU-only Parakeet samples
peaked at 0%. These measurements are not directly comparable across rows because
the lifecycle boundaries differ. The smaller Parakeet model's GPU startup cost
outweighed its benefit on this short clip.

## Dictation

- Decktation 0.3.18 loaded its resident Whisper worker using Vulkan0.
- Physical L1+R1 presses started and stopped microphone capture. A spoken phrase
  produced a transcript, proving the actual microphone-to-model path.
- The original Ctrl+V injection did not paste into Herdr. The focused-app patch
  selected Super+V and inserted a harmless comment into a local Herdr shell,
  without pressing Enter. A compositor screenshot confirmed the inserted text.
- A second complete spoken-phrase test after that paste fix has not been observed.
- After reboot, plugin status reported model ready, inference device GPU, input
  ready, controller receiving input, and manual send enabled.
- Parakeet is available as a local CLI engine. It is not connected to the L1+R1
  dictation path. That path still uses Whisper.

## Automation boundaries

CUA is installed, and window enumeration works. Its mouse guards and virtual
input are not reliable under Gamescope. X11 window screenshots can be black for
Vulkan apps. The Gamescope capture path in `deckctl.py` was tested successfully.
Its macOS conversion dependency is `sips`.

Unit tests cover repeated VDF keys and the generated profile, preserving unrelated
Steam entries, backup behavior, not duplicating existing Herdr shortcuts, and
artifact checksum failures. The Decktation patch was dry-run and applied against
the exact upstream source in a disposable directory before publication.

No clean-device full installation was performed from the finished repository.
Setup notes document the deployed steps; the repository is not a one-command
provisioner. SteamOS and Decky upgrades may need revalidation. In particular, a
Decktation update can replace the paste patch.
