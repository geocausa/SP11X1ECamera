#!/usr/bin/env bash
# E004ll: source-locked one-shot, guarded non-streaming native RGB route check.
set -Eeuo pipefail
umask 077
D=/var/lib/sp11-camera-e004ll
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
O=$D/output
mkdir -p "$O"
status=FAIL_PRECHECK
at_exit() {
  rc=$?
  trap - EXIT
  if [[ $rc -eq 0 && "$status" != PASS_NATIVE_ROUTE_CYCLE ]]; then rc=1; fi
  printf 'status=%s\nrc=%s\nboot_id=%s\n' "$status" "$rc" "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-RESULT.txt" || :
  sync
  exit "$rc"
}
trap at_exit EXIT
[[ $EUID -eq 0 && "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
grep -Fq 'sp11_camera_e004ll_native_route=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004ll-native-route' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
[[ ! -e "$D/ATTEMPT-CONSUMED" ]]
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$env"
grep -qx 'next_entry=' <<<"$env"
for unit in grub-initrd-fallback.service grub2-common.service; do
  [[ "$(systemctl show "$unit" -p Result --value)" == success ]]
  [[ "$(systemctl show "$unit" -p ExecMainStatus --value)" == 0 ]]
  start=$(systemctl show "$unit" -p ExecMainStartTimestampMonotonic --value)
  finish=$(systemctl show "$unit" -p ExecMainExitTimestampMonotonic --value)
  [[ "$start" =~ ^[0-9]+$ && "$finish" =~ ^[0-9]+$ ]]
  (( start > 0 && finish >= start ))
done
fallback_exit=$(systemctl show grub-initrd-fallback.service -p ExecMainExitTimestampMonotonic --value)
grub2_start=$(systemctl show grub2-common.service -p ExecMainStartTimestampMonotonic --value)
(( fallback_exit <= grub2_start ))
[[ "$(systemctl show grub2-common.service -p DropInPaths --value)" == /etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e /dev/media0 && ! -e /dev/video90 && ! -e /dev/video91 ]]
for module in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d /sys/module/$module ]]; done
( cd "$D"; sha256sum -c SESSION-ASSETS.sha256 > "$O/ASSET-VERIFICATION.txt" )
status=FAIL_DRIVER_BIND
modprobe i2c_qcom_cci
find_sensor() {
  local addr=$1 compat=$2 dev
  for dev in /sys/bus/i2c/devices/*-"$addr"; do
    [[ -r "$dev/of_node/compatible" ]] || continue
    [[ "$(tr -d '\0' < "$dev/of_node/compatible")" == "$compat" ]] && { echo "$dev"; return 0; }
  done
  return 1
}
IR=; REAR=; FRONT=
for _ in $(seq 1 80); do
  IR=$(find_sensor 0060 microsoft,sp11-vd55g0 || :)
  REAR=$(find_sensor 0010 ovti,ov13858 || :)
  FRONT=$(find_sensor 0010 sony,imx681 || :)
  [[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]] && break
  sleep 0.05
done
[[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]]
for dev in "$IR" "$REAR" "$FRONT"; do [[ ! -e "$dev/driver" ]]; done
for mod in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do modprobe "$mod"; done
insmod "$D/modules/qcom-camss.ko" e004j_ir_dphy_windows_parity=1
insmod "$D/modules/ov13858.ko"
insmod "$D/modules/imx681.ko"
insmod "$D/modules/sp11-vd55g0.ko"
for dev in "$IR" "$REAR" "$FRONT"; do
  for _ in $(seq 1 80); do
    [[ "$(cat "$dev/power/runtime_status" 2>/dev/null || :)" == suspended ]] && break
    sleep 0.05
  done
  [[ "$(cat "$dev/power/runtime_status" 2>/dev/null || :)" == suspended ]]
done
# Guarded native media link writes ONLY, no video node open, libcamera,
# streaming, IR illumination or pixel/image recording.
# Strictly bounded root-only native link graph exercise, no video STREAMON.
status=FAIL_NATIVE_ROUTE
[[ -c /dev/media0 ]]
command -v fuser >/dev/null
if fuser -s /dev/video* /dev/v4l-subdev*; then
  echo E004LL_DENY_EXTERNAL_CAMERA_DEVICE_USER >&2
  exit 1
fi
timeout --signal=TERM --kill-after=2s 12s "$D/sp11-e004ll-native-route-probe" /dev/media0 > "$O/NATIVE-ROUTE-RESULT.txt" 2> "$O/NATIVE-ROUTE-ERROR.txt"
for phase in front neutral rear; do
  grep -Fqx "E004LL_NATIVE_ROUTE=$phase FRESH_FULL_GRAPH=PASS" "$O/NATIVE-ROUTE-RESULT.txt"
done
[[ "$(grep -Fc ' FRESH_FULL_GRAPH=PASS' "$O/NATIVE-ROUTE-RESULT.txt")" -eq 4 ]]
grep -Fqx 'E004LL_NATIVE_ROUTE_CYCLE=PASS STREAMON=0 IR_EMITTER=0' "$O/NATIVE-ROUTE-RESULT.txt"
if fuser -s /dev/video* /dev/v4l-subdev*; then
  echo E004LL_DENY_POSTSESSION_DEVICE_USER >&2
  exit 1
fi
[[ ! -e /dev/video90 && ! -e /dev/video91 ]]
status=PASS_NATIVE_ROUTE_CYCLE
