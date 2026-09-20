#!/usr/bin/env python3
"""E004jv: camera-free tests of independently timed bounded 4K app input."""
from pathlib import Path
import re
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
APP=HERE/"nv12-4k-sustained-app.py"
FRAME=3840*2160*3//2


class Long4kApp(unittest.TestCase):
    def run_app(self, frames, payload, timeout=25):
        return subprocess.run(["/usr/bin/python3",str(APP),"--frames",str(frames)],
                              input=payload,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,timeout=timeout)

    def test_three_different_synthetic_buffers_and_real_clock_metrics(self):
        # Offline source intentionally comes as fast as the host can supply it.
        # Neither the encoded frame PTS nor this test establishes real 4K30.
        frame=bytearray(bytes([128])*FRAME)
        data=bytearray()
        for first_y in (10,20,30):
            frame[0]=first_y
            data.extend(frame)
        p=self.run_app(3,data)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        msg=p.stderr.decode()
        self.assertIn("E004JV_NV12_APPSRC_CONSUMER=PASS FRAMES=3",msg)
        self.assertIn("INTERARRIVAL_SAMPLES=2",msg)
        self.assertIn("SAMPLED_FRAME_PAYLOAD_VARIATION=YES",msg)
        for field in ("SINK_OBSERVED_FPS","SINK_P95_INTERARRIVAL_MS",
                      "SINK_MAX_INTERARRIVAL_MS","PIPELINE_MS"):
            m=re.search(r"\b"+field+r"=([0-9]+(?:\.[0-9]+)?)",msg)
            self.assertIsNotNone(m,msg)
            self.assertGreater(float(m.group(1)),0.0,msg)
        self.assertIn("SYNTHETIC_PTS_ONLY=YES",msg)
        self.assertIn("LIVE_CAMERA_PROVEN=NO",msg)

    def test_fail_closed_truncated_and_excess(self):
        for data,token in ((b"x"*4096,b"truncated NV12"),
                           (bytes([128])*(FRAME+1),b"EXTRA_NV12_BYTES")):
            p=self.run_app(1,data)
            self.assertNotEqual(p.returncode,0)
            self.assertIn(token,p.stderr)

    def test_rejects_invalid_bounds_without_read(self):
        for count in (0,121,-1):
            p=self.run_app(count,b"")
            self.assertNotEqual(p.returncode,0)
            self.assertIn(b"FRAME_BOUND_MUST_BE_1_TO_120",p.stderr)

    def test_code_measures_sink_wall_clock_not_synthetic_pts(self):
        s=APP.read_text()
        self.assertIn("MAX_FRAMES = 120",s)
        self.assertIn("sink_arrival_ns.append(time.monotonic_ns())",s)
        self.assertIn("SINK_OBSERVED_FPS",s)
        self.assertIn("SYNTHETIC_PTS_ONLY=YES",s)
        for banned in ("/dev/video","insmod","modprobe","grub-reboot",
                       "media-ctl","BootNext","ILLUMINATION_ON"):
            self.assertNotIn(banned,s)


if __name__=="__main__":
    unittest.main()
