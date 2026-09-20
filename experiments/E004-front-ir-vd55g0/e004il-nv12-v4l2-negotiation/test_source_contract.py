#!/usr/bin/env python3
"""E004il static / negative contract checks for a disposable V4L2 overlay."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
O=runpy.run_path(str(HERE/"offline-v4l2-overlay.py"))
EXPECTED=O["EXPECTED"]

def audit(camss):
    original=ROOT/"src/front-imx681/kernel/camss"
    for filename,sha in EXPECTED.items():
        if hashlib.sha256((original/filename).read_bytes()).hexdigest()!=sha:
            raise ValueError("accepted production source changed: "+filename)
    vfe=(camss/"camss-vfe.c").read_text()
    video=(camss/"camss-video.c").read_text()
    if (camss/"camss-vfe-680.c").read_bytes() != (original/"camss-vfe-680.c").read_bytes():
        raise ValueError("accepted VFE680 MMIO implementation changed")
    # New NV12 formats must appear *only* in the SP11 dedicated PIX table.
    original_vfe=(original/"camss-vfe.c").read_text()
    for needle in ("vfe_formats_pix_8x16", "vfe_formats_rdi_8x96"):
        if vfe.count(needle)!=original_vfe.count(needle):
            raise ValueError("other media format tables touched")
    m=re.search(r"static const struct camss_format_info formats_pix_x1e80100\[\] = \{(.*?)\n\};",vfe,re.S)
    if not m:
        raise ValueError("missing dedicated X1E front format table")
    if not re.search(r"V4L2_PIX_FMT_QC10C.*?V4L2_PIX_FMT_NV12",m.group(1),re.S):
        raise ValueError("accepted default QC10C no longer first")
    if m.group(1).count("V4L2_PIX_FMT_NV12")!=1 or m.group(1).count("V4L2_PIX_FMT_QC10C")!=1:
        raise ValueError("unexpected X1E PIX format set")
    for token in (
        "CAMSS_X1E80100_NV12_WIDTH\t\t2560",
        "CAMSS_X1E80100_NV12_HEIGHT\t\t1440",
        "CAMSS_X1E80100_NV12_STRIDE\t\t2560",
        "CAMSS_X1E80100_NV12_SIZEIMAGE\t\t5529600",
        "f->code == MEDIA_BUS_FMT_SRGGB10_1X10",
        "fi->pixelformat == V4L2_PIX_FMT_NV12 &&\n\t    video_is_x1e_front_pix(video)",
        "fsize->pixel_format == V4L2_PIX_FMT_NV12 &&\n\t    video_is_x1e_front_pix(video)",
        "f->pixelformat == V4L2_PIX_FMT_NV12",
        "video->active_fmt.fmt.pix_mp.pixelformat == V4L2_PIX_FMT_NV12",
        "video_is_x1e_front_pix(video) &&\n\t      pix_mp->pixelformat == V4L2_PIX_FMT_NV12",
        "CAMSS_X1E80100_QC10C_SIZEIMAGE\t\t0x76b000",
        "V4L2_PIX_FMT_QC10C",
    ):
        if token not in video:
            raise ValueError("format isolation or geometry contract absent: "+token[:35])
    # New format explicitly rejects even the PM prepare stage. Hard secondary
    # gate at start_streaming protects against internal vb2 call variants.
    prep=video.split("static int video_prepare_streaming(",1)[1].split(
        "static int video_start_streaming(",1)[0]
    start=video.split("static int video_start_streaming(",1)[1].split(
        "static void video_stop_streaming(",1)[0]
    if not (prep.index("pixelformat == V4L2_PIX_FMT_NV12") <
            prep.index("return -EOPNOTSUPP") <
            prep.index("v4l2_pipeline_pm_get")):
        raise ValueError("PM may run before NV12 rejection")
    if not (start.index("pixelformat == V4L2_PIX_FMT_NV12") <
            start.index("ret = -EOPNOTSUPP") <
            start.index("goto flush_buffers") <
            start.index("video_device_pipeline_alloc_start")):
        raise ValueError("media pipeline may start before NV12 rejection")
    # No new Linux driver writes. Existing production source retains every
    # byte; the overlay touches only the format table and video IOCTL path.
    production_video=(original/"camss-video.c").read_text()
    for token in ("writel(", "writel_relaxed(", "regmap_write(", "ioremap("):
        if video.count(token)!=production_video.count(token):
            raise ValueError("overlay added hardware operation: "+token)
    return {"status":"PASS_OFFLINE_NV12_V4L2_NEGOTIATION_STREAM_FAILS_BEFORE_PM",
      "accepted_production_source_unchanged":True,
      "default_fourcc":"QC10C","staged_alternate_fourcc":"NV12",
      "staged_nv12_sizeimage":5529600,"staged_nv12_width":2560,"staged_nv12_height":1440,
      "staged_streamon_allowed":False,"experimental_driver_installed":False,
      "camera_access":False,"ISP_linear_output_proven":False}

class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="sp11-e004il-test-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.accepted=ROOT/"src/front-imx681/kernel/camss"
        for filename in EXPECTED:
            shutil.copyfile(self.accepted/filename,self.root/filename)
        O["patch"](self.accepted,self.root)

    def test_unchanged_production_and_both_gates(self):
        self.assertTrue(audit(self.root)["accepted_production_source_unchanged"])

    def tamper(self,old,new,which="camss-video.c"):
        p=self.root/which
        data=p.read_text()
        self.assertIn(old,data)
        p.write_text(data.replace(old,new,1))
        with self.assertRaises(ValueError):
            audit(self.root)

    def test_reject_format_table_default_swap(self):
        self.tamper("V4L2_PIX_FMT_QC10C, 1", "V4L2_PIX_FMT_NV12, 1", "camss-vfe.c")

    def test_reject_missing_early_pm_block(self):
        self.tamper("return -EOPNOTSUPP;", "return 0;")

    def test_reject_missing_streamon_block(self):
        self.tamper("ret = -EOPNOTSUPP;", "ret = 0;")

    def test_reject_wrong_allocation_size(self):
        self.tamper("CAMSS_X1E80100_NV12_SIZEIMAGE\t\t5529600",
                    "CAMSS_X1E80100_NV12_SIZEIMAGE\t\t7778304")

    def test_reject_mmio_added(self):
        self.tamper("static int video_start_streaming(",
                    "writel(0, vfe->base);\nstatic int video_start_streaming(")

    def test_reject_vfe680_change(self):
        self.tamper("VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL\t0x00001046",
                    "VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL\t0x00000000",
                    "camss-vfe-680.c")

if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--inspect":
        print(json.dumps(audit(Path(sys.argv[2])),sort_keys=True))
    else:
        unittest.main(verbosity=2)
