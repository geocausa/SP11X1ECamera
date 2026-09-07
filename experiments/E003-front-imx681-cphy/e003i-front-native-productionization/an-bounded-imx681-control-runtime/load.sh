#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/an-bounded-imx681-control-runtime
AM=$BASE/am-imx681-exposure-cluster-fix
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$BASE/z-live-3a-runtime/qcom-camss-e003i-y.ko"
sudo -n insmod "$AM/imx681.ko" 'dyndbg=+p'
grep -q '^imx681 ' /proc/modules
sudo -n dmesg | tail -n 120 > "$D/LOAD-DMESG.txt"
echo 'PASS: AN exact Z/Y CAMSS + AM IMX681 loaded with dynamic debug; no stream executed'
