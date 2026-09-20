#!/usr/bin/env python3
"""E004in: independently pinned, UNINSTALLED combined NV12 + pure FULL WM plan."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IM=ROOT/"experiments/E004-front-ir-vd55g0/e004im-combined-nv12-kernel-scratch"
COMBINED=runpy.run_path(str(IM/"make_combined.py"))
AUDIT=runpy.run_path(str(IM/"test_combined.py"))["audit"]
SIDECAR_SHA="0f87d64288ad3787a632cfc7bac14cfd827679438ddf874aea31ccdf03246c44"

def audit(stage):
    combined=(stage/"camss-vfe-680.c").read_text()
    original=(ROOT/"src/front-imx681/kernel/camss/camss-vfe-680.c").read_text()
    im_sidecar=(ROOT/"experiments/E004-front-ir-vd55g0/e004ik-kernel-nv12-plan/nv12-kernel-sidecar.cfrag").read_text()
    candidate=(HERE/"full-wm-dryrun.cfrag").read_text()
    if hashlib.sha256(candidate.encode()).hexdigest()!=SIDECAR_SHA:
        raise ValueError("E004in dryrun sidecar changed without review")
    if combined!=original+"\n"+im_sidecar+"\n"+"\n"+candidate+"\n":
        raise ValueError("unreviewed scratch VFE680 source changes")
    if not ("vfe680_x1e_linear_nv12_full_dryrun_build(" in candidate and
            "vfe680_x1e_linear_nv12_buffer_plan(vfe, buffer, &p)" in candidate):
        raise ValueError("missing validated single-buffer DMA planner")
    if not ("return -EOPNOTSUPP;" in candidate and
            "out->approved_for_hardware = false;" in candidate and
            "out->verified_ubwc_state_transition = false;" in candidate):
        raise ValueError("hardware authorization not fail-closed")
    if any(re.search(r"\b"+fn+r"\s*\(", candidate)
           for fn in ("writel","writel_relaxed","readl","readl_relaxed",
                      "ioremap","regmap_write","v4l2_subdev_call","pm_runtime_get")):
        raise ValueError("hardware or power call in pure NV12 FULL plan")
    if combined.count("vfe680_x1e_linear_nv12_full_dryrun_build(")!=1:
        raise ValueError("unexpected caller of alternate FULL plan")
    for fn in ("camss.c","camss-video.c","camss-vfe.c"):
        if "vfe680_x1e_linear_nv12_full_dryrun_build(" in (stage/fn).read_text():
            raise ValueError("alternate FULL plan gained live caller")
    required=(
        "out->full[0].client = 0;", "out->full[1].client = 1;",
        "out->full[0].image_cfg2 = p.y_stride;",
        "out->full[1].image_cfg2 = p.uv_stride;",
        "out->full[0].frame_incr = p.y_bytes;",
        "out->full[1].frame_incr = p.uv_bytes;",
        "out->full[0].image_addr = p.y_dma;",
        "out->full[1].image_addr = p.uv_dma;",
        "out->full[0].packer_cfg = 3;",
        "out->full[1].packer_cfg = 3;",
        "out->allocation_bytes = p.allocation_bytes;",
        "VFE680_X1E_LINEAR_NV12_HEIGHT / 2",
        "out->approved_for_hardware = false;",
    )
    if any(k not in candidate for k in required):
        raise ValueError("proposed plane geometry/address or fail-closed flags altered")
    return {"status":"PASS_COMBINED_NV12_DMA_PLUS_FULL_YC_DRYRUN_NO_HW",
        "full0_image_cfg0":"0x05a00a00","full1_image_cfg0":"0x02d00a00",
        "proposed_full_packer":3,"proposed_full_stride":2560,
        "full0_frame_increment":3686400,"full1_frame_increment":1843200,
        "compression_mode_register_value_proven":False,
        "isp_linear_nv12_output_proven":False,"actual_register_writes":0,
        "hardware_access_authorized":False}

def make(source, stage):
    COMBINED["combined"](source,stage)
    parent=AUDIT(stage)
    if parent["nv12_streaming_rejected_before_power"] is not True:
        raise ValueError("E004im pre-power gate changed")
    candidate=(HERE/"full-wm-dryrun.cfrag").read_text()
    if hashlib.sha256(candidate.encode()).hexdigest()!=SIDECAR_SHA:
        raise ValueError("unreviewed E004in source digest")
    path=stage/"camss-vfe-680.c"
    with path.open("a") as f:
        f.write("\n"+candidate+"\n")
    result=audit(stage)
    result["parent_combined"] = parent["status"]
    return result

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: make_full_dryrun.py ACCEPTED_CAMSS SCRATCH_COPY")
    print(json.dumps(make(Path(sys.argv[1]),Path(sys.argv[2])),indent=2,sort_keys=True))
