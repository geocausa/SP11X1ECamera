#!/usr/bin/python3
"""Strict camera-free analysis of physical same-frame RAW8/NV12 Y before
and after the finite uniquely guarded supported RGB gain/exposure trial.

Monotonic ms timestamps align the C publisher and Python sensor-control
driver with CLOCK_MONOTONIC, while each publisher owns the SAME mmap RAW
frame until scalar luma conversion is sampled and source QBUF completes.
Only aggregate statistics and bounded control metadata are persisted.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys

FIRST=(1,30,90,180)
METRICS=("raw_mean8","raw_p95","raw_p99","raw_gt32","nv12_y_mean",
         "nv12_y_p95","nv12_y_p99","nv12_y_gt32")
REQUIRED={"raw8_upper_only":"YES","frame_pair":"YES","pixels_saved":"NO"}


def parse(text:str,camera:str)->list[dict]:
    records=[]
    for line in text.splitlines():
        if not line.startswith("E004MY_PAIRED_RAW_NV12 "):
            continue
        kv={}
        for token in line.split()[1:]:
            pair=token.split("=",1)
            if len(pair)!=2 or pair[0] in kv:
                raise ValueError("BAD_PAIRED_METRIC_TOKEN")
            kv[pair[0]]=pair[1]
        if kv.get("camera")!=camera:
            raise ValueError("WRONG_CAMERA_IN_PAIRED_METRIC")
        if any(kv.get(k)!=v for k,v in REQUIRED.items()):
            raise ValueError("PIXELS_OR_SOURCE_PAIR_CONTRACT_NOT_MET")
        if not all(k in kv for k in (*METRICS,"frame","mono_ms",
              "source_bright_nv12_dark","raw_samples","y_samples")):
            raise ValueError("MISSING_SOURCE_CONVERTED_PAIR_METRICS")
        r={"frame":int(kv["frame"]),"mono_ms":float(kv["mono_ms"])}
        for k in METRICS:r[k]=float(kv[k])
        for k in ("raw_samples","y_samples","source_bright_nv12_dark"):
            r[k]=int(kv[k])
        if (not math.isfinite(r["mono_ms"]) or r["mono_ms"]<=0 or
            any(not math.isfinite(r[k]) for k in METRICS) or
            r["raw_samples"]<1000 or
            r["raw_samples"]!=4*r["y_samples"] or
            r["source_bright_nv12_dark"] not in (0,1) or
            any(not 0<=r[k]<=255 for k in
                ("raw_mean8","raw_p95","raw_p99","nv12_y_mean",
                 "nv12_y_p95","nv12_y_p99")) or
            any(not 0<=r[k]<=1 for k in ("raw_gt32","nv12_y_gt32"))):
            raise ValueError("INVALID_REAL_SOURCE_FRAME_AGGREGATES")
        records.append(r)
    if tuple(r["frame"] for r in records[:4])!=FIRST or len(records)<7:
        raise ValueError("MISSING_REQUIRED_INITIAL_OR_GAIN_RESPONSE_PAIRS")
    if any(r["frame"]!=FIRST[i] if i<4 else
           r["frame"]<=180 or r["frame"]>3600 or r["frame"]%30!=0
           for i,r in enumerate(records)):
        raise ValueError("PAIRED_FRAME_SAMPLING_IDENTITY_DRIFT")
    if any(a["frame"]>=b["frame"] or a["mono_ms"]>=b["mono_ms"]
           for a,b in zip(records,records[1:])):
        raise ValueError("SOURCE_FRAME_OR_MONOTONIC_TIMESTAMP_REORDERED")
    return records


def validate(output:Path)->dict:
    summary={}
    selector=json.loads((output/"RGB-SELECTOR-ACCEPTANCE.json").read_text())
    if selector.get("status")!="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K":
        raise ValueError("RGB_GAIN_TRIAL_SELECTOR_NOT_PROVEN_PASS")
    for camera in ("front","rear"):
        trial=selector["gain_trials"][camera]
        records=parse((output/(camera+"-SERVICE-STDERR.txt")).read_text(),camera)
        pre=records[:4]
        start=float(trial["settled_ms"])+300.
        end=float(trial["restore_started_ms"])-30.
        post=[r for r in records if start<=r["mono_ms"]<=end]
        if (len(post)<2 or end<=start or
            pre[-1]["mono_ms"]>=float(trial["first_changed_ms"]) or
            trial["restored_controls"]!=trial["baseline_controls"] or
            trial["modified_controls"]==trial["baseline_controls"] or
            trial["driver_supported_v4l2_controls_only"] is not True):
            raise ValueError("PRE_POST_RGB_GAIN_WINDOW_OR_CONTROL_RESTORE_NOT_PROVEN")
        def avg(rows,key):
            return round(sum(r[key] for r in rows)/len(rows),4)
        before=avg(pre,"raw_p99")
        after=avg(post,"raw_p99")
        y_before=avg(pre,"nv12_y_p99")
        y_after=avg(post,"nv12_y_p99")
        summary[camera]={
            "baseline_source_frames":[r["frame"] for r in pre],
            "post_gain_source_frames":[r["frame"] for r in post],
            "baseline_mean_raw_upper8_p99":before,
            "after_gain_mean_raw_upper8_p99":after,
            "raw_upper8_p99_delta":round(after-before,4),
            "baseline_mean_converted_nv12_y_p99":y_before,
            "after_gain_mean_converted_nv12_y_p99":y_after,
            "converted_nv12_y_p99_delta":round(y_after-y_before,4),
            "app_p99_y_before":trial["baseline_app"]["p99_y"],
            "app_p99_y_after":trial["gain_changed_app"]["p99_y"],
            "sensor_control_pre_changed_restored":trial,
            "gain_response_measured_in_source":abs(after-before)>=2.,
            "gain_response_measured_in_app":
                abs(trial["effect_on_app_p99_y"])>=2.,
            "all_source_frames_aggregate_only":True,
            "raw10_low_two_bits_and_black_level_calibrated":False}
    return {"status":"PASS_BOUNDED_SUPPORTED_RGB_SENSOR_GAIN_CONTROL_RESPONSE_MEASURED",
            "camera_results":summary,
            "positive_sensor_gain_image_response_required_to_pass_test":False,
            "visible_scene_or_windows_IQ_parity_proven":False,
            "pixel_files_or_hashes_saved":False}


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("OUTPUT_DIRECTORY_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),indent=2,sort_keys=True))
