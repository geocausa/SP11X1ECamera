#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/gv-limited-redundant-write-live-r27
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
"$D/build-camss.sh" "$D/build/qcom-camss-gv.ko" >/dev/null
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$D/build/qcom-camss-gv.ko"
sudo -n insmod "$CW/imx681.ko" 'dyndbg=+p'
grep -q '^imx681 ' /proc/modules;grep -q '^qcom_camss ' /proc/modules
sudo -n dmesg | tail -n 160 > "$D/LOAD-DMESG.txt"
echo 'PASS: GV limited-write GN-twenty-seven-frame CAMSS + CW IMX681 loaded; no stream executed'
