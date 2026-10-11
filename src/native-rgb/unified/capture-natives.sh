#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# capture-natives.sh <out-dir>: in the daily camera boot, stop the bridges and
# keep the last 6 native NV12 frames (after AE settles) of each camera, private.
set -e
O=$1; D=/var/lib/sp11-camera-daily2; B=/home/geoca/Documents/SP11-PROJECT/02-kernel/libcamera-unified-21
CAM=$B/src/apps/cam/cam
[ -x $CAM ] || exit 1
mkdir -p -m 700 "$O" /dev/shm/sp11cap
systemctl stop sp11-webcam-front sp11-webcam-rear
export LD_LIBRARY_PATH=$D/lib LIBCAMERA_IPA_MODULE_PATH=$D/lib/ipa LIBCAMERA_IPA_PROXY_PATH=$D/lib/proxy LIBCAMERA_LOG_LEVELS='*:ERROR'
for c in rear front; do
  rm -f /dev/shm/sp11cap/*
  if [ $c = rear ]; then H=camss-x1e-rear; else H=camss-x1e; fi
  LIBCAMERA_PIPELINES_MATCH_LIST=$H LIBCAMERA_CAMSS_X1E_TUNING_FILE=$D/tuning/imx681-front.yaml \
    timeout 12 $CAM -c1 --capture=60 -F/dev/shm/sp11cap/$c-#.bin > /dev/null 2>&1 || true
  ls /dev/shm/sp11cap | sort | tail -6 | while read f; do mv /dev/shm/sp11cap/$f "$O/"; done
done
rm -rf /dev/shm/sp11cap
systemctl start sp11-webcam-front sp11-webcam-rear
ls "$O" | wc -l; date -u +%FT%TZ
