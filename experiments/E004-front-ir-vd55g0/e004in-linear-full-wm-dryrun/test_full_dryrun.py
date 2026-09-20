#!/usr/bin/env python3
"""Offline positive + mutation tests; NEVER loads scratch camera module."""
from pathlib import Path
import json
import runpy
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ORIGINAL=ROOT/"src/front-imx681/kernel/camss"
PLAN=runpy.run_path(str(HERE/"make_full_dryrun.py"))

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="sp11-e004in-test-")
        self.addCleanup(self.tmp.cleanup)
        self.stage=Path(self.tmp.name)/"camss"
        shutil.copytree(ORIGINAL,self.stage,symlinks=True)
        PLAN["make"](ORIGINAL,self.stage)

    def test_pass_and_nondefault(self):
        result=PLAN["audit"](self.stage)
        self.assertEqual(result["full0_image_cfg0"],"0x05a00a00")
        self.assertEqual(result["full1_image_cfg0"],"0x02d00a00")
        self.assertEqual(result["full0_frame_increment"],3686400)
        self.assertEqual(result["full1_frame_increment"],1843200)
        self.assertEqual(result["actual_register_writes"],0)
        self.assertFalse(result["hardware_access_authorized"])

    def replace(self,name,old,new):
        f=self.stage/name
        s=f.read_text()
        self.assertIn(old,s)
        f.write_text(s.replace(old,new,1))
        with self.assertRaises(ValueError):
            PLAN["audit"](self.stage)

    def test_reject_active_mode(self):
        self.replace("camss-vfe-680.c","out->approved_for_hardware = false;",
                     "out->approved_for_hardware = true;")

    def test_reject_mismatched_chroma_stride(self):
        self.replace("camss-vfe-680.c","out->full[1].image_cfg2 = p.uv_stride;",
                     "out->full[1].image_cfg2 = 3584;")

    def test_reject_new_mmio(self):
        self.replace("camss-vfe-680.c","out->full[0].image_cfg2 = p.y_stride;",
                     "writel_relaxed(0, vfe->base);\n\tout->full[0].image_cfg2 = p.y_stride;")

    def test_reject_new_live_caller(self):
        self.replace("camss.c","static int camss_x1e_pix_v4l2_buffer(",
                     "vfe680_x1e_linear_nv12_full_dryrun_build(vfe,b, &plan);\nstatic int camss_x1e_pix_v4l2_buffer(")

    def test_reject_skip_shared_dma_guard(self):
        self.replace("camss-vfe-680.c",
                     "vfe680_x1e_linear_nv12_buffer_plan(vfe, buffer, &p)",
                     "vfe680_x1e_linear_nv12_buffer_plan(vfe, NULL, &p)")

    def test_reject_compression_claim(self):
        self.replace("camss-vfe-680.c","out->verified_ubwc_state_transition = false;",
                     "out->verified_ubwc_state_transition = true;")

if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--inspect":
        print(json.dumps(PLAN["audit"](Path(sys.argv[2])),sort_keys=True,indent=2))
    else:
        unittest.main(verbosity=2)
