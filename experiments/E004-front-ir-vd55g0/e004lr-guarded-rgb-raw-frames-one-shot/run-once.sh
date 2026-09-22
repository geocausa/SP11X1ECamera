#!/usr/bin/env bash
# E004lr: source-locked root-sealed libcamera RGB registration-only one shot.
set -Eeuo pipefail
umask 077
D=/var/lib/sp11-camera-e004lr
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
O=$D/output
mkdir -p "$O"
status=FAIL_PRECHECK
at_exit() {
  rc=$?
  trap - EXIT
  if [[ $rc -eq 0 && "$status" != PASS_GUARDED_RAW_FRAMES_AND_NEUTRAL ]]; then rc=1; fi
  printf 'status=%s\nrc=%s\nboot_id=%s\n' "$status" "$rc" "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-RESULT.txt" || :
  sync
  exit "$rc"
}
trap at_exit EXIT
[[ $EUID -eq 0 && "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
grep -Fq 'sp11_camera_e004lr_raw_frames=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004lr-raw-frames' /proc/cmdline
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
insmod "$D/candidate/qcom-camss.ko" e004j_ir_dphy_windows_parity=1
insmod "$D/modules/ov13858.ko"
insmod "$D/candidate/imx681.ko"
insmod "$D/modules/sp11-vd55g0.ko"
for dev in "$IR" "$REAR" "$FRONT"; do
  for _ in $(seq 1 80); do
    [[ "$(cat "$dev/power/runtime_status" 2>/dev/null || :)" == suspended ]] && break
    sleep 0.05
  done
  [[ "$(cat "$dev/power/runtime_status" 2>/dev/null || :)" == suspended ]]
done
# SINGLE PURPOSE: root-only, no stream, libcamera guarded registration.
# Root-owned 0600 device nodes enforce exclusion of non-root normal clients.
# Root-equivalent competing clients cannot be prevented via DAC alone; reject
# any existing node users before the worker, and never claim production safety.
status=FAIL_EXCLUSIVE_NODE_SEAL
[[ -c /dev/media0 ]]
command -v fuser >/dev/null
node_count=0; video_count=0; subdev_count=0; media_count=0
for node in /dev/media[0-9]* /dev/video[0-9]* /dev/v4l-subdev[0-9]*; do
  [[ -c "$node" ]] || continue
  if fuser -s "$node"; then
    echo "E004LR_DENY_CAMERA_DEVICE_IN_USE" >&2
    exit 1
  fi
  chown 0:0 "$node"
  chmod 0600 "$node"
  [[ "$(stat -c '%u:%g:%a' "$node")" == "0:0:600" ]]
  case "$node" in
    /dev/media*) (( ++media_count )) ;;
    /dev/video*) (( ++video_count )) ;;
    /dev/v4l-subdev*) (( ++subdev_count )) ;;
  esac
  (( ++node_count ))
done
[[ "$media_count" -eq 1 && "$video_count" -eq 16 &&
   "$subdev_count" -eq 28 && "$node_count" -eq 45 ]]
( cd "$D"; sha256sum -c SESSION-ASSETS.sha256 > "$O/ASSET-BEFORE-LIBCAMERA.txt" )
status=FAIL_GUARDED_LIBCAMERA_RAW_FRAMES
B=$D/bundle
export LIBCAMERA_LOG_LEVELS='*:INFO'
export LIBCAMERA_IPA_MODULE_PATH="$B/build/src/ipa/simple"
export LIBCAMERA_IPA_CONFIG_PATH="$B/source/src/ipa"
export LIBCAMERA_IPA_PROXY_PATH="$B/build/src/libcamera/proxy/worker"
export LD_LIBRARY_PATH="$B/build/src/libcamera:$B/build/src/libcamera/base"
# Guarded independent RAW app sessions; no frame payload files.
# First match exact real RGB identity and require no IR registration.
timeout --signal=TERM --kill-after=2s 15s "$B/build/src/apps/cam/cam" --list > "$O/CAMERA-LIST.txt" 2> "$O/CAMERA-LIST-LOG.txt"
REAR_ID='/base/soc@0/cci@ac15000/i2c-bus@1/camera@10'
FRONT_ID='/base/soc@0/cci@ac16000/i2c-bus@1/camera@10'
[[ "$(grep -Fc "'ov13858' ($REAR_ID)" "$O/CAMERA-LIST.txt")" -eq 1 ]]
[[ "$(grep -Fc "'imx681' ($FRONT_ID)" "$O/CAMERA-LIST.txt")" -eq 1 ]]
! grep -Eiq "'vd55g0'|sp11-vd55g0" "$O/CAMERA-LIST.txt"
"$B/neutral-probe" > "$O/NEUTRAL-BEFORE.txt"
# Six metadata-confirmed independent frames each. --file is NOT passed.
# The entire independent cam process must exit before the other sensor runs.
for camera in rear front; do
  [[ "$camera" == rear ]] && id=$REAR_ID || id=$FRONT_ID
  if fuser -s /dev/media* /dev/video* /dev/v4l-subdev*; then
    echo E004LR_DENY_EXTERNAL_CAMERA_DEVICE_FD >&2
    exit 1
  fi
  timeout --signal=TERM --kill-after=2s 25s "$B/build/src/apps/cam/cam" \
    --camera="$id" --stream=role=raw --capture=6 > "$O/$camera-RAW-CAM.txt" 2> "$O/$camera-RAW-LOG.txt"
  python3 "$B/validate-cam-output.py" "$O/$camera-RAW-CAM.txt" "$camera" > "$O/$camera-RAW-SUMMARY.txt"
  if grep -Eqi 'Mandatory V4L2 control|Failed to create sensor|No valid pipeline|SP11 guarded camera session absent|SP11 active subdev routes not admitted|Failed to set link|STREAMOFF unconfirmed|SP11 route shutdown failed|Failed to start capture|Failed to stop capture' "$O/$camera-RAW-LOG.txt" "$O/$camera-RAW-CAM.txt"; then
    echo E004LR_DENY_LIBCAMERA_CAPTURE_OR_STOP >&2
    exit 1
  fi
  "$B/neutral-probe" > "$O/NEUTRAL-AFTER-$camera.txt"
  if fuser -s /dev/media* /dev/video* /dev/v4l-subdev*; then
    echo E004LR_DENY_LEAKED_CAMERA_FD >&2
    exit 1
  fi
done
for node in /dev/media[0-9]* /dev/video[0-9]* /dev/v4l-subdev[0-9]*; do
  [[ -c "$node" ]] || continue
  [[ "$(stat -c '%u:%g:%a' "$node")" == "0:0:600" ]]
done
# No devices may be held after cam process exits.
if fuser -s /dev/media* /dev/video* /dev/v4l-subdev*; then
  echo E004LR_DENY_CAM_LEAKED_DEVICE_FD >&2
  exit 1
fi
echo 'E004LR_RAW_FRAMES=PASS ROOT_SEALED=YES BOTH_REAL_RGB=YES STREAMON=YES SHUTDOWN=NEUTRAL' > "$O/RAW-FRAMES-SUMMARY.txt"
status=PASS_GUARDED_RAW_FRAMES_AND_NEUTRAL
