#!/usr/bin/env python3
"""E004jl: source-only 4K NV12 rear experiment; no camera activation."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE / "rear-bayer-to-nv12-4k.c"
COLORBAR = REPO / ("experiments/E004-front-ir-vd55g0/"
                   "e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw")
SRC_BYTES = 5104 * 2806
DST_BYTES = 3840 * 2160 * 3 // 2


class Rear4kOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="sp11-e004jl-test-")
        cls.binary = Path(cls.tmp.name) / "rear4k"
        subprocess.run(["gcc", "-O3", "-std=c11", "-Wall", "-Wextra",
                        "-Werror", "-pedantic", "-fno-fast-math",
                        "-ffp-contract=off", str(SOURCE), "-o",
                        str(cls.binary)], check=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_converter(self, payload, frames="1"):
        return subprocess.run([str(self.binary), "--frames", frames],
                              input=payload, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=25)

    def test_source_has_no_camera_or_boot_interfaces(self):
        src = SOURCE.read_text()
        for forbidden in ("/dev/video", "ioctl(", "grub", "system(",
                          "modprobe", "insmod", "EFI/", "PMIC", "iris"):
            self.assertNotIn(forbidden, src)
        self.assertIn("CROP_X=118, CROP_Y=322", src)
        self.assertIn("DST_W=3840, DST_H=2160", src)

    def test_rejects_invalid_bounds(self):
        for n in ("0", "9", "-1", "oops", "1x", "999999999999999999999"):
            p = self.run_converter(b"", n)
            self.assertEqual(p.returncode, 2)
            self.assertEqual(p.stdout, b"")

    def test_rejects_front_qc10c_length_and_partial_raw(self):
        p = self.run_converter(bytes(7778304))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(b"TRUNCATED_REAR_RAW10_INPUT", p.stderr)
        self.assertEqual(p.stdout, b"")

    def test_known_hardware_colorbar_one_frame_hash_and_length(self):
        fixture = COLORBAR.read_bytes()
        self.assertEqual(len(fixture), SRC_BYTES)
        p = self.run_converter(fixture)
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertEqual(len(p.stdout), DST_BYTES)
        self.assertIn(b"LIVE_4K_CAPTURE=NO", p.stderr)
        self.assertEqual(hashlib.sha256(p.stdout).hexdigest(),
                         "42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d")

    def test_extra_byte_fails_closed_on_status(self):
        fixture = COLORBAR.read_bytes()
        p = self.run_converter(fixture + b"x")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(b"EXTRA_INPUT_OR_READ_ERROR", p.stderr)

    def test_two_synthetic_frames_remain_separate(self):
        row0 = bytes([80, 80, 80, 80, 0]) * (4076 // 4) + bytes(9)
        row1 = bytes([160, 160, 160, 160, 0]) * (4076 // 4) + bytes(9)
        self.assertEqual(len(row0), 5104)
        p = self.run_converter(row0 * 2806 + row1 * 2806, "2")
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertEqual(len(p.stdout), DST_BYTES * 2)
        a, b = p.stdout[:DST_BYTES], p.stdout[DST_BYTES:]
        self.assertEqual(a[:32], bytes([80]) * 32)
        self.assertEqual(b[:32], bytes([160]) * 32)
        self.assertEqual(a[DST_BYTES-32:], bytes([128]) * 32)
        self.assertEqual(b[DST_BYTES-32:], bytes([128]) * 32)
        self.assertNotEqual(hashlib.sha256(a).digest(), hashlib.sha256(b).digest())

    def test_gstreamer_consumes_exact_4k_nv12(self):
        if not shutil.which("gst-launch-1.0"):
            self.skipTest("GStreamer is unavailable")
        fixture = COLORBAR.read_bytes()
        conv = self.run_converter(fixture)
        self.assertEqual(conv.returncode, 0, conv.stderr.decode())
        pipe = subprocess.run([
            "gst-launch-1.0", "-q", "fdsrc", "blocksize=65536", "!",
            "rawvideoparse", "format=nv12", "width=3840", "height=2160",
            "framerate=30/1", "!", "videoconvert", "!", "fakesink", "sync=false"
        ], input=conv.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=25)
        self.assertEqual(pipe.returncode, 0, pipe.stderr.decode())


if __name__ == "__main__":
    unittest.main()
