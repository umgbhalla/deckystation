#!/usr/bin/env python3
"""Add the Herdr non-Steam shortcut without changing other shortcuts."""
import argparse
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import zlib
import vdf


def install(root, user, home):
    target=root/'userdata'/user/'config/shortcuts.vdf'
    data={'shortcuts': {}}
    if target.exists():
        with target.open('rb') as stream:
            data=vdf.binary_load(stream)
    entries=data['shortcuts']
    existing=[key for key, entry in entries.items() if entry.get('AppName','').casefold()=='herdr']
    if len(existing)>1:
        raise SystemExit('Multiple Herdr shortcuts found; resolve duplicates first')
    if existing:
        print('Herdr already exists; leaving its shortcut unchanged')
        return
    key=str(max((int(k) for k in entries),default=-1)+1)
    exe='"/usr/bin/env"'
    appid=zlib.crc32((exe+'Herdr').encode())|0x80000000
    entries[key]={
        'appid': appid-(1<<32), 'AppName': 'Herdr', 'Exe': exe,
        'StartDir': '"'+str(home/'hub')+'"',
        'icon': str(home/'.local/share/icons/hicolor/scalable/apps/herdr-gpui.svg'),
        'ShortcutPath': str(home/'.local/share/applications/so.pen.herdr-gpui.desktop'),
        'LaunchOptions': '-u LD_PRELOAD -u WAYLAND_DISPLAY '+str(home/'.local/bin/herdr-gpui'),
        'IsHidden':0, 'AllowDesktopConfig':1, 'AllowOverlay':0, 'OpenVR':0,
        'Devkit':0, 'DevkitGameID':'', 'DevkitOverrideAppID':0, 'LastPlayTime':0,
        'FlatpakAppID':'', 'tags':{'0':'Tools'},
    }
    payload=vdf.binary_dumps(data)
    assert vdf.binary_load(io.BytesIO(payload))==data
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():shutil.copy2(target,target.with_name(target.name+'.backup-'+str(time.time_ns())))
    fd,temp=tempfile.mkstemp(dir=target.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(payload)
        os.replace(temp,target)
    finally:
        if os.path.exists(temp):os.unlink(temp)
    print('Herdr app ID:',appid,'launch ID:',(appid<<32)|0x02000000)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steam-root',type=Path,default=Path.home()/'.local/share/Steam')
    parser.add_argument('--user-id',required=True)
    args=parser.parse_args()
    if not args.user_id.isdecimal():parser.error('--user-id must be numeric')
    if subprocess.run(['pgrep','-x','steam'],stdout=subprocess.DEVNULL).returncode==0:
        parser.error('Exit Steam first')
    install(args.steam_root,args.user_id,Path.home())
