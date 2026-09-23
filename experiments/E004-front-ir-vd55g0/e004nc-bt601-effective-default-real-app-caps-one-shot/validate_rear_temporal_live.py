#!/usr/bin/env python3
"""Text-only actual native source rear 4K opt-in filter acceptance.

Every metric is a scalar log from one authentic candidate physical
session; no images, photo hashes, RAW buffers, implicit AE, color/SNR or
moving-subject quality assertions. This parser cannot enable cameras.
"""
from __future__ import annotations
import json,math,re,sys
from pathlib import Path

REQUIRED=(600,601,610,630,631,640,650)
def parse(log:str)->dict:
    records={}
    for line in log.splitlines():
        if not line.startswith("E004NC_REAR_LIVE_TEMPORAL frame="):continue
        kv={}
        for tok in line.split()[1:]:
            a=tok.split("=",1)
            if len(a)!=2 or a[0] in kv:raise ValueError("DUPLICATE_OR_BAD_METRIC_TOKEN")
            kv[a[0]]=a[1]
        if kv.get("uv_unchanged")!="1" or kv.get("motion_detail_calibrated")!="NO" or            kv.get("prior_Y_buffers_volatile_only")!="YES":
            raise ValueError("PRIVATE_BUFFER_OR_CHROMA_OR_QUALITY_CLAIM_DRIFT")
        f=int(kv["frame"])
        if f in records:raise ValueError("DUPLICATE_REAL_PUBLISHER_FRAME")
        for field in ("tone","seeded","filtered","reset_scene","reset_seq",
                      "reset_tone","median","blocks_filtered","blocks_bypassed",
                      "pixels_changed","sample_count","seq"):
            kv[field]=int(kv[field])
        for field in ("unfiltered_consecutive_RMS",
                      "input_to_previous_filtered_RMS",
                      "output_to_previous_filtered_RMS",
                      "sampled_global_abs_delta",
                      "sampled_high_motion_fraction"):
            kv[field]=float(kv[field])
            if not math.isfinite(kv[field]) or kv[field]<0:
                raise ValueError("NONFINITE_OR_NEGATIVE_FRAME_SCALAR")
        records[f]=kv
    if any(f not in records for f in REQUIRED):
        raise ValueError("MISSING_PRE_POST_REAL_GAIN_FRAME_METRIC")
    for f in (1,30,90,180):
        if f not in records or records[f]["tone"]!=0 or            records[f]["filtered"]!=0 or records[f]["reset_tone"]!=1:
            raise ValueError("BASELINE_MUST_BYPASS_TEMPORAL_FILTER")
    for f in REQUIRED:
        d=records[f]
        if d["tone"]!=1 or d["filtered"]!=1 or d["sample_count"]<1000 or            d["blocks_filtered"]==0 or d["blocks_bypassed"]<0 or            d["reset_tone"]!=0 or d["reset_scene"]!=0 or            d["output_to_previous_filtered_RMS"] >              d["input_to_previous_filtered_RMS"]+0.001:
            raise ValueError("REAL_BOUNDED_GAIN_TEMPORAL_FILTER_NOT_STABLE")
    m=re.search(r"E004NC_REAR_LIVE_TEMPORAL_FINAL filtered_frames=([0-9]+) "
                r"paired_before_after_frames=([0-9]+) "
                r"filter_cpu_mean_ms=([0-9.]+) "
                r"all_private_Y_histories_cleared=YES optical_pixels_saved=NO",log)
    if not m:raise ValueError("VOLATILE_ONE_FRAME_HISTORY_NOT_CLEARED")
    filtered,paired=int(m[1]),int(m[2])
    cpu=float(m[3])
    if filtered<30 or paired<30 or not math.isfinite(cpu) or not 0<cpu<15:
        raise ValueError("INSUFFICIENT_REAL_TEMPORAL_FRAMES_OR_CPU_BUDGET")
    return {"records":records,"filtered_frames":filtered,
            "paired_before_after_frames":paired,"cpu_mean_ms":cpu}

