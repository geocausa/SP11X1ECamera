#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-first-irq-geometry-0050-candidate
CAMSS=$NEW/qcom-camss.ko
SENSOR=$NEW/imx681.ko
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$NEW/runtime-preflight.sh"
grep -q 'sp11_camera_e003h_csidseq_0050=1' /proc/cmdline || fail 'not 0050 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-csidseq-0050/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
[ "$(sha256sum "$CAMSS" | cut -d' ' -f1)" = b69a20b517953a96cf5ff806a26c78e52ce5e177ef8dcdf69afa0dd561e8439b ] || fail 'CAMSS hash'
[ "$(sha256sum "$SENSOR" | cut -d' ' -f1)" = 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388 ] || fail 'IMX681 hash'
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
[ ! -d /sys/module/qcom_camss ] || fail 'qcom_camss already loaded'
[ ! -d /sys/module/imx681 ] || fail 'imx681 already loaded'
sudo -n insmod "$CAMSS" e003h_pix_runtime_arm=1
sudo -n insmod "$SENSOR"
[ -e /sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once ] || fail 'trigger attribute absent'
[ -r /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag ] || fail 'persistent RT-CDM observer absent'
echo 'PASS: 0050 CAMSS + IMX681 loaded; trigger present and still unused'
