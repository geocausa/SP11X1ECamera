#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ho-repeated-stream-shadow-r27
P=$D/package-root/usr/lib/sp11-front-imx681
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$P/build/qcom-camss.ko"
sudo -n insmod "$P/build/imx681.ko" 'dyndbg=+p'
grep -q '^imx681 ' /proc/modules; grep -q '^qcom_camss ' /proc/modules
sudo -n dmesg | tail -n 200 > "$D/LOAD-DMESG.txt"
echo 'HO_LOAD=PASS HN production CAMSS+IMX681 loaded; no stream executed'
