#!/usr/bin/env bash
# E004js: distinct bounded NON-STREAMING camera media-graph diagnostic ONLY.
# Golden is not changed. Any service exit schedules immediate Golden reboot.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004js
H=$R/experiments/E004-front-ir-vd55g0/e004js-live-graph-diagnostic-one-shot
O=$D/output
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
ok=0
mkdir -m 0700 "$O"
at_exit() {
  rc=$?
  trap - EXIT
  if [[ "$ok" -ne 1 && "$rc" -eq 0 ]]; then rc=1; fi
  { printf 'E004JS_STATUS=%s\n' "$([[ "$rc" -eq 0 ]] && echo PASS_GRAPH_DIAGNOSTIC || echo FAIL_CLOSED_NO_STREAM)";
    printf 'boot_id=%s\n' "$(cat /proc/sys/kernel/random/boot_id)";
    printf 'optical_frames=0\nvirtual_webcam_frames=0\n'; } > "$D/ATTEMPT-RESULT.txt" || :
  dmesg | tail -n 320 > "$O/KERNEL-TAIL.txt" 2>/dev/null || :
  sync
  exit "$rc"
}
trap at_exit EXIT
[[ "$EUID" -eq 0 && "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
grep -Fq 'sp11_camera_e004js_diag=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004js-graph' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<< "$env"
grep -qx 'next_entry=' <<< "$env"
for unit in grub-initrd-fallback.service grub2-common.service; do
  [[ "$(systemctl show "$unit" -p Result --value)" == success ]]
  [[ "$(systemctl show "$unit" -p ConditionResult --value)" == yes ]]
  [[ "$(systemctl show "$unit" -p ExecMainStatus --value)" == 0 ]]
  a=$(systemctl show "$unit" -p ExecMainStartTimestampMonotonic --value)
  b=$(systemctl show "$unit" -p ExecMainExitTimestampMonotonic --value)
  [[ "$a" =~ ^[0-9]+$ && "$b" =~ ^[0-9]+$ ]] && (( a>0 && b>=a ))
done
f=$(systemctl show grub-initrd-fallback.service -p ExecMainExitTimestampMonotonic --value)
g=$(systemctl show grub2-common.service -p ExecMainStartTimestampMonotonic --value)
(( f<=g ))
[[ "$(systemctl show grub2-common.service -p DropInPaths --value)" == /etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf ]]
[[ ! -e "$D/ATTEMPT-CONSUMED" && ! -e /dev/media0 && ! -e /dev/video90 ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
[[ "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" == "$(runuser -u geoca -- git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | cut -d' ' -f1)" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$D/stack"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 > "$O/PACKAGE-VERIFY.txt" )
[[ "$(sha256sum "$HW/modules/qcom-camss.ko" | cut -d' ' -f1)" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sha256sum "$HW/modules/ov13858.ko" | cut -d' ' -f1)" == 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ]]
[[ "$(sha256sum "$HW/modules/imx681.ko" | cut -d' ' -f1)" == ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ]]
[[ "$(sha256sum "$HW/modules/sp11-vd55g0.ko" | cut -d' ' -f1)" == 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ]]
[[ "$(sha256sum "$D/camera-media-graph-diagnostic.py" | cut -d' ' -f1)" == "$(cat "$D/EXPECTED-DIAGNOSTIC-SHA256")" ]]
# Consume identity before ANY camera module initialization. This is NOT a
# camera stream. Sensors are probed/bound and remain unstreamed in standby.
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
modprobe i2c_qcom_cci
find_compat() {
  local addr=$1 compat=$2 p
  for p in /sys/bus/i2c/devices/*-"$addr"; do
    [[ -e "$p" && -r "$p/of_node/compatible" ]] || continue
    [[ "$(tr -d '\0' < "$p/of_node/compatible")" == "$compat" ]] && { echo "$p";return 0; }
  done
  return 1
}
IR=; REAR=; FRONT=
for _ in $(seq 1 120); do
  IR=$(find_compat 0060 microsoft,sp11-vd55g0 || :)
  REAR=$(find_compat 0010 ovti,ov13858 || :)
  FRONT=$(find_compat 0010 sony,imx681 || :)
  [[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]] && break
  sleep .05
done
[[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]]
for dev in "$IR" "$REAR" "$FRONT"; do [[ ! -e "$dev/driver" ]]; done
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do modprobe "$m"; done
insmod "$HW/modules/qcom-camss.ko" e004j_ir_dphy_windows_parity=1
insmod "$HW/modules/ov13858.ko"
insmod "$HW/modules/imx681.ko" 'dyndbg=+p'
insmod "$HW/modules/sp11-vd55g0.ko"
# Preserve per-device non-image binding and media node inventory even if
# graph discovery fails. No test-pattern or s_stream is ever called.
for dev in "$REAR" "$FRONT" "$IR"; do
  for _ in $(seq 1 120); do [[ -L "$dev/driver" ]] && break; sleep .05; done
  [[ -L "$dev/driver" ]]
done
for dev in "$REAR" "$FRONT" "$IR"; do
  name=$(basename "$dev")
  printf 'device=%s driver=%s runtime_status=%s\n' "$dev" "$(readlink -f "$dev/driver")" "$(cat "$dev/power/runtime_status" 2>/dev/null || echo unavailable)" >> "$O/BIND-STATUS.txt"
done
find /dev -maxdepth 1 -regextype posix-extended -regex '/dev/(media|video|v4l-subdev)[0-9]+' -printf '%f\n' | sort -V > "$O/MEDIA-NODES.txt"
set +e
/usr/bin/python3 "$D/camera-media-graph-diagnostic.py" --live --out-dir "$O" > "$O/DIAGNOSTIC-CLI.txt" 2> "$O/DIAGNOSTIC-ERROR.txt"
diag_rc=$?
set -e
echo "diagnostic_exit_code=$diag_rc" > "$O/DIAGNOSTIC-RC.txt"
# Preserve BOTH expected and unexpected graph states as a useful distinct
# one-shot result. No optical frame or device graph link is changed.
if grep -Eiq 'BUG:|Oops:|Kernel panic|ILLUMINATION_ON' <(dmesg | tail -n 320); then
  echo E004JS_FATAL_KERNEL_OR_IR_MARKER > "$O/SAFETY-ABORT.txt"
  exit 1
fi
[[ -d /sys/module/qcom_camss ]]
[[ -d /sys/module/imx681 && -d /sys/module/ov13858 && -d /sys/module/sp11_vd55g0 ]]
[[ ! -e /dev/video90 && ! -d /sys/module/v4l2loopback ]]
[[ ! -e "$O/rear-colorbar.raw" && ! -e "$O/real-optical.raw" && ! -e "$O/normal.nv12" ]]
ok=1
echo E004JS_BOUNDED_READ_ONLY_GRAPH_INVENTORY_COMPLETED_NO_STREAM=PASS
