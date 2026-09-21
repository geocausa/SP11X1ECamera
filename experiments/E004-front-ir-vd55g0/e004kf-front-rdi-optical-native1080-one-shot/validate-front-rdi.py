#!/usr/bin/env python3
"""E004kf: text-only real front RDI RAW10 -> NV12 GStreamer app validator."""
import re
import sys
from pathlib import Path

SOURCE_BYTES=10368000
NV12_BYTES=3110400
def check(source, meter, converter, app):
    frames=[(int(seq),int(size)) for seq,size in
            re.findall(r"cap dqbuf:\s*\d+ seq:\s*(\d+) bytesused:\s*(\d+)",source)]
    if len(frames)!=8 or any(size!=SOURCE_BYTES for _,size in frames):
        raise ValueError(f"NOT_EIGHT_EXACT_FRONT_RAW10_BUFFERS observed={len(frames)} sizes={[v for _,v in frames]}")
    sequences=[seq for seq,_ in frames]
    if not all(y==x+1 for x,y in zip(sequences,sequences[1:])):
        raise ValueError("FRONT_RDI_CAPTURE_SEQUENCE_NOT_CONSECUTIVE")
    times=[float(x) for x in re.findall(r"\bts:\s*([0-9]+\.[0-9]+)",source)]
    if len(times)!=8 or not all(y>x for x,y in zip(times,times[1:])):
        raise ValueError("NO_EIGHT_MONOTONIC_FRONT_SENSOR_TIMESTAMPS")
    meter_needed=(
        "E004KF_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=8 FULL_FRAMES=8 ",
        "BYTES_IN=82944000 BYTES_OUT=82944000 INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF"
    )
    if any(token not in meter for token in meter_needed):
        raise ValueError("FRONT_RAW_PIPE_METER_NOT_EIGHT_COMPLETE_FRAMES")
    converter_needed=(
       "E004KE_FRONT_RDI_BAYER_TO_NV12=PASS ",
       "SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=8",
       "REAL_SENSOR_PROVEN_BY_CALLER=NO QC10C_DECODED=NO OEM_ISP_PARITY=NO"
    )
    if any(token not in converter for token in converter_needed):
        raise ValueError("FRONT_RAW_BAYER_TO_NV12_CONVERTER_UNVERIFIED")
    app_needed=(
        "E004KF_NV12_APPSRC_CONSUMER=PASS FRAMES=8 REQUESTED_FRAMES=8 ",
        "SIZE=3110400 VIDEO=NV12_1920x1080_30 ",
        "DISTINCT_PAYLOADS_VERIFIED=YES",
        "SYNTHETIC_PTS_ONLY=YES",
    )
    if any(token not in app for token in app_needed):
        raise ValueError("FRONT_APP_EIGHT_COMPLETE_DISTINCT_FRAMES_UNVERIFIED")
    m=re.search(r"SINK_OBSERVED_FPS=([0-9.]+).*?INTERARRIVAL_SAMPLES=(\d+)",app)
    if m is None or int(m.group(2))!=7 or float(m.group(1))<=0:
        raise ValueError("APP_REAL_CALLBACK_TIMING_INVALID")
    fps=7/(times[-1]-times[0])
    return (
      "E004KF_REAL_FRONT_RDI_RAW10_TO_GSTREAMER_NV12_1080P=PASS "
      f"front_sensor=IMX681 source_fourcc=pRAA source_3840x2160_frames=8 "
      f"source_first_last_sequences={sequences[0]}..{sequences[-1]} "
      f"source_hardware_timestamp_fps={fps:.4f} "
      f"source_raw10_pipe_bytes=82944000 app_nv12_1920x1080_frames=8 "
      f"app_observed_callback_fps={m.group(1)} "
      "all_app_frame_payloads_distinct_in_memory=YES "
      "QC10C_DECODED=NO OEM_WINDOWS_ISP_PARITY=NO "
      "VIRTUAL_WEBCAM_NOT_CREATED=YES OPTICAL_IMAGE_FILES=NO"
    )
def main():
    if len(sys.argv)!=5:
        raise SystemExit("USAGE: 4 text-only evidence files")
    try:
        result=check(*(Path(p).read_text() for p in sys.argv[1:]))
    except Exception as err:
        print(f"E004KF_FRONT_RDI_VALIDATION=FAIL {type(err).__name__}: {err}",file=sys.stderr)
        return 1
    print(result)
    return 0
if __name__=="__main__":
    raise SystemExit(main())
