#!/usr/bin/python3
import json, subprocess, unittest, runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
class DirectApp(unittest.TestCase):
 def call(self,*args):
  p=subprocess.run(['/usr/bin/python3',str(HERE/'direct-camera-app.py'),*args],capture_output=True,text=True,timeout=15)
  return p,json.loads(p.stdout.splitlines()[-1])
 def test_real_gstreamer_synthetic_front_and_rear(self):
  for camera,size in [('front',3110400),('rear',12441600)]:
   p,r=self.call('--camera',camera,'--frames','24','--require-distinct')
   self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertEqual(r['complete_bytes'],24*size)
   self.assertTrue(r['all_payloads_distinct']);self.assertTrue(r['normal_eos'])
 def test_duplicate_frames_rejected(self):
  p,r=self.call('--camera','front','--frames','3','--source','constant','--require-distinct')
  self.assertNotEqual(p.returncode,0);self.assertEqual(r['distinct_payloads'],1)
 def test_live_on_golden_refused_before_device_access(self):
  p,r=self.call('--camera','rear','--frames','1','--source','device')
  self.assertNotEqual(p.returncode,0);self.assertIn('REQUIRES_NEW_E004KM',r['error'])
 def test_quality_statistics_known_planes(self):
  m=runpy.run_path(str(HERE/'direct-camera-app.py'))
  y=bytes([100])*64*64;u=bytes([120])*32*32;v=bytes([140])*32*32
  q=m['quality'](y+u+v,64,64)
  self.assertEqual((q['y_mean'],q['u_mean'],q['v_mean']),(100,120,140))
  self.assertEqual(q['y_zero_fraction'],0);self.assertEqual(q['y_255_fraction'],0)
 def test_frame_and_deadline_bounds(self):
  for args in [('--frames','0'),('--frames','2401'),('--frames','1','--deadline-seconds','241')]:
   p,r=self.call('--camera','front',*args);self.assertNotEqual(p.returncode,0)
if __name__=='__main__':unittest.main()
