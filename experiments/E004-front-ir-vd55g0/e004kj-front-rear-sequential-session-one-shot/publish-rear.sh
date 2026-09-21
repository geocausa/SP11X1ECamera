#!/usr/bin/env bash
REARVIDEO=$1
O=$2
BRIDGE_BIN=$3
LOOP_DEV=$4
  set +e
  timeout --foreground --signal=TERM --kill-after=3s 75s bash -o pipefail -c '
    v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=240 --stream-to=- --verbose 2>"$2" |
      "$3" --frames 240 2>"$4" |
      gst-launch-1.0 -q fdsrc fd=0 blocksize=12441600 \
        ! rawvideoparse format=nv12 width=3840 height=2160 framerate=30/1 \
        ! "video/x-raw,format=NV12,width=3840,height=2160,framerate=30/1" \
        ! v4l2sink device="$5" sync=true qos=true max-lateness=-1 >"$6" 2>&1
  ' bash "$REARVIDEO" "$O/REAL-REAR-CAPTURE240.txt" \
    "$BRIDGE_BIN" "$O/REAL-REAR-CONVERT240.txt" "$LOOP_DEV" \
    "$O/REAL-REAR-TO-VIRTUAL-PUBLISHER.txt"
  publisher_inner_rc=$?
  # Record true process completion BEFORE the later subscriber wait/reap.
  printf 'PUBLISHER_END_NS=%s\n' "$(date +%s%N)" > "$O/REAR-4K-PUBLISHER-DONE.txt"
  exit "$publisher_inner_rc"
