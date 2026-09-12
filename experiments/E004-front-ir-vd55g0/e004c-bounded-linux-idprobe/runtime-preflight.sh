#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -Fq 'sp11_camera_e004c_ir_idprobe=1' /proc/cmdline || fail candidate_marker
[ "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' ] || fail kernel
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail one_shot_not_consumed
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || fail already_consumed
[ ! -d /sys/module/sp11_vd55g0_idprobe ] || fail idprobe_already_loaded
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "forbidden_module_$m"; done
if pgrep -af 'libcamera|v4l2-ctl|ffmpeg|gst-launch' >/dev/null; then fail camera_process; fi
COMP=/proc/device-tree/soc@0/cci@ac15000/i2c-bus@0/camera@60/compatible
[ -r "$COMP" ] || fail ir_dt_node
[ "$(tr -d '\0' < "$COMP")" = 'microsoft,sp11-vd55g0-idprobe' ] || fail compatible
if [ ! -d /sys/module/i2c_qcom_cci ]; then
  sudo -n modprobe i2c_qcom_cci
fi
DEV=
for _ in $(seq 1 50); do
  DEV=$(find /sys/bus/i2c/devices -maxdepth 1 -type l -name '*-0060' -print -quit 2>/dev/null || true)
  [ -n "$DEV" ] && break
  sleep 0.1
done
[ -n "$DEV" ] || fail i2c_client_0x60
[ ! -e "$DEV/driver" ] || fail unexpected_driver_bound
[ "$(sha256sum "$D/build/sp11-vd55g0-idprobe.ko"|awk '{print $1}')" = 'd749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed' ] || fail module_hash
{
 echo 'schema=sp11-camera-e004c-runtime-preflight-v1'
 echo 'status=PASS_READY_FOR_SINGLE_INSMOD'
 echo "time=$(date -Ins)"
 echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
 echo "i2c_client=$DEV"
 echo "cci_module=$( [ -d /sys/module/i2c_qcom_cci ] && echo loaded || echo absent )"
 echo 'idprobe_module=absent'
 echo 'attempt_consumed=NO'
} > "$D/RUNTIME-PREFLIGHT.txt"
echo "E004C_RUNTIME_PREFLIGHT=PASS I2C_CLIENT=$DEV IDPROBE=NOT_LOADED"
