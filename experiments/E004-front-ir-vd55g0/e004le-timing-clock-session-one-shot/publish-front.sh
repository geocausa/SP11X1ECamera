#!/usr/bin/env bash
FRONTRDIVIDEO=$1
O=$2
FRONT_AUDIT=$3
FRONT_BRIDGE=$4
LOOP_DEV=$5
 set +e
 timeout --foreground --signal=TERM --kill-after=3s 150s bash -o pipefail -c '
   v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=2400 --stream-to=- --verbose 2>"$2" |
     "$3" --frames 2400 --idle-ms 7000 2>"$4" |
     "$5" --frames 2400 2>"$6" |
     gst-launch-1.0 -q fdsrc fd=0 blocksize=3110400 \
       ! rawvideoparse format=nv12 width=1920 height=1080 framerate=30/1 \
       ! "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1" \
       ! v4l2sink device="$7" sync=true qos=true max-lateness=-1 >"$8" 2>&1
 ' bash "$FRONTRDIVIDEO" "$O/REAL-FRONT-RAW2400-CAPTURE.txt" \
   "$FRONT_AUDIT" "$O/FRONT-RAW2400-BYTE-METER.txt" "$FRONT_BRIDGE" \
   "$O/FRONT-NV12-2400-CONVERTER.txt" "$LOOP_DEV" "$O/FRONT-NV12-TO-VIRTUAL-PUBLISHER.txt"
 publisher_inner_rc=$?
 printf 'PUBLISHER_END_NS=%s\n' "$(date +%s%N)" > "$O/FRONT-PUBLISHER-DONE.txt"
 exit "$publisher_inner_rc"
