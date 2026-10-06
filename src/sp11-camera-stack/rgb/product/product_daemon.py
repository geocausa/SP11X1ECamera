#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pre-release opt-in SP11 front/rear RGB product selector daemon.

Normal users in the `video` group may request front/rear/off/status.  The daemon
remains the only route owner and reuses the already physically accepted
RGBSession/RGBDeviceBackend safety state machine.  `quit` is intentionally not
a user command; systemd SIGTERM performs an orderly stop/neutral close.
"""
from __future__ import annotations
import argparse, grp, json, os, signal, socket, stat, struct, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
SERVICE=HERE.parent/'service'
for p in (str(HERE),str(SERVICE)):
    if p not in sys.path: sys.path.insert(0,p)
from product_owner import ProductOwner, ROOT
from rgb_device_backend import RGBDeviceBackend
from session import RGBSession, SessionRejected

SOCKET_DIR=Path('/run/sp11-camera-rgb')
SOCKET_PATH=SOCKET_DIR/'control.sock'


def peer_in_group(pid:int,uid:int,gid:int,allowed_gid:int)->bool:
    if uid==0: return True
    if pid<1: return False
    if gid==allowed_gid: return True
    try:
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            if line.startswith('Groups:'):
                return allowed_gid in {int(x) for x in line.split()[1:]}
    except (OSError,ValueError): return False
    return False


class ProductSelector:
    def __init__(self,session:RGBSession): self.session=session; self.commands=0
    def dispatch(self,command:str)->dict:
        if command not in ('front','rear','off','status'):
            return {'status':'REJECTED','reason':'UNKNOWN_RGB_COMMAND'}
        if self.session.poisoned: raise SessionRejected('RGB_PRODUCT_SESSION_POISONED')
        if command=='status':
            active=self.session.active
            if active is None:
                self.session.backend._guard()
                if self.session.backend.route_phase()!='neutral': raise SessionRejected('IDLE_NATIVE_GRAPH_DRIFT')
            elif not self.session.backend.publisher_running(active) or self.session.backend.route_phase()!=active:
                raise SessionRejected('ACTIVE_RGB_PRODUCT_DRIFT')
            return {'status':'OK','selected':active or 'off'}
        if command=='off':
            if self.session.active is not None: self.session.stop()
            else: self.session.close()
            self.commands+=1; return {'status':'OK','selected':'off'}
        if self.session.active==command:
            if not self.session.backend.publisher_running(command) or self.session.backend.route_phase()!=command:
                raise SessionRejected('SELECTED_RGB_PRODUCT_CAMERA_UNHEALTHY')
            return {'status':'OK','selected':command,'already_active':True}
        if self.session.active is None: self.session.open(command)
        else: self.session.switch(command)
        self.commands+=1; return {'status':'OK','selected':command}


def serve(*,max_seconds:int=14400)->dict:
    if not 60<=max_seconds<=14400: raise SessionRejected('INVALID_PRE_RELEASE_RUNTIME_BOUND')
    discovery=json.loads((ROOT/'output/UNIFIED.json').read_text())
    owner=ProductOwner(discovery=discovery)
    selector=ProductSelector(RGBSession(RGBDeviceBackend(discovery,owner)))
    video_gid=grp.getgrnam('video').gr_gid
    stop=False
    def requested(sig,frame):
        nonlocal stop; stop=True
    signal.signal(signal.SIGTERM,requested); signal.signal(signal.SIGINT,requested)
    summary={'status':'INCOMPLETE_FAIL_CLOSED','accepted_commands':0,'last_selected':'off','runtime_bound_seconds':max_seconds}
    sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    try:
        if SOCKET_DIR.exists():
            s=SOCKET_DIR.stat(follow_symlinks=False)
            if not stat.S_ISDIR(s.st_mode) or s.st_uid!=0: raise SessionRejected('UNTRUSTED_PRODUCT_SOCKET_DIR')
        else:
            SOCKET_DIR.mkdir(mode=0o770)
        os.chown(SOCKET_DIR,0,video_gid); os.chmod(SOCKET_DIR,0o770)
        if SOCKET_PATH.exists() or SOCKET_PATH.is_symlink(): raise SessionRejected('PREEXISTING_PRODUCT_CONTROL_SOCKET')
        sock.bind(str(SOCKET_PATH)); os.chown(SOCKET_PATH,0,video_gid); os.chmod(SOCKET_PATH,0o660)
        s=SOCKET_PATH.stat(follow_symlinks=False)
        if not stat.S_ISSOCK(s.st_mode) or s.st_uid!=0 or s.st_gid!=video_gid or stat.S_IMODE(s.st_mode)!=0o660:
            raise SessionRejected('PRODUCT_CONTROL_SOCKET_PERMISSIONS')
        sock.listen(8); sock.settimeout(1.0); deadline=time.monotonic()+max_seconds
        while not stop:
            if time.monotonic()>=deadline: raise SessionRejected('PRE_RELEASE_RUNTIME_BOUND_EXPIRED')
            if not owner.authorized() or not owner.lease_held() or not owner.ir_off(): raise SessionRejected('PRODUCT_GUARD_LOST')
            try: conn,_=sock.accept()
            except socket.timeout:
                if selector.session.active is not None:
                    a=selector.session.active
                    if not selector.session.backend.publisher_running(a) or selector.session.backend.route_phase()!=a:
                        raise SessionRejected('UNEXPECTED_ACTIVE_RGB_PRODUCT_FAILURE')
                continue
            with conn:
                conn.settimeout(6.0)
                pid,uid,gid=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                if not peer_in_group(pid,uid,gid,video_gid):
                    conn.sendall(b'{"status":"REJECTED","reason":"VIDEO_GROUP_CONTROL_REQUIRED"}\n'); continue
                request=conn.recv(129)
                if len(request)>128 or b'\n' not in request or request.split(b'\n',1)[1] not in (b'',):
                    conn.sendall(b'{"status":"REJECTED","reason":"INVALID_COMMAND_FRAME"}\n'); continue
                try: command=request[:-1].decode('ascii','strict')
                except UnicodeDecodeError: command=''
                response=selector.dispatch(command)
                conn.sendall((json.dumps(response,sort_keys=True)+'\n').encode('ascii'))
                if response.get('status')=='OK' and command!='status':
                    summary['accepted_commands']+=1; summary['last_selected']=response['selected']
        if selector.session.poisoned: raise SessionRejected('PRODUCT_STOP_WITH_POISONED_SESSION')
        if selector.session.active is not None: selector.session.stop()
        selector.session.close()
        summary['status']='PASS_PRE_RELEASE_RGB_PRODUCT_DAEMON_CLEAN_STOP'
        summary['last_selected']='off'; return summary
    finally:
        sock.close()
        try:
            if SOCKET_PATH.is_socket() and not SOCKET_PATH.is_symlink(): SOCKET_PATH.unlink()
            if SOCKET_DIR.is_dir() and not any(SOCKET_DIR.iterdir()): SOCKET_DIR.rmdir()
        except OSError: pass
        owner.close()
        (ROOT/'output/PRODUCT-DAEMON-RESULT.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--max-seconds',type=int,default=14400); a=p.parse_args()
    if os.geteuid()!=0: raise SystemExit('ROOT_RGB_PRODUCT_DAEMON_REQUIRED')
    print(json.dumps(serve(max_seconds=a.max_seconds),sort_keys=True),flush=True); return 0
if __name__=='__main__': sys.exit(main())
