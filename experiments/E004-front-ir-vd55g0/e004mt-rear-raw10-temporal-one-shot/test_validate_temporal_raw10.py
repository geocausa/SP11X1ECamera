#!/usr/bin/env python3
"""Pure source-only negative/positive tests: no camera device or pixel file."""
from __future__ import annotations
import unittest
from validate_temporal_raw10 import parse

def make(a,ma):
 v={"frame_a":a,"frame_b":a+1,"seq_a":a-1,"seq_b":a,
 "source_gap_ms":33.31,"monotonic_ms":ma,"blocks":11264,
 "mean_a":85.,"mean_b":85.01,"std_a":14.,"std_b":14.01,
 "tile_std_a":9.,"tile_std_b":9.1,"tile_corr":0.998,
 "delta_mean":0.01,"delta_abs_mean":2.1,"delta_rms":2.9,"tile_delta_rms":0.3,
 "exact_native_GRBG10":"YES","volatile_only":"YES",
 "calibrated_black":"NO","motion_flicker_excluded":"NO",
 "semantic_scene_detail":"UNPROVEN"}
 v.update({'frame_a':a,'monotonic_ms':ma})
 return 'E004MT_REAR_REAL_RAW10_TEMPORAL '+ ' '.join(f'{k}={value}' for k,value in v.items())
class Tests(unittest.TestCase):
 def setUp(self):self.s='\n'.join(make(a,1000+200*i) for i,a in enumerate((90,600,630)))
 def test_accept(self):
  rows=parse(self.s);self.assertEqual([x['frame_a'] for x in rows],[90,600,630]);self.assertEqual(rows[2]['blocks'],11264)
 def test_missing_duplicated_and_wrong_format(self):
  with self.assertRaises(ValueError):parse(self.s.splitlines()[1]+'\n'+self.s.splitlines()[2])
  with self.assertRaises(ValueError):parse(self.s+'\n'+self.s.splitlines()[0])
  with self.assertRaises(ValueError):parse(self.s.replace('exact_native_GRBG10=YES','exact_native_GRBG10=NO'))
 def test_wrong_sequence_and_gap_and_opaque_hash(self):
  for bad in (self.s.replace('seq_b=90','seq_b=91'),
              self.s.replace('source_gap_ms=33.31','source_gap_ms=500.1'),
              self.s.replace('tile_corr=0.998','tile_corr=1.01'),
              self.s.replace('mean_b=85.01','mean_b=nan'),
              self.s.replace('semantic_scene_detail=UNPROVEN','semantic_scene_detail=PROVEN'),
              self.s.replace('blocks=11264','blocks=10')):
   with self.assertRaises(ValueError):parse(bad)
if __name__=='__main__':unittest.main()
