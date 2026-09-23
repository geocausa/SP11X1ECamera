#!/usr/bin/python3
import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).with_name("paired_source_validator.py")
sp=importlib.util.spec_from_file_location("paired_source_validator",p)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def lines(cam,frames=(1,30,90,180)):
 return "\n".join(
  f"E004MC_PAIRED_RAW_NV12 camera={cam} frame={i} raw_mean8=80.000 "
  f"raw_p95=80 raw_p99=80 raw_gt32=1.00000 nv12_y_mean=16.000 "
  f"nv12_y_p95=16 nv12_y_p99=16 nv12_y_gt32=0.00000 "
  f"source_bright_nv12_dark=1 raw_samples=32000 y_samples=8000 "
  f"raw8_upper_only=YES frame_pair=YES pixels_saved=NO"
  for i in frames)
class ProbeReportTests(unittest.TestCase):
 def test_both_cameras_parse(self):
  for cam in ("front","rear"):
   x=m.parse(lines(cam),cam)
   self.assertEqual(len(x),4)
   self.assertTrue(all(z["raw_p99"]==80 and z["nv12_y_p99"]==16 for z in x))
 def test_missing_or_duplicate_source_pairs_refused(self):
  with self.assertRaises(ValueError):m.parse(lines("front",(1,30,90)),"front")
  with self.assertRaises(ValueError):m.parse(lines("front",(1,30,90,90)),"front")
 def test_mismatch_and_pixel_saved_refused(self):
  with self.assertRaises(ValueError):m.parse(lines("rear"),"front")
  with self.assertRaises(ValueError):m.parse(lines("front").replace("pixels_saved=NO","pixels_saved=YES"),"front")
if __name__=="__main__":unittest.main()
