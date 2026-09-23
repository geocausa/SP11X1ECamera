#!/usr/bin/python3
"""Exact source/converted Y paired-scalar evidence from stopped publishers.

Read-only textual validation. No camera, image, frame, sensor or route access.
Fail closed if source RAW8/Y metrics were not actually emitted for BOTH
separately owned sessions on the candidate.
"""
import json
from pathlib import Path
import sys

FRAMES=(1,30,90,180)
METRICS=("raw_mean8","raw_p95","raw_p99","raw_gt32","nv12_y_mean",
         "nv12_y_p95","nv12_y_p99","nv12_y_gt32")
REQUIRED={"raw8_upper_only":"YES","frame_pair":"YES","pixels_saved":"NO"}

def parse(text:str,camera:str)->list[dict]:
    records=[]
    for line in text.splitlines():
        if not line.startswith("E004MC_PAIRED_RAW_NV12 "):
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
        if not all(k in kv for k in (*METRICS,"frame",
                                    "source_bright_nv12_dark",
                                    "raw_samples","y_samples")):
            raise ValueError("MISSING_SOURCE_CONVERTED_PAIR_METRICS")
        record={"frame":int(kv["frame"])}
        for k in METRICS:
            record[k]=float(kv[k])
        for k in ("raw_samples","y_samples","source_bright_nv12_dark"):
            record[k]=int(kv[k])
        if (record["raw_samples"]<1000 or
            record["raw_samples"]!=4*record["y_samples"] or
            record["source_bright_nv12_dark"] not in (0,1) or
            any(not 0<=record[k]<=255 for k in
                ("raw_mean8","raw_p95","raw_p99",
                 "nv12_y_mean","nv12_y_p95","nv12_y_p99")) or
            any(not 0<=record[k]<=1 for k in ("raw_gt32","nv12_y_gt32"))):
            raise ValueError("UNSAFE_OR_INVALID_SOURCE_FRAME_AGGREGATES")
        records.append(record)
    if tuple(d["frame"] for d in records)!=FRAMES:
        raise ValueError("MISSING_DUPLICATE_OR_REORDERED_PHYSICAL_FRAME_PAIR")
    return records

def validate(output:Path)->dict:
    summary={}
    for camera in ("front","rear"):
        p=output/(camera+"-SERVICE-STDERR.txt")
        r=parse(p.read_text(),camera)
        summary[camera]={
            "same_frame_pairs":r,
            "source_p99_raw8_range":[min(x["raw_p99"] for x in r),
                                     max(x["raw_p99"] for x in r)],
            "converted_p99_y_range":[min(x["nv12_y_p99"] for x in r),
                                      max(x["nv12_y_p99"] for x in r)],
            "source_bright_converted_dark_observed":
                any(x["source_bright_nv12_dark"] for x in r),
            "raw10_low_two_bits_and_sensor_black_level_preserved":False,
            "calibrated_image_quality_or_3a_proven":False}
    return {"status":"PASS_BOUNDED_REAL_PAIRED_SOURCE_RAW8_VS_NV12_SCALAR_FRAMES",
            "camera_results":summary,
            "pixel_files_or_hashes_saved":False,
            "windows_isp_or_visible_scene_parity_proven":False}

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("OUTPUT_DIRECTORY_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),indent=2,sort_keys=True))
