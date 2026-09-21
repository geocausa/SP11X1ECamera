#!/usr/bin/env python3
"""E004ke offline RAW10 RGGB -> actual NV12 byte/caps tests; no physical front claim."""
from pathlib import Path
import hashlib
import re
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE/"front-rggb10p-to-nv12-1080.c"
BINARY=Path("/tmp/sp11-e004ke-front-rggb-to-nv12")
FRONT_BYTES=3840*2160*5//4
NV12_BYTES=1920*1080*3//2


def pack_uniform_mosaic(r=220,g=95,b=50):
    # MIPI RGGB RAW10 high-eight-bit samples, low two bits set to zero.
    row0=(bytes([r,g,r,g,0])*(3840//4))
    row1=(bytes([g,b,g,b,0])*(3840//4))
    raw=(row0+row1)*(2160//2)
    assert len(raw)==FRONT_BYTES
    return raw


class FrontRGGB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=subprocess.run(["gcc","-O3","-std=c11","-Wall","-Wextra",
                          "-Werror","-pedantic","-fno-fast-math",
                          "-ffp-contract=off",str(SOURCE),"-o",str(BINARY)],
                         capture_output=True,text=True,timeout=25)
        if p.returncode:
            raise RuntimeError(p.stderr)
        cls.frame=pack_uniform_mosaic()

    def run_convert(self,data,n=1):
        return subprocess.run([str(BINARY),"--frames",str(n)],
            input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=25)

    def test_one_uniform_raw10_rggb_frame_outputs_correct_full_resolution_nv12(self):
        p=self.run_convert(self.frame)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(len(p.stdout),NV12_BYTES)
        r,g,b=220,95,50
        y=(77*r+150*g+29*b+128)>>8
        u=128+((-43*r-85*g+128*b+128)>>8)
        v=128+((128*r-107*g-21*b+128)>>8)
        self.assertEqual(p.stdout[:1920*1080],bytes([y])*(1920*1080))
        self.assertEqual(p.stdout[1920*1080:],bytes([u,v])*(1920*1080//4))
        self.assertIn(b"E004KE_FRONT_RDI_BAYER_TO_NV12=PASS",p.stderr)
        self.assertIn(b"QC10C_DECODED=NO OEM_ISP_PARITY=NO",p.stderr)

    def test_two_full_distinct_mosaics_produce_two_distinct_complete_nv12_frames(self):
        frame2=pack_uniform_mosaic(r=40,g=180,b=210)
        p=self.run_convert(self.frame+frame2,n=2)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(len(p.stdout),2*NV12_BYTES)
        h0=hashlib.sha256(p.stdout[:NV12_BYTES]).digest()
        h1=hashlib.sha256(p.stdout[NV12_BYTES:]).digest()
        self.assertNotEqual(h0,h1)
        self.assertIn(b"FRAMES=2 SRC_BYTES_PER_FRAME=10368000",p.stderr)

    def test_wrong_input_type_qc10c_length_does_not_decode_or_claim_front(self):
        # The accepted compressed front frame is 7,778,304 bytes, NOT RAW10.
        p=self.run_convert(bytes([0])*7778304)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(p.stdout,b"")
        self.assertIn(b"TRUNCATED_FRONT_RDI_RAW10_INPUT",p.stderr)

    def test_input_truncation_excess_and_wrong_frame_count_fail_closed(self):
        for data,n in ((self.frame[:-1],1),(self.frame+b"x",1),
                       (self.frame,2)):
            p=self.run_convert(data,n)
            self.assertNotEqual(p.returncode,0)
        for n in (0,17,-1):
            p=self.run_convert(b"",n)
            self.assertEqual(p.returncode,2)

    def test_raw_bypass_graph_and_driver_only_supports_candidate_not_hardware_proof(self):
        graph=(ROOT/"experiments/E004-front-ir-vd55g0/"
              "e004ec-side-light-post-g3-shadow-observation/evidence/LOAD-MEDIA.txt")
        text=graph.read_text()
        for entity in ("imx681 1-0010","msm_csiphy2","msm_csid1",
                       "msm_vfe0_rdi0","msm_vfe0_video0"):
            self.assertIn(entity,text)
        csid=re.search(r"^- entity \d+: msm_csid1 \(.*?(?=^- entity |\Z)",
                       text,re.M|re.S)
        self.assertIsNotNone(csid)
        self.assertRegex(csid.group(0),r'-> "msm_vfe0_rdi0":0 \[\]')
        vfe=(ROOT/"src/front-imx681/kernel/camss/camss-vfe.c").read_text()
        self.assertIn("MEDIA_BUS_FMT_SRGGB10_1X10, 10, V4L2_PIX_FMT_SRGGB10P",vfe)
        camss=(ROOT/"src/front-imx681/kernel/camss/camss.c").read_text()
        self.assertIn(".formats_rdi = &vfe_formats_rdi_845",camss)
        sensor=(ROOT/"src/front-imx681/kernel/imx681/imx681.c").read_text()
        self.assertIn("{ 3840, 2160, 6752, 3554, 548570000, 30 }",sensor)
        self.assertIn("MEDIA_BUS_FMT_SRGGB10_1X10",sensor)

    def test_no_camera_ir_boot_pixel_file_api_and_10bit_claim(self):
        s=SOURCE.read_text()
        for forbidden in ("/dev/video","/dev/media","media-ctl","grub-reboot",
                          "modprobe","insmod","ILLUMINATION_ON","fopen(","O_CREAT"):
            self.assertNotIn(forbidden,s)
        self.assertIn("QC10C_DECODED=NO",s)
        self.assertIn("OEM_ISP_PARITY=NO",s)


if __name__=="__main__":
    unittest.main()
