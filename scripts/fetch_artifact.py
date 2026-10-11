#!/usr/bin/env python3
"""Download one pinned public artifact and verify its SHA-256 before renaming."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request


def fetch(name, destination):
    manifest = json.loads((Path(__file__).resolve().parents[1]/'config/artifacts.json').read_text())
    if name not in manifest:
        raise SystemExit('Unknown artifact: ' + name)
    entry = manifest[name]
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        with destination.open('rb') as f:
            if hashlib.file_digest(f, 'sha256').hexdigest() == entry['sha256']:
                print('Already verified:', destination)
                return
        raise SystemExit('Destination exists with a different hash; choose another path')
    fd, temporary = tempfile.mkstemp(dir=destination.parent)
    try:
        digest = hashlib.sha256()
        with os.fdopen(fd, 'wb') as output, urllib.request.urlopen(entry['url'], timeout=60) as response:
            while chunk := response.read(1024*1024):
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != entry['sha256']:
            raise SystemExit('SHA-256 mismatch; download was not installed')
        os.replace(temporary, destination)
        print('Verified:', destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    parser.add_argument('destination', type=Path)
    args=parser.parse_args()
    fetch(args.name,args.destination)
