#!/usr/bin/env python3
"""E004kg fails closed on any fabricated front RDI / NV12 application proof."""
from pathlib import Path
import runpy
import unittest

HERE=Path(__file__).resolve().parent
AUDIT=runpy.run_path(str(HERE/"validate-front-rdi.py"))
CHECK=AUDIT["check"]
def source(n=8,bytes_used=10368000,seq_skip=False):
    return "".join(
      f"cap dqbuf: {i%4} seq: {i+(1 if seq_skip and i>3 else 0):6d} "
      f"bytesused: {bytes_used} ts: {10+i/29.95:.6f} field: None\n"
      for i in range(n))
METER=("E004KG_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=8 FULL_FRAMES=8 "
       "BYTES_IN=82944000 BYTES_OUT=82944000 INCOMPLETE_TAIL_BYTES=0 "
       "TERMINATION=EOF PIXELS_SAVED=NO\n")
CONVERT=("E004KE_FRONT_RDI_BAYER_TO_NV12=PASS "
         "SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 "
         "FRAMES=8 SRC_BYTES_PER_FRAME=10368000 DEST_BYTES_PER_FRAME=3110400 "
         "REAL_SENSOR_PROVEN_BY_CALLER=NO QC10C_DECODED=NO OEM_ISP_PARITY=NO\n")
APP=("E004KG_NV12_APPSRC_CONSUMER=PASS FRAMES=8 REQUESTED_FRAMES=8 "
     "INPUT_SHORTFALL_REASON=NONE SIZE=3110400 VIDEO=NV12_1920x1080_30 "
     "SINK_OBSERVED_FPS=29.6000 SINK_P95_INTERARRIVAL_MS=35.210 "
     "SINK_MAX_INTERARRIVAL_MS=36.004 INTERARRIVAL_SAMPLES=7 "
     "DISTINCT_PAYLOADS_VERIFIED=YES SYNTHETIC_PTS_ONLY=YES "
     "LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO\n")


class StrictFront(unittest.TestCase):
    def test_eight_full_raw_bytes_and_eight_distinct_1080p_app_output(self):
        report=CHECK(source(),METER,CONVERT,APP)
        self.assertIn("E004KG_REAL_FRONT_RDI_RAW10_TO_GSTREAMER_NV12_1080P=PASS",report)
        self.assertIn("source_hardware_timestamp_fps=",report)
        self.assertIn("app_nv12_1920x1080_frames=8",report)
        self.assertIn("VIRTUAL_WEBCAM_NOT_CREATED=YES",report)
        self.assertIn("QC10C_DECODED=NO",report)

    def test_seven_source_frames_and_bad_raw10_length_fail(self):
        for txt in (source(7),source(8,bytes_used=7778304),source(8,seq_skip=True)):
            with self.assertRaises(ValueError):
                CHECK(txt,METER,CONVERT,APP)

    def test_malformed_meter_fails(self):
        for wrong in ("BYTES_IN=82944000 BYTES_OUT=82944000",
                      "INCOMPLETE_TAIL_BYTES=0","TERMINATION=EOF","FULL_FRAMES=8"):
            with self.assertRaises(ValueError):
                CHECK(source(),METER.replace(wrong,"INVALID"),CONVERT,APP)

    def test_fake_app_bad_caps_and_missing_distinctness_fail(self):
        for bad in (APP.replace("DISTINCT_PAYLOADS_VERIFIED=YES",
                                "DISTINCT_PAYLOADS_VERIFIED=NO"),
                    APP.replace("FRAMES=8 REQUESTED_FRAMES=8",
                                "FRAMES=7 REQUESTED_FRAMES=8"),
                    APP.replace("SIZE=3110400 VIDEO=NV12_1920x1080_30",
                                "SIZE=7778304 VIDEO=QC10C_2560x1440")):
            with self.assertRaises(ValueError):
                CHECK(source(),METER,CONVERT,bad)

    def test_no_qc10c_decode_claim_or_real_video_device_pretense(self):
        check_source=(HERE/"validate-front-rdi.py").read_text()
        for forbidden in ("modprobe","grub-reboot","media-ctl","/dev/video",
                          "O_CREAT","fopen(","ILLUMINATION_ON"):
            self.assertNotIn(forbidden,check_source)
        self.assertIn("QC10C_DECODED=NO",check_source)
        self.assertIn("VIRTUAL_WEBCAM_NOT_CREATED=YES",check_source)


if __name__=="__main__":
    unittest.main()
