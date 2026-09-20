#!/usr/bin/env bash
# E004ka: bounded real rear Bayer to standard 4K V4L2 webcam, no front streaming.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004ka
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$HW/modules/qcom-camss.ko
LOOP_MOD=$D/v4l2loopback.ko
LOOP_DEV=/dev/video90
publisher_pid=
H=$R/experiments/E004-front-ir-vd55g0/e004ka-rear4k-byte-boundary-one-shot
O=$D/output
MEDIA=
REAR_PATTERN_ACTIVE=0
START=0
done_ok=0
mkdir -p "$O"
at_exit() {
  rc=$?
  trap - EXIT
  if [ "$done_ok" -ne 1 ] && [ "$rc" -eq 0 ]; then rc=1; fi
  if [ "${REAR_PATTERN_ACTIVE:-0}" -eq 1 ] && [ -n "${REARSENSORDEV:-}" ]; then
    v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0 > "$O/REAR-PATTERN-RESET.txt" 2>&1 || :
  fi
  if [ -n "${publisher_pid:-}" ]; then
    kill -TERM "$publisher_pid" >/dev/null 2>&1 || :
    wait "$publisher_pid" >/dev/null 2>&1 || :
  fi
  if [ -d /sys/module/v4l2loopback ]; then
    timeout --signal=TERM --kill-after=3s 6s rmmod v4l2loopback > "$O/VIRTUAL-UNDO.txt" 2>&1 || rc=1
  fi
  if [ -e "$LOOP_DEV" ] || [ -d /sys/module/v4l2loopback ]; then
    rc=1
    echo E004KA_VIRTUAL_DEVICE_STILL_PRESENT > "$O/VIRTUAL-FINAL.txt"
  else
    echo E004KA_VIRTUAL_DEVICE_AND_MODULE_REMOVED=PASS > "$O/VIRTUAL-FINAL.txt"
  fi
  if [ -n "$MEDIA" ]; then
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]' > "$O/REAR-UNDO-1.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]' > "$O/REAR-UNDO-2.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]' > "$O/UNDO-1.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]' > "$O/UNDO-2.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -p > "$O/FINAL-MEDIA.txt" 2>&1 || :
  fi
  dmesg | tail -n +$((START+1)) > "$O/DMESG.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then echo PASS_REAL_REAR180_TO_STANDARD_VIRTUAL_NV12_4K_WEB_CAM90_NO_FRONT_STREAM > "$D/ATTEMPT-RESULT.txt"
  else echo "FAIL_RC=$rc ONE_SHOT_NO_RETRY" > "$D/ATTEMPT-RESULT.txt"; fi
  printf 'boot_id=%s\ncandidate_sha256=862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7\n' \
    "$(cat /proc/sys/kernel/random/boot_id)" >> "$D/ATTEMPT-RESULT.txt" || :
  sync
  exit "$rc"
}
trap at_exit EXIT
[[ "$EUID" -eq 0 && "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
[[ "$(systemctl show grub2-common.service -p Result --value)" == success ]]
[[ "$(systemctl show grub-initrd-fallback.service -p Result --value)" == success ]]
# A oneshot unit's Result can be "success" even without executing.
# Require both actual ExecMain statuses and this boot's monotonic timestamps,
# with the fallback writer finished before the grub2 writer started.
for unit in grub-initrd-fallback.service grub2-common.service; do
  [[ "$(systemctl show "$unit" -p ConditionResult --value)" == yes ]]
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
[[ "$(sha256sum /etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf | awk '{print $1}')" == "$(sha256sum "$R/experiments/E004-front-ir-vd55g0/e004iy-grub-writer-order-reversible/90-sp11-serialize-grubenv-writers.conf" | awk '{print $1}')" ]]
grep -Fq 'sp11_camera_e004ka_rear4k_boundary=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004ka-boundary' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$env"
grep -qx 'next_entry=' <<<"$env"
[[ ! -e "$D/ATTEMPT-CONSUMED" && ! -e /dev/media0 && ! -e "$LOOP_DEV" && ! -d /sys/module/v4l2loopback ]]
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' \
  "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
START=$(dmesg | wc -l)
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d "/sys/module/$m" ]]; done
[[ "$(sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$D/stack"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 > "$O/PACKAGE-VERIFY.txt" )
[[ "$(sha256sum "$CAND" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ -f "$LOOP_MOD" && ! -L "$LOOP_MOD" && "$(sha256sum "$LOOP_MOD" | awk '{print $1}')" == 967caa8fc9e71cb65280d03e3763800ad59cb7fc8798c3d04d42d693e39b35c9 ]]
[[ "$(modinfo -F vermagic "$LOOP_MOD")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
# E004jd production package includes the SHA-pinned derived R4 bootstrap.
# Require the complete 51-file package and verified launcher plan before
# any camera module is loaded, then additionally validate our rear bridge.
R4=$P/userspace/iq/authority/r4-bootstrap.bin
[[ -f "$R4" && ! -L "$R4" && "$(stat -c%s "$R4")" == 41088 ]]
[[ "$(sha256sum "$R4" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
python3 - "$D/FRONT-LAUNCH-DRYRUN.json" "$R4" <<'PY'
import json,sys
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text())
assert p['r4_sha256']=='1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa'
assert p['execute'] is False and p['post_g3_write_policy']=='shadow'
assert p['discovery']['proven_capture_fourcc']=='QC10C'
assert p['capture_command'][2]==sys.argv[2]
print('E004KA_PRECAMERA_SOURCE_LOCKED_PACKAGED_R4_LAUNCH_PLAN=PASS')
PY
# Source-pinned E004je streaming bridge must be root-only and validated
# BEFORE camera power or any kernel module loading.
BRIDGE_BIN=$D/bridge/rear-bayer-to-nv12-4k
BRIDGE_APP=$D/bridge/nv12-4k-partial-telemetry-app.py
[[ -f "$BRIDGE_BIN" && ! -L "$BRIDGE_BIN" && -f "$BRIDGE_APP" && ! -L "$BRIDGE_APP" ]]
[[ "$(stat -c%a "$BRIDGE_BIN")" == 700 && "$(stat -c%a "$BRIDGE_APP")" == 600 ]]
[[ "$(sha256sum "$BRIDGE_BIN" | awk '{print $1}')" == 06b4851544b5f9f48bda60df997ab7d96c7b93b77f8c19b90c6f4cc3e31c7454 ]]
[[ "$(sha256sum "$BRIDGE_APP" | awk '{print $1}')" == 1e129b385d9d849808eadd1e8b43224e721c19c3bb364513975604d05ce7e0b8 ]]
[[ -f "$D/validate-partial.py" && ! -L "$D/validate-partial.py" ]]
[[ "$(sha256sum "$D/validate-partial.py" | awk '{print $1}')" == 64dae0934bf6e1e67c2ad03c1978d032e039941132971cfcb80aa6f1d7c36b15 ]]
PIPE_AUDIT=$D/bridge/nv12-4k-pipe-audit
[[ -f "$PIPE_AUDIT" && ! -L "$PIPE_AUDIT" && "$(stat -c%a "$PIPE_AUDIT")" == 700 ]]
[[ "$(sha256sum "$PIPE_AUDIT" | awk '{print $1}')" == aad050944551f77f71c760031bfa3d25968e9ab2e5accf74ffdae561be3e852b ]]
grep -Fq 'E004JZ_4K_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/REAR-PIPE-AUDIT-DRYRUN.txt"
grep -Fq 'E004KA_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
grep -Fq 'E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
grep -Fq 'E004KA_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
[[ "$(sha256sum "$HW/modules/imx681.ko" | awk '{print $1}')" == ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ]]
[[ "$(sha256sum "$HW/modules/ov13858.ko" | awk '{print $1}')" == 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ]]
[[ "$(sha256sum "$HW/modules/sp11-vd55g0.ko" | awk '{print $1}')" == 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
[[ "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" == "$(runuser -u geoca -- git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
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
 sleep 0.05
done
[[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]]
for dev in "$IR" "$REAR" "$FRONT"; do [[ ! -e "$dev/driver" ]]; done
for mod in mc videodev v4l2_async v4l2_fwnode videobuf2_common \
  videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do modprobe "$mod"; done
insmod "$CAND" e004j_ir_dphy_windows_parity=1
insmod "$HW/modules/ov13858.ko"
insmod "$HW/modules/imx681.ko" 'dyndbg=+p'
insmod "$HW/modules/sp11-vd55g0.ko"
wait_suspend() {
  local dev
  for dev in "$IR" "$REAR" "$FRONT"; do
    for _ in $(seq 1 120); do
      [[ "$(cat "$dev/power/runtime_status" 2>/dev/null || :)" == suspended ]] && break
      sleep 0.05
    done
    [[ "$(cat "$dev/power/runtime_status")" == suspended ]]
  done
}
for dev in "$IR" "$REAR" "$FRONT"; do
  for _ in $(seq 1 120); do [[ -L "$dev/driver" ]] && break; sleep 0.05; done
  [[ -L "$dev/driver" ]]
done
wait_suspend
# E004jq failed at the first media discovery while swallowing stderr.
# E004js proved that this same accepted camera stack can expose all 44
# media entities. Preserve the ACTUAL current candidate graph or its failure
# before any route changes, sensor test pattern or real optical stream.
[[ -f "$D/camera-media-graph-diagnostic.py" && ! -L "$D/camera-media-graph-diagnostic.py" ]]
[[ "$(sha256sum "$D/camera-media-graph-diagnostic.py" | awk '{print $1}')" == 4435c52d364e4030285c3e74372446eb452fa5722c355301201812a6d2341348 ]]
set +e
timeout --signal=TERM --kill-after=2s 12s /usr/bin/python3 "$D/camera-media-graph-diagnostic.py" --live --out-dir "$O" > "$O/MEDIA-DISCOVERY-CLI.txt" 2> "$O/MEDIA-DISCOVERY-ERROR.txt"
graph_rc=$?
set -e
printf 'graph_diagnostic_exit=%s\n' "$graph_rc" > "$O/MEDIA-DISCOVERY-RC.txt"
[[ "$graph_rc" -eq 0 && -s "$O/ACCEPTED-MEDIA-GRAPH.txt" && -s "$O/DISCOVERY.json" ]] || {
  echo E004KA_STOP_NO_COMPLETE_MEDIA_GRAPH_BEFORE_CAPTURE >&2
  exit 1
}
python3 "$H/discover-unified.py" --from-file "$O/ACCEPTED-MEDIA-GRAPH.txt" > "$O/UNIFIED.tmp" 2> "$O/UNIFIED-ERROR.txt" || {
  echo E004KA_UNIFIED_PARSER_REJECTED_ARCHIVED_CURRENT_GRAPH >&2
  exit 1
}
mv "$O/UNIFIED.tmp" "$O/UNIFIED.json"
[[ -s "$O/UNIFIED.json" ]]
MEDIA=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['media'])")
media-ctl -d "$MEDIA" -p > "$O/INITIAL-MEDIA.txt"
# CAMSS can expose both mutable rear links enabled at idle. E004iz
# proved this exact state on SP11. Reject partial/mixed/front states;
# explicitly neutralize ONLY the two known rear mutable links, and verify.
initial=$(/usr/bin/python3 "$H/route-state.py" "$O/INITIAL-MEDIA.txt")
case "$initial" in
  "IF_ROUTE_STATE=neutral "*) ;;
  "IF_ROUTE_STATE=rear-only "*)
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
    ;;
  *) echo "E004KA_REJECT_UNEXPECTED_IDLE_GRAPH=$initial" >&2; exit 1 ;;
esac
media-ctl -d "$MEDIA" -p > "$O/INITIAL-NORMALIZED-MEDIA.txt"
/usr/bin/python3 "$H/route-state.py" "$O/INITIAL-NORMALIZED-MEDIA.txt" --expect neutral
wait_suspend
REARSENSOR=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_sensor_entity'])")
REARSENSORDEV=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_sensor_device'])")
REARVIDEO=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_video_device'])")
[[ "$REARSENSOR" == ov13858\ * && -c "$REARSENSORDEV" && -c "$REARVIDEO" ]]
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'
media-ctl -d "$MEDIA" -p > "$O/REAR-ON-MEDIA.txt"
/usr/bin/python3 "$H/route-state.py" "$O/REAR-ON-MEDIA.txt" --expect rear-only
media-ctl -d "$MEDIA" -V "\"$REARSENSOR\":0 [fmt:SGRBG10_1X10/4076x2806]" > "$O/REAR-CONFIG.txt" 2>&1
for e in msm_csiphy1:0 msm_csiphy1:1 msm_csid0:0 msm_csid0:1 msm_vfe0_rdi0:0 msm_vfe0_rdi0:1; do
  IFS=: read -r entity pad <<< "$e"
  media-ctl -d "$MEDIA" -V "\"$entity\":$pad [fmt:SGRBG10_1X10/4076x2806]" >> "$O/REAR-CONFIG.txt" 2>&1
done
v4l2-ctl -d "$REARVIDEO" --set-fmt-video=width=4076,height=2806,pixelformat=pgAA >> "$O/REAR-CONFIG.txt" 2>&1
v4l2-ctl -d "$REARVIDEO" --get-fmt-video >> "$O/REAR-CONFIG.txt" 2>&1
grep -q "Width/Height.*4076/2806" "$O/REAR-CONFIG.txt"
grep -q "Pixel Format.*pgAA" "$O/REAR-CONFIG.txt"
v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=1
REAR_PATTERN_ACTIVE=1
timeout 20s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=1 --stream-to="$O/rear-colorbar.raw" --verbose > "$O/REAR-COLORBAR.txt" 2>&1
v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0
REAR_PATTERN_ACTIVE=0
[[ "$(stat -c%s "$O/rear-colorbar.raw")" == 14321824 ]]
[[ "$(sha256sum "$O/rear-colorbar.raw" | awk '{print $1}')" == 6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346 ]]
# E004jf proved real Bayer→NV12→GStreamer appsrc; E004jg proved a standard
# synthetic NV12→/dev/video90→independent V4L2 reader path. Here we require
# the ACTUAL optical OV13858 to publish to that STANDARD virtual device.
# The root-owned helper/source package were separately SHA-pinned BEFORE PM.
modprobe videodev
insmod "$LOOP_MOD" devices=1 video_nr=90 card_label=SP11-Rear-Preview \
  exclusive_caps=0 max_buffers=8 max_openers=5
udevadm settle
[[ -c "$LOOP_DEV" ]]
v4l2-ctl -d "$LOOP_DEV" -D > "$O/REAR-VIRTUAL-DEVICE.txt"
grep -Fq 'SP11-Rear-Preview' "$O/REAR-VIRTUAL-DEVICE.txt"
v4l2-ctl --list-devices > "$O/REAR-VIRTUAL-DISCOVERY.txt"
grep -Fq 'SP11-Rear-Preview' "$O/REAR-VIRTUAL-DISCOVERY.txt"
REAR_VIRTUAL_START_NS=$(date +%s%N)
printf 'PUBLISHER_START_NS=%s\n' "$REAR_VIRTUAL_START_NS" > "$O/REAR-4K-PROCESS-EVENTS.txt"
# Keep the SAME 180-source/90-subscriber workload as consumed E004jw.
# Change only bounded partial app telemetry and record producer vs subscriber
# lifecycle so no app-count or end-to-end 4K30 claim survives a shortfall.
(
  set +e
  timeout --signal=TERM --kill-after=3s 75s bash -o pipefail -c '
    v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=180 --stream-to=- --verbose 2>"$2" |
      "$3" --frames 180 2>"$4" |
      gst-launch-1.0 -q fdsrc fd=0 blocksize=12441600 \
        ! rawvideoparse format=nv12 width=3840 height=2160 framerate=30/1 \
        ! "video/x-raw,format=NV12,width=3840,height=2160,framerate=30/1" \
        ! v4l2sink device="$5" sync=true >"$6" 2>&1
  ' bash "$REARVIDEO" "$O/REAL-REAR-CAPTURE180.txt" \
    "$BRIDGE_BIN" "$O/REAL-REAR-CONVERT180.txt" "$LOOP_DEV" \
    "$O/REAL-REAR-TO-VIRTUAL-PUBLISHER.txt"
  publisher_inner_rc=$?
  # Record true process completion BEFORE the later subscriber wait/reap.
  printf 'PUBLISHER_END_NS=%s\n' "$(date +%s%N)" > "$O/REAR-4K-PUBLISHER-DONE.txt"
  exit "$publisher_inner_rc"
) &
publisher_pid=$!
virtual_ready=0
for _ in $(seq 1 100); do
  if timeout 2s v4l2-ctl -d "$LOOP_DEV" --get-fmt-video > "$O/REAR-VIRTUAL-FORMAT.txt" 2>/dev/null &&
     grep -q 'Width/Height.*3840/2160' "$O/REAR-VIRTUAL-FORMAT.txt" &&
     grep -q 'Pixel Format.*NV12' "$O/REAR-VIRTUAL-FORMAT.txt"; then
    virtual_ready=1; break
  fi
  kill -0 "$publisher_pid"
  sleep 0.05
done
[[ "$virtual_ready" -eq 1 ]]
printf 'VIRTUAL_FORMAT_READY_NS=%s\n' "$(date +%s%N)" >> "$O/REAR-4K-PROCESS-EVENTS.txt"
# Subscriber opens the independent V4L2 endpoint at the FIRST 4K-format-ready
# observation. Bounded reader and E004jx app report progress in the face of
# upstream starvation, instead of waiting 65s then losing all app timing.
printf 'READER_START_NS=%s\n' "$(date +%s%N)" >> "$O/REAR-4K-PROCESS-EVENTS.txt"
set +e
timeout --signal=TERM --kill-after=3s 28s bash -o pipefail -c '
  v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=90 --stream-to=- --verbose 2>"$2" |
    "$4" --frames 90 --idle-ms 6000 2>"$5" |
    /usr/bin/python3 "$3" --frames 90 --idle-seconds 6 2>"$6"
' bash "$LOOP_DEV" "$O/REAL-REAR-VIRTUAL-READER90.txt" \
  "$BRIDGE_APP" "$PIPE_AUDIT" "$O/REAR-4K-BYTE-BOUNDARY.txt" \
  "$O/REAL-REAR-VIRTUAL-GSTREAMER-APP90.txt"
reader_rc=$?
printf 'READER_END_NS=%s\n' "$(date +%s%N)" >> "$O/REAR-4K-PROCESS-EVENTS.txt"
wait "$publisher_pid"
publisher_rc=$?
publisher_pid=
if [[ -s "$O/REAR-4K-PUBLISHER-DONE.txt" ]]; then
  cat "$O/REAR-4K-PUBLISHER-DONE.txt" >> "$O/REAR-4K-PROCESS-EVENTS.txt"
else
  echo E004KA_MISSING_ACTUAL_PUBLISHER_COMPLETION_TIME >&2
fi
printf 'reader_rc=%s\npublisher_rc=%s\n' "$reader_rc" "$publisher_rc" > "$O/REAR-4K-PROCESS-RC.txt"
/usr/bin/python3 "$D/validate-partial.py" \
  "$O/REAL-REAR-CAPTURE180.txt" \
  "$O/REAL-REAR-VIRTUAL-READER90.txt" \
  "$O/REAL-REAR-VIRTUAL-GSTREAMER-APP90.txt" \
  "$O/REAR-4K-PROCESS-EVENTS.txt" \
  --meter "$O/REAR-4K-BYTE-BOUNDARY.txt" \
  --publisher-rc "$publisher_rc" --reader-rc "$reader_rc" \
  > "$O/REAR-4K-TEXT-ONLY-VALIDATION.txt" \
  2> "$O/REAR-4K-TEXT-ONLY-VALIDATION-ERROR.txt"
validator_rc=$?
set -e
grep -Fq 'SIZE=12441600 VIDEO=NV12_3840x2160_30' "$O/REAL-REAR-VIRTUAL-GSTREAMER-APP90.txt"
grep -Fq 'LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO' "$O/REAL-REAR-VIRTUAL-GSTREAMER-APP90.txt"
[[ ! -e "$O/rear-normal90.raw" && ! -e "$O/rear-normal90.nv12" ]]
REAR_VIRTUAL_END_NS=$(date +%s%N)
printf 'E004KA_REAL_REAR_4K_MEASURED reader_rc=%s publisher_rc=%s validator_rc=%s elapsed_ms=%s optical_frame_files=NO\n' \
  "$reader_rc" "$publisher_rc" "$validator_rc" "$(((REAR_VIRTUAL_END_NS-REAR_VIRTUAL_START_NS)/1000000))" \
  > "$O/REAR-VIRTUAL-RESULT.txt"
if [[ "$reader_rc" -ne 0 || "$publisher_rc" -ne 0 || "$validator_rc" -ne 0 ]]; then
  echo 'E004KA_BOUNDED_REAL_4K_APP_INCOMPLETE_OR_UNVERIFIED_FAIL_CLOSED' >&2
  exit 1
fi
grep -Fq 'E004KA_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=180' "$O/REAL-REAR-CONVERT180.txt"
grep -Fq 'E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=90 REQUESTED_FRAMES=90' "$O/REAL-REAR-VIRTUAL-GSTREAMER-APP90.txt"
# Isolate the physical rear-only candidate: unload virtual endpoint and
# neutralize the rear route. Neither front nor IR is streamed.
rmmod v4l2loopback > "$O/REAR-VIRTUAL-RMMOD.txt" 2>&1
udevadm settle
[[ ! -e "$LOOP_DEV" && ! -d /sys/module/v4l2loopback ]]
sleep 0.5
wait_suspend
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/NEUTRAL-MEDIA.txt"
/usr/bin/python3 "$H/route-state.py" "$O/NEUTRAL-MEDIA.txt" --expect neutral
wait_suspend
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$O/KERNEL-HEALTH.txt"
[[ ! -e "$O/front" ]]
done_ok=1
echo E004KA_REAL_REAR_4K_V4L2_TO_STANDARD_VIDEO90_90_APP_FRAMES_NO_FRONT_STREAM=PASS
