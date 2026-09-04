#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate
D=$R/experiments/E003-front-imx681-cphy/e003h-0075a-hardened-0072-control
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$B/qcom-camss.ko" e003h_pix_runtime_arm=1
sudo -n insmod "$B/imx681.ko"
test -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
echo 'PASS: exact accepted 0072 modules loaded'
