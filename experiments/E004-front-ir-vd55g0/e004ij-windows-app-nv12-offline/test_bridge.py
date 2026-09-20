#!/usr/bin/env python3
"""Bounded real-SP11 GStreamer offline app-format bridge acceptance."""
import hashlib
from pathlib import Path
import runpy
import tempfile
import unittest

S = runpy.run_path(str(Path(__file__).with_name("nv12-desktop-bridge.py")))
bridge = S["bridge"]
SRC_FRAME = S["SRC_FRAME"]
DST_FRAME = S["DST_FRAME"]
DST_W, DST_H = S["DST_W"], S["DST_H"]

def fixture(shades):
    y = 2560 * 1440
    return b"".join(bytes([shade]) * y + bytes([128]) * (y // 2) for shade in shades)

class OfflineWindowsRecordTarget(unittest.TestCase):
    def test_source_oracle_sha(self):
        repo = Path(__file__).resolve().parents[3]
        original = repo / "experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-cgc-cold-path/HOLDER-SUCCESS.txt"
        data = original.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), S["WINDOWS_RECORD_PROVENANCE_SHA256"])
        self.assertIn(b"kind=Color stream=VideoRecord fmt=NV12 dims=1920x1080", data)
        self.assertIn(b"E003H_START_STATUS=Success", data)

    def test_actual_gstreamer_two_frames(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004ij-") as d:
            d = Path(d)
            payload = fixture([52,148])
            (d / "source.nv12").write_bytes(payload)
            r = bridge(d / "source.nv12", d / "output.nv12", 2)
            output = (d / "output.nv12").read_bytes()
            self.assertEqual(len(output), DST_FRAME * 2)
            n = DST_W * DST_H
            self.assertEqual(output[:n], bytes([52])*n)
            self.assertEqual(output[n:DST_FRAME], bytes([128])*(DST_FRAME-n))
            self.assertEqual(output[DST_FRAME:DST_FRAME+n], bytes([148])*n)
            self.assertEqual(output[DST_FRAME+n:], bytes([128])*(DST_FRAME-n))
            self.assertEqual(r["output_format"], "NV12")
            self.assertEqual((r["output_width"], r["output_height"]), (1920,1080))
            self.assertFalse(r["colorimetry_optical_parity_proven"])
            self.assertFalse(r["camera_or_hardware_used"])
            self.assertEqual((d / "source.nv12").read_bytes(), payload)

    def test_failclosed_lengths_and_frame_counts(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004ij-") as d:
            d = Path(d)
            source, out = d/"source.nv12", d/"output.nv12"
            for n in (SRC_FRAME-1,SRC_FRAME+1):
                with self.subTest(length=n):
                    source.write_bytes(bytes(n))
                    with self.assertRaisesRegex(ValueError, "input length"):
                        bridge(source,out,1)
                    self.assertFalse(out.exists())
            for count in (0,-1,28,1.0,True):
                with self.subTest(count=count), self.assertRaises(ValueError):
                    bridge(source,out,count)
                self.assertFalse(out.exists())

    def test_existing_output_is_unchanged(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004ij-") as d:
            d = Path(d); src=d/"src.nv12";out=d/"out.nv12"
            src.write_bytes(fixture([55]));out.write_bytes(b"PROTECT_EXISTING")
            with self.assertRaisesRegex(ValueError,"preexisting output"):
                bridge(src,out,1)
            self.assertEqual(out.read_bytes(),b"PROTECT_EXISTING")

    def test_input_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004ij-") as d:
            d=Path(d); src=d/"src.nv12";alias=d/"alias.nv12";out=d/"out.nv12"
            src.write_bytes(fixture([55]));alias.symlink_to(src)
            with self.assertRaisesRegex(ValueError,"input must"):
                bridge(alias,out,1)
            self.assertFalse(out.exists())

    def test_no_hardware_and_nonprivate_output_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004ij-") as d:
            d=Path(d);src=d/"src.nv12";src.write_bytes(fixture([55]))
            with self.assertRaisesRegex(ValueError,"output must be"):
                bridge(src,Path("/etc/sp11-camera-no-write.nv12"),1)
            with self.assertRaisesRegex(ValueError,"do not replace"):
                bridge(src,src,1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
