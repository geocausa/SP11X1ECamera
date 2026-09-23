#!/usr/bin/env python3
"""No camera/images: exact synthetic front gain gate scalar log tests."""
import unittest
from validate_front_tone_live import parse

FRAMES=(1,30,90,180,600,630)
def line(frame,kind):
    is_gain=kind=="gain"
    p01,p50,p99=(30,34,61) if is_gain else (30,31,37)
    q01,q50,q99=(100,108,162) if is_gain else (p01,p50,p99)
    d=dict(frame=frame,seq=frame-1,applied=int(is_gain),
           p01=p01,p50=p50,p99=p99,
           output_p01=q01,output_p50=q50,output_p99=q99,
           uv_unchanged=1,optical_detail_calibrated="NO",
           source_RAW10_unchanged="YES")
    return "E004NH_FRONT_PREVIEW_TONE "+" ".join(f"{k}={v}" for k,v in d.items())
GOOD="\n".join(line(f,"gain" if f>=600 else "baseline") for f in FRAMES)
class FrontTimestampWordBoundaryTests(unittest.TestCase):
    def test_real_native_source_frame_token_parser_has_no_ascii_backspace(self):
        from pathlib import Path
        from validate_front_tone_live import __file__ as source_path
        text=Path(source_path).read_text()
        self.assertNotIn(chr(8),text)
        self.assertIn(chr(92)+"bframe=",text)
        import re
        actual="E004NH_PAIRED_RAW_NV12 camera=front frame=600 mono_ms=38471.846 raw_mean8=22.127"
        m=re.search(r"\bframe=(\d+) mono_ms=([0-9.]+)",actual)
        self.assertIsNotNone(m)
        self.assertEqual(m[1],"600")

class ParserTests(unittest.TestCase):
    def test_good(self):
        o=parse(GOOD)
        self.assertEqual(o[600]["output_p99"],162)
        self.assertEqual(o[1]["applied"],0)
    def test_fails_closed(self):
        for bad in (
             GOOD.replace("frame=600","frame=601"),
             GOOD.replace("frame=630","frame=600"),
             GOOD.replace("uv_unchanged=1","uv_unchanged=0"),
             GOOD.replace("source_RAW10_unchanged=YES",
                          "source_RAW10_unchanged=NO"),
             GOOD.replace("optical_detail_calibrated=NO",
                          "optical_detail_calibrated=YES"),
             GOOD.replace("output_p99=162","output_p99=110"),
             GOOD.replace("output_p01=100","output_p01=30"),
             GOOD.replace("applied=0","applied=1"),
             GOOD.replace("applied=1","applied=0"),
             GOOD.replace("p99=61","p99=99")):
            with self.subTest(bad=bad[:80]):
                with self.assertRaises(ValueError):
                    parse(bad)
if __name__=="__main__":
    unittest.main()
