#!/usr/bin/env bash
# E004kp: bounded rear-only direct mmap publication; no front or IR.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kp
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$HW/modules/qcom-camss.ko
H=$R/experiments/E004-front-ir-vd55g0/e004kp-direct-rear-mmap-one-shot
O=$D/output
MEDIA=
FRONT_RAW_STREAM_STARTED=0
LOOP_MOD=$D/v4l2loopback.ko
LOOP_DEV=/dev/video91
publisher_pid=
thermal_pid=
START=0
done_ok=0
mkdir -p "$O"
assert_publisher_group_exited() {
  local pgid=$1
  if kill -0 -- "-$pgid" 2>/dev/null; then
    echo E004KP_PUBLISHER_DESCENDANTS_STILL_ALIVE >&2
    return 1
  fi
}
assert_idle_devices() {
  # Known publishers are waited/reaped; independently refuse any remaining device opener.
  if fuser -s /dev/video* /dev/v4l-subdev*; then
    echo E004KP_CAMERA_DEVICE_STILL_OPEN >&2
    return 1
  fi
}
at_exit() {
  rc=$?
  trap - EXIT
  if [ "$done_ok" -ne 1 ] && [ "$rc" -eq 0 ]; then rc=1; fi
  if [ -n "${thermal_pid:-}" ]; then
    kill -TERM "$thermal_pid" 2>/dev/null || :
    wait "$thermal_pid" 2>/dev/null || :
  fi
  # A bounded publisher cannot survive an early failure or a delayed reboot.
  if [ -n "${publisher_pid:-}" ]; then
    kill -TERM -- "-$publisher_pid" >/dev/null 2>&1 || :
    for _ in $(seq 1 30); do
      kill -0 -- "-$publisher_pid" 2>/dev/null || break
      sleep 0.1
    done
    kill -KILL -- "-$publisher_pid" >/dev/null 2>&1 || :
    wait "$publisher_pid" >/dev/null 2>&1 || :
    if ! assert_publisher_group_exited "$publisher_pid"; then
      echo FAIL_PUBLISHER_GROUP_REMAINS_AUTO_GOLDEN > "$D/ATTEMPT-RESULT.txt"
      exit 1
    fi
  fi
  if [ -n "$MEDIA" ] && ! assert_idle_devices; then
    echo FAIL_DEVICE_OPEN_AUTO_GOLDEN_NO_ROUTE_MUTATION > "$D/ATTEMPT-RESULT.txt"
    exit 1
  fi
  if [ -d /sys/module/v4l2loopback ]; then
    timeout --signal=TERM --kill-after=3s 6s rmmod v4l2loopback > "$O/FRONT-VIRTUAL-UNDO.txt" 2>&1 || rc=1
  fi
  [[ ! -e /dev/video90 && ! -e "$LOOP_DEV" && ! -d /sys/module/v4l2loopback ]] || rc=1
  if [ -n "$MEDIA" ]; then
    # Front C-PHY/RDI MUST be neutral on success AND on any failure/timeout.
    media-ctl -d "$MEDIA" -l '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [0]' > "$O/FRONT-RDI-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]' > "$O/FRONT-PHY-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]' > "$O/FRONT-PIX-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]' > "$O/REAR-PHY-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]' > "$O/REAR-RDI-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -p > "$O/FINAL-MEDIA.txt" 2>&1 || :
  fi
  dmesg | tail -n +$((START+1)) > "$O/DMESG.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then echo PASS_E004KP_REAR1800_DIRECT_MMAP_APP_SUSTAINED_NO_IR > "$D/ATTEMPT-RESULT.txt"
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
grep -Fq 'sp11_camera_e004kp_rgb_session=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004kp-rgb-session' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$env"
grep -qx 'next_entry=' <<<"$env"
[[ ! -e "$D/ATTEMPT-CONSUMED" && ! -e /dev/media0 && ! -e /dev/video90 && ! -e /dev/video91 && ! -d /sys/module/v4l2loopback ]]
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' \
  "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
