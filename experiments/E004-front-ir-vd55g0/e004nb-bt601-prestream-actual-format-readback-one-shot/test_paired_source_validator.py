#!/usr/bin/python3
"""Camera-free pre-/post-gain scalar paired source evidence tests."""
import importlib.util,json,tempfile
from pathlib import Path
from unittest import TestCase,main
p=Path(__file__).with_name("paired_source_validator.py")
sp=importlib.util.spec_from_file_location("paired_source_validator",p)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
FRAMES=(1,30,90,180,210,240,270,300,330,360)
def lines(cam,frames=FRAMES):
 return "\n".join(
  f"E004NB_PAIRED_RAW_NV12 camera={cam} frame={i} mono_ms={200000+i*10:.3f} "
  f"raw_mean8={80 if i>=240 else 16}.000 "
  f"raw_p95={80 if i>=240 else 16} raw_p99={80 if i>=240 else 16} "
  f"raw_gt32={1 if i>=240 else 0}.00000 nv12_y_mean={70 if i>=240 else 16}.000 "
  f"nv12_y_p95={70 if i>=240 else 16} nv12_y_p99={70 if i>=240 else 16} "
  f"nv12_y_gt32={1 if i>=240 else 0}.00000 "
  f"source_bright_nv12_dark=0 raw_samples=32000 y_samples=8000 "
  f"raw8_upper_only=YES frame_pair=YES pixels_saved=NO"
  for i in frames)
def trial(cam):
 return dict(baseline_controls={"exposure":3546 if cam=="front" else 1600,
                                "analogue_gain":0 if cam=="front" else 128,
                                "digital_gain":256 if cam=="front" else 1024},
             modified_controls={"exposure":3546 if cam=="front" else 3200,
                                "analogue_gain":512 if cam=="front" else 256,
                                "digital_gain":512 if cam=="front" else 2048},
             first_changed_ms=202000.,settled_ms=202100.,
             restore_started_ms=204000.,
             restored_controls={"exposure":3546 if cam=="front" else 1600,
                                "analogue_gain":0 if cam=="front" else 128,
                                "digital_gain":256 if cam=="front" else 1024},
             driver_supported_v4l2_controls_only=True,
             baseline_app={"p99_y":16},gain_changed_app={"p99_y":70},
             effect_on_app_p99_y=54.)
class ProbeReportTests(TestCase):
 def test_dual_camera_pre_post_gain_report(self):
  with tempfile.TemporaryDirectory(prefix="e004nb-offline-") as td:
   d=Path(td)
   for cam in ("front","rear"):
    (d/(cam+"-SERVICE-STDERR.txt")).write_text(lines(cam)+"\n")
   (d/"RGB-SELECTOR-ACCEPTANCE.json").write_text(json.dumps(dict(
     status="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K",
     gain_trials={c:trial(c) for c in ("front","rear")})))
   out=m.validate(d)
   self.assertTrue(out["camera_results"]["front"]["gain_response_measured_in_source"])
   self.assertEqual(out["camera_results"]["rear"]["raw_upper8_p99_delta"],64)
   self.assertFalse(out["visible_scene_or_windows_IQ_parity_proven"])
 def test_missing_or_duplicate_baseline_frames_refused(self):
  for frames in ((1,30,90), (1,30,90,90,180,210,240,270)):
   with self.assertRaises(ValueError):
    m.parse(lines("front",frames),"front")
 def test_wrong_camera_or_pixel_file_refused(self):
  with self.assertRaises(ValueError):m.parse(lines("rear"),"front")
  with self.assertRaises(ValueError):
   m.parse(lines("front").replace("pixels_saved=NO","pixels_saved=YES"),"front")
 def test_nonmonotonic_timestamp_refused(self):
  t=lines("front").replace("mono_ms=200900.000","mono_ms=200000.000")
  with self.assertRaises(ValueError):m.parse(t,"front")
if __name__=="__main__":main()
