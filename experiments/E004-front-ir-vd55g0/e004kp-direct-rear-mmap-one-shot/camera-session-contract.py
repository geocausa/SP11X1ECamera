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

def complete_graph(text: str) -> set[tuple[str,int,str,int]]:
    """Validate all 119 links, both directions, against accepted topology.

    Sensor I2C bus numbers and entity/device numbers are boot-dependent.
    Only sensor names are normalized; pads and graph edges remain exact.
    """
    def canonical(name):
        for sensor,addr in (("imx681","0010"),("ov13858","0010"),
                            ("sp11-vd55g0","0060")):
            if re.fullmatch(rf"{sensor} [0-9]+-{addr}",name):
                return sensor
        return name
    pads={f"msm_csiphy{i}":2 for i in (0,1,2,4)}
    pads.update({f"msm_csid{i}":5 for i in range(5)})
    expected={}
    def edge(a,ap,b,bp,immutable=False):
        expected[(a,ap,b,bp)]=immutable
    for phy in (0,1,2,4):
        for csid in range(5):
            edge(f"msm_csiphy{phy}",1,f"msm_csid{csid}",0)
    for vfe in range(4):
        for port in range(4):
            suffix="pix" if vfe<2 and port==3 else f"rdi{port}"
            capture=f"msm_vfe{vfe}_{suffix}"
            video=f"msm_vfe{vfe}_video{port}"
            pads[capture]=2; pads[video]=1
            edge(capture,1,video,0,True)
            for csid in range(5):
                edge(f"msm_csid{csid}",port+1,capture,0)
    for sensor,phy in (("sp11-vd55g0",0),("ov13858",1),("imx681",2)):
        pads[sensor]=1; edge(sensor,0,f"msm_csiphy{phy}",0,True)
    outgoing={}; incoming={}; entities=set(); ids=set(); devices=set()
    source=None; pad=None; seen_pads=set(); declared_links={}; counts={}
    for line in text.splitlines():
        if line.startswith("- entity "):
            if source is not None and seen_pads!=set(range(pads[source])):
                raise ValueError("INCOMPLETE_ENTITY_PADS")
            m=re.fullmatch(r"- entity (\d+): (.*?) \((\d+) pads?, (\d+) links?(?:, (\d+) routes?)?\)",line)
            if not m: raise ValueError("MALFORMED_ENTITY")
            ident,name,np,nl,nr=m.groups(); source=canonical(name); pad=None
            if ident in ids or source in entities or source not in pads:
                raise ValueError("DUPLICATE_OR_UNEXPECTED_ENTITY")
            if int(np)!=pads[source] or (nr is not None and nr!="0"):
                raise ValueError("UNEXPECTED_PAD_OR_ROUTE_COUNT")
            ids.add(ident); entities.add(source); seen_pads=set()
            declared_links[source]=int(nl); counts[source]=0
        elif "device node name" in line:
            m=re.fullmatch(r"\s*device node name (/dev/(?:v4l-subdev|video)\d+)",line)
            if not m or source is None or m[1] in devices:
                raise ValueError("INVALID_OR_DUPLICATE_DEVICE_NODE")
            devices.add(m[1])
        elif re.match(r"\s*pad\d+:",line):
            m=re.fullmatch(r"\s*pad(\d+): (SINK|SOURCE)",line)
            if not m or source is None: raise ValueError("MALFORMED_PAD")
            pad=int(m[1])
            if pad in seen_pads or pad not in range(pads[source]):
                raise ValueError("DUPLICATE_OR_INVALID_PAD")
            expected_direction="SOURCE" if source in ("imx681","ov13858","sp11-vd55g0") or pad>0 else "SINK"
            if m[2]!=expected_direction: raise ValueError("WRONG_PAD_DIRECTION")
            seen_pads.add(pad)
        elif "->" in line or "<-" in line:
            m=re.fullmatch(r'\s*(->|<-) "([^"]+)":(\d+) \[([^\]]*)\]',line)
            if not m or source is None or pad is None:
                raise ValueError("MALFORMED_LINK")
            arrow,target,tp,raw=m.groups(); target=canonical(target); tp=int(tp)
            tokens=[] if not raw else raw.split(",")
            if len(tokens)!=len(set(tokens)) or set(tokens)-{"ENABLED","IMMUTABLE"}:
                raise ValueError("UNEXPECTED_LINK_FLAGS")
            flags=frozenset(tokens)
            key=(source,pad,target,tp) if arrow=="->" else (target,tp,source,pad)
            table=outgoing if arrow=="->" else incoming
            if key in table: raise ValueError("DUPLICATE_LINK")
            table[key]=flags; counts[source]+=1
    if source is None or seen_pads!=set(range(pads[source])):
        raise ValueError("INCOMPLETE_ENTITY_PADS")
    if entities!=set(pads) or len(devices)!=44 or declared_links!=counts:
        raise ValueError("INCOMPLETE_GRAPH_ENTITIES_DEVICES_OR_LINK_COUNTS")
    if outgoing!=incoming or set(outgoing)!=set(expected):
        raise ValueError("INCOMPLETE_OR_ASYMMETRIC_GRAPH_LINKS")
    enabled=set()
    for key,immutable in expected.items():
        flags=outgoing[key]
        if immutable:
            if flags!={"ENABLED","IMMUTABLE"}:
                raise ValueError("IMMUTABLE_LINK_DRIFT")
        else:
            if "IMMUTABLE" in flags: raise ValueError("MUTABLE_LINK_FALSIFIED")
            if "ENABLED" in flags: enabled.add(key)
    allowed={
        "neutral":set(),
        "front-rdi-only":{("msm_csiphy2",1,"msm_csid1",0),
                          ("msm_csid1",1,"msm_vfe1_rdi0",0)},
        "rear-only":{("msm_csiphy1",1,"msm_csid0",0),
                     ("msm_csid0",1,"msm_vfe0_rdi0",0)},
    }
    if enabled not in allowed.values():
        raise ValueError("UNAUTHORIZED_ENABLED_ROUTE_IN_COMPLETE_GRAPH")
    return enabled


def classify(media_text:str)->tuple[str,dict[str,bool]]:
    if len(re.findall(r"^- entity \d+:",media_text,re.M))!=44:
        raise ValueError("MUST_HAVE_EXACTLY_44_CURRENT_BOOT_MEDIA_ENTITIES")
    complete_graph(media_text)
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
    if len(args.snapshot)!=3 or not args.all_processes_stopped:
        raise SystemExit("E004KP_EXPECTS_THREE_GRAPHS_AND_EXPLICIT_IDLE_PROOFS")
    actual=[classify(x.read_text())[0] for x in args.snapshot]
    if actual!=["neutral","rear-only","neutral"]:
        raise SystemExit("E004KP_REJECT_GRAPH_CYCLE")
    for before,after in zip(actual,actual[1:]):
        authorize(before,after,True,True)
    print(json.dumps({"status":"PASS","verified_media_graph_phases":actual,
                      "all_processes_stopped":True,"ir_or_front_streaming":False}))
if __name__=="__main__":main()
