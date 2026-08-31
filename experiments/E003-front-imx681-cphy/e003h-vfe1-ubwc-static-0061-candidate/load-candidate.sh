#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera; NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-ubwc-static-0061-candidate
"$NEW/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
[ ! -d /sys/module/qcom_camss ]; [ ! -d /sys/module/imx681 ]
sudo -n insmod "$NEW/qcom-camss.ko" e003h_pix_runtime_arm=1; sudo -n insmod "$NEW/imx681.ko"
[ -e /sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once ]; [ -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag ]
echo 'PASS: 0061 UBWC-static parity CAMSS + frozen mode2 IMX681 loaded'
