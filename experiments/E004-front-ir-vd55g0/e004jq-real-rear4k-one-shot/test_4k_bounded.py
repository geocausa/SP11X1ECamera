#!/usr/bin/env python3
"""E004jq rear 4K fixed-output, bounded 27-frame offline source gate."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
SRC=HERE/"rear-bayer-to-nv12-4k-live-bounded.c"
BASE=PARENT/"e004jm-rear-4k-fused-offline"/"rear-bayer-to-nv12-4k-fused.c"
FIXTURE=PARENT/"e004dz-canonical-package-rgb-handoff"/"runtime-output"/"rear-colorbar.raw"
FRAME_IN=5104*2806
FRAME_OUT=3840*2160*3//2
CC=("gcc","-O3","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-fno-fast-math","-ffp-contract=off")
DIGEST="42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d"


class Rear4kBounded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="sp11-e004jq-")
        cls.bin=Path(cls.tmp.name)/"rear4k"
        cls.original=Path(cls.tmp.name)/"original"
        for src,out in ((SRC,cls.bin),(BASE,cls.original)):
            subprocess.run([*CC,str(src),"-o",str(out)],check=True,timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def feed(self,exe,data,n=1):
        return subprocess.run([str(exe),"--frames",str(n)],input=data,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)

    def test_colorbar_exact_baseline(self):
        frame=FIXTURE.read_bytes()
        self.assertEqual(len(frame),FRAME_IN)
        a,b=(self.feed(x,frame) for x in (self.original,self.bin))
        self.assertEqual((a.returncode,b.returncode),(0,0))
        self.assertEqual(a.stdout,b.stdout)
        self.assertEqual(len(b.stdout),FRAME_OUT)
        self.assertEqual(hashlib.sha256(b.stdout).hexdigest(),DIGEST)
        self.assertIn(b"PROVENANCE_VERIFIED_BY_CALLER=NO",b.stderr)

    def test_nonuniform_synthetic_baseline(self):
        row=bytes((x*31+(x//5)*13+(x%5)*17)&255 for x in range(5104))
        data=b"".join(row.translate(bytes((i+19*y)&255 for i in range(256)))
                      for y in range(2806))
        a,b=(self.feed(x,data) for x in (self.original,self.bin))
        self.assertEqual((a.returncode,b.returncode),(0,0))
        self.assertEqual(a.stdout,b.stdout)
        self.assertNotEqual(hashlib.sha256(b.stdout).hexdigest(),DIGEST)

    def test_count_bound_and_extra_input_fail_closed(self):
        for n in (0,28,-1,999):
            p=self.feed(self.bin,b"",n)
            self.assertEqual(p.returncode,2)
            self.assertEqual(p.stdout,b"")
        for data,token in ((bytes(7778304),b"TRUNCATED_REAR_RAW10_INPUT"),
                           (FIXTURE.read_bytes()+b"x",b"EXTRA_INPUT_OR_READ_ERROR")):
            p=self.feed(self.bin,data)
            self.assertNotEqual(p.returncode,0)
            self.assertIn(token,p.stderr)

    def test_exact_two_frame_byte_stream(self):
        frame=FIXTURE.read_bytes()
        p=self.feed(self.bin,frame*2,n=2)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(len(p.stdout),FRAME_OUT*2)
        self.assertEqual(p.stdout[:FRAME_OUT],p.stdout[FRAME_OUT:])

    def test_source_confinement_and_27_bound(self):
        src=SRC.read_text()
        for token in ("DST_W=3840", "DST_H=2160", "SRC_W=4076",
                      "CROP_X=118, CROP_Y=322", "n>27", "PROVENANCE_VERIFIED_BY_CALLER=NO"):
            self.assertIn(token,src)
        for forbidden in ("/dev/video","ioctl(","modprobe","insmod",
                          "grub-reboot","BootNext"):
            self.assertNotIn(forbidden,src)


if __name__=="__main__":
    unittest.main()
