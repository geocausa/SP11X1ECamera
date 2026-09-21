#!/usr/bin/env python3
"""E004kh synthetic full 1080p NV12 stdout->real GStreamer appsink test."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
BIN=Path("/tmp/sp11-e004kh-test-front-nv12-1080p-meter")
FRAME=1920*1080*3//2

class Front1080pVirtual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=subprocess.run(["gcc","-O2","-std=c11","-Wall","-Wextra",
                          "-Werror","-pedantic",str(HERE/"front-nv12-1080p-pipe-audit.c"),
                          "-o",str(BIN)],capture_output=True,text=True,timeout=20)
        if p.returncode:raise RuntimeError(p.stderr)

    def test_twenty_four_bytewise_distinct_complete_1080p_buffers_reach_real_gstreamer(self):
        generator=(
            "import sys\n"
            "f=bytearray([100])*(1920*1080*3//2)\n"
            "for i in range(24):\n"
            " f[100]=i\n"
            " sys.stdout.buffer.write(f)\n"
            "sys.stdout.buffer.flush()\n")
        p=subprocess.run(["bash","-o","pipefail","-c",
                          "/usr/bin/python3 -c \"$1\" | \"$2\" --frames 24 --idle-ms 4500 "
                          "| /usr/bin/python3 \"$3\" --frames 24 --require-distinct --idle-seconds 5",
                          "bash",generator,str(BIN),str(HERE/"front-1080p-app.py")],
                         capture_output=True,timeout=40)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=24 FULL_FRAMES=24",p.stderr)
        self.assertIn(b"BYTES_IN=74649600 BYTES_OUT=74649600 INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF",p.stderr)
        self.assertIn(b"E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=24 REQUESTED_FRAMES=24",p.stderr)
        self.assertIn(b"DISTINCT_PAYLOADS_VERIFIED=YES",p.stderr)
        self.assertIn(b"VIRTUAL_WEBCAM_CREATED=NO",p.stderr)

    def test_repeated_1080p_frames_fail_app_24_distinctness(self):
        raw=bytes([91])*FRAME
        p=subprocess.run(["/usr/bin/python3",str(HERE/"front-1080p-app.py"),
                          "--frames","3","--require-distinct","--idle-seconds","2"],
                         input=raw*3,capture_output=True,timeout=20)
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b"E004KH_OUTPUT_FRAMES_NOT_DISTINCT",p.stderr)

    def test_extra_or_short_nv12_meter_payload_fail_closed(self):
        for data in (bytes([111])*(FRAME-1), bytes([111])*(FRAME+1)):
            p=subprocess.run([str(BIN),"--frames","1","--idle-ms","800"],
                             input=data,capture_output=True,timeout=8)
            self.assertNotEqual(p.returncode,0)
            self.assertNotIn(b"E004KH_NV12_1080P_PIPE=PASS",p.stderr)

if __name__=="__main__":
    unittest.main()
