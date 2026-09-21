#!/usr/bin/env python3
"""E004kf byte-exact synthetic front RAW10->NV12->real GStreamer pipeline gate."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CONVERTER=ROOT/"experiments/E004-front-ir-vd55g0/e004ke-front-rdi-rggb-raw-bypass/front-rggb10p-to-nv12-1080.c"
AUDIT=HERE/"front-rdi-raw10-pipe-audit.c"
BIN="/tmp/sp11-e004kf-test-front-raw-audit"
CONV="/tmp/sp11-e004kf-test-front-nv12"


class FrontRawToApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for source,target,args in (
            (AUDIT,BIN,["-O2"]),
            (CONVERTER,CONV,["-O3","-fno-fast-math","-ffp-contract=off"])):
            r=subprocess.run(["gcc",*args,"-std=c11","-Wall","-Wextra",
                              "-Werror","-pedantic",str(source),"-o",target],
                             capture_output=True,text=True,timeout=25)
            if r.returncode:
                raise RuntimeError(r.stderr)

    def test_eight_independent_distinct_rg100_frames_to_gstreamer(self):
        generator=(
          "import sys\n"
          "out=sys.stdout.buffer\n"
          "for i in range(8):\n"
          " row0=bytes([100+i*7,90,100+i*7,90,0])*(3840//4)\n"
          " row1=bytes([90,40,90,40,0])*(3840//4)\n"
          " raw=(row0+row1)*1080\n"
          " assert len(raw)==10368000\n"
          " out.write(raw)\n"
          "out.flush()\n")
        pipeline=(
            "/usr/bin/python3 -c \"$1\" | \"$2\" --frames 8 --idle-ms 4500 | "
            "\"$3\" --frames 8 | /usr/bin/python3 \"$4\" --frames 8 "
            "--require-distinct --idle-seconds 5")
        p=subprocess.run(["bash","-o","pipefail","-c",pipeline,"bash",
                          generator,BIN,CONV,str(HERE/"front-1080p-app.py")],
                         capture_output=True,timeout=45)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"E004KF_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=8 FULL_FRAMES=8",p.stderr)
        self.assertIn(b"BYTES_IN=82944000 BYTES_OUT=82944000 INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF",p.stderr)
        self.assertIn(b"E004KE_FRONT_RDI_BAYER_TO_NV12=PASS",p.stderr)
        self.assertIn(b"OUTPUT=NV12_1920x1080 FRAMES=8",p.stderr)
        self.assertIn(b"E004KF_NV12_APPSRC_CONSUMER=PASS FRAMES=8 REQUESTED_FRAMES=8",p.stderr)
        self.assertIn(b"DISTINCT_PAYLOADS_VERIFIED=YES",p.stderr)
        self.assertIn(b"REAL_SENSOR_PROVEN_BY_CALLER=NO",p.stderr)

    def test_offline_does_not_claim_front_rdi_hardware_or_qc10c_decode(self):
        source=(HERE/"front-1080p-app.py").read_text()
        self.assertIn("LIVE_CAMERA_PROVEN=NO",source)
        self.assertIn("VIRTUAL_WEBCAM_CREATED=NO",source)
        c=CONVERTER.read_text()
        self.assertIn("QC10C_DECODED=NO",c)
        for forbidden in ("/dev/video","media-ctl","insmod","modprobe","grub-reboot",
                          "ILLUMINATION_ON","O_CREAT","fopen("):
            self.assertNotIn(forbidden,c)
            self.assertNotIn(forbidden,AUDIT.read_text())


if __name__=="__main__":
    unittest.main()
