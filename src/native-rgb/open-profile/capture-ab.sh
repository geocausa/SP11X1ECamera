#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-only
# A/B still capture of the front camera in the daily camera boot: pauses both
# webcam bridges, captures 300 fixed-exposure + 300 automatic frames with
# capture-front-still (6 full frames kept per phase), then restarts the bridges.
# Compare two runs with ablate-compare.py 6 <a> <b>.
# usage: capture-ab.sh <outdir>
D=/var/lib/sp11-camera-daily2
OUT=$1
mkdir -p -m 700 "$OUT"
grep -q sp11_camera_daily2=1 /proc/cmdline || { echo 'not camera boot' > "$OUT/exit.txt"; exit 1; }
systemctl stop sp11-webcam-front sp11-webcam-rear
sleep 2
cd "$OUT"
env LD_LIBRARY_PATH=$D/lib LIBCAMERA_IPA_MODULE_PATH=$D/lib/ipa LIBCAMERA_IPA_PROXY_PATH=$D/lib/proxy \
  LIBCAMERA_PIPELINES_MATCH_LIST=camss-x1e LIBCAMERA_IPA_FORCE_ISOLATION=1 LIBCAMERA_LOG_LEVELS='CAMSSX1E:INFO,Camera:INFO' \
  LIBCAMERA_CAMSS_X1E_TUNING_FILE=$D/tuning/imx681-front.yaml SP11_PATTERN_DIR="$OUT" \
  SP11_PATTERN_FRAMES_PER_PHASE=300 SP11_KEEP_PER_PHASE=6 \
  timeout 150 /home/geoca/Documents/SP11-PROJECT/02-kernel/libcamera-front-robust-20/capture-front-still > stdout.txt 2> stderr.txt
echo "exit=$?" > exit.txt
modinfo -F firmware $D/modules/qcom-camss.ko > module-firmware.txt
systemctl start sp11-webcam-front sp11-webcam-rear