START=$(dmesg | wc -l)
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d "/sys/module/$m" ]]; done
[[ "$(sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$D/stack"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 > "$O/PACKAGE-VERIFY.txt" )
[[ "$(sha256sum "$CAND" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
# Exact accepted R4 front package stays intact, but RDI bypass does not run QC10C PIX IQ.
[[ -f "$P/userspace/iq/authority/r4-bootstrap.bin" ]]
[[ "$(stat -c%s "$P/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sha256sum "$P/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
FRONT_BRIDGE=$D/bridge/front-rggb10p-to-nv12-1080
FRONT_APP=$D/bridge/front-1080p-app.py
FRONT_AUDIT=$D/bridge/front-rdi-raw10-pipe-audit
[[ -f "$FRONT_BRIDGE" && ! -L "$FRONT_BRIDGE" && -f "$FRONT_APP" && ! -L "$FRONT_APP" && -f "$FRONT_AUDIT" && ! -L "$FRONT_AUDIT" ]]
[[ "$(sha256sum "$FRONT_BRIDGE" | awk '{print $1}')" == 820a6871f78e9ecaecfd4b1a16fc1e0bad9600aeeb6a1505133e467c1354dc82 ]]
[[ "$(sha256sum "$FRONT_APP" | awk '{print $1}')" == e165491ea22bcc4c452ea03073525662293c30ff3c274c67c4c6d4872e1c6b0a ]]
[[ "$(sha256sum "$FRONT_AUDIT" | awk '{print $1}')" == 377a9c2e8704bd57687c5449608c632e1e06cc39067b87cc28aa3ac8a060d186 ]]
FRONT_NV12_AUDIT=$D/bridge/front-nv12-1080p-pipe-audit
[[ -f "$LOOP_MOD" && ! -L "$LOOP_MOD" && "$(sha256sum "$LOOP_MOD" | awk '{print $1}')" == 1d34a54eac776d780add46097dff2bd0bf49405e5ca8337e2694451022e89bb6 ]]
[[ "$(modinfo -F vermagic "$LOOP_MOD")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ -f "$FRONT_NV12_AUDIT" && ! -L "$FRONT_NV12_AUDIT" && "$(sha256sum "$FRONT_NV12_AUDIT" | awk '{print $1}')" == 23e5152cea7dab8b437eae309f16a8f33e7c01b50f9ab61fa26f952d90b3600e ]]
grep -Fq 'E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
[[ "$(sha256sum "$D/route-state.py" | awk '{print $1}')" == 53c2230114512b954c67fa4572df569394d3bd259fb3ae036691f72002009861 ]]
[[ "$(sha256sum "$D/validate-front-rdi.py" | awk '{print $1}')" == 934fb0aea58c8996ec9edd1e9581c3ce83d7c48cff0ba8ae10923c4877ec95f4 ]]
grep -Fq 'E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
[[ "$(sha256sum "$HW/modules/imx681.ko" | awk '{print $1}')" == ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ]]
[[ "$(sha256sum "$HW/modules/ov13858.ko" | awk '{print $1}')" == 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ]]
[[ "$(sha256sum "$HW/modules/sp11-vd55g0.ko" | awk '{print $1}')" == 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
[[ "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" == "$(runuser -u geoca -- git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
sha256sum -c "$D/SESSION-ASSETS.sha256" > "$O/SESSION-ASSETS-VERIFY.txt"
command -v fuser >/dev/null
python3 "$D/thermal-monitor.py" > "$O/THERMAL.jsonl" &
thermal_pid=$!
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
  echo E004KH_STOP_NO_COMPLETE_MEDIA_GRAPH_BEFORE_CAPTURE >&2
  exit 1
}
python3 "$D/discover-unified.py" --from-file "$O/ACCEPTED-MEDIA-GRAPH.txt" > "$O/UNIFIED.tmp" 2> "$O/UNIFIED-ERROR.txt" || {
  echo E004KH_UNIFIED_PARSER_REJECTED_ARCHIVED_CURRENT_GRAPH >&2
  exit 1
}
mv "$O/UNIFIED.tmp" "$O/UNIFIED.json"
[[ -s "$O/UNIFIED.json" ]]
MEDIA=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['media'])")
media-ctl -d "$MEDIA" -p > "$O/INITIAL-MEDIA.txt"
initial=$(/usr/bin/python3 "$D/route-state.py" "$O/INITIAL-MEDIA.txt")
case "$initial" in
  "E004KH_MEDIA_ROUTE=neutral "*) ;;
  "E004KH_MEDIA_ROUTE=rear-only "*)
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
    ;;
  *) echo "E004KH_REJECT_UNEXPECTED_INITIAL_MEDIA=$initial" >&2; exit 1 ;;
esac
media-ctl -d "$MEDIA" -p > "$O/FRONT-PRE-NEUTRAL.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FRONT-PRE-NEUTRAL.txt" --expect neutral
wait_suspend
LOOP_DEV=/dev/video90
BRIDGE_BIN=$D/bridge/rear-bayer-to-nv12-4k
BRIDGE_APP=$D/bridge/nv12-4k-partial-telemetry-app.py
PIPE_AUDIT=$D/bridge/nv12-4k-pipe-audit
REARSENSOR=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_sensor_entity'])")
REARSENSORDEV=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_sensor_device'])")
REARVIDEO=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_video_device'])")
[[ "$REARSENSOR" == ov13858\ * && -c "$REARSENSORDEV" && -c "$REARVIDEO" ]]
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'
media-ctl -d "$MEDIA" -p > "$O/REAR-ON-MEDIA.txt"
/usr/bin/python3 "$D/route-state.py" "$O/REAR-ON-MEDIA.txt" --expect rear-only
media-ctl -d "$MEDIA" -V "\"$REARSENSOR\":0 [fmt:SGRBG10_1X10/4076x2806]" > "$O/REAR-CONFIG.txt" 2>&1
for e in msm_csiphy1:0 msm_csiphy1:1 msm_csid0:0 msm_csid0:1 msm_vfe0_rdi0:0 msm_vfe0_rdi0:1; do
  IFS=: read -r entity pad <<< "$e"
  media-ctl -d "$MEDIA" -V "\"$entity\":$pad [fmt:SGRBG10_1X10/4076x2806]" >> "$O/REAR-CONFIG.txt" 2>&1
done
v4l2-ctl -d "$REARVIDEO" --set-fmt-video=width=4076,height=2806,pixelformat=pgAA >> "$O/REAR-CONFIG.txt" 2>&1
v4l2-ctl -d "$REARVIDEO" --get-fmt-video >> "$O/REAR-CONFIG.txt" 2>&1
grep -q "Width/Height.*4076/2806" "$O/REAR-CONFIG.txt"
grep -q "Pixel Format.*pgAA" "$O/REAR-CONFIG.txt"
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
setsid /bin/bash "$D/publish-rear.sh" "$REARVIDEO" "$O" "$BRIDGE_BIN" "$LOOP_DEV" &
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
timeout --signal=TERM --kill-after=3s 190s /usr/bin/python3 "$D/direct-camera-app.py" --camera rear --source device --frames 1800 --require-distinct --deadline-seconds 180 > "$O/REAR-DIRECT-APP.jsonl" 2> "$O/REAR-DIRECT-APP-ERROR.txt"
reader_rc=$?
printf 'READER_END_NS=%s\n' "$(date +%s%N)" >> "$O/REAR-4K-PROCESS-EVENTS.txt"
wait "$publisher_pid"
publisher_rc=$?
assert_publisher_group_exited "$publisher_pid" || exit 1
publisher_pid=
if [[ -s "$O/REAR-4K-PUBLISHER-DONE.txt" ]]; then
  cat "$O/REAR-4K-PUBLISHER-DONE.txt" >> "$O/REAR-4K-PROCESS-EVENTS.txt"
else
  echo E004KD_MISSING_ACTUAL_PUBLISHER_COMPLETION_TIME >&2
fi
printf 'reader_rc=%s\npublisher_rc=%s\n' "$reader_rc" "$publisher_rc" > "$O/REAR-4K-PROCESS-RC.txt"
set -e
[[ "$reader_rc" -eq 0 && "$publisher_rc" -eq 0 ]]
python3 "$D/validate-session.py" rear "$O" > "$O/REAR-DIRECT-VALIDATION.json"

# Isolate the physical rear-only candidate: unload virtual endpoint and
# neutralize the rear route. Neither front nor IR is streamed.
assert_idle_devices
rmmod v4l2loopback > "$O/REAR-VIRTUAL-RMMOD.txt" 2>&1
udevadm settle
[[ ! -e "$LOOP_DEV" && ! -d /sys/module/v4l2loopback ]]
sleep 0.5
wait_suspend
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/NEUTRAL-MEDIA.txt"
/usr/bin/python3 "$D/route-state.py" "$O/NEUTRAL-MEDIA.txt" --expect neutral
wait_suspend
assert_idle_devices
printf 'rear_publishers_and_readers_exited=YES\n' >> "$O/SESSION-STOP-PROOFS.txt"
python3 "$D/camera-session-contract.py" --all-processes-stopped \
 --snapshot "$O/FRONT-PRE-NEUTRAL.txt" --snapshot "$O/REAR-ON-MEDIA.txt" \
 --snapshot "$O/NEUTRAL-MEDIA.txt" > "$O/SESSION-GRAPH-CYCLE.json"
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$O/KERNEL-HEALTH.txt"
[[ ! -e "$O/front-normal.raw" && ! -e "$O/front-normal.nv12" ]]
done_ok=1
echo E004KP_REAR1800_DIRECT_MMAP_APP_SESSION=PASS
