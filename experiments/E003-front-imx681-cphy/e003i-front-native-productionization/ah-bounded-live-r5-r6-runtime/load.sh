#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ah-bounded-live-r5-r6-runtime
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$BASE/z-live-3a-runtime/qcom-camss-e003i-y.ko"
sudo -n insmod "$B/imx681.ko"
echo 'PASS: AH exact Z/Y CAMSS + accepted IMX681 loaded; no stream executed'
