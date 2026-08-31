#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate
CAMSS=$NEW/qcom-camss.ko
SENSOR=$NEW/imx681.ko
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$NEW/runtime-preflight.sh"
grep -q 'sp11_camera_e003h_rupclear_0051=1' /proc/cmdline || fail 'not 0051 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-rupclear-0051/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
[ "$(sha256sum "$CAMSS" | cut -d' ' -f1)" = 6b7287e6eb96c44060d58691333b82f4e4103df929f98ad39ec50347b379f020 ] || fail 'CAMSS hash'
[ "$(sha256sum "$SENSOR" | cut -d' ' -f1)" = 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388 ] || fail 'IMX681 hash'
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
[ ! -d /sys/module/qcom_camss ] || fail 'qcom_camss already loaded'
[ ! -d /sys/module/imx681 ] || fail 'imx681 already loaded'
sudo -n insmod "$CAMSS" e003h_pix_runtime_arm=1
sudo -n insmod "$SENSOR"
[ -e /sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once ] || fail 'trigger attribute absent'
[ -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag ] || fail 'persistent RT-CDM observer absent'
echo 'PASS: 0051 CAMSS + IMX681 loaded; trigger present and still unused'
