#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Independent numerical and invalid-input checks; no camera or profile access."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import open_config as c


def sign13(v):
    return v - 8192 if v & 4096 else v


class ConfigTests(unittest.TestCase):
    def test_exact_front_layout(self):
        d = c.Mode(2560, 1440).nv12()
        self.assertEqual(d["y"]["bytes"], 3686400)
        self.assertEqual(d["uv"]["offset"], 3686400)
        self.assertEqual(d["total_bytes"], 5529600)

    def test_exact_rear_layout(self):
        self.assertEqual(c.Mode(3840, 2160).nv12()["total_bytes"], 12441600)

    def test_padded_nv12(self):
        d = c.Mode(642, 482).nv12()
        self.assertEqual(d["stride"], 704)
        self.assertEqual(d["total_bytes"], 704 * 723)

    def test_bad_dimensions(self):
        for args in [(0, 480), (640, 481), (641, 480), (-2, 480), (True, 2),
                     (640.0, 480), (65536, 2), (65534, 65534)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                c.Mode(*args).nv12()

    def test_bad_alignment(self):
        for a in [0, 1, 3, 63, 8192, False]:
            with self.subTest(a=a), self.assertRaises(ValueError):
                c.Mode(640, 480, a).nv12()

    def test_grid_bounds_and_bayer_alignment(self):
        for w, h in [(3840, 2160), (4064, 2286), (66, 66), (1920, 1080)]:
            g = c.metering_grid(w, h)
            self.assertLessEqual(g["x"] + g["covered_width"], w)
            self.assertLessEqual(g["y"] + g["covered_height"], h)
            for key in ("x", "y", "region_width", "region_height"):
                self.assertEqual(g[key] % 2, 0)
            self.assertEqual(g["samples_per_colour_per_region"] * 4,
                             g["region_width"] * g["region_height"])

    def test_grid_rejects_unrepresentable(self):
        for args in [(62, 62), (3841, 2160), (3840, 2160, 0, 32), (3840, 2160, 65, 32)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                c.metering_grid(*args)

    def test_known_bt601_coefficients(self):
        self.assertEqual(c.bt601_q10_gbr(), [[601, 117, 306], [-339, 512, -173], [-429, -83, 512]])

    def test_neutral_preservation_every_u8_level(self):
        matrix = c.bt601_q10_gbr()
        for v in range(256):
            result = [sum(a * v for a in row) / 1024 for row in matrix]
            self.assertEqual(result, [v, 0, 0])

    def test_primary_colours_against_standard(self):
        matrix = c.bt601_q10_gbr()
        for rgb in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (37, 119, 203)]:
            r, g, b = rgb
            y = .299 * r + .587 * g + .114 * b
            ref = [y, (b - y) / 1.772, (r - y) / 1.402]
            actual = [sum(a * v for a, v in zip(row, (g, b, r))) / 1024 for row in matrix]
            for a, v in zip(actual, ref):
                self.assertLess(abs(a - v), .15)

    def test_signed_field_encoding_exhaustive(self):
        for v in range(-4096, 4096):
            word = c.pack_s13_pair(v, -v if v != -4096 else 4095)
            self.assertEqual(sign13(word & 8191), v)
            self.assertEqual(word & 0xe000e000, 0)

    def test_bad_matrix_values_and_shapes(self):
        for m in [[], [[0]*3]*2, [[0]*4]*3, [[4096, 0, 0]]*3, [[True, 0, 0]]*3]:
            with self.subTest(m=m), self.assertRaises(ValueError):
                c.matrix_words(m)

    def test_ccm_transpose_with_asymmetric_fixture(self):
        m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.assertEqual(c.matrix_words(m, True), [1 | 4 << 16, 7, 2 | 5 << 16, 8, 3 | 6 << 16, 9])

    def test_ccm_numerical_range_distinct_from_cst(self):
        for boundary in (-2048, 2047):
            m = [[0, 0, 0], [0, 0, 0], [0, 0, boundary]]
            words = c.matrix_words(m, transpose=True, coefficient_bits=12)
            self.assertEqual(sign13(words[-1]), boundary)
        for outside in (-2049, 2048):
            m = [[0, 0, 0], [0, 0, 0], [0, 0, outside]]
            with self.assertRaises(ValueError):
                c.matrix_words(m, transpose=True, coefficient_bits=12)
            self.assertEqual(sign13(c.matrix_words(m)[-1]), outside)
        config = c.generate("front")
        self.assertEqual(config["ccm"]["coefficient_range"], [-2048, 2047])
        self.assertEqual(config["cst"]["coefficient_range"], [-4096, 4095])

    def test_invalid_coefficient_range_policy(self):
        for bits in (11, 14, True, 12.0):
            with self.assertRaises(ValueError):
                c.matrix_words([[0] * 3] * 3, coefficient_bits=bits)

    def test_gamma_round_trip_and_endpoints(self):
        for curve in ("identity", "srgb"):
            points = c.gamma_points(curve)
            self.assertEqual((points[0], points[-1]), (0, 4095))
            words = c.gamma_words(points)
            for i, word in enumerate(words):
                delta = (word >> 12) & 4095
                if delta & 2048:
                    delta -= 4096
                self.assertEqual(word & 4095, points[i])
                self.assertEqual((word & 4095) + delta, points[i+1])
                self.assertGreaterEqual(delta, 0)
                self.assertEqual(word >> 24, 0)

    def test_srgb_midpoint(self):
        # Independent published sRGB midpoint: 0.5 linear -> ~0.735357 encoded.
        self.assertAlmostEqual(c.gamma_points("srgb")[128] / 4095, .735356983, delta=1/4095)

    def test_gamma_signed_negative_delta(self):
        self.assertEqual(c.gamma_words([100] + [99]*256)[0], 100 | 4095 << 12)

    def test_gamma_rejects_bad_inputs(self):
        bad = [[0]*256, [0]*256 + [4096], [0, 2048] + [2048]*255,
               [4095, 0] + [0]*255, [False]*257]
        for p in bad:
            with self.subTest(p=p[:3]), self.assertRaises(ValueError):
                c.gamma_words(p)

    def test_unity_mesh_neutral_and_reserved_bits(self):
        g = c.unity_lsc()
        self.assertEqual(len(g["red_green"]), 221)
        for word in g["red_green"] + g["blue_green"]:
            self.assertEqual(word & 8191, 1024)
            self.assertEqual((word >> 14) & 8191, 1024)
            self.assertEqual(word & 0xf8002000, 0)
        self.assertFalse(g["calibrated"])

    def test_bad_mesh_extents(self):
        for args in [(0, 13), (17, 65), (True, 13), (17.0, 13)]:
            with self.assertRaises(ValueError):
                c.unity_lsc(*args)

    def test_both_camera_modes_are_distinct(self):
        front, rear = c.generate("front"), c.generate("rear")
        self.assertEqual(front["source_mode"]["bayer_order"], "RGGB")
        self.assertEqual(rear["source_mode"]["width"], 4064)
        self.assertEqual(rear["source_mode"]["bayer_order"], "GRBG")
        self.assertNotEqual(front["nv12"], rear["nv12"])
        self.assertFalse(rear["complete_startup_profile"])

    def test_generator_has_no_runtime_inputs(self):
        for name in ("front", "rear"):
            a = c.dumps(c.generate(name))
            self.assertEqual(a, c.dumps(c.generate(name)))
            self.assertEqual(json.loads(a)["runtime_file_dependencies"], [])
            self.assertNotIn("/home/", a)
            self.assertNotIn("firmware", a)

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "open.json"
            cmd = [sys.executable, str(Path(c.__file__)), "--camera", "front", "--output", str(f)]
            subprocess.run(cmd, check=True, capture_output=True)
            old = f.read_bytes()
            p = subprocess.run(cmd, capture_output=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(f.read_bytes(), old)


if __name__ == "__main__":
    unittest.main(verbosity=2)
