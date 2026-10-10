#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Write a front still-capture run JSON for one IFE module ablation.
Usage: make-ablation-run.py <n> <label> [lsc] [reg,and,or ...]  (lsc = load our own LSC mesh)
The run captures the static SP7 chart: phase 0 manual, phase 1 automatic,
SP11_KEEP_PER_PHASE full frames from each. No reg triples = baseline.
"""
import json, sys
from pathlib import Path

K = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel")
LIB = K / "libcamera-front-ae-19"
n, label, masks = sys.argv[1], sys.argv[2], sys.argv[3:]
lsc = "lsc" in masks
masks = [m for m in masks if m != "lsc"]
params = ["e004j_ir_dphy_windows_parity=1", "native_linear_nv12_trial=1", "native_front_owner_trial=1",
          "native_front_queue_trial=1", "native_front_meta_trial=1", "native_front_params_trial=1",
          "native_front_profile_trial=1", "native_front_sof_trial=1", "native_front_param_queue_trial=1",
          "native_front_ccm_q7=216,-26,-61,-72,205,-5,-92,-5,224", "csiphy_x1e_cphy_gpl=1"]
if lsc:
    params.append("native_front_lsc=1")
if masks:
    params.append("native_front_reg_mask=" + ",".join(masks))
run = {
    "identity": f"E-FRONT-ABLATE-{label.upper()}-{n}",
    "id": f"sp11-camera-front-ae-{n}",
    "marker": f"sp11_camera_front_ae_{n}",
    "title": f"SP11 front ISP ablation {label}",
    "modules": str(K / "native-rgb-front-ae-43"),
    "libbuild": str(LIB),
    "extra": {str(LIB / "capture-front-still"): "capture-front-still",
              str(K / "front-ae-18/tuning-v9.yaml"): "tuning-v9.yaml"},
    "capture": "capture-front-still",
    "tuning": "tuning-v9.yaml",
    "frames_per_phase": 300,
    "capture_timeout": 150,
    "watchdog_seconds": 420,
    "env": {"SP11_KEEP_PER_PHASE": "6"},
    "camss_params": params,
    "log_levels": "CAMSSX1E:DEBUG,Camera:INFO",
}
if lsc:
    run["extra"][str(K / "front-lsc-v1/imx681-front-lsc-v1.bin")] = "imx681-front-lsc-v1.bin"
    run["firmware_extra"] = ["imx681-front-lsc-v1.bin"]
d = K / f"front-ae-{n}"
d.mkdir(exist_ok=True)
(d / f"run-{n}.json").write_text(json.dumps(run, indent=1) + "\n")
print(d / f"run-{n}.json")
