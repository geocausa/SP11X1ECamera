#!/usr/bin/env python3
"""E004jz: source-only exact-bytes 4K pipe boundary telemetry tests."""
from pathlib import Path
import hashlib
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"nv12-4k-pipe-audit.c"
FRAME=3840*2160*3//2
EXEC="/tmp/sp11-e004jz-pipe-audit"


class AuditOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=subprocess.run(["gcc","-O2","-std=c11","-Wall","-Wextra",
                          "-Werror","-pedantic",str(SOURCE),"-o",EXEC],
                         capture_output=True,text=True,timeout=25)
        if p.returncode:
            raise RuntimeError(p.stderr)
        cls.frame=bytes([71])*FRAME

    def call(self,frames,data,idle=1000):
        return subprocess.run([EXEC,"--frames",str(frames),"--idle-ms",str(idle)],
            input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=12)

    def test_exact_byte_for_byte_single_frame_sha_and_no_disk(self):
        p=self.call(1,self.frame)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(len(p.stdout),FRAME)
        self.assertEqual(hashlib.sha256(p.stdout).digest(),
                         hashlib.sha256(self.frame).digest())
        self.assertIn(b"E004JZ_4K_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1",p.stderr)
        self.assertIn(f"BYTES_IN={FRAME} BYTES_OUT={FRAME}".encode(),p.stderr)
        self.assertIn(b"INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF",p.stderr)

    def test_two_full_frames_progress_and_full_frame_boundary_rate(self):
        f=bytearray(self.frame)
        f[0]=42
        payload=self.frame+bytes(f)
        p=self.call(2,payload)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(hashlib.sha256(p.stdout).digest(),hashlib.sha256(payload).digest())
        self.assertIn(b"FULL_FRAMES=2",p.stderr)
        self.assertIn(b"PIPE_FULL_FRAME_BOUNDARY_FPS=",p.stderr)
        self.assertIn(b"CAMERA_PROVEN_BY_THIS_TOOL=NO",p.stderr)

    def test_exact_2048_missing_bytes_exposed_without_counting_partial_frame(self):
        n=FRAME-2048
        p=self.call(1,self.frame[:n])
        self.assertEqual(p.returncode,1)
        self.assertEqual(len(p.stdout),n)
        self.assertIn(f"E004JZ_4K_PIPE=PARTIAL REQUESTED_FRAMES=1 FULL_FRAMES=0 BYTES_IN={n}".encode(),p.stderr)
        self.assertIn(f"INCOMPLETE_TAIL_BYTES={n} TERMINATION=EOF".encode(),p.stderr)

    def test_stalled_open_upstream_reports_partial_not_hang(self):
        proc=subprocess.Popen([EXEC,"--frames","1","--idle-ms","150"],
                              stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE)
        try:
            proc.stdin.write(b"x"*8192)
            proc.stdin.flush()
            self.assertEqual(proc.wait(timeout=5),1)
            report=proc.stderr.read()
            self.assertIn(b"BYTES_IN=8192 BYTES_OUT=8192",report)
            self.assertIn(b"INCOMPLETE_TAIL_BYTES=8192 TERMINATION=INPUT_IDLE",report)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            for file in (proc.stdin,proc.stderr):
                if file and not file.closed:
                    file.close()

    def test_extra_bytes_and_invalid_bounds_fail_closed(self):
        p=self.call(1,self.frame+b"x")
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b"TERMINATION=FRAME_BOUND_EXCEEDED",p.stderr)
        for args in (["--frames","0","--idle-ms","150"],
                     ["--frames","121","--idle-ms","150"],
                     ["--frames","1","--idle-ms","20"],
                     ["--frames","1","--idle-ms","15001"]):
            bad=subprocess.run([EXEC,*args],input=b"",capture_output=True,timeout=4)
            self.assertEqual(bad.returncode,2)

    def test_two_complete_synthetic_frames_through_real_gstreamer_app(self):
        app=(HERE.parent/"e004jx-rear-4k-partial-telemetry"/
             "nv12-4k-partial-telemetry-app.py")
        self.assertTrue(app.exists())
        pipeline=(
            "/usr/bin/python3 -c 'import sys;f=bytes([108])*(3840*2160*3//2);"
            "[sys.stdout.buffer.write(f) for _ in range(2)]' "
            "| \"$1\" --frames 2 --idle-ms 2000 "
            "| /usr/bin/python3 \"$2\" --frames 2 --idle-seconds 2"
        )
        p=subprocess.run(["bash","-o","pipefail","-c",pipeline,"bash",
                          EXEC,str(app)],stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,timeout=22)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"E004JZ_4K_PIPE=PASS REQUESTED_FRAMES=2 FULL_FRAMES=2",p.stderr)
        self.assertIn(b"E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=2 REQUESTED_FRAMES=2",p.stderr)

    def test_no_camera_device_or_frame_file_side_effects(self):
        code=SOURCE.read_text()
        for word in ("/dev/video","media-ctl","insmod","modprobe",
                     "grub-reboot","BootNext","ILLUMINATION_ON",
                     "fopen(", "open(", "O_CREAT"):
            self.assertNotIn(word,code)
        self.assertIn("BYTES_IN=",code)
        self.assertIn("BYTES_OUT=",code)
        self.assertIn("INCOMPLETE_TAIL_BYTES=",code)
        self.assertIn("PIXELS_SAVED=NO",code)


if __name__=="__main__":
    unittest.main()
