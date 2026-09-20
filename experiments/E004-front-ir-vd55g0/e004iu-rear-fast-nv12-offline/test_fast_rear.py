#!/usr/bin/env python3
"""E004iu: real archived rear frame, synthetic Bayer colour, and fail-closed IO."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
FILE=HERE/"rear-fast-bridge.py"
SPEC=importlib.util.spec_from_file_location("rear_fast_bridge",FILE)
BRIDGE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BRIDGE)
REAL=REPO/"experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw"

class FastRearTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="sp11-e004iu-test-",dir="/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.directory=Path(self.tmp.name)

    def run_bridge(self,source:Path,out:Path,*,reference=False,sanitizer=False):
        args=[sys.executable,str(FILE),"--input",str(source),"--output",str(out)]
        if reference:args.append("--reference-colorbar")
        if sanitizer:args.append("--sanitizer")
        return subprocess.run(args,capture_output=True,text=True,timeout=70)

    def synthetic(self,filename="synthetic-grbg10p.raw"):
        # 10-bit SGRBG10P: high 8-bit samples, low two bits are zero.
        # Every 2x2 GRBG tile yields RGB=(200,100,50) exactly.
        image=np.zeros((2806,5104),dtype=np.uint8)
        groups=image[:,:5095].reshape(2806,1019,5)
        groups[0::2,:,0]=100
        groups[0::2,:,1]=200
        groups[0::2,:,2]=100
        groups[0::2,:,3]=200
        groups[1::2,:,0]=50
        groups[1::2,:,1]=100
        groups[1::2,:,2]=50
        groups[1::2,:,3]=100
        path=self.directory/filename
        path.write_bytes(image.tobytes())
        return path

    def test_previous_real_rear_colorbar_binary_and_gstreamer(self):
        self.assertEqual(hashlib.sha256(REAL.read_bytes()).hexdigest(),BRIDGE.EXAMPLE_SHA)
        out=self.directory/"reference.nv12"
        r=self.run_bridge(REAL,out,reference=True)
        self.assertEqual(r.returncode,0,r.stderr[-700:])
        evidence=json.loads(r.stdout)
        self.assertEqual(evidence["output_bytes"],3110400)
        self.assertEqual(evidence["output_sha256"],
                         "86f496416883d7728675802c70a0c83adb10d1a02591a56de1fe45cc3e223d0b")
        self.assertFalse(evidence["live_30fps_pipeline_proven"])
        self.assertFalse(evidence["colour_calibrated"])
        self.assertEqual(out.stat().st_size,3110400)
        self.assertEqual(out.stat().st_mode&0o777,0o600)
        gst=subprocess.run(["gst-launch-1.0","-q","filesrc",f"location={out}",
                "!","rawvideoparse","format=nv12","width=1920",
                "height=1080","framerate=30/1","!",
                "video/x-raw,format=NV12,width=1920,height=1080",
                "!","videoconvert","!","fakesink","sync=false"],
                capture_output=True,text=True,timeout=35)
        self.assertEqual(gst.returncode,0,gst.stderr[-500:])
        self.assertEqual(hashlib.sha256(REAL.read_bytes()).hexdigest(),BRIDGE.EXAMPLE_SHA)

    def test_known_grbg_synthetic_tile_rgb_to_y_uv(self):
        src=self.synthetic()
        out=self.directory/"synthetic.nv12"
        r=self.run_bridge(src,out)
        self.assertEqual(r.returncode,0,r.stderr[-700:])
        data=np.fromfile(out,dtype=np.uint8)
        self.assertEqual(len(data),3110400)
        # integer Y (77r+150g+29b+128)>>8, chroma after four-pixel mean
        y=(77*200+150*100+29*50+128)>>8
        u=128+((-43*200-85*100+128*50+128)>>8)
        v=128+((128*200-107*100-21*50+128)>>8)
        self.assertTrue(np.all(data[:2073600]==y))
        self.assertTrue(np.all(data[2073600::2]==u))
        self.assertTrue(np.all(data[2073601::2]==v))
        self.assertEqual((y,u,v),(124,86,182))

    def test_compiled_helper_asan_ubsan_on_previous_rear_frame(self):
        r=self.run_bridge(REAL,self.directory/"sanitized.nv12",
                          reference=True,sanitizer=True)
        self.assertEqual(r.returncode,0,r.stderr[-1000:])

    def test_wrong_front_qc10c_byte_length_rejected(self):
        f=self.directory/"fake-qc10c"
        f.write_bytes(bytes(7778304))
        out=self.directory/"not-created.nv12"
        r=self.run_bridge(f,out)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(out.exists())

    def test_partial_rear_frame_rejected(self):
        f=self.directory/"short"
        f.write_bytes(bytes(14321823))
        out=self.directory/"not-created.nv12"
        r=self.run_bridge(f,out)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(out.exists())

    def test_source_symlink_rejected(self):
        alias=self.directory/"source-alias"
        alias.symlink_to(REAL)
        out=self.directory/"not-created.nv12"
        r=self.run_bridge(alias,out)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(out.exists())

    def test_existing_output_preserved(self):
        f=self.synthetic()
        out=self.directory/"already-there.nv12"
        out.write_bytes(b"do not overwrite")
        r=self.run_bridge(f,out)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(out.read_bytes(),b"do not overwrite")

    def test_destination_symlink_preserved(self):
        f=self.synthetic()
        original=self.directory/"original"
        original.write_bytes(b"original")
        link=self.directory/"symlink"
        link.symlink_to(original)
        r=self.run_bridge(f,link)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(original.read_bytes(),b"original")
        self.assertTrue(link.is_symlink())

    def test_insecure_destination_parent_rejected(self):
        f=self.synthetic()
        out=Path("/tmp")/"direct-unsafe-e004iu-test.nv12"
        self.assertFalse(out.exists())
        r=self.run_bridge(f,out)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(out.exists())

    def test_reject_false_reference_flag_on_arbitrary_frame(self):
        f=self.synthetic()
        out=self.directory/"bad-reference.nv12"
        r=self.run_bridge(f,out,reference=True)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(out.exists())

    def test_four_frame_bounded_batch_one_compiled_helper(self):
        source=self.synthetic()
        single=self.directory/"single.nv12"
        sr=self.run_bridge(source,single)
        self.assertEqual(sr.returncode,0,sr.stderr[-400:])
        one=single.read_bytes()
        stream=self.directory/"four-frames.raw"
        with stream.open("xb") as dst:
            with source.open("rb") as src:
                block=src.read()
            for _ in range(4):
                dst.write(block)
        output=self.directory/"four-frame-stream.nv12"
        r=subprocess.run([sys.executable,str(FILE),"--input",str(stream),
                          "--output",str(output),"--frames","4"],
                         capture_output=True,text=True,timeout=80)
        self.assertEqual(r.returncode,0,r.stderr[-700:])
        evidence=json.loads(r.stdout)
        self.assertEqual(evidence["frames"],4)
        self.assertEqual(evidence["source_bytes"],4*BRIDGE.REAR_BYTES)
        self.assertEqual(evidence["output_bytes"],4*BRIDGE.NV12_BYTES)
        self.assertEqual(evidence["output_sha256"],
                         hashlib.sha256(one*4).hexdigest())
        self.assertEqual(output.read_bytes(),one*4)
        self.assertGreater(evidence["c_average_batch_io_and_conversion_ms_excluding_compile"],0)
        self.assertFalse(evidence["live_30fps_pipeline_proven"])
        # The data path is a normal four-frame NV12 video stream, not a
        # fourfold byte count masquerading as a single frame.
        gst=subprocess.run(["gst-launch-1.0","-q",
            "filesrc",f"location={output}",
            "!","rawvideoparse","format=nv12","width=1920","height=1080",
            "framerate=30/1","!",
            "video/x-raw,format=NV12,width=1920,height=1080","!",
            "videoconvert","!","fakesink","sync=false"],
            capture_output=True,text=True,timeout=35)
        self.assertEqual(gst.returncode,0,gst.stderr[-500:])

    def test_two_different_frames_preserve_order_without_stale_buffer(self):
        a=self.synthetic("red-blue-first.raw")
        second=self.synthetic("red-blue-second.raw")
        mutable=bytearray(second.read_bytes())
        # Change the red high byte in each packed four-pixel group, both
        # rows. The second image must NOT accidentally reuse first frame.
        raw=np.frombuffer(mutable,dtype=np.uint8).reshape(2806,5104)
        groups=raw[:,:5095].reshape(2806,1019,5)
        groups[0::2,:,1]=80
        groups[0::2,:,3]=80
        second.write_bytes(mutable)
        first_out=self.directory/"first.nv12"
        second_out=self.directory/"second.nv12"
        for source,out in ((a,first_out),(second,second_out)):
            r=self.run_bridge(source,out)
            self.assertEqual(r.returncode,0,r.stderr[-700:])
        first_bytes=first_out.read_bytes()
        second_bytes=second_out.read_bytes()
        self.assertNotEqual(hashlib.sha256(first_bytes).digest(),
                            hashlib.sha256(second_bytes).digest())
        combined=self.directory/"two-different-frames.raw"
        with combined.open("xb") as stream:
            stream.write(a.read_bytes())
            stream.write(second.read_bytes())
        dest=self.directory/"two-frames.nv12"
        r=subprocess.run([sys.executable,str(FILE),"--input",str(combined),
                          "--output",str(dest),"--frames","2"],
                         capture_output=True,text=True,timeout=75)
        self.assertEqual(r.returncode,0,r.stderr[-700:])
        self.assertEqual(dest.read_bytes(),first_bytes+second_bytes)

    def test_reject_mismatched_batch_count_without_output(self):
        source=self.synthetic()
        output=self.directory/"not-created-batch.nv12"
        for n in ("2","0","28","-1","unknown"):
            r=subprocess.run([sys.executable,str(FILE),"--input",str(source),
                "--output",str(output),"--frames",n],
                capture_output=True,text=True,timeout=25)
            self.assertNotEqual(r.returncode,0,n)
            self.assertFalse(output.exists())

    def test_reference_colorbar_cannot_claim_multiple_frames(self):
        output=self.directory/"not-created-reference-batch.nv12"
        r=subprocess.run([sys.executable,str(FILE),"--input",str(REAL),
            "--output",str(output),"--frames","2","--reference-colorbar"],
            capture_output=True,text=True,timeout=25)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(output.exists())

    def test_no_hardware_or_publication_capabilities_in_source(self):
        content=(HERE/"rear_fast.c").read_text()+(HERE/"rear-fast-bridge.py").read_text()
        for forbidden in ("VIDIOC_STREAMON","/dev/video","/dev/media",
                "modprobe ","insmod ","grub-reboot","v4l2loopback",
                "sp11-vd55g0.ko"):
            self.assertNotIn(forbidden,content)

if __name__=="__main__":unittest.main(verbosity=2)
