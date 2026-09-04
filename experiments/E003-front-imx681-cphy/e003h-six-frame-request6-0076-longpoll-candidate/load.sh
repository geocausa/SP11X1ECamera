#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
D=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$B/qcom-camss.ko" e003h_pix_runtime_arm=1
sudo -n insmod "$B/imx681.ko"
test -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
echo 'PASS: exact 0074 CAMSS + IMX681 loaded; no stream executed'
