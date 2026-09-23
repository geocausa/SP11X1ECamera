#!/usr/bin/env python3
"""E004kh: physical IMX681 72 raw-to-24 independent front webcam app, text only."""
import argparse
import re
from pathlib import Path

RAW_BYTES=10368000
NV12_BYTES=3110400
SOURCE_FRAMES=72
READER_FRAMES=24

def capture(text,size):
    frames=[(int(seq),int(n)) for seq,n in
        re.findall(r"cap dqbuf:\s*\d+ seq:\s*(\d+) bytesused:\s*(\d+)",text)]
    if any(n!=size for _,n in frames):
        raise ValueError("V4L2_WRONG_FULL_FRAME_BYTE_LENGTH")
    return [seq for seq,_ in frames]

def check(source,raw_meter,converter,virtual,meter,app,publisher_rc,reader_rc):
    ss=capture(source,RAW_BYTES)
    if len(ss)!=SOURCE_FRAMES or ss!=list(range(SOURCE_FRAMES)):
        raise ValueError("PHYSICAL_FRONT_RAW_CAPTURE_NOT_72_CONTIGUOUS")
    times=[float(v) for v in re.findall(r"\bts:\s*([0-9]+\.[0-9]+)",source)]
    if len(times)!=SOURCE_FRAMES or any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError("PHYSICAL_FRONT_TIMESTAMPS_NOT_MONOTONIC_72")
    if ("E004KH_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=72 FULL_FRAMES=72" not in raw_meter or
        "BYTES_IN=746496000 BYTES_OUT=746496000 INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF"
            not in raw_meter):
        raise ValueError("RAW10_METER_72_FRAME_BYTE_ACCOUNTING_FAIL")
    if ("E004KH_FRONT_RDI_BAYER_TO_NV12=PASS " not in converter or
        "SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=72" not in converter or
        "QC10C_DECODED=NO OEM_ISP_PARITY=NO" not in converter):
        raise ValueError("PHYSICAL_SOURCE_CONVERTER_72_NOT_VERIFIED")
    vv=capture(virtual,NV12_BYTES)
    if len(vv)!=READER_FRAMES or len(set(vv))!=len(vv) or any(y<=x for x,y in zip(vv,vv[1:])):
        raise ValueError("INDEPENDENT_STANDARD_V4L2_FRONT_24_NOT_VERIFIED")
    if ("E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=24 FULL_FRAMES=24" not in meter or
        "BYTES_IN=74649600 BYTES_OUT=74649600 INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF"
            not in meter):
        raise ValueError("FRONT_VIRTUAL_READER_PIPE_24_FRAME_BYTE_ACCOUNTING_FAIL")
    for token in (
        "E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=24 REQUESTED_FRAMES=24 ",
        "SIZE=3110400 VIDEO=NV12_1920x1080_30 ",
        "DISTINCT_PAYLOADS_VERIFIED=YES",
        "SYNTHETIC_PTS_ONLY=YES",
    ):
        if token not in app:
            raise ValueError("INDEPENDENT_FRONT_GSTREAMER_APP_24_NOT_VERIFIED")
    m=re.search(r"SINK_OBSERVED_FPS=([0-9.]+).*?INTERARRIVAL_SAMPLES=(\d+)",app)
    if m is None or int(m.group(2))!=23 or float(m.group(1))<=0:
        raise ValueError("APP_MONOTONIC_CALLBACK_TIMING_INVALID")
    if publisher_rc!=0 or reader_rc!=0:
        raise ValueError("READER_OR_PUBLISHER_EXIT_NONZERO")
    missing=sum(max(b-a-1,0) for a,b in zip(vv,vv[1:]))
    physical_fps=(SOURCE_FRAMES-1)/(times[-1]-times[0])
    return (
        "E004KH_REAL_FRONT_1080P_STANDARD_V4L2_INDEPENDENT_APP=PASS "
        f"sensor=IMX681 physical_raw10_source_frames={SOURCE_FRAMES} "
        f"source_hardware_timestamp_fps={physical_fps:.4f} "
        f"source_pipe_bytes={SOURCE_FRAMES*RAW_BYTES} software_nv12_frames={SOURCE_FRAMES} "
        f"independent_v4l2_1080p_frames={READER_FRAMES} "
        f"independent_reader_first_last_sequences={vv[0]}..{vv[-1]} "
        f"independent_reader_missing_sequence_ids={missing} "
        f"reader_meter_full_nv12_bytes={READER_FRAMES*NV12_BYTES} "
        f"gstreamer_app_1080p_complete_frames={READER_FRAMES} "
        f"gstreamer_app_observed_callback_fps={m.group(1)} "
        "all_24_app_payloads_bytewise_distinct_in_memory=YES "
        "QC10C_DECODED=NO OEM_WINDOWS_ISP_PARITY=NO "
        "SOURCE_AND_APP_MEASUREMENT_WINDOWS_DIFFER=YES "
        "SUSTAINED_30FPS_NOT_PROVEN=YES OPTICAL_IMAGE_FILES=NO")
def main():
    p=argparse.ArgumentParser()
    for name in ("source","raw_meter","converter","virtual","meter","app"):
        p.add_argument(name,type=Path)
    p.add_argument("--publisher-rc",type=int,required=True)
    p.add_argument("--reader-rc",type=int,required=True)
    a=p.parse_args()
    try:
        result=check(*(getattr(a,name).read_text() for name in
                       ("source","raw_meter","converter","virtual","meter","app")),
                     a.publisher_rc,a.reader_rc)
    except Exception as exc:
        print(f"E004KH_FRONT_V4L2_VALIDATION=FAIL {type(exc).__name__}: {exc}",
              file=__import__("sys").stderr)
        return 1
    print(result)
    return 0
if __name__=="__main__":
    raise SystemExit(main())
