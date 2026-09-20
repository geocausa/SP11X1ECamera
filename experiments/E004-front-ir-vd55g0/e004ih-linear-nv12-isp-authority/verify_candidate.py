#!/usr/bin/env python3
"""Offline, fail-closed source/geometry gate for a *separate* SP11 front NV12 candidate.

No camera, kernel, GPU, boot, PMIC, or privileged operations. The generated
candidate is NOT runnable: its register programming remains deliberately unknown.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = {
    "src/front-imx681/kernel/camss/camss-vfe-680.c": "5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec",
    "src/front-imx681/kernel/camss/camss-vfe.c": "98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
    "src/front-imx681/kernel/camss/camss-video.c": "c046b3156f5507755fd6df6cc5398ea1513ce4365ee1feb9395828f2495121ac",
    "src/front-imx681/userspace/runtime/front-imx681-production-capture.c": "8cb1e4135007bf93abf241bb4122c57ff62592e35dd15e283bab4807162d6eb1",
    "src/front-imx681/desktop-output-contract.json": "72486cd33a9a8d6b560faa1db44ddab5a50c88be1de901de25f99a4863e5edfa",
}

def geometry(width=2560, height=1440, stride=2560):
    if not all(isinstance(n, int) and not isinstance(n, bool) for n in (width, height, stride)):
        raise ValueError("integer dimensions required")
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("NV12 requires positive even width and height")
    if stride < width or stride % 64:
        raise ValueError("proposed stride must be >= width and aligned to 64")
    y = stride * height
    uv = stride * (height // 2)
    return {"width": width, "height": height, "proposed_stride_bytes": stride,
            "y": {"offset": 0, "bytes": y, "rows": height},
            "uv": {"offset": y, "bytes": uv, "rows": height // 2},
            "proposed_total_bytes": y + uv,
            "v4l2_memory_planes": 1, "isp_clients": [0, 1]}

def verify_source(root=ROOT):
    actual = {}
    for relative, wanted in EXPECTED.items():
        file = root / relative
        data = file.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != wanted:
            raise ValueError(f"source authority changed: {relative}: {digest}")
        actual[relative] = digest
    contract = json.loads((root / "src/front-imx681/desktop-output-contract.json").read_text())
    if (contract["v4l2_fourcc"], contract["width"], contract["height"],
        contract["bytesperline"], contract["allocation_bytes"],
        contract["desktop_conversion_proven"]) != ("Q10C", 2560, 1440, 3584, 0x76b000, False):
        raise ValueError("accepted QC10C contract differs")
    vfe = (root / "src/front-imx681/kernel/camss/camss-vfe.c").read_text()
    section = re.search(r"static const struct camss_format_info formats_pix_x1e80100\[\] = \{(.*?)\n\};", vfe, re.S)
    if not section or section.group(1).count("V4L2_PIX_FMT_QC10C") != 1 or "V4L2_PIX_FMT_NV12" in section.group(1):
        raise ValueError("accepted front PIX format table changed")
    bus = (root / "src/front-imx681/kernel/camss/camss-vfe-680.c").read_text()
    if not (re.search(r"VFE680_X1E_WINDOWS_CLIENT\(0,.*?0x0b, 0x0b, 0x400, 0x23", bus, re.S) and
            re.search(r"VFE680_X1E_WINDOWS_CLIENT\(1,.*?0x0b, 0x0b, 0x400, 0x33", bus, re.S) and
            "VFE680_X1E_QC10C_C_DATA_OFF     0x004f5000" in bus):
        raise ValueError("accepted front compressed BUS recipe changed")
    video = (root / "src/front-imx681/kernel/camss/camss-video.c").read_text()
    if not ("format->pixelformat == V4L2_PIX_FMT_NV12" in video and
            "buffer->addr[1] = buffer->addr[0] +" in video and
            "CAMSS_X1E80100_QC10C_SIZEIMAGE" in video):
        raise ValueError("existing V4L2 buffer assumptions changed")
    return actual

def candidate(root=ROOT):
    source = verify_source(root)
    image = geometry()
    return {
        "experiment": "E004ih", "status": "OFFLINE_NV12_GEOMETRY_ONLY_NOT_HARDWARE_AUTHORIZED",
        "based_on": "555f086882131626eb1b5ceea641d2fa0bdf3f4d",
        "accepted_source_sha256": source,
        "accepted_qc10c_unchanged": True,
        "candidate_name": "front-rgb-linear-nv12-separate-mode",
        "candidate_format": "NV12",
        "memory_layout_proposal_only": image,
        "public_vendor_vfe_bus_ver3": {
            "separate_uncompressed_nv12_full_yc_case": True,
            "nv12_packer_enum_name": "PACKER_FMT_VER3_PLAIN_8_LSB_MSB_10",
            "same_sp11_isp_register_value_confirmed": False,
        },
        "not_authorized": ["kernel mode selection", "ISP register writes", "camera boot",
                           "camera capture", "QC10C replacement", "continuous output"],
        "required_before_hardware": [
            "prove exact X1E80100 FULL_Y/FULL_C uncompressed NV12 register set and IP compatibility",
            "prove disable/restore compression and metadata controls without changing accepted QC10C",
            "specify and isolate alternate V4L2 format, buffers, 32-bit DMA spans and both-client completion",
            "verify ISP scaler, colourimetry, chroma order and per-plane stride from independent authority",
            "offline build/regression and bounded fresh one-shot candidate with Golden rollback",
        ],
        "golden_modified": False,
        "camera_runtime": False,
    }

if __name__ == "__main__":
    print(json.dumps(candidate(), sort_keys=True, indent=2))
