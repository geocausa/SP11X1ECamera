#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
EXP=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
CAMSS=$ROOT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko
SENSOR=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko
[ "$(sha256sum "$CAMSS" | cut -d' ' -f1)" = 96e48ff176a048c391841d2c56bafdce76cfbe8a78b7310173caf175af49c9e9 ] || { echo 'FAIL: CAMSS hash'; exit 1; }
[ "$(sha256sum "$SENSOR" | cut -d' ' -f1)" = 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388 ] || { echo 'FAIL: IMX681 hash'; exit 1; }
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
[ ! -d /sys/module/qcom_camss ] || { echo 'FAIL: qcom_camss already loaded'; exit 1; }
[ ! -d /sys/module/imx681 ] || { echo 'FAIL: imx681 already loaded'; exit 1; }
sudo -n insmod "$CAMSS" e003h_pix_runtime_arm=1
sudo -n insmod "$SENSOR"
[ -e /sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once ] || { echo 'FAIL: trigger attribute absent'; exit 1; }
echo 'PASS: candidate CAMSS+IMX681 loaded; PIX trigger present but not invoked'
