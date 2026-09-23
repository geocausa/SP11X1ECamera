#!/usr/bin/env python3
"""Camera-free strict six-frame full RAW10 scalar profiling contract.

Takes only private publisher stderr text, never a pixel plane or device.
Fails closed on partial/truncated/mislabelled source, wrong Bayer channel
sample counts or invalid bit distributions. Does NOT infer image quality.
"""
import json
from pathlib import Path
import sys

FRAMES=(1,30,90,180,600,630)
CHANNELS=("R","G0","G1","B")
BLOCKS={"front":8160,"rear":11264}
PERCENTILES=("p01","p50","p95","p99")

def validate(folder:Path)->dict:
    result={"status":"INCOMPLETE_FAIL_CLOSED","cameras":{}}
    for camera,blocks in BLOCKS.items():
        path=folder/(camera+"-SERVICE-STDERR.txt")
        observations={}
        for line in path.read_text().splitlines():
            if not line.startswith("SP11_RGB_RAW10_PROFILE "):
                continue
            parts=line.split()
            fields={}
            for item in parts[1:]:
                if item.count("=")!=1:
                    raise ValueError("INVALID_PROFILE_FIELD_SYNTAX")
                name,value=item.split("=",1)
                if not name or name in fields:
                    raise ValueError("DUPLICATE_PROFILE_FIELD")
                fields[name]=value
            if fields.get("camera")!=camera:
                raise ValueError("UNKNOWN_OR_WRONG_CAMERA")
            if set(fields)!={"camera","frame","blocks"}|{
                    f"{c}_{m}" for c in CHANNELS for m in
                    (*PERCENTILES,"min","max","lsb0","lsb1","lsb2","lsb3")}:
                raise ValueError("MISSING_OR_UNEXPECTED_PROFILE_METRIC")
            frame=int(fields["frame"])
            if frame not in FRAMES or frame in observations or int(fields["blocks"])!=blocks:
                raise ValueError("INVALID_OR_DUPLICATE_RAW10_SOURCE_FRAME")
            channels={}
            for c in CHANNELS:
                metric={m:int(fields[c+"_"+m]) for m in
                    (*PERCENTILES,"min","max","lsb0","lsb1","lsb2","lsb3")}
                ordered=[metric[k] for k in ("min",*PERCENTILES,"max")]
                if not all(0<=n<=1023 for n in ordered) or ordered!=sorted(ordered):
                    raise ValueError("INVALID_FULL10_BIT_CHANNEL_DISTRIBUTION")
                bits=[metric[f"lsb{k}"] for k in range(4)]
                if any(n<0 or n>blocks for n in bits) or sum(bits)!=blocks:
                    raise ValueError("LOW_BITS_OR_BAYER_SAMPLE_COUNT_INVALID")
                channels[c]=metric
            observations[frame]=channels
        if tuple(sorted(observations))!=FRAMES:
            raise ValueError("REQUIRED_SAME_SOURCE_SPARSE_FRAMES_MISSING_"+camera)
        result["cameras"][camera]={"expected_native_bayer_blocks_per_frame":blocks,
          "profiled_source_frames":list(FRAMES),"channels_per_frame":observations,
          "pixels_or_images_exported":False}
    result["status"]="PASS_SIX_SPARSE_SAME_SOURCE_FULL10_RAW_BAYER_CHANNEL_PROFILES_FRONT_REAR"
    result["ir_or_illumination_touched"]=False
    result["recognizable_scene_or_colour_accuracy_proven"]=False
    return result

if __name__=="__main__":
    assert len(sys.argv)==2
    try:
        print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True))
    except (OSError,ValueError,KeyError) as exc:
        print(json.dumps({"status":"FAIL_CLOSED","reason":str(exc)[:200]}))
        raise SystemExit(1)
