#!/usr/bin/env bash
# E004jg: one isolated synthetic V4L2 virtual rear device test.
# No physical camera, no normal optical pixels, no IR, no Golden writes.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004jg
O=$D/output
MOD=$D/v4l2loopback.ko
RECEIVER=$D/nv12-appsrc-consumer.py
VIDEO=/dev/video90
done_ok=0
writer_pid=
START=0
mkdir -p "$O"
at_exit() {
  rc=$?
  trap - EXIT
  if [ "$done_ok" -ne 1 ] && [ "$rc" -eq 0 ]; then rc=1; fi
  if [ -n "$writer_pid" ]; then
    kill -TERM "$writer_pid" >/dev/null 2>&1 || :
    wait "$writer_pid" >/dev/null 2>&1 || :
  fi
  if [ -d /sys/module/v4l2loopback ]; then
    timeout --signal=TERM --kill-after=2s 5s rmmod v4l2loopback > "$O/RMMOD.txt" 2>&1 || rc=1
  fi
  if [ -e "$VIDEO" ] || [ -d /sys/module/v4l2loopback ]; then
    rc=1
    echo "E004JG_VIRTUAL_MODULE_STILL_ACTIVE" > "$O/FINAL-DEVICE.txt"
  else
    echo "E004JG_MODULE_AND_DEVICE_REMOVED=PASS" > "$O/FINAL-DEVICE.txt"
  fi
  dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then
    echo PASS_SYNTHETIC_REAR_V4L2_DEVICE_GSTREAMER_APPLICATION > "$D/ATTEMPT-RESULT.txt"
  else
    echo "FAIL_RC=$rc ONE_SHOT_NO_RETRY" > "$D/ATTEMPT-RESULT.txt"
  fi
  printf 'boot_id=%s\nloopback_sha256=2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1\n' \
    "$(cat /proc/sys/kernel/random/boot_id)" >> "$D/ATTEMPT-RESULT.txt" || :
  sync
  exit "$rc"
}
trap at_exit EXIT
[[ "$EUID" -eq 0 && "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
[[ "$(systemctl show grub2-common.service -p Result --value)" == success ]]
[[ "$(systemctl show grub-initrd-fallback.service -p Result --value)" == success ]]
for unit in grub-initrd-fallback.service grub2-common.service; do
  [[ "$(systemctl show "$unit" -p ConditionResult --value)" == yes ]]
  [[ "$(systemctl show "$unit" -p ExecMainStatus --value)" == 0 ]]
  started=$(systemctl show "$unit" -p ExecMainStartTimestampMonotonic --value)
  finished=$(systemctl show "$unit" -p ExecMainExitTimestampMonotonic --value)
  [[ "$started" =~ ^[0-9]+$ && "$finished" =~ ^[0-9]+$ ]]
  (( started > 0 && finished >= started ))
done
fallback_finish=$(systemctl show grub-initrd-fallback.service -p ExecMainExitTimestampMonotonic --value)
grub2_start=$(systemctl show grub2-common.service -p ExecMainStartTimestampMonotonic --value)
(( fallback_finish <= grub2_start ))
[[ "$(systemctl show grub2-common.service -p DropInPaths --value)" == /etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf ]]
[[ "$(sha256sum /etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf | awk '{print $1}')" == "$(sha256sum "$R/experiments/E004-front-ir-vd55g0/e004iy-grub-writer-order-reversible/90-sp11-serialize-grubenv-writers.conf" | awk '{print $1}')" ]]
grep -Fq 'sp11_virtual_rear_e004jg=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-e004jg-virtual-rear' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<< "$env"
grep -qx 'next_entry=' <<< "$env"
[[ ! -e "$D/ATTEMPT-CONSUMED" && ! -e "$VIDEO" && ! -e /dev/media0 ]]
[[ -f "$MOD" && ! -L "$MOD" ]]
[[ "$(sha256sum "$MOD" | awk '{print $1}')" == 2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1 ]]
[[ "$(modinfo -F vermagic "$MOD")" == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]]
[[ "$(modinfo -F license "$MOD")" == GPL ]]
[[ "$(sha256sum "$RECEIVER" | awk '{print $1}')" == 9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613 ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
[[ "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" == "$(runuser -u geoca -- git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' \
  "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
START=$(dmesg | wc -l)
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d "/sys/module/$m" ]]; done
modprobe videodev
insmod "$MOD" devices=1 video_nr=90 card_label=SP11-Rear-Preview exclusive_caps=0 max_buffers=8 max_openers=5
udevadm settle
[[ -c "$VIDEO" ]]
v4l2-ctl -d "$VIDEO" -D > "$O/DEVICE-CAPABILITIES.txt"
grep -Fq 'SP11-Rear-Preview' "$O/DEVICE-CAPABILITIES.txt"
v4l2-ctl --list-devices > "$O/DISCOVERABLE-DEVICES.txt"
grep -Fq 'SP11-Rear-Preview' "$O/DISCOVERABLE-DEVICES.txt"
# Startup synthetic publisher with 90 is-live frames to leave a bounded
# window for a separate standard V4L2 capture client to open the device.
timeout --signal=TERM --kill-after=2s 12s gst-launch-1.0 -q \
  videotestsrc pattern=ball is-live=true num-buffers=90 \
  '!' video/x-raw,width=1920,height=1080,framerate=30/1 \
  '!' videoconvert \
  '!' video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 \
  '!' v4l2sink device="$VIDEO" sync=false > "$O/SYNTHETIC-PUBLISHER.txt" 2>&1 &
writer_pid=$!
format_ok=0
for _ in $(seq 1 100); do
  if timeout 2s v4l2-ctl -d "$VIDEO" --get-fmt-video > "$O/LOOPBACK-FORMAT.txt" 2>/dev/null &&
    grep -q 'Width/Height.*1920/1080' "$O/LOOPBACK-FORMAT.txt" &&
    grep -q 'Pixel Format.*NV12' "$O/LOOPBACK-FORMAT.txt"; then
    format_ok=1; break
  fi
  kill -0 "$writer_pid"
  sleep 0.05
done
[[ "$format_ok" -eq 1 ]]
# The receiver accesses the dynamically created standard /dev/video90
# CAPTURE interface (not the sender's anonymous pipe).
timeout --signal=TERM --kill-after=3s 15s bash -o pipefail -c '
  v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=8 --stream-to=- --verbose 2>"$2" |
  /usr/bin/python3 "$3" --frames 8 2>"$4"
' bash "$VIDEO" "$O/STANDARD-CAPTURE.txt" "$RECEIVER" "$O/GSTREAMER-APPLICATION.txt"
grep -Fq 'E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=8' "$O/GSTREAMER-APPLICATION.txt"
grep -Fq 'APP_CONSUMER=GSTREAMER_APPSINK_I420' "$O/GSTREAMER-APPLICATION.txt"
[[ ! -e "$O/rear-normal8.raw" && ! -e "$O/rear-normal8.nv12" ]]
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d "/sys/module/$m" ]]; done
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON' "$O/KERNEL-HEALTH.txt"
done_ok=1
echo E004JG_SYNTHETIC_SYSTEM_V4L2_REAR_DEVICE_TO_APPLICATION=PASS
