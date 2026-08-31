#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate; CAMSS=$NEW/qcom-camss.ko; SENSOR=$NEW/imx681.ko
"$NEW/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$CAMSS" e003h_pix_runtime_arm=1
sudo -n insmod "$SENSOR"
[ -e /sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once ]; [ -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag ]
echo 'PASS: 0058 exact frozen 0057 CAMSS + mode2 IMX681 loaded; no programming delta'
