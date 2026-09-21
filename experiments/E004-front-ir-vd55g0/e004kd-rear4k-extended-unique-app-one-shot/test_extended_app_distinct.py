#!/usr/bin/env python3
"""E004kd: all-app-frame optical-output uniqueness fail-closed source test."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
APP=HERE.parent/"e004jx-rear-4k-partial-telemetry"/"nv12-4k-partial-telemetry-app.py"
F=3840*2160*3//2


class ExtendedAppUniqueness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flat=bytes([100])*F

    def run_app(self,payload,n=3):
        return subprocess.run(
            ["/usr/bin/python3",str(APP),"--frames",str(n),
             "--require-distinct","--idle-seconds","1.5"],
            input=payload,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=24)

    def test_three_distinct_full_4k_input_frames_pass_without_hash_export(self):
        a=bytearray(self.flat);b=bytearray(self.flat)
        a[150]=120;b[150]=175
        p=self.run_app(self.flat+bytes(a)+bytes(b))
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"PASS FRAMES=3 REQUESTED_FRAMES=3",p.stderr)
        self.assertIn(b"DISTINCT_PAYLOADS_VERIFIED=YES",p.stderr)
        self.assertIn(b"SINK_OBSERVED_FPS=",p.stderr)
        self.assertNotIn(b"SHA256",p.stderr)

    def test_repeated_full_4k_input_frames_rejected(self):
        p=self.run_app(self.flat*3)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"E004JX_OUTPUT_FRAMES_NOT_DISTINCT",p.stderr)
        self.assertNotIn(b"DISTINCT_PAYLOADS_VERIFIED=YES",p.stderr)

    def test_missing_frame_never_claimed_unique_or_pass(self):
        p=self.run_app(self.flat*2)
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b"PARTIAL FRAMES=2 REQUESTED_FRAMES=3",p.stderr)
        self.assertNotIn(b"E004JX_NV12_APPSRC_CONSUMER=PASS",p.stderr)

    def test_source_only_no_camera_and_pixel_file_write(self):
        s=APP.read_text()
        for banned in ("/dev/video","media-ctl","insmod","modprobe",
                       "grub-reboot","BootNext","ILLUMINATION_ON"):
            self.assertNotIn(banned,s)
        self.assertIn("require_distinct",s)
        self.assertIn("len(set(hashes)) != frames",s)


if __name__=="__main__":
    unittest.main()
