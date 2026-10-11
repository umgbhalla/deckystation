#!/usr/bin/env python3
"""Operate the configured Steam Deck over its existing SSH alias."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess


def remote(*args: str) -> str:
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "steamdeck",
         shlex.join(args)], text=True, stdout=subprocess.PIPE
    )
    if result.returncode:
        print(result.stdout, end="")
        raise SystemExit(result.returncode)
    return result.stdout


def capture(destination: Path) -> None:
    # Gamescope captures Vulkan surfaces that X11 GetImage returns as black.
    script = """import pathlib, subprocess, time
p = pathlib.Path('/tmp')
before = set(p.glob('gamescope_*.avif')) | set(p.glob('gamescope_*.png'))
pids = subprocess.check_output(['pgrep', '-x', 'gamescope-wl'], text=True).split()
assert len(pids) == 1, 'Expected one Gamescope compositor'
subprocess.run(['kill', '-USR2', pids[0]], check=True)
deadline = time.monotonic() + 8
while time.monotonic() < deadline:
    added = (set(p.glob('gamescope_*.avif')) | set(p.glob('gamescope_*.png'))) - before
    if added:
        shot = max(added, key=lambda f: f.stat().st_mtime_ns)
        size = shot.stat().st_size
        time.sleep(0.3)
        if size > 0 and shot.stat().st_size == size:
            print(shot)
            break
    time.sleep(0.1)
else:
    raise RuntimeError('Gamescope did not finish a capture within 8 seconds')
"""
    shot = remote("python3", "-c", script).strip()
    assert shot.startswith("/tmp/gamescope_") and "\n" not in shot
    destination.parent.mkdir(parents=True, exist_ok=True)
    raw = destination.with_suffix(Path(shot).suffix)
    subprocess.run(["scp", "-q", f"steamdeck:{shot}", str(raw)], check=True)
    if raw != destination:
        subprocess.run(["sips", "-s", "format", "png", str(raw), "--out", str(destination)],
                       check=True, stdout=subprocess.DEVNULL)
    print(destination.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("launch")
    sub.add_parser("self-test")
    shot = sub.add_parser("capture")
    shot.add_argument("path", type=Path, nargs="?", default=Path("evidence/latest.png"))
    execute = sub.add_parser("exec")
    execute.add_argument("args", nargs=argparse.REMAINDER)
    cua = sub.add_parser("cua")
    cua.add_argument("tool")
    cua.add_argument("json", nargs="?", default="{}")
    args = parser.parse_args()
    if args.command == "self-test":
        tokens = ["echo", "space here", "$(touch nope)", "it's literal", "line\nbreak"]
        assert shlex.split(shlex.join(tokens)) == tokens
        assert json.loads(json.dumps({"text": tokens})) == {"text": tokens}
        print("Argument quoting and JSON checks passed")
    elif args.command == "capture":
        capture(args.path)
    elif args.command == "launch":
        print(remote("env", "DISPLAY=:0", "/usr/bin/steam",
                     "steam://rungameid/10223974072530763776"), end="")
    elif args.command == "status":
        print(remote("sh", "-c", "hostname; uptime; systemctl is-active tailscaled sshd; "
                     "systemctl --user is-active herdr; pgrep -a herdr-gpui; "
                     "/opt/tailscale/tailscale status --json | jq '{BackendState,Health}'"), end="")
    elif args.command == "cua":
        payload = json.loads(args.json)
        print(remote("/home/deck/.local/bin/cua-driver", args.tool, json.dumps(payload)), end="")
    else:
        if not args.args:
            parser.error("exec requires a command")
        print(remote(*args.args), end="")


if __name__ == "__main__":
    main()
