#!/usr/bin/python3
"""No camera, no filesystem pixels: pure statistics test."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
p=Path(__file__).with_name("scene_probe.py")
spec=importlib.util.spec_from_file_location("scene_probe",p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class SceneProbeTests(unittest.TestCase):
    def test_near_black_does_not_falsely_claim_detail(self):
        y=np.full((480,640),16,dtype=np.uint8)
        s=mod.stats_from_y(y)
        self.assertEqual(s["mean_y"],16)
        self.assertEqual(s["p99_y"],16)
        self.assertEqual(s["spatial_tile_means_std_y"],0)
        self.assertEqual(s["fraction_y_above_32"],0)
    def test_tonal_spatial_scene(self):
        y=np.full((480,640),16,dtype=np.uint8)
        y[:240,:320]=100
        y[240:,320:]=70
        s=mod.stats_from_y(y)
        self.assertGreater(s["p99_y"],90)
        self.assertGreater(s["spatial_tile_means_std_y"],10)
        self.assertGreater(s["fraction_y_above_32"],.2)
    def test_invalid_input_refused(self):
        with self.assertRaises(ValueError):
            mod.stats_from_y(np.full((8,8),16,dtype=np.uint8))
        with self.assertRaises(ValueError):
            mod.stats_from_y(np.full((480,640),16,dtype=np.int32))
        with self.assertRaises(ValueError):
            mod.run("ir",90)
        with self.assertRaises(ValueError):
            mod.run("rear",0)
if __name__=="__main__":unittest.main()
