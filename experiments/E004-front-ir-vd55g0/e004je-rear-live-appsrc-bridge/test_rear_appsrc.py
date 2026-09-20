#!/usr/bin/env python3
"""E004je: bounded optical-byte pipe -> NV12 -> GStreamer application tests.

No camera devices are opened, installed, configured or even enumerated.
The sole archived input is the accepted *test pattern*, not fresh optics.
"""
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
CFILE=HERE/"rear-bayer-stdin-to-nv12.c"
APP=HERE/"nv12-appsrc-consumer.py"
FIXTURE=REPO/"experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw"
INPUT_BYTES=14321824
OUTPUT_BYTES=3110400
FIXTURE_SHA="6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346"
NV12_SHA="86f496416883d7728675802c70a0c83adb10d1a02591a56de1fe45cc3e223d0b"

class RearStreamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="sp11-e004je-test-",dir="/tmp")
        cls.binary=Path(cls.tmp.name)/"rear-bayer-stdin-to-nv12"
        p=subprocess.run(["gcc","-O3","-std=c11","-Wall","-Wextra","-Werror",
                         "-pedantic","-fno-fast-math","-ffp-contract=off",
                          str(CFILE),"-lm","-o",str(cls.binary)],
                         capture_output=True,text=True,timeout=35)
        if p.returncode:raise RuntimeError(p.stderr)
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
    def run_c(self,payload: bytes,frames=1):
        return subprocess.run([str(self.binary),"--frames",str(frames)],
                              input=payload,capture_output=True,timeout=35)
    def run_app(self,payload:bytes,frames=1):
        return subprocess.run(["/usr/bin/python3",str(APP),"--frames",str(frames)],
                              input=payload,capture_output=True,timeout=35)

    def test_accepted_archived_rear_colourbar_exact_nv12_identity(self):
        self.assertEqual(FIXTURE.stat().st_size,INPUT_BYTES)
        raw=FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),FIXTURE_SHA)
        p=self.run_c(raw)
        self.assertEqual(p.returncode,0,p.stderr.decode(errors="replace")[-300:])
        self.assertEqual(len(p.stdout),OUTPUT_BYTES)
        self.assertEqual(hashlib.sha256(p.stdout).hexdigest(),NV12_SHA)
        self.assertIn(b"FRAMES=1",p.stderr)
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),FIXTURE_SHA)

    def test_accepted_archived_colorbar_to_actual_gstreamer_appsrc(self):
        c=self.run_c(FIXTURE.read_bytes())
        self.assertEqual(c.returncode,0,c.stderr[-300:])
        a=self.run_app(c.stdout)
        self.assertEqual(a.returncode,0,a.stderr[-500:])
        self.assertIn(b"E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=1",a.stderr)
        self.assertIn(b"VIRTUAL_WEBCAM_CREATED=NO",a.stderr)

    def test_eight_frames_real_bounded_pipe_and_gstreamer(self):
        source=(
          "from pathlib import Path;import sys;"
          "d=Path(sys.argv[1]).read_bytes();"
          "assert len(d)==14321824;"
          "[(sys.stdout.buffer.write(d),sys.stdout.buffer.flush()) for _ in range(8)]"
        )
        commands=[
            ["python3","-c",source,str(FIXTURE)],
            [str(self.binary),"--frames","8"],
            ["/usr/bin/python3",str(APP),"--frames","8"],
        ]
        processes=[]
        try:
            for i,cmd in enumerate(commands):
                p=subprocess.Popen(cmd,stdin=processes[-1].stdout if processes else None,
                    stdout=subprocess.PIPE if i<len(commands)-1 else subprocess.DEVNULL,
                    stderr=subprocess.PIPE)
                if processes:processes[-1].stdout.close()
                processes.append(p)
            # Wait for final consumer first, then each producer. Pipe sizes,
            # queue backpressure and exactly bounded frame counts are exercised.
            out,err=processes[-1].communicate(timeout=60)
            self.assertEqual(processes[-1].returncode,0,err[-700:])
            self.assertIn(b"APP_CONSUMER=GSTREAMER_APPSINK_I420",err)
            self.assertIn(b"PASS FRAMES=8",err)
            for p in reversed(processes[:-1]):
                _,producer_err=p.communicate(timeout=18)
                self.assertEqual(p.returncode,0,producer_err[-700:])
        finally:
            for p in processes:
                if p.poll() is None:
                    p.kill()
                    p.wait(timeout=5)

    def test_filter_rejects_front_qc10c_byte_count(self):
        p=self.run_c(bytes(7778304))
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"TRUNCATED_INPUT",p.stderr)

    def test_filter_rejects_partial_and_extra_rear_frames(self):
        src=FIXTURE.read_bytes()
        short=self.run_c(src[:-1])
        self.assertNotEqual(short.returncode,0)
        self.assertEqual(short.stdout,b"")
        long=self.run_c(src+b"x")
        self.assertNotEqual(long.returncode,0)
        self.assertEqual(len(long.stdout),OUTPUT_BYTES)
        self.assertIn(b"EXTRA_INPUT",long.stderr)

    def test_filter_rejects_bad_frame_bound(self):
        for value in ("0","28","-1","1x"):
            p=subprocess.run([str(self.binary),"--frames",value],input=b"",
                capture_output=True,timeout=7)
            self.assertNotEqual(p.returncode,0,value)
            self.assertEqual(p.stdout,b"")

    def test_application_rejects_short_and_extra_nv12(self):
        p=self.run_app(bytes(OUTPUT_BYTES-1))
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b"truncated NV12 payload",p.stderr)
        p=self.run_app(bytes(OUTPUT_BYTES+1))
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b"EXTRA_NV12_BYTES",p.stderr)

    def test_application_rejects_bad_frame_bound(self):
        for val in (0,28,-1):
            p=self.run_app(b"",val)
            self.assertNotEqual(p.returncode,0)
            self.assertIn(b"FRAME_BOUND",p.stderr)

    def test_no_device_or_boot_access_in_stream_sources(self):
        c=CFILE.read_text()
        app=APP.read_text()
        for forbidden in ("VIDIOC_", "modprobe ", "insmod ", "grub-reboot",
                          "ILLUMINATION_ON", "/dev/video", "/dev/media"):
            self.assertNotIn(forbidden,c)
            self.assertNotIn(forbidden,app)
        self.assertIn("e004iu-rear-fast-nv12-offline/rear_fast.c",c)
        self.assertIn("format=NV12,width=1920,height=1080,framerate=30/1",app)
        self.assertIn("videoconvert",app)
        self.assertIn("appsink name=application",app)

if __name__=="__main__":unittest.main(verbosity=2)
