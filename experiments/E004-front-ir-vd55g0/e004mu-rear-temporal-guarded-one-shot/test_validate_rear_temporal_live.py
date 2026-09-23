#!/usr/bin/env python3
"""Pure fake logs: fail closed without imaging hardware/photograph."""
from __future__ import annotations
import unittest
from validate_rear_temporal_live import parse

def rec(f:int)->str:
    tone=int(f>180)
    filtered=tone
    d=dict(frame=f,seq=f-1,tone=tone,seeded=0,filtered=filtered,
           reset_scene=0,reset_seq=0,reset_tone=int(not tone),
           median=142 if tone else 30,blocks_filtered=1700000 if tone else 0,
           blocks_bypassed=0,pixels_changed=10000 if tone else 0,
           sample_count=8100 if tone else 0,
           unfiltered_consecutive_RMS=4.5 if tone else 0.0,
           input_to_previous_filtered_RMS=3.2 if tone else 0.0,
           output_to_previous_filtered_RMS=1.6 if tone else 0.0,
           sampled_global_abs_delta=2.3 if tone else 0.0,
           sampled_high_motion_fraction=0.01 if tone else 0.0,
           uv_unchanged=1,motion_detail_calibrated="NO",
           prior_Y_buffers_volatile_only="YES")
    return "E004MU_REAR_LIVE_TEMPORAL "+" ".join(str(k)+"="+str(v) for k,v in d.items())
FRAMES=(1,30,90,180,600,601,610,630,631,640,650)
GOOD="\n".join(rec(f) for f in FRAMES)+"\nE004MU_REAR_LIVE_TEMPORAL_FINAL filtered_frames=90 paired_before_after_frames=90 filter_cpu_mean_ms=6.2 all_private_Y_histories_cleared=YES optical_pixels_saved=NO"
class Tests(unittest.TestCase):
    def test_good(self):
        out=parse(GOOD)
        self.assertEqual(out["filtered_frames"],90)
        self.assertEqual(out["records"][630]["unfiltered_consecutive_RMS"],4.5)
    def test_fail_closed(self):
        for s in (
           GOOD.replace("uv_unchanged=1","uv_unchanged=0"),
           GOOD.replace("E004MU_REAR_LIVE_TEMPORAL frame=601","IGNORED frame=601"),
           GOOD.replace("output_to_previous_filtered_RMS=1.6","output_to_previous_filtered_RMS=4.7"),
           GOOD.replace("all_private_Y_histories_cleared=YES","all_private_Y_histories_cleared=NO"),
           GOOD.replace("filtered_frames=90","filtered_frames=2"),
           GOOD.replace("filter_cpu_mean_ms=6.2","filter_cpu_mean_ms=35.1"),
           GOOD.replace("reset_tone=0","reset_tone=1"),
           GOOD.replace("sample_count=8100","sample_count=0"),
           GOOD.replace("motion_detail_calibrated=NO","motion_detail_calibrated=YES")):
            with self.assertRaises(ValueError):parse(s)
if __name__=="__main__":unittest.main()
