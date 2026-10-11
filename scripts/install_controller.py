#!/usr/bin/env python3
"""Install only Herdr's Steam Input profile, with Steam stopped."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import vdf


def load(path):
    with path.open() as f:
        return vdf.load(f, mapper=vdf.VDFDict, merge_duplicate_keys=False)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + '.backup-' + str(time.time_ns())))
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(vdf.dumps(data, pretty=True))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install(root, user):
    base = root / 'steamapps/common/Steam Controller Configs' / user / 'config'
    configset = base / 'configset_controller_neptune.vdf'
    if not configset.is_file():
        raise SystemExit('No existing Steam Deck controller config for this account')
    data = load(configset)
    while 'herdr' in data['controller_config']:
        data['controller_config'].pop('herdr')
    data['controller_config']['herdr'] = vdf.VDFDict([('autosave', '1')])
    profile = load(Path(__file__).resolve().parents[1] / 'config/herdr-controller.vdf')
    target = base / 'herdr/controller_neptune.vdf'
    profile['controller_mappings']['url'] = 'autosave://' + str(target)
    if target.exists():
        creator = load(target)['controller_mappings'].get('creator')
        if creator:
            profile['controller_mappings']['creator'] = creator
    write(target, profile)
    write(configset, data)
    print('Installed:', target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steam-root', type=Path, default=Path.home()/'.local/share/Steam')
    parser.add_argument('--user-id', required=True, help='Numeric local Steam account directory')
    args = parser.parse_args()
    if not args.user_id.isdecimal():
        parser.error('--user-id must be numeric')
    if subprocess.run(['pgrep', '-x', 'steam'], stdout=subprocess.DEVNULL).returncode == 0:
        parser.error('Exit Steam first so it cannot overwrite the controller profile')
    install(args.steam_root, args.user_id)
