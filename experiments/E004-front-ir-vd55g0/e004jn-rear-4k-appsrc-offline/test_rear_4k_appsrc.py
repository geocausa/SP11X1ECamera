#!/usr/bin/env python3
"""E004jn: bounded 4K NV12 offline Bayer converter → GStreamer application."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
CONVERTER = PARENT / "e004jm-rear-4k-fused-offline" / "rear-bayer-to-nv12-4k-fused.c"
CONSUMER = HERE / "nv12-4k-appsrc-consumer.py"
COLORBAR = PARENT / ("e004dz-canonical-package-rgb-handoff/"
                     "runtime-output/rear-colorbar.raw")
INPUT_BYTES = 5104 * 2806
FRAME_BYTES = 3840 * 2160 * 3 // 2


def patterned_frame(seed):
    """Synthetic packed RAW10-like test bytes, no real optical pixels."""
    row = bytes((x*17+(x//5)*3+(x%5)*31+seed*19)&255 for x in range(5104))
    return b"".join(row.translate(bytes((i+7*y+13*((y//2)%11))&255
                                        for i in range(256)))
                    for y in range(2806))


class Rear4kApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="sp11-e004jn-test-")
        cls.binary = Path(cls.tmp.name) / "rear4k"
        subprocess.run(["gcc", "-O3", "-std=c11", "-Wall", "-Wextra",
                        "-Werror", "-pedantic", "-fno-fast-math",
                        "-ffp-contract=off", str(CONVERTER), "-o",
                        str(cls.binary)], check=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def convert(self, data, n=1):
        p = subprocess.run([str(self.binary), "--frames", str(n)],
                           input=data, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertEqual(len(p.stdout), FRAME_BYTES*n)
        return p.stdout

    def consume(self, data, n=1, distinct=False):
        args = ["/usr/bin/python3", str(CONSUMER), "--frames", str(n)]
        if distinct:
            args += ["--require-distinct"]
        return subprocess.run(args, input=data, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=50)

    def test_archived_real_hardware_colorbar_one_app_frame(self):
        fixture = COLORBAR.read_bytes()
        self.assertEqual(len(fixture), INPUT_BYTES)
        frames = self.convert(fixture)
        self.assertEqual(hashlib.sha256(frames).hexdigest(),
                         "42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d")
        p = self.consume(frames)
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertIn(b"FRAMES=1 SIZE=12441600", p.stderr)
        self.assertIn(b"SYNTHETIC_PTS_ONLY=YES", p.stderr)
        self.assertIn(b"VIRTUAL_WEBCAM_CREATED=NO", p.stderr)
        self.assertEqual(p.stdout, b"")

    def test_two_distinct_synthetic_frames_reach_app(self):
        a, b = patterned_frame(1), patterned_frame(2)
        frames = self.convert(a+b, 2)
        self.assertNotEqual(frames[:FRAME_BYTES], frames[FRAME_BYTES:])
        p = self.consume(frames, 2, distinct=True)
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertIn(b"FRAMES=2 SIZE=12441600", p.stderr)
        self.assertIn(b"DISTINCT_PAYLOADS_VERIFIED=YES", p.stderr)

    def test_identical_input_fails_optional_distinct_gate(self):
        frame = self.convert(COLORBAR.read_bytes())
        p = self.consume(frame+frame, 2, distinct=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(b"OUTPUT_FRAMES_NOT_DISTINCT", p.stderr)

    def test_truncation_and_extra_input_rejected(self):
        for data, n, text in ((b"Z"*4096, 1, b"truncated NV12"),
                              (b"Z"*(FRAME_BYTES+1), 1, b"EXTRA_NV12_BYTES")):
            p = self.consume(data, n)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn(text, p.stderr)

    def test_invalid_frame_bounds_rejected(self):
        for n in (0, 9, -1):
            p = self.consume(b"", n)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn(b"FRAME_BOUND", p.stderr)

    def test_reader_source_only_and_explicit_not_live(self):
        src = CONSUMER.read_text()
        for forbidden in ("subprocess", "/dev/video", "modprobe", "insmod",
                          "BootNext", "grub-editenv", "os.system"):
            self.assertNotIn(forbidden, src)
        for required in ("WIDTH = 3840", "HEIGHT = 2160",
                         "SYNTHETIC_PTS_ONLY=YES", "LIVE_CAMERA_PROVEN=NO",
                         "VIRTUAL_WEBCAM_CREATED=NO", "require_distinct"):
            self.assertIn(required, src)


if __name__ == "__main__":
    unittest.main()
