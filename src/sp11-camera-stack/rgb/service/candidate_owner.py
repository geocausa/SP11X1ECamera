# SPDX-License-Identifier: MIT
"""Explicitly guarded SP11 root-private real Linux RGB service owner.

Not a Golden install, daemon, boot initializer or arbitrary CLI. Instantiate
only inside a freshly armed, disposable one-shot camera candidate AFTER its
separate hardware-package/module/device and GRUB-writer-order preflights.
Neither this module nor its tests activates hardware or initiates system sleep.
"""
from __future__ import annotations
import fcntl
import glob
import json
import os
import pwd
import re
import stat
import subprocess
from pathlib import Path

from media_backend import bounded_command
from session import SessionRejected

GOLDEN="sp11-audio-fullio-v19c"
KERNEL="7.1.5-sp11-render-parity-v4+"


class CandidateOwner:
    """One process, one protected camera session. Caller must close() lease."""
    def __init__(self, candidate: str, *, staged: Path, discovery: dict):
        if not re.fullmatch(r"e004[a-z]{2}",candidate):
            raise SessionRejected("INVALID_FRESH_CANDIDATE_IDENTITY")
        if os.geteuid()!=0:
            raise SessionRejected("ROOT_PRIVATE_CANDIDATE_REQUIRED")
        self.id=candidate
        self.root=Path("/var/lib/sp11-camera-"+candidate)
        if staged!=self.root or staged.is_symlink() or not staged.is_dir():
            raise SessionRejected("UNTRUSTED_OR_MISSING_CANDIDATE_ROOT")
        st=staged.stat()
        if st.st_uid!=0 or stat.S_IMODE(st.st_mode)!=0o700:
            raise SessionRejected("CANDIDATE_ASSETS_NOT_ROOT_SEALED")
        self.discovery=discovery
        self.media=discovery.get("media")
        self.physical=(discovery.get("front_rdi_video_device"),
                       discovery.get("rear_video_device"))
        if (not isinstance(self.media,str) or
            not re.fullmatch(r"/dev/media(?:0|[1-9][0-9]*)",self.media) or
            any(not isinstance(n,str) or
                not re.fullmatch(r"/dev/video(?:0|[1-9][0-9]*)",n) or
                n in ("/dev/video90","/dev/video91") for n in self.physical) or
            self.physical[0]==self.physical[1]):
            raise SessionRejected("UNTRUSTED_LIVE_DEVICE_DISCOVERY")
        self.boot=Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        self.token="sp11_camera_"+candidate+"_rgb_session=1"
        self._lease_fd: int | None=None
        self._closed=False
        self._started_invocations={}
        self._initial_admission()
        # A separate controller.lock coexists with the publisher's dedicated
        # session.lock; holding publisher's lock would deadlock ExecStart.
        fd=os.open(str(staged/"controller.lock"),
                   os.O_CREAT|os.O_RDWR|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
        try:
            fs=os.fstat(fd)
            if not stat.S_ISREG(fs.st_mode) or fs.st_uid!=0 or stat.S_IMODE(fs.st_mode)!=0o600:
                raise SessionRejected("UNTRUSTED_CONTROLLER_LOCK")
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BaseException:
            os.close(fd)
            raise
        self._lease_fd=fd

    def _initial_admission(self):
        if os.uname().release!=KERNEL:
            raise SessionRejected("GOLDEN_KERNEL_ABI_MISMATCH")
        if not self.authorized():
            raise SessionRejected("BOOT_TOKEN_CONSUMPTION_OR_GOLDEN_GUARD_MISMATCH")
        # The owning candidate preflight must have checked the complete
        # 51-file hardware manifest and exact source HEAD before starting.
        # This only revalidates presence/identity, not the external preflight.
        manifest=self.root/"SESSION-ASSETS.sha256"
        if not manifest.is_file() or manifest.stat().st_size<100:
            raise SessionRejected("MISSING_PINNED_CANDIDATE_MANIFEST")
        for node in (self.media,*self.physical,"/dev/video90","/dev/video91"):
            try:
                if not stat.S_ISCHR(os.stat(node,follow_symlinks=False).st_mode):
                    raise SessionRejected("MISSING_VALIDATED_CAMERA_NODE")
            except FileNotFoundError as exc:
                raise SessionRejected("MISSING_VALIDATED_CAMERA_NODE") from exc

    def authorized(self):
        if os.geteuid()!=0 or self._closed:
            return False
        cmdline=Path("/proc/cmdline").read_text().split()
        if self.token not in cmdline:
            return False
        if ("sp11_entry=7.1.5-sp11-camera-"+self.id+"-rgb-session") not in cmdline:
            return False
        if Path("/proc/sys/kernel/random/boot_id").read_text().strip()!=self.boot:
            return False
        consumed=(self.root/"ATTEMPT-CONSUMED")
        if not consumed.is_file() or f"boot_id={self.boot}" not in consumed.read_text().splitlines():
            return False
        expected=(self.root/"EXPECTED-HEAD")
        if not expected.is_file() or not re.fullmatch(r"[0-9a-f]{40}",expected.read_text().strip()):
            return False
        try:
            env=bounded_command(("grub-editenv","/boot/grub/grubenv","list"),timeout=4.0)
        except (subprocess.SubprocessError,OSError):
            return False
        return ("saved_entry="+GOLDEN) in env.splitlines() and "next_entry=" in env.splitlines()

    def lease_held(self):
        if self._lease_fd is None or self._closed:
            return False
        try:
            fdstat=os.fstat(self._lease_fd)
            pathstat=os.stat(self.root/"controller.lock",follow_symlinks=False)
            return fdstat.st_ino==pathstat.st_ino and fdstat.st_dev==pathstat.st_dev and pathstat.st_uid==0
        except OSError:
            return False

    def no_camera_users(self):
        if not self.authorized() or not self.lease_held():
            return False
        for camera in ("front","rear"):
            if self.service_state(camera)["active"]:
                return False
        nodes=sorted(set(glob.glob("/dev/video[0-9]*")+
                         glob.glob("/dev/v4l-subdev[0-9]*")+
                         glob.glob("/dev/media[0-9]*")))
        mandatory={self.media,*self.physical,"/dev/video90","/dev/video91"}
        if not mandatory.issubset(nodes):
            return False
        try:
            x=subprocess.run(("fuser","-s",*nodes),stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                             timeout=5,check=False,close_fds=True)
        except (subprocess.SubprocessError,OSError):
            return False
        # 1 means no device user. 0 means open FDs, >1 is an error.
        return x.returncode==1

    def ir_off(self):
        if not self.authorized() or not self.lease_held():
            return False
        # The candidate boot hardware authority already prohibits VD55G0
        # native streaming/illumination. Require an independent read-only
        # sensor-idle check and complete RGB-only graph checks on every route.
        match=[]
        for dev in glob.glob("/sys/bus/i2c/devices/*-0060"):
            compat=Path(dev)/"of_node/compatible"
            try:
                if compat.read_bytes().rstrip(b"\0")==b"microsoft,sp11-vd55g0":
                    match.append(Path(dev))
            except OSError:
                continue
        if len(match)!=1:
            return False
        try:
            return (match[0]/"power/runtime_status").read_text().strip()=="suspended"
        except OSError:
            return False

    def unit(self,camera: str):
        if camera not in ("front","rear"):
            raise SessionRejected("INVALID_RGB_UNIT")
        return "sp11-camera-"+self.id+"-session@"+camera+".service"

    def run(self,argv: tuple[str,...], *, timeout: float):
        if not self.authorized() or not self.lease_held():
            raise SessionRejected("CANDIDATE_IDENTITY_OR_LEASE_LOST_BEFORE_OPERATION")
        if argv[:2]==("systemctl","start") or argv[:2]==("systemctl","stop"):
            if len(argv)!=3 or argv[2] not in (self.unit("front"),self.unit("rear")):
                raise SessionRejected("UNADMITTED_SYSTEMD_OPERATION")
        elif argv and argv[0]=="media-ctl":
            if len(argv)<4 or argv[1:3]!=("-d",self.media) or argv[3] not in ("-p","-V","-l"):
                raise SessionRejected("UNADMITTED_MEDIA_COMMAND")
        elif argv and argv[0]=="v4l2-ctl":
            if len(argv)<4 or argv[1]!="-d" or argv[2] not in self.physical:
                raise SessionRejected("UNADMITTED_V4L2_COMMAND")
            if len(argv)!=4 or not (argv[3].startswith("--set-fmt-video=") or argv[3]=="--get-fmt-video"):
                raise SessionRejected("UNADMITTED_V4L2_OPERATION")
        else:
            raise SessionRejected("UNADMITTED_CANDIDATE_OPERATION")
        if timeout<=0 or timeout>12:
            raise SessionRejected("UNBOUNDED_CANDIDATE_OPERATION")
        return bounded_command(argv,timeout=timeout)

    def service_state(self,camera: str):
        self.unit(camera)  # validate exact enum before an external process.
        text=bounded_command(("systemctl","show",self.unit(camera),
            "-p","ActiveState","-p","MainPID","-p","InvocationID",
            "--no-pager"),timeout=5.0)
        d=dict(x.split("=",1) for x in text.splitlines() if "=" in x)
        if not all(k in d for k in ("ActiveState","MainPID","InvocationID")):
            raise SessionRejected("INCOMPLETE_SYSTEMD_STATE")
        if d["ActiveState"] not in ("active","inactive"):
            raise SessionRejected("FAILED_OR_UNEXPECTED_SYSTEMD_STATE")
        if not re.fullmatch(r"[0-9]+",d["MainPID"]):
            raise SessionRejected("INVALID_SYSTEMD_MAIN_PID")
        return {"active":d["ActiveState"]=="active","pid":int(d["MainPID"]),
                "invocation_id":d["InvocationID"]}

    def stop_proof(self,camera: str,invocation_id: str):
        if not self.authorized() or not self.lease_held():
            return False
        try:
            if not re.fullmatch(r"[0-9a-f]{32}",invocation_id):
                return False
            event=json.loads((self.root/"output"/(camera+"-SERVICE-EXIT.json")).read_text())
            if not (event["boot_id"]==self.boot and event["invocation_id"]==invocation_id
                    and event["exit_code"]=="exited" and event["exit_status"]=="143"
                    and event["service_result"]=="success"):
                return False
            text=(self.root/"output"/(camera+"-SERVICE-STDERR.txt")).read_text()
            events=[x for x in text.splitlines() if x.startswith("E004KQ_LIFECYCLE ")]
            records=[json.loads(x) for x in text.splitlines()
                     if x.startswith('{"status":')]
            if not events or not records:
                return False
            return ("termination_requested=1" in events[-1] and
                    "streamoff_completed=1" in events[-1] and
                    records[-1].get("status")=="STOPPED" and
                    records[-1].get("continuous") is True and
                    records[-1].get("source_sequence_gaps")==0)
        except (OSError,KeyError,IndexError,json.JSONDecodeError):
            return False

    def close(self):
        if self._lease_fd is not None:
            os.close(self._lease_fd)
            self._lease_fd=None
        self._closed=True
