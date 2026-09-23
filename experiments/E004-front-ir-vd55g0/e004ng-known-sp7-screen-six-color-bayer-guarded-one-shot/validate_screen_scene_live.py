#!/usr/bin/env python3
"""New-screen rear4K source IQ structural gate, NOT a dark corner tone test.

Uses only actual scalar source/event logs and independent ordinary
unprivileged RGB app metadata. Does NOT inspect/send/store pixels,
RAW, photographs, thumbnails, image hashes or spatial grids.
A bright region is not proof of SP7 screen content or Windows parity.
"""
from __future__ import annotations
import json,math,re,sys
from pathlib import Path
from validate_rear_temporal_live import gain_window_fps

CAMS={"front":(1920,1080),"rear":(3840,2160)}
CAMERA_SAMPLES=(1,30,90,180,600,630)
GAIN_FRAMES=(600,630)
FRONT_GAIN_RATE_FRAMES=(570,600,630,660,690)

def parse_tone(log:str,camera:str)->dict:
    if camera not in CAMS:raise ValueError("CAMERA_UNEXPECTED")
    prefix=f"E004NG_{camera.upper()}_PREVIEW_TONE frame="
    records={}
    for line in log.splitlines():
        if not line.startswith(prefix):continue
        fields={}
        for field in line.split()[1:]:
            if "=" not in field:raise ValueError("INVALID_REAL_TONE_SCALAR")
            k,v=field.split("=",1)
            if k in fields:raise ValueError("DUPLICATE_REAL_TONE_SCALAR_FIELD")
            fields[k]=v
        i=int(fields["frame"])
        if i in records:raise ValueError("DUPLICATE_REAL_TONE_FRAME")
        if camera=="rear":
            for k in ("applied","input_p01","input_p50","input_p99",
                      "output_p01_est","output_p50_est","output_p99_est"):
                fields[k]=int(fields[k])
            if (fields.get("calibrated_black")!="NO" or
                fields.get("recognized_detail")!="NO" or
                fields.get("chroma_unchanged")!="YES" or
                fields.get("sensor_controls_unchanged")!="YES"):
                raise ValueError("OPTICAL_DETAIL_OR_SENSOR_COLOR_CLAIM_NOT_SUPPORTED")
            if not 0<=fields["input_p01"]<=fields["input_p50"]<=fields["input_p99"]<=255:
                raise ValueError("INVALID_GAIN_LUMA_HISTOGRAM")
        else:
            for k in ("applied","p01","p50","p99",
                      "output_p01","output_p50","output_p99"):
                fields[k]=int(fields[k])
            if (fields.get("uv_unchanged")!="1" or
                fields.get("optical_detail_calibrated")!="NO" or
                fields.get("source_RAW10_unchanged")!="YES"):
                raise ValueError("FRONT_SOURCE_OR_CHROMA_NOT_UNCHANGED")
            if not 0<=fields["p01"]<=fields["p50"]<=fields["p99"]<=255:
                raise ValueError("INVALID_FRONT_LUMA_HISTOGRAM")
        records[i]=fields
    if any(i not in records for i in CAMERA_SAMPLES):
        raise ValueError("REAL_FRONT_REAR_REQUIRED_FRAME_LOG_MISSING")
    return records

def native_summary(log:str,camera:str)->dict:
    summaries=[json.loads(s) for s in log.splitlines()
               if s.startswith('{"status":"STOPPED","frames":')
               and '"source_sequence_gaps":' in s]
    if len(summaries)!=1:raise ValueError("REAL_NATIVE_SOURCE_SUMMARY_MISSING")
    s=summaries[0]
    fps=s["frames"]/s["source_span_s"]
    if (s["source_sequence_gaps"]!=0 or s["frames"]<690
        or not 29<=fps<=31.5 or not 0<s["conversion_mean_ms"]<33.3
        or s["raw_pipe_copy"] is not False
        or s["pixel_files_written"] is not False):
        raise ValueError("REAL_NATIVE_SOURCE_RATE_CPU_ZERO_GAPS_OR_PRIVACY_FAILED")
    return {"actual_source_frames":s["frames"],
            "actual_source_fps":fps,
            "source_sequence_gaps":0,
            "source_converter_plus_tone_mean_ms":s["conversion_mean_ms"]}

def front_gain_rate(source:str)->list[float]:
    timestamps={}
    for line in source.splitlines():
        if not line.startswith("E004NG_PAIRED_RAW_NV12 camera=front frame="):continue
        match=re.search(r"\bframe=(\d+) mono_ms=([0-9.]+)",line)
        if not match:raise ValueError("INVALID_REAL_FRONT_TIMESTAMP")
        i=int(match[1])
        if i in FRONT_GAIN_RATE_FRAMES:
            if i in timestamps:raise ValueError("DUPLICATE_REAL_FRONT_GAIN_TIMESTAMP")
            timestamps[i]=float(match[2])
    if set(timestamps)!=set(FRONT_GAIN_RATE_FRAMES):
        raise ValueError("MISSING_REAL_FRONT_GAIN_FRAME_TIMESTAMPS")
    result=[30000.0/(timestamps[b]-timestamps[a])
            for a,b in zip(FRONT_GAIN_RATE_FRAMES,FRONT_GAIN_RATE_FRAMES[1:])]
    if any(not math.isfinite(f) or not 29<=f<=31.5 for f in result):
        raise ValueError("REAL_FRONT_HIGH_GAIN_NATIVE_30FRAME_FPS_INVALID")
    return result

