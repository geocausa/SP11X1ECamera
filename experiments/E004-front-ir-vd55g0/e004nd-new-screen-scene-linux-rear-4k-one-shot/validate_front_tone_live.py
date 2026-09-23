#!/usr/bin/env python3
"""Real source/ordinary UID1000 app front1080 opt-in gain tone scalar gate.

No optical pixels/images/files or image hashes in output. The front
RAW10->NV12 same-frame scalar pair is taken BEFORE front display Y tone.
Independent app luminance post-tone is not a claim of real details.
Never alters sensor, IR, camera, boot, Windows or any system settings.
"""
from __future__ import annotations
import json,math,re,sys
from pathlib import Path

FRAMES=(1,30,90,180,600,630)
GAIN_WINDOW=(570,600,630,660,690)
def parse(source:str)->dict:
    frames={}
    for line in source.splitlines():
        if not line.startswith("E004ND_FRONT_PREVIEW_TONE frame="):continue
        vals={}
        for field in line.split()[1:]:
            if "=" not in field:raise ValueError("MALFORMED_REAL_FRONT_TONE_METRIC")
            k,v=field.split("=",1)
            if k in vals:raise ValueError("DUPLICATE_FRONT_TONE_METRIC_FIELD")
            vals[k]=v
        if vals.get("uv_unchanged")!="1" or            vals.get("optical_detail_calibrated")!="NO" or            vals.get("source_RAW10_unchanged")!="YES":
            raise ValueError("FRONT_CHROMA_OR_SENSOR_OR_CLAIM_INVALID")
        i=int(vals["frame"])
        if i in frames:raise ValueError("REPEATED_FRONT_PUBLISHER_FRAME")
        for k in ("seq","applied","p01","p50","p99",
                  "output_p01","output_p50","output_p99"):
            vals[k]=int(vals[k])
        if not 16<=vals["p01"]<=vals["p50"]<=vals["p99"]<=235:
            raise ValueError("FRONT_UNSUPPORTED_VIDEO_RANGE_HISTOGRAM")
        if not 16<=vals["output_p01"]<=vals["output_p50"]<=vals["output_p99"]<=235:
            raise ValueError("FRONT_INVALID_OUTPUT_TONE_RANGE")
        frames[i]=vals
    if any(i not in frames for i in FRAMES):
        raise ValueError("FRONT_BASELINE_OR_GAIN_REAL_SOURCE_TONE_LOG_MISSING")
    for i in (1,30,90,180):
        v=frames[i]
        if v["applied"]!=0 or any(v[k]!=v["output_"+k]
                                    for k in ("p01","p50","p99")):
            raise ValueError("FRONT_BASELINE_MUST_REMAIN_UNTONED")
    for i in (600,630):
        v=frames[i]
        if v["applied"]!=1 or not 20<=v["p01"]<=55 or            not v["p99"]-v["p01"]>=12 or not v["p99"]<=75 or            v["output_p01"]!=100 or v["output_p50"]<100 or            not 140<=v["output_p99"]<=215:
            raise ValueError("FRONT_GAIN_REQUIRED_GATED_DISPLAY_LIFT_NOT_MEASURED")
    return frames

