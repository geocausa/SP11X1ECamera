#!/usr/bin/env python3
"""Offline negative tests for exact public-source provenance."""
import runpy
import unittest
from pathlib import Path

scope = runpy.run_path(str(Path(__file__).with_name("verify-vendor.py")))
verify = scope["verify"]

class VendorAuthority(unittest.TestCase):
    def test_real_sha_pinned_source(self):
        source = Path("/tmp/sp11-camera-e004ii-public-cam-vfe-bus-ver3.c")
        if not source.is_file():
            self.skipTest("public source scratch cache not present; use README fetch recipe")
        r = verify(source.read_bytes())
        self.assertEqual(r["public_vfe_bus_ver3_nv12_packer"], 3)
        self.assertEqual(r["public_vfe_bus_ver3_tp10_packer"], 11)
        self.assertFalse(r["x1e80100_nv12_register_recipe_proven"])
        self.assertFalse(r["safe_transition_from_existing_qc10c_ubwc_state_proven"])

    def test_reject_bad_digest(self):
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify(b"enum cam_vfe_bus_ver3_packer_format { /* spoofed */ };")

    def test_reject_empty_or_short_source(self):
        for bad in (b"", b"x", b"CAM_FORMAT_NV12"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                verify(bad)

if __name__ == "__main__":
    unittest.main(verbosity=2)
