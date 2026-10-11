#!/usr/bin/env python3
"""Apply the version-specific Decktation paste fix with backups."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time


def apply(plugin, app_id):
    metadata = json.loads((plugin/'plugin.json').read_text())
    if metadata.get('version') != '0.3.18':
        raise SystemExit('This patch only supports Decktation 0.3.18')
    patch = (Path(__file__).resolve().parents[1]/'decktation-herdr-paste.patch').read_text()
    patch = patch.replace('2380454464', str(app_id))
    command = ['patch', '--batch', '--forward', '-p1', '-d', str(plugin)]
    subprocess.run(command + ['--dry-run'], input=patch, text=True, check=True)
    backup = plugin/('backup-deckystation-' + str(time.time_ns()))
    backup.mkdir()
    for name in ['clipboard_injection.py', 'wow_voice_chat.py']:
        shutil.copy2(plugin/'bin'/name, backup/name)
    subprocess.run(command, input=patch, text=True, check=True)
    print('Backup:', backup)
    print('Restart plugin_loader to load the changed Python modules.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plugin-dir', type=Path, required=True)
    p.add_argument('--app-id', type=int, required=True, help='Unsigned Steam shortcut app ID')
    args = p.parse_args()
    if not 0 < args.app_id <= 0xffffffff:
        p.error('--app-id must be an unsigned 32-bit ID')
    apply(args.plugin_dir, args.app_id)