def validate(output:Path)->dict:
    sel=json.loads((output/"RGB-SELECTOR-ACCEPTANCE.json").read_text())
    assert sel["status"]=="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K"
    assert sel["camera_order"]==["front","rear"]
    assert sel["verified_reversible_command_sequence"]==["front","rear","off","quit"]
    trial=sel["gain_trials"]["front"]
    assert trial["baseline_controls"]=={"exposure":3546,"analogue_gain":0,"digital_gain":256}
    assert trial["modified_controls"]=={"exposure":3546,"analogue_gain":512,"digital_gain":512}
    assert trial["restored_controls"]==trial["baseline_controls"]
    source=(output/"front-SERVICE-STDERR.txt").read_text()
    records=parse(source)
    summary=[]
    timestamps={}
    for line in source.splitlines():
        if line.startswith('{"status":"STOPPED","frames":') and '"source_sequence_gaps":' in line:
            summary.append(json.loads(line))
        if line.startswith("E004ND_PAIRED_RAW_NV12 camera=front frame="):
            mt=re.search(r"\bframe=(\d+) mono_ms=([0-9.]+)",line)
            if mt:
                frame=int(mt[1]);ts=float(mt[2])
                if frame in GAIN_WINDOW:
                    if frame in timestamps or not math.isfinite(ts):
                        raise ValueError("DUPLICATED_INVALID_FRONT_NATIVE_TIMESTAMP")
                    timestamps[frame]=ts
    if len(summary)!=1:
        raise ValueError("FRONT_SOURCE_OR_STREAMOFF_SUMMARY_MISSING")
    s=summary[0]
    whole=s["frames"]/s["source_span_s"]
    if s["source_sequence_gaps"]!=0 or not 29.0<=whole<=31.5 or        not 0<s["conversion_mean_ms"]<33.3:
        raise ValueError("FRONT_1080_REAL_FPS_OR_COMBINED_TONE_CPU_BUDGET_FAILED")
    if set(timestamps)!=set(GAIN_WINDOW):
        raise ValueError("FRONT_GAIN_NATIVE_30_FRAME_TIMESTAMPS_MISSING")
    gain_rates=[]
    for a,b in zip(GAIN_WINDOW,GAIN_WINDOW[1:]):
        dt=timestamps[b]-timestamps[a]
        if dt<=0:raise ValueError("FRONT_SOURCE_TIME_REGRESSION")
        fps=30000.0/dt
        if not 29<=fps<=31.5:
            raise ValueError("FRONT_GAIN_NATIVE_30_FRAME_INTERVAL_BELOW_29FPS")
        gain_rates.append(fps)
    for frame in (600,630):
        ts=timestamps[frame]
        if not float(trial["settled_ms"])+100<=ts<=             float(trial["restore_started_ms"])-20:
            raise ValueError("FRONT_TONE_FRAME_OUTSIDE_EXACT_SENSOR_GAIN_WINDOW")
    base=json.loads((output/"FRONT-DAYLIGHT-PROBE.json").read_text())
    gain=json.loads((output/"FRONT-GAIN-PROBE.json").read_text())
    if (base["camera"]!="front" or gain["camera"]!="front" or
        base["effective_uid"]!=1000 or gain["effective_uid"]!=1000 or
        base["frames"]!=90 or gain["frames"]!=90 or
        base["max_sampled_p99_y"]>65 or
        gain["max_sampled_p99_y"]<140 or
        not all(float(v["median_y"])>=95 and float(v["p99_y"])>=140
                    for v in gain["sparse_snapshots"])):
        raise ValueError("ORDINARY_FRONT_APP_REAL_GAIN_BRIGHTNESS_NOT_MEASURED")
    return {"status":"PASS_REAL_FRONT_OPTIN_GAIN_ONLY_TONE_1080P_WITH_UID1000_APP_FPS",
        "native_front_untoned_baseline_and_gain_tone_source_frames":FRAMES,
        "real_gain_source_frames_600_630_after_verified_native_gain":True,
        "actual_front_native_full_session_fps":whole,
        "four_30_frame_real_gain_window_fps":gain_rates,
        "source_sequence_gaps":s["source_sequence_gaps"],
        "combined_front_1080_RAW10_NV12_tone_mean_cpu_ms":s["conversion_mean_ms"],
        "front_baseline_untoned_max_app_p99_y":base["max_sampled_p99_y"],
        "front_gain_toned_min_app_snapshot_p99_y":min(
                            x["p99_y"] for x in gain["sparse_snapshots"]),
        "front_gain_toned_min_app_snapshot_p50_y":min(
                            x["median_y"] for x in gain["sparse_snapshots"]),
        "real_front_source_gain_frame_600_predicted_display_p99":records[600]["output_p99"],
        "actual_exact_native_sensor_controls_restored":True,
        "source_RAW10_unchanged_and_UV_chroma_unchanged":True,
        "real_scene_semantic_detail_colour_fidelity_true_SNR_or_Windows_ISP_parity_proven":False,
        "normal_Golden_front_camera_or_autoexposure_changed":False,
        "optical_pixels_images_thumbnails_RAW_or_image_hashes_exported":False}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("EXACT_SCALAR_OUTPUT_FOLDER_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True,indent=2))
