# SPDX-License-Identifier: MIT
"""Fail-closed owner for the opt-in SP11 front/rear RGB product boot.

This is deliberately distinct from the single-use CandidateOwner.  It may be
reused across product-boot sessions, but only when the dedicated boot token,
root-sealed ENABLE contract, installed camera package manifest, Golden saved
entry, exclusive controller lease, IR-idle state and exact discovered RGB
nodes all agree.  It never arms GRUB, loads modules or changes routes itself.
"""
from __future__ import annotations
import fcntl, glob, hashlib, json, os, re, stat, subprocess
from pathlib import Path
import sys

SERVICE_DIR=Path(__file__).resolve().parents[1]/"service"
if str(SERVICE_DIR) not in sys.path: sys.path.insert(0,str(SERVICE_DIR))
from media_backend import bounded_command
from session import SessionRejected

GOLDEN="sp11-audio-fullio-v19c"
KERNEL="7.1.5-sp11-render-parity-v4+"
ROOT=Path("/var/lib/sp11-camera-rgb")
STACK_STATE=Path("/var/lib/sp11-camera-stack")
TOKEN="sp11_camera_rgb_product=1"
ENTRY="sp11_entry=7.1.5-sp11-camera-rgb-product"


def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


class ProductOwner:
    """One long-lived daemon owns one exclusive shared CAMSS RGB graph."""
    def __init__(self, *, root: Path=ROOT, discovery: dict):
        if os.geteuid()!=0: raise SessionRejected("ROOT_RGB_PRODUCT_DAEMON_REQUIRED")
        self.root=Path(root); self.discovery=discovery; self._lease_fd=None; self._closed=False
        if self.root!=ROOT or self.root.is_symlink() or not self.root.is_dir():
            raise SessionRejected("UNTRUSTED_PRODUCT_RUNTIME_ROOT")
        st=self.root.stat()
        if st.st_uid!=0 or stat.S_IMODE(st.st_mode)!=0o700:
            raise SessionRejected("PRODUCT_RUNTIME_NOT_ROOT_SEALED")
        self.media=discovery.get("media")
        self.physical=(discovery.get("front_rdi_video_device"),discovery.get("rear_video_device"))
        if (not isinstance(self.media,str) or not re.fullmatch(r"/dev/media(?:0|[1-9][0-9]*)",self.media)
            or any(not isinstance(x,str) or not re.fullmatch(r"/dev/video(?:0|[1-9][0-9]*)",x)
                   or x in ("/dev/video90","/dev/video91") for x in self.physical)
            or self.physical[0]==self.physical[1]):
            raise SessionRejected("UNTRUSTED_PRODUCT_DEVICE_DISCOVERY")
        self.boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        self._initial_admission()
        fd=os.open(str(self.root/'controller.lock'),os.O_CREAT|os.O_RDWR|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=0o600:
                raise SessionRejected("UNTRUSTED_PRODUCT_CONTROLLER_LOCK")
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BaseException:
            os.close(fd); raise
        self._lease_fd=fd

    @staticmethod
    def _parse_enable(text: str):
        rows={}
        for line in text.splitlines():
            if '=' not in line: return None
            k,v=line.split('=',1)
            if not k or k in rows: return None
            rows[k]=v
        if set(rows)!={'schema','enabled','package_manifest_sha256','product_assets_sha256','source_head'}: return None
        if rows.get('schema')!='sp11-camera-rgb-product-v1' or rows.get('enabled')!='YES': return None
        if not re.fullmatch(r'[0-9a-f]{64}',rows.get('package_manifest_sha256','')): return None
        if not re.fullmatch(r'[0-9a-f]{64}',rows.get('product_assets_sha256','')): return None
        if not re.fullmatch(r'[0-9a-f]{40}',rows.get('source_head','')): return None
        return rows

    def _enable_contract(self):
        p=self.root/'ENABLE'
        if not p.is_file() or p.is_symlink(): return None
        st=p.stat()
        if st.st_uid!=0 or stat.S_IMODE(st.st_mode)!=0o600: return None
        try: text=p.read_text()
        except OSError: return None
        return self._parse_enable(text)

    def _initial_admission(self):
        if os.uname().release!=KERNEL: raise SessionRejected("RGB_PRODUCT_KERNEL_ABI_MISMATCH")
        if not self.authorized(): raise SessionRejected("RGB_PRODUCT_BOOT_OR_ENABLE_CONTRACT_MISMATCH")
        manifest=STACK_STATE/'installed-camera-stack-manifest.sha256'
        assets=self.root/'PRODUCT-ASSETS.sha256'
        source_head=self.root/'SOURCE-HEAD'
        enable=self._enable_contract()
        if enable is None or not manifest.is_file() or _sha(manifest)!=enable['package_manifest_sha256']:
            raise SessionRejected("RGB_PRODUCT_PACKAGE_MANIFEST_MISMATCH")
        if (not assets.is_file() or _sha(assets)!=enable['product_assets_sha256'] or
                not source_head.is_file() or source_head.read_text().strip()!=enable['source_head']):
            raise SessionRejected("RGB_PRODUCT_SOURCE_OR_ASSET_MANIFEST_MISMATCH")
        check=subprocess.run(('sha256sum','-c',str(assets)),cwd='/',text=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=8,check=False)
        if check.returncode!=0: raise SessionRejected("RGB_PRODUCT_ASSET_HASH_DRIFT")
        for node in (self.media,*self.physical,'/dev/video90','/dev/video91'):
            try: ok=stat.S_ISCHR(os.stat(node,follow_symlinks=False).st_mode)
            except FileNotFoundError: ok=False
            if not ok: raise SessionRejected("RGB_PRODUCT_CAMERA_NODE_MISSING")

    def authorized(self):
        if os.geteuid()!=0 or self._closed: return False
        cmd=Path('/proc/cmdline').read_text().split()
        if TOKEN not in cmd or ENTRY not in cmd: return False
        if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=self.boot: return False
        if self._enable_contract() is None: return False
        try: env=bounded_command(('grub-editenv','/boot/grub/grubenv','list'),timeout=4.0)
        except (subprocess.SubprocessError,OSError): return False
        return ('saved_entry='+GOLDEN) in env.splitlines() and 'next_entry=' in env.splitlines()

    def lease_held(self):
        if self._lease_fd is None or self._closed: return False
        try:
            a=os.fstat(self._lease_fd); b=os.stat(self.root/'controller.lock',follow_symlinks=False)
            return a.st_ino==b.st_ino and a.st_dev==b.st_dev and b.st_uid==0
        except OSError: return False

    def no_camera_users(self):
        if not self.authorized() or not self.lease_held(): return False
        for camera in ('front','rear'):
            if self.service_state(camera)['active']: return False
        nodes=sorted(set(glob.glob('/dev/video[0-9]*')+glob.glob('/dev/v4l-subdev[0-9]*')+glob.glob('/dev/media[0-9]*')))
        if not {self.media,*self.physical,'/dev/video90','/dev/video91'}.issubset(nodes): return False
        try:
            p=subprocess.run(('fuser','-s',*nodes),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,timeout=5,check=False,close_fds=True)
        except (subprocess.SubprocessError,OSError): return False
        return p.returncode==1

    def ir_off(self):
        if not self.authorized() or not self.lease_held(): return False
        found=[]
        for dev in glob.glob('/sys/bus/i2c/devices/*-0060'):
            try:
                if (Path(dev)/'of_node/compatible').read_bytes().rstrip(b'\0')==b'microsoft,sp11-vd55g0': found.append(Path(dev))
            except OSError: pass
        if len(found)!=1: return False
        try: return (found[0]/'power/runtime_status').read_text().strip()=='suspended'
        except OSError: return False

    def unit(self,camera):
        if camera not in ('front','rear'): raise SessionRejected("INVALID_RGB_PRODUCT_UNIT")
        return f'sp11-camera-rgb-publisher@{camera}.service'

    def run(self,argv: tuple[str,...], *, timeout: float):
        if not self.authorized() or not self.lease_held():
            raise SessionRejected("RGB_PRODUCT_IDENTITY_OR_LEASE_LOST")
        if argv[:2] in (("systemctl","start"),("systemctl","stop")):
            if len(argv)!=3 or argv[2] not in (self.unit('front'),self.unit('rear')):
                raise SessionRejected("UNADMITTED_PRODUCT_SYSTEMD_OPERATION")
        elif argv and argv[0]=='media-ctl':
            if len(argv)<4 or argv[1:3]!=("-d",self.media) or argv[3] not in ('-p','-V','-l'):
                raise SessionRejected("UNADMITTED_PRODUCT_MEDIA_OPERATION")
        elif argv and argv[0]=='v4l2-ctl':
            if len(argv)!=4 or argv[1]!='-d' or argv[2] not in self.physical or not (
                    argv[3].startswith('--set-fmt-video=') or argv[3]=='--get-fmt-video'):
                raise SessionRejected("UNADMITTED_PRODUCT_V4L2_OPERATION")
        else: raise SessionRejected("UNADMITTED_PRODUCT_OPERATION")
        if timeout<=0 or timeout>12: raise SessionRejected("UNBOUNDED_PRODUCT_OPERATION")
        return bounded_command(argv,timeout=timeout)

    def service_state(self,camera):
        unit=self.unit(camera)
        text=bounded_command(('systemctl','show',unit,'-p','ActiveState','-p','MainPID','-p','InvocationID','--no-pager'),timeout=5.0)
        d=dict(x.split('=',1) for x in text.splitlines() if '=' in x)
        if not all(k in d for k in ('ActiveState','MainPID','InvocationID')): raise SessionRejected("INCOMPLETE_PRODUCT_SYSTEMD_STATE")
        if d['ActiveState'] not in ('active','inactive') or not re.fullmatch(r'[0-9]+',d['MainPID']):
            raise SessionRejected("UNEXPECTED_PRODUCT_SYSTEMD_STATE")
        return {'active':d['ActiveState']=='active','pid':int(d['MainPID']),'invocation_id':d['InvocationID']}

    def stop_proof(self,camera,invocation_id):
        if not self.authorized() or not self.lease_held() or not re.fullmatch(r'[0-9a-f]{32}',invocation_id or ''): return False
        try:
            event=json.loads((self.root/'output'/f'{camera}-SERVICE-EXIT.json').read_text())
            log=(self.root/'output'/f'{camera}-SERVICE-STDERR.txt').read_text().splitlines()
            lifecycle=[x for x in log if x.startswith('E004KQ_LIFECYCLE ')]
            records=[json.loads(x) for x in log if x.startswith('{"status":')]
            return (event['boot_id']==self.boot and event['invocation_id']==invocation_id and
                    event['exit_code']=='exited' and event['exit_status']=='143' and event['service_result']=='success' and
                    lifecycle and records and 'termination_requested=1' in lifecycle[-1] and
                    'streamoff_completed=1' in lifecycle[-1] and records[-1].get('status')=='STOPPED' and
                    records[-1].get('continuous') is True and records[-1].get('source_sequence_gaps')==0)
        except (OSError,KeyError,IndexError,json.JSONDecodeError): return False

    def close(self):
        if self._lease_fd is not None: os.close(self._lease_fd); self._lease_fd=None
        self._closed=True
