#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ak-bounded-imx681-control-runtime
AJ=$BASE/aj-imx681-exposure-controls
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$BASE/z-live-3a-runtime/qcom-camss-e003i-y.ko"
# CONFIG_DYNAMIC_DEBUG=y on Golden; enable only this module's dev_dbg sites.
sudo -n insmod "$AJ/imx681.ko" 'dyndbg=+p'
grep -q '^imx681 ' /proc/modules
sudo -n dmesg | tail -n 120 > "$D/LOAD-DMESG.txt"
echo 'PASS: AK exact Z/Y CAMSS + AJ IMX681 loaded with dynamic debug; no stream executed'
