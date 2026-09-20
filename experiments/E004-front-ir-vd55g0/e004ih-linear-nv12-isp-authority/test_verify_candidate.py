#!/usr/bin/env python3
"""Fail-closed, offline E004ih geometry/source authority regression."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import verify_candidate as v

class GeometryTests(unittest.TestCase):
    def test_exact_proposed_layout(self):
        g = v.geometry()
        self.assertEqual(g["y"], {"offset": 0, "bytes": 3686400, "rows": 1440})
        self.assertEqual(g["uv"], {"offset": 3686400, "bytes": 1843200, "rows": 720})
        self.assertEqual(g["proposed_total_bytes"], 5529600)
        self.assertEqual(g["v4l2_memory_planes"], 1)
        self.assertEqual(g["isp_clients"], [0, 1])

    def test_reject_odd_dimensions(self):
        for width, height in [(1, 1440), (2560, 1), (2559, 1440), (2560, 1439)]:
            with self.subTest(width=width, height=height), self.assertRaises(ValueError):
                v.geometry(width, height)

    def test_reject_invalid_stride(self):
        for stride in (0, 2559, 2557, 2630, -64):
            with self.subTest(stride=stride), self.assertRaises(ValueError):
                v.geometry(stride=stride)

    def test_reject_nonintegers(self):
        with self.assertRaises(ValueError):
            v.geometry(width=True)
        with self.assertRaises(ValueError):
            v.geometry(height=1440.5)

    def test_allow_larger_aligned_stride_as_proposal_only(self):
        g = v.geometry(stride=2816)
        self.assertEqual(g["uv"]["offset"], 2816 * 1440)
        self.assertEqual(g["proposed_total_bytes"], 2816 * 2160)

class AuthorityTests(unittest.TestCase):
    def test_exact_baseline_is_present(self):
        self.assertEqual(v.verify_source(), v.EXPECTED)

    def test_no_runtime_authority(self):
        result = v.candidate()
        self.assertFalse(result["public_vendor_vfe_bus_ver3"]["same_sp11_isp_register_value_confirmed"])
        self.assertIn("camera boot", result["not_authorized"])
        self.assertIn("ISP register writes", result["not_authorized"])
        self.assertTrue(result["accepted_qc10c_unchanged"])

    def test_refuse_changed_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = next(iter(v.EXPECTED))
            path = root / target
            path.parent.mkdir(parents=True)
            path.write_text("untrusted altered source")
            with self.assertRaisesRegex(ValueError, "source authority changed"):
                v.verify_source(root)

    def test_refuse_missing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                v.verify_source(Path(temp))

    def test_refuse_unknown_baseline_digest(self):
        first = next(iter(v.EXPECTED))
        with mock.patch.dict(v.EXPECTED, {first: "0"*64}):
            with self.assertRaisesRegex(ValueError, "source authority changed"):
                v.candidate()

if __name__ == "__main__":
    unittest.main(verbosity=2)
