#!/usr/bin/env python3
"""E004jx: source-only incomplete app sink cadence without saving optical pixels."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
APP=HERE/"nv12-4k-partial-telemetry-app.py"
BYTES=3840*2160*3//2


def run_app(n:int, payload:bytes, idle:float=0.5):
    return subprocess.run(["/usr/bin/python3",str(APP),"--frames",str(n),
                           "--idle-seconds",str(idle)],
                          input=payload,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=20)


class PartialSink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.static=bytes([128])*BYTES

    def test_all_frames_real_sink_callback_and_synthetic_pts_disclaimer(self):
        frame=bytearray(self.static)
        payload=bytearray()
        for value in (11,22,33):
            frame[0]=value
            payload.extend(frame)
        p=run_app(3,payload)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        for part in (b"E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=3 REQUESTED_FRAMES=3",
                     b"INPUT_SHORTFALL_REASON=NONE",
                     b"INTERARRIVAL_SAMPLES=2",
                     b"SAMPLED_FRAME_PAYLOAD_VARIATION=YES",
                     b"SINK_OBSERVED_FPS=",
                     b"SYNTHETIC_PTS_ONLY=YES",
                     b"LIVE_CAMERA_PROVEN=NO"):
            self.assertIn(part,p.stderr)

    def test_upstream_early_eof_preserves_partial_arrival_stats(self):
        p=run_app(3,self.static*2)
        self.assertEqual(p.returncode,1,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        for part in (b"E004JX_NV12_APPSRC_CONSUMER=PARTIAL FRAMES=2 REQUESTED_FRAMES=3",
                     b"INPUT_SHORTFALL_REASON=INPUT_EOF_OFFSET_0",
                     b"INTERARRIVAL_SAMPLES=1",
                     b"SINK_OBSERVED_FPS="):
            self.assertIn(part,p.stderr)

    def test_stalled_upstream_open_pipe_reports_partial_before_timeout(self):
        p=subprocess.Popen(["/usr/bin/python3",str(APP),"--frames","3",
                            "--idle-seconds","0.2"],stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            p.stdin.write(self.static*2)
            p.stdin.flush()
            code=p.wait(timeout=12)
            out=p.stdout.read()
            err=p.stderr.read()
            self.assertEqual(code,1,err.decode())
            self.assertEqual(out,b"")
            self.assertIn(b"PARTIAL FRAMES=2 REQUESTED_FRAMES=3",err)
            self.assertIn(b"INPUT_SHORTFALL_REASON=INPUT_IDLE_TIMEOUT_OFFSET_0",err)
            self.assertIn(b"SINK_OBSERVED_FPS=",err)
        finally:
            if p.poll() is None:
                p.kill()
                p.wait(timeout=4)
            for pipe in (p.stdin, p.stdout, p.stderr):
                if pipe is not None and not pipe.closed:
                    pipe.close()

    def test_progress_line_persists_before_eos(self):
        p=run_app(10,self.static*10)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertIn(b"E004JX_APP_PROGRESS SINK_FRAMES=10 WALL_FPS=",p.stderr)
        self.assertIn(b"FRAMES=10 REQUESTED_FRAMES=10",p.stderr)

    def test_refuses_invalid_count_and_idle_and_extra_input(self):
        for n,idle in ((0,0.5),(121,0.5),(1,0.01),(1,16.0)):
            p=run_app(n,b"",idle)
            self.assertNotEqual(p.returncode,0)
            self.assertIn(b"FAIL",p.stderr)
        p=run_app(1,self.static+b"x")
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b"EXTRA_NV12_BYTES",p.stderr)

    def test_strictly_no_hardware_stream_boot_or_image_exports(self):
        text=APP.read_text()
        for banned in ("/dev/video","media-ctl","grub-reboot",
                       "insmod","modprobe","BootNext","ILLUMINATION_ON"):
            self.assertNotIn(banned,text)
        self.assertIn("time.monotonic_ns()",text)
        self.assertIn("selectors.DefaultSelector()",text)
        self.assertIn("E004JX_APP_PROGRESS",text)


if __name__=="__main__":
    unittest.main()
