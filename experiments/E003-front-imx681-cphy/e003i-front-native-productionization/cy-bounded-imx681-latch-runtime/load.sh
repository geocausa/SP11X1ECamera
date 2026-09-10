#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/cy-bounded-imx681-latch-runtime
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$BASE/z-live-3a-runtime/qcom-camss-e003i-y.ko"
sudo -n insmod "$CW/imx681.ko" 'dyndbg=+p'
grep -q '^imx681 ' /proc/modules
sudo -n dmesg | tail -n 140 > "$D/LOAD-DMESG.txt"
echo 'PASS: CY exact Z/Y CAMSS + CW IMX681 loaded; no stream executed'
