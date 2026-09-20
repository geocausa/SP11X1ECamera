#!/usr/bin/env python3
"""E004jm: preserve original rear 4K output exactly while reducing redundant work."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "e004jl-rear-4k-nv12-offline"
OLD = BASE / "rear-bayer-to-nv12-4k.c"
NEW = HERE / "rear-bayer-to-nv12-4k-fused.c"
FIXTURE = HERE.parent / ("e004dz-canonical-package-rgb-handoff/"
                          "runtime-output/rear-colorbar.raw")
IN_SIZE = 5104 * 2806
OUT_SIZE = 3840 * 2160 * 3 // 2
FLAGS = ["gcc", "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
         "-pedantic", "-fno-fast-math", "-ffp-contract=off"]


def patterned_frame(seed=0):
    """Synthetic nonuniform packed RAW10-like bytes; not an optical image."""
    row = bytes((x * 17 + (x // 5) * 3 + (x % 5) * 31 + seed * 19) & 255
                for x in range(5104))
    frame = b"".join(row.translate(bytes((i + 7 * y + 13 * ((y // 2) % 11))
                                  & 255 for i in range(256)))
                     for y in range(2806))
    assert len(frame) == IN_SIZE
    return frame


class FusedRear4k(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="sp11-e004jm-test-")
        cls.old = Path(cls.tmp.name) / "baseline"
        cls.new = Path(cls.tmp.name) / "fused"
        for src, binary in ((OLD, cls.old), (NEW, cls.new)):
            subprocess.run(FLAGS + [str(src), "-o", str(binary)],
                           timeout=30, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_one(self, binary, frame, frames="1"):
        return subprocess.run([str(binary), "--frames", frames], input=frame,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=30)

    def assert_bit_exact(self, frame):
        base = self.run_one(self.old, frame)
        fast = self.run_one(self.new, frame)
        self.assertEqual(base.returncode, 0, base.stderr.decode())
        self.assertEqual(fast.returncode, 0, fast.stderr.decode())
        self.assertEqual(len(base.stdout), OUT_SIZE)
        self.assertEqual(len(fast.stdout), OUT_SIZE)
        self.assertEqual(fast.stdout, base.stdout)
        self.assertIn(b"CALIBRATED=NO", fast.stderr)
        self.assertIn(b"LIVE_4K_CAPTURE=NO", fast.stderr)
        return hashlib.sha256(fast.stdout).hexdigest()

    def test_archived_hardware_colourbar_bit_exact(self):
        pattern = FIXTURE.read_bytes()
        self.assertEqual(len(pattern), IN_SIZE)
        self.assertEqual(self.assert_bit_exact(pattern),
                         "42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d")

    def test_nonuniform_synthetic_mosaic_bit_exact(self):
        self.assertEqual(self.assert_bit_exact(patterned_frame()),
                         "d28f598edd6f5f8691f851419eaae258ea864e2e53111580e4067d931fe91f22")

    def test_another_independent_synthetic_seed(self):
        self.assert_bit_exact(patterned_frame(3))

    def test_two_different_frames_order_and_byte_count(self):
        a, b = patterned_frame(1), patterned_frame(2)
        base = self.run_one(self.old, a+b, "2")
        fast = self.run_one(self.new, a+b, "2")
        self.assertEqual(base.returncode, 0, base.stderr.decode())
        self.assertEqual(fast.returncode, 0, fast.stderr.decode())
        self.assertEqual(len(fast.stdout), OUT_SIZE*2)
        self.assertEqual(base.stdout, fast.stdout)
        self.assertNotEqual(fast.stdout[:OUT_SIZE], fast.stdout[OUT_SIZE:])

    def test_rejects_front_qc10c_and_bad_bounds(self):
        for count, src, expected_rc in (("1", bytes(7778304), 1),
                                        ("0", b"", 2),
                                        ("9", b"", 2),
                                        ("foo", b"", 2)):
            p = self.run_one(self.new, src, count)
            self.assertEqual(p.returncode, expected_rc)
            self.assertEqual(p.stdout, b"")

    def test_fail_closed_excess_bytes(self):
        p = self.run_one(self.new, FIXTURE.read_bytes()+b"X")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(b"EXTRA_INPUT_OR_READ_ERROR", p.stderr)

    def test_source_preserves_crop_and_nonactivation(self):
        src = NEW.read_text()
        base = OLD.read_text()
        for invariant in ("SRC_W=4076", "DST_W=3840", "DST_H=2160",
                          "CROP_X=118, CROP_Y=322", "DST_BYTES=DST_Y*3/2"):
            self.assertIn(invariant, src)
            self.assertIn(invariant, base)
        for forbidden in ("/dev/video", "ioctl(", "modprobe", "insmod",
                          "grub-editenv", "BootNext", "EFI/", "system("):
            self.assertNotIn(forbidden, src)
        self.assertIn("LIVE_4K_CAPTURE=NO", src)

    def test_gstreamer_accepts_same_4k_nv12(self):
        if not shutil.which("gst-launch-1.0"):
            self.skipTest("GStreamer unavailable")
        p = self.run_one(self.new, FIXTURE.read_bytes())
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        result = subprocess.run([
            "gst-launch-1.0", "-q", "fdsrc", "blocksize=65536", "!",
            "rawvideoparse", "format=nv12", "width=3840", "height=2160",
            "framerate=30/1", "!", "videoconvert", "!", "fakesink", "sync=false"
        ], input=p.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
