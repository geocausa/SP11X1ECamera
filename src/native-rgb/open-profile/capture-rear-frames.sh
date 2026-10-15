#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# capture-rear-frames.sh <out-dir> [frames]: in the daily camera boot, pause the
# webcam bridges, stream the rear camera (rear IPA auto exposure) with cam and
# keep the last 8 native NV12 frames (3840x2160). Output stays private.
set -e
O=$1; N=${2:-90}; D=/var/lib/sp11-camera-daily2; B=/home/geoca/Documents/SP11-PROJECT/02-kernel/libcamera-unified-21
mkdir -p -m 700 "$O" /dev/shm/sp11rear
rm -f /dev/shm/sp11rear/*
systemctl stop sp11-webcam-front sp11-webcam-rear
LD_LIBRARY_PATH=$D/lib LIBCAMERA_IPA_MODULE_PATH=$D/lib/ipa LIBCAMERA_IPA_PROXY_PATH=$D/lib/proxy \
LIBCAMERA_LOG_LEVELS='*:ERROR' LIBCAMERA_PIPELINES_MATCH_LIST=camss-x1e-rear \
  timeout 25 $B/src/apps/cam/cam -c1 --capture=$N -F/dev/shm/sp11rear/rear-#.bin > "$O/cam.txt" 2>&1 || true
ls /dev/shm/sp11rear | sort -V | tail -8 | while read f; do mv /dev/shm/sp11rear/$f "$O/"; done
rm -rf /dev/shm/sp11rear
systemctl start sp11-webcam-front sp11-webcam-rear
ls "$O" | grep -c bin
