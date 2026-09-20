#!/usr/bin/env python3
"""Static fail-closed audit of E004ik disposable kernel source overlay."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASELINE_SHA = "5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec"

def inspect(section: str, *, root=ROOT):
    source = (root / "src/front-imx681/kernel/camss/camss-vfe-680.c").read_bytes()
    if hashlib.sha256(source).hexdigest() != BASELINE_SHA:
        raise ValueError("accepted camera source changed")
    # No source code of the accepted driver can refer to the experimental
    # function. The guard is strict: a new stage cannot silently go live.
    for rel in ("camss-vfe-680.c", "camss-vfe.c", "camss-video.c", "camss.c"):
        existing = (root / "src/front-imx681/kernel/camss" / rel).read_text()
        if "vfe680_x1e_linear_nv12_buffer_plan" in existing or "vfe680_x1e_linear_nv12_stream_authorize" in existing:
            raise ValueError("accepted runtime now references unproven NV12 path")
    formats = (root / "src/front-imx681/kernel/camss/camss-vfe.c").read_text()
    m = re.search(r"static const struct camss_format_info formats_pix_x1e80100\[\] = \{(.*?)\n\};", formats, re.S)
    if not m or m.group(1).count("V4L2_PIX_FMT_QC10C") != 1 or "V4L2_PIX_FMT_NV12" in m.group(1):
        raise ValueError("accepted live V4L2 format table no longer QC10C-only")
    if re.search(r"\b(?:writel|writel_relaxed|readl|regmap_write|iowrite32|ioremap)\s*\(", section):
        raise ValueError("unproven sidecar accesses hardware")
    required = (
        "static int __used vfe680_x1e_linear_nv12_stream_authorize(void)",
        "return -EOPNOTSUPP;",
        "fmt->pixelformat != V4L2_PIX_FMT_NV12",
        "fmt->plane_fmt[0].sizeimage !=",
        "fmt->plane_fmt[0].bytesperline !=",
        "buffer->vb.vb2_buf.vb2_queue != &video->vb2_q",
        "buffer->vb.vb2_buf.state != VB2_BUF_STATE_ACTIVE",
        "vb2_plane_size(&buffer->vb.vb2_buf, 0) <",
        "end - 1 > U32_MAX",
        "VFE680_X1E_LINEAR_NV12_ALLOCATION     5529600U",
    )
    if any(token not in section for token in required):
        raise ValueError("NV12 format, buffer or authorization gate is missing")
    if section.count("vfe680_x1e_linear_nv12_stream_authorize(") != 1:
        raise ValueError("authorization stub acquired unexpected call sites")
    return {
        "stage": "E004ik",
        "status": "PASS_KERNEL_NATIVE_NV12_OFFLINE_COMPILED_NOT_ENABLED",
        "accepted_vfe680_source_sha256": BASELINE_SHA,
        "overlay_sha256": hashlib.sha256(section.encode()).hexdigest(),
        "production_pix_advertised_format": "QC10C_ONLY",
        "experimental_planned_format": "NV12",
        "new_kernel_buffer_plan_build": "PASS",
        "experimental_stream_authorization": "EOPNOTSUPP_ALWAYS",
        "new_hardware_writes": False,
        "module_loaded": False,
        "golden_modified": False,
        "exact_sp11_uncompressed_bus_reset_recipe_proven": False,
        "real_linear_camera_frames_captured": False,
    }

class StaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.section = (HERE / "nv12-kernel-sidecar.cfrag").read_text()

    def test_static_authority(self):
        r = inspect(self.section)
        self.assertEqual(r["production_pix_advertised_format"], "QC10C_ONLY")
        self.assertEqual(r["experimental_stream_authorization"], "EOPNOTSUPP_ALWAYS")

    def test_refuse_authorize_without_hardware(self):
        with self.assertRaisesRegex(ValueError, "authorization gate"):
            inspect(self.section.replace("return -EOPNOTSUPP;", "return 0;"))

    def test_refuse_mmio_write(self):
        with self.assertRaisesRegex(ValueError, "accesses hardware"):
            inspect(self.section + "\nwritel_relaxed(0, vfe->base);\n")

    def test_refuse_non_nv12_queue(self):
        with self.assertRaisesRegex(ValueError, "gate is missing"):
            inspect(self.section.replace("fmt->pixelformat != V4L2_PIX_FMT_NV12",
                                         "fmt->pixelformat != V4L2_PIX_FMT_QC10C"))

    def test_refuse_missing_protection(self):
        with self.assertRaisesRegex(ValueError, "gate is missing"):
            inspect(self.section.replace("buffer->vb.vb2_buf.vb2_queue != &video->vb2_q",
                                         "0 /* not checked */"))

    def test_refuse_unbound_dma(self):
        with self.assertRaisesRegex(ValueError, "gate is missing"):
            inspect(self.section.replace("end - 1 > U32_MAX", "0 /* not checked */"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
