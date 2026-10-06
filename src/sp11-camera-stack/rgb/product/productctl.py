#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""User-facing control client for the opt-in pre-release RGB product daemon."""
from __future__ import annotations
import argparse, grp, json, os, socket, stat, sys
from pathlib import Path
SOCKET=Path('/run/sp11-camera-rgb/control.sock')

def command(action:str)->dict:
    if action not in ('front','rear','off','status'): raise ValueError('INVALID_RGB_ACTION')
    s=SOCKET.stat(follow_symlinks=False); vg=grp.getgrnam('video').gr_gid
    if not stat.S_ISSOCK(s.st_mode) or s.st_uid!=0 or s.st_gid!=vg or stat.S_IMODE(s.st_mode)!=0o660:
        raise PermissionError('UNTRUSTED_RGB_PRODUCT_CONTROL_SOCKET')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
        c.settimeout(16); c.connect(str(SOCKET)); c.sendall((action+'\n').encode('ascii')); data=bytearray()
        while not data.endswith(b'\n'):
            part=c.recv(512)
            if not part: raise OSError('RGB_PRODUCT_DAEMON_DID_NOT_REPLY')
            data.extend(part)
            if len(data)>2048: raise OSError('OVERSIZED_RGB_PRODUCT_RESPONSE')
    r=json.loads(data.decode('ascii'))
    if not isinstance(r,dict) or r.get('status') not in ('OK','REJECTED'): raise OSError('UNTRUSTED_RGB_PRODUCT_RESPONSE')
    return r

def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=('front','rear','off','status')); a=p.parse_args()
    r=command(a.action); print(json.dumps(r,sort_keys=True)); return 0 if r['status']=='OK' else 1
if __name__=='__main__': sys.exit(main())