def gain_window_fps(source:str)->list[float]:
    # A slow 4K rear stream during the actual high-gain exposure must
    # never pass just because earlier unfiltered baseline frames were
    # faster. Require independent native source mono_ms samples at
    # exactly 570,600,630,660,690; each spans 30 source frame counts.
    frames=(570,600,630,660,690)
    timestamps={}
    for line in source.splitlines():
        if not line.startswith("E004NC_PAIRED_RAW_NV12 camera=rear frame="):
            continue
        match=re.search(r"\bframe=(\d+) mono_ms=([0-9.]+)",line)
        if not match:raise ValueError("MALFORMED_NATIVE_SOURCE_MONOTONIC_PROBE")
        frame=int(match[1]);value=float(match[2])
        if frame in frames:
            if frame in timestamps or not math.isfinite(value):
                raise ValueError("DUPLICATE_OR_NONFINITE_GAIN_SOURCE_TIMESTAMP")
            timestamps[frame]=value
    if set(timestamps)!=set(frames):
        raise ValueError("MISSING_NATIVE_30FRAME_GAIN_WINDOW_PROBE")
    rates=[]
    for a,b in zip(frames,frames[1:]):
        diff=timestamps[b]-timestamps[a]
        if diff<=0:raise ValueError("OUT_OF_ORDER_NATIVE_SOURCE_TIMESTAMPS")
        fps=30000.0/diff
        if fps<29.0 or fps>31.5:
            raise ValueError("ACTUAL_REAR_GAIN_30FRAME_WINDOW_BELOW_STRICT_29FPS_OR_INVALID")
        rates.append(fps)
    return rates

def validate(output:Path)->dict:
    selector=json.loads((output/"RGB-SELECTOR-ACCEPTANCE.json").read_text())
    if selector.get("status")!="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K" or        selector.get("camera_order")!=["front","rear"]:
        raise ValueError("REAL_FRONT_REAR_SELECTOR_AND_UID1000_APPS_NOT_PASSED")
    control=selector["gain_trials"]["rear"]
    if control["baseline_controls"]!={"exposure":1600,"analogue_gain":128,"digital_gain":1024} or        control["modified_controls"]!={"exposure":3200,"analogue_gain":512,"digital_gain":2048} or        control["restored_controls"]!=control["baseline_controls"]:
        raise ValueError("NATIVE_SENSOR_READBACK_EXACT_CONTROL_RESTORE_REQUIRED")
    source=(output/"rear-SERVICE-STDERR.txt").read_text()
    record=parse(source)
    high_gain_fps=gain_window_fps(source)
    summary=[]
    for line in source.splitlines():
        if line.startswith('{"status":"STOPPED","frames":') and '"source_sequence_gaps":' in line:
            summary.append(json.loads(line))
    if len(summary)!=1 or summary[0]["source_sequence_gaps"]!=0 or        not 29.0<=summary[0]["frames"]/summary[0]["source_span_s"]<=31.5 or        not 0<summary[0]["conversion_mean_ms"]<33.3:
        raise ValueError("ACTUAL_REAR_SOURCE_CONTINUITY_OR_COMBINED_4K_CPU_BUDGET_FAILED")
    # Only frame600 and frame630 have independent paired RAW10 native
    # monotonic timestamp. Do NOT interpolate remaining log timestamps.
    for f in (600,630):
        actual=source_timestamp(output,f)
        if not float(control["settled_ms"])+100<=actual<=                 float(control["restore_started_ms"])-20:
            raise ValueError("NATIVE_SOURCE_FRAME_OUTSIDE_EXACT_SENSOR_GAIN_WINDOW")
    gain=[record["records"][i] for i in REQUIRED]
    return {"status":"PASS_E004NC_REAL_OPTIN_REAR_TEMPORAL_FRONT_REAR_UID1000_4K_FRAME_CADENCE",
            "source":"actual_NATIVE_4K_rear_sensor_and_named_unprivileged_RGB_app",
            "frame_samples":[{k:v for k,v in d.items() if k not in
                     ("prior_Y_buffers_volatile_only","motion_detail_calibrated")}
                     for d in gain],
            "baseline_bypass_verified":True,"reported_mean_filter_cpu_ms":record["cpu_mean_ms"],
            "combined_mean_convert_filter_ms":summary[0]["conversion_mean_ms"],
            "raw_source_fps":summary[0]["frames"]/summary[0]["source_span_s"],
            "measured_actual_rear_high_gain_30frame_fps":high_gain_fps,
            "zero_native_source_frame_sequence_gaps":True,
            "actual_real_gain_control_readback_and_restoration":True,
            "sensor_autoexposure_registered_or_approved":False,
            "colour_fidelity_true_noise_SNR_object_recognition_or_motion_safety_proven":False,
            "source_photos_pixels_thumbnails_hashes_or_private_Y_buffers_exported":False,
            "windows_isp_parity_or_user_default_Golden_change":False}

def source_timestamp(output:Path,frame:int)->float:
    for line in (output/"rear-SERVICE-STDERR.txt").read_text().splitlines():
        if line.startswith("E004NC_PAIRED_RAW_NV12 camera=rear frame="+str(frame)+" "):
            m=re.search(r"mono_ms=([0-9.]+)",line)
            if m:return float(m[1])
    raise ValueError("NO_REAL_NATIVE_MONOTONIC_TIMESTAMP_FOR_REQUIRED_RAW10_FRAME")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("EXACT_OUTPUT_PATH_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True,indent=2))
