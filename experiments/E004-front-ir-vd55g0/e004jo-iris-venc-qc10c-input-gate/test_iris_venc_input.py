#!/usr/bin/env python3
"""E004jo: source-locked, offline current-Golden Iris VENC front format gate."""
import hashlib
from pathlib import Path
import re
import subprocess
import unittest

VENC_SHA = "4b50d72b2bdc0804ab2a5a5367fd0fa8a23840aaad575c3e117664e6d54a1b03"

def golden_source():
    release = subprocess.run(["uname", "-r"], check=True, capture_output=True,
                             text=True, timeout=5).stdout.strip()
    path = Path("/lib/modules") / release / "source" / (
        "drivers/media/platform/qcom/iris/iris_venc.c")
    if not path.exists():
        raise FileNotFoundError("E004JO_INSTALLED_GOLDEN_SOURCE_LINK_UNAVAILABLE")
    return path


def format_table(src, name):
    match = re.search(r"static const struct iris_fmt\s+"+re.escape(name)
                      +r"\[\]\s*=\s*\{(.*?)\n\};", src, re.S)
    if match is None:
        raise AssertionError(f"E004JO_{name}_TABLE_NOT_FOUND")
    table = match.group(1)
    return set(re.findall(r"\.pixfmt\s*=\s*(V4L2_PIX_FMT_[A-Z0-9_]+)", table)), table


class GoldenIrisCodecInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = golden_source()
        cls.data = cls.path.read_bytes()
        cls.src = cls.data.decode("utf8")

    def test_kernel_source_cryptographic_identity(self):
        self.assertEqual(hashlib.sha256(self.data).hexdigest(), VENC_SHA)
        self.assertIn("iris_venc_formats_out[]", self.src)

    def test_encoder_input_is_nv12_or_qc08c_not_qc10c(self):
        fmts, table = format_table(self.src, "iris_venc_formats_out")
        self.assertEqual(fmts, {"V4L2_PIX_FMT_NV12", "V4L2_PIX_FMT_QC08C"})
        self.assertIn("V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE", table)
        self.assertNotIn("V4L2_PIX_FMT_QC10C", table)
        self.assertNotIn("V4L2_PIX_FMT_P010", table)

    def test_encoder_output_is_encoded_video_not_pixel_decoder(self):
        fmts, table = format_table(self.src, "iris_venc_formats_cap")
        self.assertEqual(fmts, {"V4L2_PIX_FMT_H264", "V4L2_PIX_FMT_HEVC"})
        self.assertIn("V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE", table)

    def test_ioctl_admission_looks_up_encoder_input_table(self):
        find = self.src.index("find_format(struct iris_inst *inst,")
        tail = self.src.index("int iris_venc_enum_fmt(", find)
        body = self.src[find:tail]
        self.assertIn("case V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE:", body)
        self.assertIn("fmt = iris_venc_formats_out", body)
        self.assertIn("fmt[i].type != type", body)

    def test_only_shell_command_is_kernel_version(self):
        code = Path(__file__).read_text()
        self.assertEqual(code.count("subprocess." + "run("), 1)
        self.assertIn("subprocess." + 'run(["uname"', code)


if __name__ == "__main__":
    unittest.main()
