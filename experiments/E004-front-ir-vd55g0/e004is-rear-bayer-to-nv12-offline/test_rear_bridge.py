#!/usr/bin/env python3
"""E004is: offline rear Bayer bit order, tile proxy, source isolation tests."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
CODE=HERE/"rear-bayer-nv12-proxy.py"
M=runpy.run_path(str(CODE))
REAL=REPO/"experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw"

def frame_fixture(w=8,h=4,stride=16):
    # SGRBG mosaic = G R / B G; expected tile RGB 200/100/50
    raw=np.zeros((h,w),dtype=np.uint16)
    raw[0::2,0::2]=400
    raw[0::2,1::2]=800
    raw[1::2,0::2]=200
    raw[1::2,1::2]=400
    return raw,M["pack_grbg10p"](raw,stride=stride)

class RearTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(prefix="sp11-e004is-test-")
        self.addCleanup(self.td.cleanup)
        self.d=Path(self.td.name)

    def test_exact_v4l2_mipi_packing_low_bits(self):
        row=np.array([[0,1,2,1023]],dtype=np.uint16)
        payload=M["pack_grbg10p"](np.vstack([row,row]),stride=16)
        self.assertEqual(list(payload[:5]),[0,0,0,255,228])
        np.testing.assert_array_equal(M["unpack_grbg10p"](payload,width=4,height=2,stride=16),
                                      np.vstack([row,row]))

    def test_grbg_2x2_tile_rgb_and_nv12_chroma_order(self):
        raw,payload=frame_fixture()
        np.testing.assert_array_equal(M["unpack_grbg10p"](payload,width=8,height=4,stride=16),raw)
        frame=M["preview_nv12_from_grbg10p"](payload,width=8,height=4,stride=16,
                                               out_width=4,out_height=2)
        self.assertEqual(len(frame),12)
        reference=Image.new("RGB",(4,2),(200,100,50)).convert("YCbCr").getpixel((0,0))
        self.assertEqual(frame[:8],bytes([reference[0]]*8))
        self.assertEqual(frame[8:],bytes([reference[1],reference[2],
                                            reference[1],reference[2]]))

    def test_reject_short_long_or_bad_stride(self):
        _,payload=frame_fixture()
        for bad in (payload[:-1],payload+b"0"):
            with self.assertRaises(ValueError):
                M["unpack_grbg10p"](bad,width=8,height=4,stride=16)
        with self.assertRaises(ValueError):
            M["unpack_grbg10p"](payload,width=8,height=4,stride=10)
        with self.assertRaises(ValueError):
            M["preview_nv12_from_grbg10p"](payload,width=8,height=4,stride=16,
                                             out_width=8,out_height=2)

    def test_reject_relabelled_qc10c_as_rear_bayer(self):
        with self.assertRaises(ValueError):
            M["unpack_grbg10p"](bytes(7778304))
        with self.assertRaises(ValueError):
            M["unpack_grbg10p"](bytes(5529600))

    def test_reject_link_existing_or_unconfined_destination(self):
        dst=self.d/"already-there"
        dst.mkdir()
        with self.assertRaises(FileExistsError):
            M["private_destination"](dst)
        link=self.d/"alias"
        link.symlink_to(dst,target_is_directory=True)
        with self.assertRaises(FileExistsError):
            M["private_destination"](link)
        with self.assertRaises(ValueError):
            M["private_destination"](Path("/var/tmp/not-private-e004is"))
        with self.assertRaises(ValueError):
            M["private_destination"](Path("/tmp/../../etc/e004is"))

    def test_reject_input_symlink(self):
        f=self.d/"frame"
        f.write_bytes(b"small")
        alias=self.d/"alias"
        alias.symlink_to(f)
        with self.assertRaises(ValueError):
            M["check_input"](alias)
        with self.assertRaises(ValueError):
            M["check_input"](f)

    def test_real_rear_colorbar_archive_to_nv12_exact_payload(self):
        self.assertTrue(REAL.is_file())
        self.assertEqual(REAL.stat().st_size,M["FRAME_BYTES"])
        self.assertEqual(hashlib.sha256(REAL.read_bytes()).hexdigest(),M["REFERENCE_SHA"])
        out=self.d/"rear-private"
        cp=subprocess.run([sys.executable,str(CODE),"--input",str(REAL),
                           "--output-dir",str(out),"--reference-colorbar"],
                          capture_output=True,text=True,timeout=75)
        self.assertEqual(cp.returncode,0,cp.stderr[-500:])
        result=json.loads(cp.stdout)
        payload=(out/"rear-proxy-1920x1080.nv12").read_bytes()
        self.assertEqual(len(payload),3110400)
        self.assertEqual(result["output_sha256"],hashlib.sha256(payload).hexdigest())
        self.assertFalse(result["real_time_performance_proven"])
        self.assertFalse(result["colour_calibrated"])
        self.assertGreater(len(set(payload[:10000])),1)
        self.assertEqual((out.stat().st_mode&0o777),0o700)
        self.assertEqual(((out/"rear-proxy-1920x1080.nv12").stat().st_mode&0o777),0o600)
        self.assertEqual(hashlib.sha256(REAL.read_bytes()).hexdigest(),M["REFERENCE_SHA"])

    def test_previous_real_rear_colourbar_gstreamer_nv12_pipeline(self):
        # Parse a real archived rear frame through the ordinary Linux raw
        # NV12 processing stack, without opening any camera or video sink.
        self.assertTrue(REAL.is_file())
        out=self.d/"rear-gstreamer"
        cp=subprocess.run([sys.executable,str(CODE),"--input",str(REAL),
                           "--output-dir",str(out),"--reference-colorbar"],
                          capture_output=True,text=True,timeout=75)
        self.assertEqual(cp.returncode,0,cp.stderr[-500:])
        raw=out/"rear-proxy-1920x1080.nv12"
        self.assertEqual(raw.stat().st_size,3110400)
        cp=subprocess.run(["gst-launch-1.0","-q",
            "filesrc",f"location={raw}",
            "!","rawvideoparse","format=nv12","width=1920","height=1080",
            "framerate=30/1","!",
            "video/x-raw,format=NV12,width=1920,height=1080","!",
            "videoconvert","!","fakesink","sync=false"],
            capture_output=True,text=True,timeout=35)
        self.assertEqual(cp.returncode,0,cp.stderr[-700:])

    def test_wrong_reference_sha_rejected_without_partial_output(self):
        frame=self.d/"fake-frame"
        frame.write_bytes(bytes(M["FRAME_BYTES"]))
        out=self.d/"should-not-exist"
        cp=subprocess.run([sys.executable,str(CODE),"--input",str(frame),
                           "--output-dir",str(out),"--reference-colorbar"],
                          capture_output=True,text=True,timeout=25)
        self.assertNotEqual(cp.returncode,0)
        self.assertFalse(out.exists())

if __name__=="__main__":unittest.main(verbosity=2)
