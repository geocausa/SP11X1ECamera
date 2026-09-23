#!/usr/bin/env python3
"""Camera-free strict validation of actual rear RAW10 frame-pair aggregates.

Only scalar root-private publisher logs; no pixels, per-position arrays,
image files, image hashes, optical black or scene recognition.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys

PREFIX="E004MV_REAR_REAL_RAW10_TEMPORAL "
STAGES=((90,91),(600,601),(630,631))
FLOATS=("source_gap_ms","monotonic_ms","mean_a","mean_b","std_a",
        "std_b","tile_std_a","tile_std_b","tile_corr","delta_mean",
        "delta_abs_mean","delta_rms","tile_delta_rms")
FIXED={"exact_native_GRBG10":"YES","volatile_only":"YES",
       "calibrated_black":"NO","motion_flicker_excluded":"NO",
       "semantic_scene_detail":"UNPROVEN"}
def parse(text:str)->list[dict]:
    data=[]
    for line in text.splitlines():
        if not line.startswith(PREFIX):continue
        kv={}
        for t in line[len(PREFIX):].split():
            v=t.split("=",1)
            if len(v)!=2 or v[0] in kv:raise ValueError("BAD_OR_DUPLICATE_SOURCE_RAW10_PAIR_TOKEN")
            kv[v[0]]=v[1]
        if not all(kv.get(k)==v for k,v in FIXED.items()):
            raise ValueError("NATIVE_FORMAT_PRIVACY_OR_INTERPRETATION_DRIFT")
        if set(kv)!=set(FIXED)|set(FLOATS)|{"frame_a","frame_b","seq_a","seq_b","blocks"}:
            raise ValueError("UNEXPECTED_SOURCE_PAIR_METRIC_KEYS")
        v={k:float(kv[k]) for k in FLOATS}
        v.update({k:int(kv[k]) for k in ("frame_a","frame_b","seq_a","seq_b","blocks")})
        if any(not math.isfinite(v[k]) for k in FLOATS):raise ValueError("NONFINITE_REAL_RAW10_METRIC")
        if (not 0<v["source_gap_ms"]<=500 or v["monotonic_ms"]<=0 or
            v["blocks"]<1000 or v["seq_b"]!=v["seq_a"]+1 or
            v["frame_b"]!=v["frame_a"]+1 or
            not -1<=v["tile_corr"]<=1 or
            any(v[k]<0 for k in ("std_a","std_b","tile_std_a","tile_std_b",
                                "delta_abs_mean","delta_rms","tile_delta_rms")) or
            v["delta_abs_mean"]>v["delta_rms"]+0.0001):
            raise ValueError("UNTRUSTED_SOURCE_SEQUENCE_OR_TEMPORAL_METRIC")
        data.append(v)
    if [(d["frame_a"],d["frame_b"]) for d in data]!=list(STAGES):
        raise ValueError("MISSING_OR_DUPLICATED_REQUIRED_REAL_RAW10_FRAME_PAIRS")
    if any(a["monotonic_ms"]>=b["monotonic_ms"] for a,b in zip(data,data[1:])):
        raise ValueError("RAW10_SOURCE_FRAME_PAIR_TIME_ORDER_MISMATCH")
    return data

def validate(output:Path)->dict:
    selector=json.loads((output/"RGB-SELECTOR-ACCEPTANCE.json").read_text())
    if (selector.get("status")!="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K" or
        selector.get("camera_order")!=["front","rear"]):
        raise ValueError("REAL_RGB_SELECTOR_NOT_PASSED")
    c=selector["gain_trials"]["rear"]
    if (c["baseline_controls"]!={"exposure":1600,"analogue_gain":128,"digital_gain":1024} or
        c["modified_controls"]!={"exposure":3200,"analogue_gain":512,"digital_gain":2048} or
        c["restored_controls"]!=c["baseline_controls"] or
        c["driver_supported_v4l2_controls_only"] is not True):
        raise ValueError("REAL_REAR_CONTROL_READBACK_AND_EXACT_RESTORE_REQUIRED")
    log=(output/"rear-SERVICE-STDERR.txt").read_text()
    pairs=parse(log)
    if (pairs[0]["monotonic_ms"]>=float(c["first_changed_ms"]) or
        any(not float(c["settled_ms"])+300.<=p["monotonic_ms"]<float(c["restore_started_ms"])-30.
            for p in pairs[1:])):
        raise ValueError("ACTUAL_RAW10_BASELINE_VS_GAIN_TIME_WINDOWS_NOT_PROVEN")
    if "E004MV_RAW10_TEMPORAL_FINAL pairs=3 volatile_source_buffer_cleared=YES optical_pixels_saved=NO" not in log:
        raise ValueError("VOLATILE_SOURCE_RELEASE_OR_REAL_PAIR_COUNT_NOT_PROVEN")
    return {"status":"PASS_REAL_REAR_THREE_BOUNDED_SAME_BOOT_NATIVE_FULL10_RAW10_GREEN_TEMPORAL_PAIRS",
            "baseline_frame_pair":[90,91],"gain_frame_pairs":[[600,601],[630,631]],
            "pairs":pairs,"same_exact_native_controls_inside_each_pair":True,
            "all_SOURCE_mmap_frame_sequence_gaps":0,
            "physical_scene_motion_or_illumination_flicker_excluded":False,
            "physical_fixed_pattern_noise_vs_real_object_identified":False,
            "calibrated_optical_black_or_true_snr_proven":False,
            "image_bytes_pixels_tiles_hashes_exported":False,
            "sensor_control_or_IR_or_FPS_changed_by_temporal_meter":False}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("OUTPUT_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True,indent=2))
