#!/usr/bin/env python3
"""Real previous scalar-only archived logs, redacted temporary event labels.

No camera, user image pixels/RAW/photos/thumbs/hash, sensor mutations.
No E004ng original full physical run is claimed from E004nd text data.
"""
import json,tempfile,unittest
from pathlib import Path
from validate_screen_scene_live import parse_tone,validate
ROOT=Path(__file__).resolve().parent.parent
OLDER=ROOT/"e004nd-new-screen-scene-linux-rear-4k-one-shot"/"evidence"
FILES=("RGB-SELECTOR-ACCEPTANCE.json","front-SERVICE-STDERR.txt",
       "rear-SERVICE-STDERR.txt","FRONT-DAYLIGHT-PROBE.json",
       "FRONT-GAIN-PROBE.json","REAR-DAYLIGHT-PROBE.json",
       "REAR-GAIN-PROBE.json")
class PriorRealScalarTextOnly(unittest.TestCase):
 def with_old(self, mutation=None):
  with tempfile.TemporaryDirectory(prefix="sp11-screen-test-nonoptical-") as tmp:
   p=Path(tmp)
   for name in FILES:
    text=(OLDER/name).read_text()
    if name.endswith(".txt"):text=text.replace("E004ND_","E004NG_")
    if mutation and name==mutation[0]:text=text.replace(mutation[1],mutation[2],1)
    (p/name).write_text(text)
   return validate(p)
 def test_prior_real_screen_scene_scalar_only_passes_not_new_physical_run(self):
  v=self.with_old()
  self.assertEqual(v["status"],
     "PASS_E004NG_REAL_NEW_SCREEN_REAR_NONFLAT_SAFE_TONE_BYPASS_FRONT_REAR_UID1000_NATIVE_29FPS")
  self.assertFalse(v["new_rear_scene_screen_identity_or_actual_text_recognized"])
  self.assertFalse(v["actual_recognizable_screen_detail_colour_chart_white_balance_SNR_Windows_ISP_parity_proven"])
 def test_requires_real_contrast_source_no_invented_lift(self):
  for original,replaced in (
   ("frame=600 applied=0 input_p01=30 input_p50=32 input_p99=141",
    "frame=600 applied=0 input_p01=30 input_p50=32 input_p99=37"),
   ("frame=630 applied=0 input_p01=30 input_p50=32 input_p99=141",
    "frame=630 applied=1 input_p01=30 input_p50=32 input_p99=141"),
   ("frame=600 seq=599 tone=0 seeded=0 filtered=0",
    "frame=600 seq=599 tone=0 seeded=0 filtered=1"),
   ('"source_sequence_gaps":0','"source_sequence_gaps":1')
  ):
   with self.subTest(changed=original[:44]):
    with self.assertRaises(ValueError):
     self.with_old(("rear-SERVICE-STDERR.txt",original,replaced))
 def test_no_normal_user_app_or_control_restore(self):
  with self.assertRaises(ValueError):
   self.with_old(("REAR-GAIN-PROBE.json",'"effective_uid": 1000','"effective_uid": 0'))
  with self.assertRaises(ValueError):
   self.with_old(("RGB-SELECTOR-ACCEPTANCE.json",'"digital_gain": 1024','"digital_gain": 999'))
 def test_safe_front_bypass_never_invents_brightness(self):
  with self.assertRaises(ValueError):
   self.with_old(("front-SERVICE-STDERR.txt",
     "frame=600 seq=599 applied=0 p01=30 p50=31 p99=34 output_p01=30",
     "frame=600 seq=599 applied=0 p01=30 p50=31 p99=34 output_p01=120"))
 def test_wrong_format_or_duplicate_frame_not_accepted(self):
  src=(OLDER/"rear-SERVICE-STDERR.txt").read_text().replace("E004ND_","E004NG_")
  d=parse_tone(src,"rear")
  self.assertEqual(d[600]["input_p99"],141)
  entry=[x for x in src.splitlines() if x.startswith("E004NG_REAR_PREVIEW_TONE frame=600")][0]
  with self.assertRaises(ValueError):parse_tone(src+"\n"+entry,"rear")

if __name__=="__main__":unittest.main()
