#!/usr/bin/env python3
"""E004hi: offline bounded in-memory IPC for provisional native C frame outputs.

No device, camera, PMIC, LED, enrollment, liveness or login API. Real camera
frames/provenance are NOT established by this protocol. A DONE marker AND
process exit 0 are required before the whole session is COMPLETE; earlier
frames MUST be discarded if any later packet/timeout/exit fails.

A caller-invoked monotonic clock and child timeout are NOT an independent
watchdog if the host itself stalls or crashes.
"""
from pathlib import Path
import os
import select
import signal
import stat
import subprocess
import time

WIDTH=644
HEIGHT=604
YLEN=WIDTH*HEIGHT
FRAME_LEN=YLEN*3//2
MAX_FRAMES=16

class StreamFault(Exception):
    """Failure intentionally excludes raw pixels and biometric metadata."""

class OfflineStream:
    """One-shot, no re-arm. Only temporary user-owned executable allowed."""

    __slots__=("_child","_stdin","_stdout","_deadline","_max_seconds",
               "count","next_index","state")

    def __init__(self,binary,count,max_seconds=30.0):
        if (type(count) is not int or not 1<=count<=MAX_FRAMES or
            type(max_seconds) not in (int,float) or
            not 0.1<=max_seconds<=120.0):
            raise StreamFault("invalid bounded offline stream contract")
        path=Path(binary)
        scratch=Path("/tmp")
        if (path.is_symlink() or not path.is_file() or
            not path.resolve().is_relative_to(scratch) or
            path.stat().st_uid!=os.getuid() or
            not (path.stat().st_mode & stat.S_IXUSR)):
            raise StreamFault("offline worker must be temporary user-owned executable")
        self.count=count
        self.next_index=1
        self.state="collecting"
        self._max_seconds=float(max_seconds)
        self._deadline=time.monotonic()+self._max_seconds
        try:
            self._child=subprocess.Popen(
                [str(path),"--frames",str(count)],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,bufsize=0,close_fds=True)
            self._stdin=self._child.stdin.fileno()
            self._stdout=self._child.stdout.fileno()
            os.set_blocking(self._stdin,False)
            os.set_blocking(self._stdout,False)
        except (OSError,ValueError) as exc:
            self.state="fault"
            raise StreamFault("failed to launch bounded offline C worker") from exc

    def _abort(self):
        self.state="fault"
        if self._child.poll() is None:
            self._child.kill()
        try:self._child.communicate(timeout=3)
        except (OSError,ValueError,subprocess.TimeoutExpired):
            if self._child.poll() is None:self._child.kill()
            self._child.wait(timeout=3)

    def _reject(self):
        if self.state!="complete":
            self._abort()
        raise StreamFault("offline stream rejected; entire session invalid")

    def _wait_io(self,read=False):
        remaining=self._deadline-time.monotonic()
        if remaining<=0:
            self._reject()
        readers=[self._stdout] if read else []
        writers=[] if read else [self._stdin]
        try:
            r,w,_=select.select(readers,writers,[],remaining)
        except (OSError,ValueError):
            self._reject()
        if not (r if read else w):
            self._reject()

    def _write(self,data):
        fd=self._stdin
        pos=0
        while pos<len(data):
            self._wait_io(read=False)
            try:
                n=os.write(fd,data[pos:pos+65536])
            except (BlockingIOError,InterruptedError):
                continue
            except OSError:
                self._reject()
            if n<=0:
                self._reject()
            pos+=n

    def _read(self,size):
        if type(size) is not int or not 1<=size<=FRAME_LEN:
            self._reject()
        buf=bytearray()
        while len(buf)<size:
            self._wait_io(read=True)
            try:
                data=os.read(self._stdout,min(size-len(buf),65536))
            except (BlockingIOError,InterruptedError):
                continue
            except OSError:
                self._reject()
            if not data:
                self._reject()
            buf.extend(data)
        return bytes(buf)

    def accept(self,index,frame):
        if self.state!="collecting":
            self._reject()
        if (type(index) is not int or index!=self.next_index or
            index>self.count or
            type(frame) is not bytes or len(frame)!=FRAME_LEN or
            frame[YLEN:]!=bytes([128])*(FRAME_LEN-YLEN)):
            self._reject()
        self._write(b"IN01"+index.to_bytes(4,"little")+frame)
        header=self._read(8)
        if header!=b"OUT1"+index.to_bytes(4,"little"):
            self._reject()
        result=self._read(FRAME_LEN)
        if result[YLEN:]!=bytes([128])*(FRAME_LEN-YLEN):
            self._reject()
        self.next_index+=1
        return result  # PROVISIONAL until finish succeeds.

    def finish(self):
        if self.state!="collecting" or self.next_index!=self.count+1:
            self._reject()
        try:
            self._child.stdin.close()
        except OSError:
            self._reject()
        marker=self._read(8)
        if marker!=b"DONE"+self.count.to_bytes(4,"little"):
            self._reject()
        self._wait_io(read=True)
        try:
            extra=os.read(self._stdout,1)
        except OSError:
            self._reject()
        if extra!=b"":
            self._reject()
        remaining=max(0,self._deadline-time.monotonic())
        try:
            code=self._child.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            self._reject()
        if code!=0:
            self._reject()
        self.state="complete"
        self._child.stdout.close()
        self._child.stderr.close()
        # Source image/model vectors are owned by caller RAM; this object
        # returns only explicitly untrusted diagnostic metadata.
        return {
            "kind":"offline-provisional-stream-diagnostic-only",
            "status":"complete",
            "frames_checked":self.count,
            "all_outputs_provisional_until_terminal_done":True,
            "frame_capture_freshness_or_liveness_proven":False,
            "face_authentication_or_enrollment_proven":False,
            "login_or_unlock_authorized":False,
            "native_ir_emitter_activated":False,
            "autonomous_hardware_cutoff_proven":False,
        }

    def cancel(self):
        if self.state=="complete":
            raise StreamFault("offline stream already terminal")
        self._reject()
