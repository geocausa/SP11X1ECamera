#!/usr/bin/python3
"""E004ki: read-only fail-closed front/rear physical route switching contract.

Does not activate sensors, create V4L2 nodes, modify the media graph or
boot anything. A physical test requires a NEW isolated one-shot identity.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

LINKS={
 "rear_phy":("msm_csiphy1","msm_csid0",0),
 "rear_rdi":("msm_csid0","msm_vfe0_rdi0",0),
 "front_phy":("msm_csiphy2","msm_csid1",0),
 "front_rdi":("msm_csid1","msm_vfe1_rdi0",0),
 "front_pix":("msm_csid1","msm_vfe1_pix",0),
 "front_cross_rdi":("msm_csid1","msm_vfe0_rdi0",0),
}
PHASES=("neutral","front-rdi-only","rear-only")
VIRTUAL={
 "front-rdi-only":{"name":"SP11-Front-Preview","node":"/dev/video91",
                   "fourcc":"NV12","width":1920,"height":1080,
                   "source_fourcc":"pRAA","source_bytes_per_frame":10368000,
                   "output_bytes_per_frame":3110400},
 "rear-only":{"name":"SP11-Rear-Preview","node":"/dev/video90",
              "fourcc":"NV12","width":3840,"height":2160,
              "source_fourcc":"pgAA","source_bytes_per_frame":14321824,
              "output_bytes_per_frame":12441600},
}

def classify(media_text:str)->tuple[str,dict[str,bool]]:
    if len(re.findall(r"^- entity \d+:",media_text,re.M))!=44:
        raise ValueError("MUST_HAVE_EXACTLY_44_CURRENT_BOOT_MEDIA_ENTITIES")
    flags={}
    for key,(source,target,pad) in LINKS.items():
        section=re.search(rf"^- entity \d+: {re.escape(source)} \("
                          rf".*?(?=^- entity |\Z)",media_text,re.M|re.S)
        if section is None:
            raise ValueError("MISSING_ENTITY_"+source)
        link=re.search(rf'^\s*-> "{re.escape(target)}":{pad} \[([^\]]*)\]\s*$',
                       section.group(0),re.M)
        if link is None:
            raise ValueError("MISSING_MUTABLE_LINK_"+key)
        flags[key]="ENABLED" in {x.strip() for x in link.group(1).split(",")}
    if flags["front_cross_rdi"]:
        raise ValueError("FORBID_CSID1_TO_VFE0_CROSS_INSTANCE_FRONT_ROUTE")
    if flags["front_pix"]:
        raise ValueError("FORBID_FRONT_PIX_QC10C_IN_RAW10_CAMERA_SERVICE")
    rear=flags["rear_phy"] or flags["rear_rdi"]
    front=flags["front_phy"] or flags["front_rdi"]
    if rear and front:
        raise ValueError("REJECT_CONCURRENT_REAR_AND_FRONT_ROUTE")
    if flags["rear_phy"]!=flags["rear_rdi"]:
        raise ValueError("REJECT_PARTIAL_REAR_ROUTE")
    if flags["front_phy"]!=flags["front_rdi"]:
        raise ValueError("REJECT_PARTIAL_FRONT_ROUTE")
    if rear:
        return "rear-only",flags
    if front:
        return "front-rdi-only",flags
    return "neutral",flags

def authorize(before:str,after:str,publisher_stopped:bool,
              reader_stopped:bool)->dict[str,object]:
    """No direct front/rear switch. Establish COMPLETE neutral between modes.

    A camera-capable candidate must independently prove publishers/readers
    have ended and media links are neutral before enabling the other sensor.
    """
    if before not in PHASES or after not in PHASES:
        raise ValueError("INVALID_SOURCE_OR_TARGET_CAMERA_PHASE")
    if before==after:
        raise ValueError("NO_DUPLICATE_CAMERA_PHASE_TRANSITION")
    if before!="neutral" and after!="neutral":
        raise ValueError("CAMERA_MODE_SWITCH_REQUIRES_INTERMEDIATE_NEUTRAL")
    if not publisher_stopped or not reader_stopped:
        raise ValueError("ALL_CAMERA_PRODUCERS_AND_READERS_MUST_BE_STOPPED")
    return {"from":before,"to":after,"publisher_stopped":True,
            "reader_stopped":True,"physical_camera_activated":False,
            "virtual_camera_activated":False,
            "ir_video_and_illumination_permitted":False,
            "persistent_golden_boot_modified":False,
            "front_and_rear_concurrent_streaming_permitted":False}

def full_cycle(snapshots:list[str],stop_proofs:list[tuple[bool,bool]])->dict:
    """Expected snapshots: neutral, front, neutral, rear, neutral."""
    expected=["neutral","front-rdi-only","neutral","rear-only","neutral"]
    if len(snapshots)!=len(expected) or len(stop_proofs)!=4:
        raise ValueError("FRONT_NEUTRAL_REAR_NEUTRAL_CYCLE_LENGTH_INVALID")
    actual=[classify(x)[0] for x in snapshots]
    if actual!=expected:
        raise ValueError("CAMERA_GRAPH_NOT_EXACT_FRONT_NEUTRAL_REAR_NEUTRAL_CYCLE")
    transitions=[authorize(x,y,*stopped)
                 for x,y,stopped in zip(actual,actual[1:],stop_proofs)]
    return {"status":"SOURCE_ONLY_CAMERA_SWITCH_CONTRACT=PASS",
            "verified_media_graph_phases":actual,
            "transition_count":len(transitions),
            "source_only":True,
            "front_device_contract":VIRTUAL["front-rdi-only"],
            "rear_device_contract":VIRTUAL["rear-only"],
            "boot_service_driver_or_sensor_activated":False,
            "real_front_rear_switching_proven":False,
            "golden_persistent_camera_installation_proven":False}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--snapshot",type=Path,action="append",required=True)
    a.add_argument("--all-processes-stopped",action="store_true")
    args=a.parse_args()
    if len(args.snapshot)!=5 or not args.all_processes_stopped:
        raise SystemExit("E004KI_SOURCE_ONLY_EXPECTS_FIVE_GRAPHS_AND_EXPLICIT_IDLE_PROOFS")
    try:
        report=full_cycle([x.read_text(errors="replace") for x in args.snapshot],
                          [(True,True)]*4)
    except ValueError as err:
        raise SystemExit(f"E004KI_SWITCH_CONTRACT=FAIL {err}")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
