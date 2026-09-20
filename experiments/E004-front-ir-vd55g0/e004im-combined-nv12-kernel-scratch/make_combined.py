#!/usr/bin/env python3
"""Build the first combined, UNINSTALLED E004ik+E004il NV12 kernel overlay.

No production source modification. No live callers, no MMIO or camera access.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IL = ROOT / "experiments/E004-front-ir-vd55g0/e004il-nv12-v4l2-negotiation"
IK = ROOT / "experiments/E004-front-ir-vd55g0/e004ik-kernel-nv12-plan"
overlay = runpy.run_path(str(IL / "offline-v4l2-overlay.py"))
inspect_il = runpy.run_path(str(IL / "test_source_contract.py"))["audit"]
inspect_ik = runpy.run_path(str(IK / "test_stage.py"))["inspect"]
EXPECTED_SIDECAR_SHA = "feed2857eef7b14b1df5a8569885815493f3ad0ac17c73296072b979e2a684af"

def combined(source: Path, scratch: Path, *, sidecar_path=IK / "nv12-kernel-sidecar.cfrag"):
    # E004il patches independently pinned current-format source, which is
    # allowed only in the temporary copy. Original VFE680 stays untouched.
    manifest = overlay["patch"](source, scratch)
    il = inspect_il(scratch)
    sidecar = sidecar_path.read_text()
    if hashlib.sha256(sidecar.encode()).hexdigest() != EXPECTED_SIDECAR_SHA:
        raise ValueError("E004ik kernel planner identity differs")
    ik = inspect_ik(sidecar)
    if ik["experimental_stream_authorization"] != "EOPNOTSUPP_ALWAYS":
        raise ValueError("unproven NV12 streaming unexpectedly enabled")
    if il["staged_streamon_allowed"]:
        raise ValueError("unproven V4L2 stream unexpectedly enabled")
    vfe680 = scratch / "camss-vfe-680.c"
    existing = vfe680.read_text()
    if "vfe680_x1e_linear_nv12_buffer_plan" in existing:
        raise ValueError("sidecar already installed or unexpected changes")
    vfe680.write_text(existing + "\n" + sidecar + "\n")
    # Compare only preexisting content; every original byte must remain.
    if not vfe680.read_text().startswith(existing + "\n"):
        raise ValueError("accepted VFE680 content changed")
    # Stage-specific format constraints must actually agree.
    video = (scratch / "camss-video.c").read_text()
    for token in ("CAMSS_X1E80100_NV12_WIDTH\t\t2560",
                  "CAMSS_X1E80100_NV12_HEIGHT\t\t1440",
                  "CAMSS_X1E80100_NV12_STRIDE\t\t2560",
                  "CAMSS_X1E80100_NV12_SIZEIMAGE\t\t5529600"):
        if token not in video:
            raise ValueError("combined buffer/queue geometry mismatch")
    if not all(t in sidecar for t in ("VFE680_X1E_LINEAR_NV12_WIDTH          2560U",
                                     "VFE680_X1E_LINEAR_NV12_HEIGHT         1440U",
                                     "VFE680_X1E_LINEAR_NV12_STRIDE         2560U",
                                     "VFE680_X1E_LINEAR_NV12_ALLOCATION     5529600U")):
        raise ValueError("combined kernel-buffer geometry mismatch")
    all_camss = (scratch / "camss.c").read_text()
    if "vfe680_x1e_linear_nv12_buffer_plan" in all_camss or (
            "vfe680_x1e_linear_nv12_stream_authorize" in all_camss):
        raise ValueError("unproven NV12 planner linked to camera runtime")
    manifest["E004im"] = {
        "status": "OFFLINE_COMBINED_NV12_V4L2_AND_DMA_PLANNER_UNINSTALLED",
        "nv12_queue": "2560x1440/2560/5529600",
        "default_format": "QC10C",
        "stage_il_safety_audit": il["status"],
        "stage_ik_safety_audit": ik["status"],
        "nv12_stream_pm": "EOPNOTSUPP",
        "nv12_stream_start": "EOPNOTSUPP",
        "actual_camera_runtime": False,
        "compression_disable_proven": False,
        "accepted_vfe680_sha256": overlay["EXPECTED"]["camss-vfe-680.c"],
        "scratch_vfe680_sha256": hashlib.sha256(vfe680.read_bytes()).hexdigest(),
        "sidecar_sha256": EXPECTED_SIDECAR_SHA,
    }
    return manifest

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: make_combined.py ACCEPTED_CAMSS_SOURCE SCRATCH_CAMSS_COPY")
    print(json.dumps(combined(Path(sys.argv[1]), Path(sys.argv[2])), sort_keys=True, indent=2))
