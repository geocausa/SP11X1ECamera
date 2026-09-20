#!/usr/bin/env python3
"""E004im offline negative tests: the combined scratch module cannot stream."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IL=ROOT/"experiments/E004-front-ir-vd55g0/e004il-nv12-v4l2-negotiation"
IK=ROOT/"experiments/E004-front-ir-vd55g0/e004ik-kernel-nv12-plan"
ORIGINAL=ROOT/"src/front-imx681/kernel/camss"
COMBINED=runpy.run_path(str(HERE/"make_combined.py"))
IL_OVERLAY=runpy.run_path(str(IL/"offline-v4l2-overlay.py"))
ORIGINAL_SHA=IL_OVERLAY["EXPECTED"]
SIDECAR=(IK/"nv12-kernel-sidecar.cfrag").read_text()
EXACT_OVERLAY_SHA={
    "camss-vfe.c":"99aeef4a7aa3ded78111bf8b0084eac35a1611caba929152e393a7a698988143",
    "camss-video.c":"fe7a2b3e0c5e45ad4bf8ea631ab635c38e3839d403a925730767958113d47d8c",
}

def audit(stage:Path):
    for filename, original_sha in ORIGINAL_SHA.items():
        if hashlib.sha256((ORIGINAL/filename).read_bytes()).hexdigest()!=original_sha:
            raise ValueError("accepted QC10C source drift")
    for filename, expected_sha in EXACT_OVERLAY_SHA.items():
        if hashlib.sha256((stage/filename).read_bytes()).hexdigest()!=expected_sha:
            raise ValueError("staged negotiation changed after safety audit: "+filename)
    vfe680=(stage/"camss-vfe-680.c").read_text()
    original=(ORIGINAL/"camss-vfe-680.c").read_text()
    if vfe680!=original+"\n"+SIDECAR+"\n":
        raise ValueError("combined sidecar must be the sole VFE680 source change")
    if vfe680.count("vfe680_x1e_linear_nv12_buffer_plan(")!=1:
        raise ValueError("unproven Y/C planner acquired another caller")
    if vfe680.count("vfe680_x1e_linear_nv12_stream_authorize(")!=1:
        raise ValueError("unproven stream authorization acquired another caller")
    if "return -EOPNOTSUPP;" not in SIDECAR:
        raise ValueError("unproven stream authorization was bypassed")
    for f in ("camss.c","camss-video.c","camss-vfe.c"):
        code=(stage/f).read_text()
        if "vfe680_x1e_linear_nv12_buffer_plan(" in code or "vfe680_x1e_linear_nv12_stream_authorize(" in code:
            raise ValueError("NV12 hardware helper called from a live path")
    video=(stage/"camss-video.c").read_text()
    prepare=video.split("static int video_prepare_streaming(",1)[1].split("static int video_start_streaming(",1)[0]
    start=video.split("static int video_start_streaming(",1)[1].split("static void video_stop_streaming(",1)[0]
    if not (prepare.index("pixelformat == V4L2_PIX_FMT_NV12") <
            prepare.index("return -EOPNOTSUPP;") <
            prepare.index("v4l2_pipeline_pm_get")):
        raise ValueError("NV12 power-before-rejection regression")
    if not (start.index("pixelformat == V4L2_PIX_FMT_NV12") <
            start.index("ret = -EOPNOTSUPP;") <
            start.index("video_device_pipeline_alloc_start")):
        raise ValueError("NV12 start-before-rejection regression")
    if "VFE680_X1E_LINEAR_NV12_ALLOCATION     5529600U" not in SIDECAR or (
        "CAMSS_X1E80100_NV12_SIZEIMAGE\t\t5529600" not in video):
        raise ValueError("combined buffer geometry drift")
    return {
        "status":"PASS_COMBINED_NV12_SCRATCH_CONTRACT",
        "accepted_qc10c_source_preserved":True,
        "nondefault_v4l2_nv12_and_native_dma_planner":True,
        "unproven_mmio_calls":0,
        "nv12_streaming_rejected_before_power":True,
        "temporary_only":True
    }

class CombinedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="sp11-e004im-test-")
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"camss"
        shutil.copytree(ORIGINAL,self.path,symlinks=True)
        COMBINED["combined"](ORIGINAL,self.path)

    def test_pass_combined_source(self):
        self.assertTrue(audit(self.path)["nv12_streaming_rejected_before_power"])

    def change(self,name,old,new):
        file=self.path/name
        content=file.read_text()
        self.assertIn(old,content)
        file.write_text(content.replace(old,new,1))
        with self.assertRaises(ValueError):
            audit(self.path)

    def test_block_unauthorized_stream(self):
        self.change("camss-video.c","return -EOPNOTSUPP;","return 0;")

    def test_block_unauthorized_pipeline(self):
        self.change("camss-video.c","ret = -EOPNOTSUPP;","ret = 0;")

    def test_block_extra_vfe680_mmio(self):
        self.change("camss-vfe-680.c",SIDECAR,SIDECAR+"\nwritel_relaxed(1, vfe->base);\n")

    def test_block_new_buffer_planner_caller(self):
        self.change("camss.c","static int camss_x1e_pix_v4l2_buffer(",
                    "vfe680_x1e_linear_nv12_buffer_plan(vfe, buffer, &plan);\nstatic int camss_x1e_pix_v4l2_buffer(")

    def test_block_other_buffer_geometry(self):
        self.change("camss-video.c","CAMSS_X1E80100_NV12_SIZEIMAGE\t\t5529600",
                    "CAMSS_X1E80100_NV12_SIZEIMAGE\t\t7778304")

    def test_block_default_fourcc_change(self):
        self.change("camss-vfe.c","V4L2_PIX_FMT_QC10C, 1","V4L2_PIX_FMT_NV12, 1")

if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--inspect":
        print(json.dumps(audit(Path(sys.argv[2])),sort_keys=True))
    else:
        unittest.main(verbosity=2)