def validate(output:Path)->dict:
    sel=json.loads((output/"RGB-SELECTOR-ACCEPTANCE.json").read_text())
    if (sel["status"]!="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K"
        or sel["camera_order"]!=["front","rear"]
        or sel["verified_reversible_command_sequence"]!=["front","rear","off","quit"]):
        raise ValueError("REAL_RGB_SELECTOR_OR_APPLICATION_LIFECYCLE_FAILED")
    f=sel["gain_trials"]["front"];r=sel["gain_trials"]["rear"]
    if (f["baseline_controls"]!={"exposure":3546,"analogue_gain":0,"digital_gain":256}
        or f["modified_controls"]!={"exposure":3546,"analogue_gain":512,"digital_gain":512}
        or r["baseline_controls"]!={"exposure":1600,"analogue_gain":128,"digital_gain":1024}
        or r["modified_controls"]!={"exposure":3200,"analogue_gain":512,"digital_gain":2048}
        or any(t["restored_controls"]!=t["baseline_controls"] or
               t["driver_supported_v4l2_controls_only"] is not True
               for t in (f,r))):
        raise ValueError("REAL_NATIVE_CONTROLS_MUST_RESTORE_EXACTLY")
    logs={cam:(output/(cam+"-SERVICE-STDERR.txt")).read_text() for cam in CAMS}
    measures={cam:native_summary(logs[cam],cam) for cam in CAMS}
    for camera in CAMS:
        for phase in ("DAYLIGHT","GAIN"):
            app=json.loads((output/(camera.upper()+"-"+phase+"-PROBE.json")).read_text())
            if app["camera"]!=camera or app["effective_uid"]!=1000 or app["frames"]!=90:
                raise ValueError("REAL_ORDINARY_USER_APP_90FRAMES_REQUIRED")
    front=parse_tone(logs["front"],"front")
    rear=parse_tone(logs["rear"],"rear")
    for i in CAMERA_SAMPLES:
        f=front[i]
        if f["applied"]==0 and any(f[k]!=f["output_"+k]
                  for k in ("p01","p50","p99")):
            raise ValueError("FRONT_SAFE_BYPASS_MUST_PRESERVE_LUMA")
    for i in GAIN_FRAMES:
        d=rear[i]
        if (d["input_p99"]<90 or
            d["input_p99"]-d["input_p01"]<25 or
            d["applied"]!=0 or
            any(d["input_"+k]!=d["output_"+k+"_est"]
                for k in ("p01","p50","p99"))):
            raise ValueError("NEW_SCREEN_SCENE_NOT_NONFLAT_OR_SAFE_REAR_TONE_BYPASS_FAILED")
        app=json.loads((output/"REAR-GAIN-PROBE.json").read_text())
        if (app["max_sampled_p99_y"]<90 or
            not all(float(s["p99_y"])>=90 for s in app["sparse_snapshots"])):
            raise ValueError("REAL_REAR_ORDINARY_USER_APP_SCENE_NOT_VISIBLE")
    rear_windows=gain_window_fps(logs["rear"])
    front_windows=front_gain_rate(logs["front"])
    temporal={}
    for line in logs["rear"].splitlines():
        if not line.startswith("E004NG_REAR_LIVE_TEMPORAL frame="):continue
        v={}
        for item in line.split()[1:]:
            if "=" not in item:raise ValueError("BAD_REAL_REAR_TEMPORAL_FIELD")
            k,value=item.split("=",1)
            if k in v:raise ValueError("REPEATED_REAL_REAR_TEMPORAL_FIELD")
            v[k]=value
        i=int(v["frame"])
        if i in temporal:raise ValueError("REPEATED_REAL_REAR_TEMPORAL_FRAME")
        temporal[i]=v
    for i in (600,601,610,630,631,640,650):
        if i not in temporal or (temporal[i]["tone"],temporal[i]["filtered"],
                                 temporal[i]["reset_tone"])!=("0","0","1"):
            raise ValueError("BRIGHT_SCENE_REAR_TEMPORAL_MUST_BYPASS_IF_NO_TONE")
    if not ("E004NG_REAR_LIVE_TEMPORAL_FINAL " in logs["rear"] and
            "all_private_Y_histories_cleared=YES optical_pixels_saved=NO" in logs["rear"]):
        raise ValueError("REAR_VOLATILE_HISTORY_NOT_CLEARED")
    return {"status":"PASS_E004NG_REAL_NEW_SCREEN_REAR_NONFLAT_SAFE_TONE_BYPASS_FRONT_REAR_UID1000_NATIVE_29FPS",
       "new_rear_scene_screen_identity_or_actual_text_recognized":False,
       "front_native":measures["front"],
       "rear_native":measures["rear"],
       "rear_real_gain_source_Y_p01_p50_p99":
           [[rear[i][k] for k in ("input_p01","input_p50","input_p99")]
             for i in GAIN_FRAMES],
       "rear_screen_like_bright_nonflat_region_p99_ge90_spread_ge25":True,
       "rear_high_gain_tone_and_temporal_safely_bypassed":True,
       "front_gain_tone_may_bypass_when_front_scene_dark_not_a_front_IQ_pilot":True,
       "real_rear_native_30frame_gain_fps":rear_windows,
       "real_front_native_30frame_gain_fps":front_windows,
       "real_front_and_rear_native_controls_exact_restored":True,
       "actual_both_cameras_UID1000_90frame_app_baseline_and_gain":True,
       "no_optical_pixels_pictures_RAW_frames_thumbnails_or_image_hashes_exported":True,
       "actual_recognizable_screen_detail_colour_chart_white_balance_SNR_Windows_ISP_parity_proven":False,
       "normal_Golden_default_settings_changed":False}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("EXACT_OUTPUT_FOLDER_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True,indent=2))
