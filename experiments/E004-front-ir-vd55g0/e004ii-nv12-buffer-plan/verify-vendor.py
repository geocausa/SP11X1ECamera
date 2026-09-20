#!/usr/bin/env python3
"""Offline and fail-closed public VFE-ver3 format mapping provenance check."""
import hashlib
import json
import re
from pathlib import Path

EXPECTED_VENDOR_SHA = "6834887a2e0afcc55c24a61d32f0996e44764dbdd6eaeccf3b52f3b712c231c8"
VENDOR_URL = ("https://android.googlesource.com/kernel/msm/+/cf55e2491a3f1915760221075433d234b18fbe83/"
              "drivers/media/platform/msm/camera/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c")

def verify(blob: bytes):
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_VENDOR_SHA:
        raise ValueError("public source digest mismatch")
    text = blob.decode("utf-8")
    m = re.search(r"enum cam_vfe_bus_ver3_packer_format\s*\{([^}]+)\}", text)
    if m is None:
        raise ValueError("public VFE enum absent")
    formats = [x.strip() for x in m.group(1).split(",") if x.strip()]
    if formats.index("PACKER_FMT_VER3_PLAIN_8_LSB_MSB_10") != 3 or formats.index("PACKER_FMT_VER3_TP_10") != 11:
        raise ValueError("packer enumeration changed")
    fn = text.split("cam_vfe_bus_ver3_get_packer_fmt(", 1)[1].split("static int cam_vfe_bus_ver3_handle_rup_top_half", 1)[0]
    expected = ("case CAM_FORMAT_NV12:", "case CAM_FORMAT_UBWC_NV12:",
                "return PACKER_FMT_VER3_PLAIN_8_LSB_MSB_10;",
                "case CAM_FORMAT_UBWC_TP10:", "return PACKER_FMT_VER3_TP_10;")
    if any(token not in fn for token in expected):
        raise ValueError("public packer decision missing")
    # Distinguish case fall-through for UBWC NV12 from standalone NV12.
    if not re.search(r"case CAM_FORMAT_UBWC_NV12:\s*rsrc_data->en_ubwc = 1;\s*/\* Fall through for NV12 \*/\s*case CAM_FORMAT_NV21:\s*case CAM_FORMAT_NV12:", text):
        raise ValueError("public FULL-client NV12 compression-selection proof missing")
    return {
        "status": "PASS_OFFLINE_PUBLIC_SOURCE_NV12_PACKER_SEMANTICS",
        "source": VENDOR_URL, "source_sha256": digest,
        "public_vfe_bus_ver3_nv12_packer": 3,
        "public_vfe_bus_ver3_tp10_packer": 11,
        "public_source_has_separate_noncompressed_nv12_full_client": True,
        "x1e80100_nv12_register_recipe_proven": False,
        "x1e80100_nv12_pixel_output_proven": False,
        "safe_transition_from_existing_qc10c_ubwc_state_proven": False,
        "camera_runtime": False,
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("public_source", type=Path, help="exact vendor source in disposable scratch, never commit OEM/unknown raw material")
    print(json.dumps(verify(parser.parse_args().public_source.read_bytes()), indent=2, sort_keys=True))
