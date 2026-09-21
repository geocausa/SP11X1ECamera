#!/usr/bin/env python3
"""E004kh strict text-only physical/front virtual-reader exact frame gate."""
from pathlib import Path
import runpy
import unittest

HERE=Path(__file__).resolve().parent
CHECK=runpy.run_path(str(HERE/"validate-front-rdi.py"))["check"]
RAW=10368000
NV12=3110400
def capture(n,bytes_used,start=0,gaps=()):
    values=[]
    seq=start
    for i in range(n):
        if i in gaps: seq+=gaps[i]
        values.append(f"cap dqbuf: {i%4} seq: {seq:6d} bytesused: {bytes_used} "
                      f"ts: {13.0+i/30:.6f} field: None\n")
        seq+=1
    return "".join(values)

SOURCE=capture(72,RAW)
RAW_METER=("E004KH_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=72 FULL_FRAMES=72 "
           "BYTES_IN=746496000 BYTES_OUT=746496000 "
           "INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF PIXELS_SAVED=NO\n")
CONVERT=("E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 "
         "OUTPUT=NV12_1920x1080 FRAMES=72 SRC_BYTES_PER_FRAME=10368000 "
         "DEST_BYTES_PER_FRAME=3110400 "
         "REAL_SENSOR_PROVEN_BY_CALLER=NO QC10C_DECODED=NO OEM_ISP_PARITY=NO\n")
VIRTUAL=capture(24,NV12,start=5,gaps={1:2})
NV12_METER=("E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=24 FULL_FRAMES=24 "
            "BYTES_IN=74649600 BYTES_OUT=74649600 "
            "INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF PIXELS_SAVED=NO\n")
APP=("E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=24 REQUESTED_FRAMES=24 "
     "INPUT_SHORTFALL_REASON=NONE SIZE=3110400 VIDEO=NV12_1920x1080_30 "
     "SINK_OBSERVED_FPS=29.2400 INTERARRIVAL_SAMPLES=23 "
     "DISTINCT_PAYLOADS_VERIFIED=YES SYNTHETIC_PTS_ONLY=YES "
     "LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO\n")


class FrontVirtual(unittest.TestCase):
    def test_complete_physical72_and_independent_v4l2_app24_pass_with_explicit_sequence_gaps(self):
        result=CHECK(SOURCE,RAW_METER,CONVERT,VIRTUAL,NV12_METER,APP,0,0)
        self.assertIn("E004KH_REAL_FRONT_1080P_STANDARD_V4L2_INDEPENDENT_APP=PASS",result)
        self.assertIn("independent_reader_missing_sequence_ids=2",result)
        self.assertIn("gstreamer_app_1080p_complete_frames=24",result)
        self.assertIn("QC10C_DECODED=NO",result)
        self.assertIn("SUSTAINED_30FPS_NOT_PROVEN=YES",result)

    def test_not_all_physical_frames_or_raw_bytes_reject(self):
        for source in (capture(71,RAW),capture(72,7778304),
                       SOURCE.replace("seq:      3","seq:     99",1)):
            with self.assertRaises(ValueError):
                CHECK(source,RAW_METER,CONVERT,VIRTUAL,NV12_METER,APP,0,0)
        for broken in (RAW_METER.replace("FULL_FRAMES=72","FULL_FRAMES=71"),
                       RAW_METER.replace("BYTES_OUT=746496000","BYTES_OUT=0")):
            with self.assertRaises(ValueError):
                CHECK(SOURCE,broken,CONVERT,VIRTUAL,NV12_METER,APP,0,0)

    def test_false_standard_video_claim_and_short_virtual_buffer_rejected(self):
        for bad in (capture(23,NV12),capture(24,7778304),
                    VIRTUAL.replace("bytesused: 3110400","bytesused: 3110399",1)):
            with self.assertRaises(ValueError):
                CHECK(SOURCE,RAW_METER,CONVERT,bad,NV12_METER,APP,0,0)

    def test_app_duplicate_or_partial_or_nonzero_subprocess_fails(self):
        for bad in (APP.replace("DISTINCT_PAYLOADS_VERIFIED=YES","DISTINCT_PAYLOADS_VERIFIED=NO"),
                    APP.replace("FRAMES=24 REQUESTED_FRAMES=24","FRAMES=23 REQUESTED_FRAMES=24"),
                    APP.replace("SIZE=3110400","SIZE=7778304")):
            with self.assertRaises(ValueError):
                CHECK(SOURCE,RAW_METER,CONVERT,VIRTUAL,NV12_METER,bad,0,0)
        for publisher,reader in ((124,0),(0,124)):
            with self.assertRaises(ValueError):
                CHECK(SOURCE,RAW_METER,CONVERT,VIRTUAL,NV12_METER,APP,publisher,reader)

    def test_validator_has_no_raw_pixel_or_device_mutation_interface(self):
        text=(HERE/"validate-front-rdi.py").read_text()
        for banned in ("/dev/video","media-ctl","modprobe","grub-reboot","O_CREAT",
                       "ILLUMINATION_ON","open(FOO"):
            self.assertNotIn(banned,text)
        self.assertIn("SOURCE_AND_APP_MEASUREMENT_WINDOWS_DIFFER=YES",text)


if __name__=="__main__":
    unittest.main()
