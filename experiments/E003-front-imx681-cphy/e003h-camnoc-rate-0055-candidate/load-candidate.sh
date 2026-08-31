#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate
"$NEW/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$NEW/qcom-camss.ko" e003h_pix_runtime_arm=1
sudo -n insmod "$NEW/imx681.ko"
[ -e /sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once ]
[ -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag ]
echo 'PASS: 0055 frozen 0054 modules loaded; trigger unused'
