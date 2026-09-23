#!/usr/bin/env bash
# E004mc: front1080p/rear4K continuous publisher, independent app, IR off.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004mc
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$HW/modules/qcom-camss.ko
H=$R/experiments/E004-front-ir-vd55g0/e004mc-guarded-raw-vs-nv12-rgb-source-probe-one-shot
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
    echo E004MC_PUBLISHER_DESCENDANTS_STILL_ALIVE >&2
    return 1
  fi
}
assert_idle_devices() {
  # Known publishers are waited/reaped; independently refuse any remaining device opener.
  if fuser -s /dev/video* /dev/v4l-subdev*; then
    echo E004MC_CAMERA_DEVICE_STILL_OPEN >&2
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
  systemctl stop sp11-camera-e004mc-session@front.service sp11-camera-e004mc-session@rear.service || rc=1
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
  # An uncertain STREAMOFF or failed app/reader prohibits speculative
  # link-disabling in the exit trap. The guarded service returns to Golden
  # on ANY failure; only the successful main path may have already
  # stopped publishers and explicitly neutralized its known active route.
  if [ "$rc" -eq 0 ]; then
    [[ ! -e /dev/video90 && ! -e /dev/video91 &&
       ! -d /sys/module/v4l2loopback ]] || rc=1
    if [ -n "$MEDIA" ] && [ "$rc" -eq 0 ]; then
      media-ctl -d "$MEDIA" -p > "$O/FINAL-MEDIA.txt" 2>&1 || rc=1
      if [ "$rc" -eq 0 ]; then
        python3 "$D/route-state.py" "$O/FINAL-MEDIA.txt" --expect neutral           > "$O/FINAL-NATIVE-NEUTRAL-PROOF.txt" 2>&1 || rc=1
      fi
    fi
  else
    echo E004MC_UNCERTAIN_EXIT_SKIP_GRAPH_AND_MODULE_MUTATION_REBOOT_GOLDEN       > "$O/FAILURE-CLEANUP-POLICY.txt"
  fi
  dmesg | tail -n +$((START+1)) > "$O/DMESG.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then echo PASS_E004MC_PAIRED_RAW8_NV12_BOTH_RGB_SCENE_NO_IR > "$D/ATTEMPT-RESULT.txt"
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
grep -Fq 'sp11_camera_e004mc_rgb_session=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004mc-rgb-session' /proc/cmdline
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
[[ -f "$LOOP_MOD" && ! -L "$LOOP_MOD" && "$(sha256sum "$LOOP_MOD" | awk '{print $1}')" == 739564139552eebdb51c64d750cb746aa96745054d21d7e2f7d0445c59e32db1 ]]
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
  *) echo "E004KH_REJECT_UNEXPECTED_INITIAL_MEDIA=$initial" >&2; exit 1 ;;
esac
media-ctl -d "$MEDIA" -p > "$O/FRONT-PRE-NEUTRAL.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FRONT-PRE-NEUTRAL.txt" --expect neutral
wait_suspend
# Retain both ordinary selectable endpoints throughout the managed handoff.
modprobe videodev
insmod "$LOOP_MOD" devices=2 video_nr=91,90 card_label=SP11-Front-Preview,SP11-Rear-Preview exclusive_caps=0,0 max_buffers=8 max_openers=5
udevadm settle
access_ready=0
for _ in $(seq 1 150); do
 if runuser -u geoca -- /bin/sh -c 'test -r /dev/video91 && test -w /dev/video91 && test -r /dev/video90 && test -w /dev/video90'; then access_ready=1; break; fi
 sleep 0.2
done
[[ "$access_ready" -eq 1 ]]
runuser -u geoca -- /usr/bin/python3 -c 'import os,json,stat; nodes=["/dev/video91","/dev/video90"]; access={p:stat.S_ISCHR(os.stat(p).st_mode) and os.access(p,os.R_OK|os.W_OK) for p in nodes}; assert os.geteuid()==1000 and all(access.values()); print(json.dumps({"uid":os.geteuid(),"read_write_access":access,"permissions_modified":False}))' > "$O/UNPRIVILEGED-ACCESS.json"
runuser -u geoca -- v4l2-ctl --list-devices > "$O/UNPRIVILEGED-DEVICE-DISCOVERY.txt"
grep -Fq 'SP11-Front-Preview' "$O/UNPRIVILEGED-DEVICE-DISCOVERY.txt"
grep -Fq 'SP11-Rear-Preview' "$O/UNPRIVILEGED-DEVICE-DISCOVERY.txt"
# E004mc: stop/reopen/route transitions are owned by the maintained
# root-private RGBSession + fresh-read exact-119-edge media backend.
# The preflight above established the immutable hardware/source stage,
# complete neutral graph, IR standby and two named unprivileged endpoints.
[[ -f "$D/rgb/service/selector.py" && -f "$D/rgb/service/rgbctl.py" &&
   -f "$D/rgb/service/selector_acceptance.py" &&
   -f /usr/local/lib/sp11-camera-e004mc/scene_probe.py &&
   -f "$D/routing/route_policy.py" ]]
# Finite root-owned Unix-socket selector: separate controller process and
# independent uid1000 V4L2 app clients, never concurrent sensor routes.
python3 "$D/rgb/service/selector_acceptance.py" --candidate e004mc \
  > "$O/RGB-SELECTOR-ACCEPTANCE-STDOUT.json" 2> "$O/RGB-SELECTOR-ACCEPTANCE-STDERR.txt"
python3 - "$O/RGB-SELECTOR-ACCEPTANCE.json" <<'VALIDATE_RGB_SELECTOR'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"]=="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K"
assert d["camera_order"]==["front","rear"]
assert d["verified_reversible_command_sequence"]==["front","rear","off","quit"]
assert set(d["scene_probe"])=={"front","rear"}
assert all(d["scene_probe"][camera]["app"]["frames"]==90 and
           d["scene_probe"][camera]["app"]["effective_uid"]==1000 and
           not d["scene_probe"][camera]["app"]["pixel_files_saved"]
           for camera in ("front","rear"))
assert all(d["client_results"][c]["normal_unprivileged_opens_with_120_complete_frames_each"]==3
           for c in ("front","rear"))
print("E004MC_REAL_RGB_ROOT_UNIX_SOCKET_SELECTOR_FRONT_REAR=PASS")
VALIDATE_RGB_SELECTOR
# E004mc: the physical SAME mmap source frame must have yielded four
# source RAW10-upper8-vs-converted-NV12-Y scalar pairs PER camera.
# Do not claim useful images if this is missing; parse only aggregate text.
python3 "$D/paired_source_validator.py" "$O" > "$O/PAIRED-RAW-NV12-RESULT.json"
grep -Fq 'PASS_BOUNDED_REAL_PAIRED_SOURCE_RAW8_VS_NV12_SCALAR_FRAMES' "$O/PAIRED-RAW-NV12-RESULT.json"
# No camera source, independent user app or root publisher FD may survive
# the session controller's independently audited stop checkpoint.
assert_idle_devices
media-ctl -d "$MEDIA" -p > "$O/NEUTRAL-MEDIA.txt"
python3 "$D/route-state.py" "$O/NEUTRAL-MEDIA.txt" --expect neutral
# Remove only this candidate's temporary virtual output module, not any
# protected Golden module, after both real cameras are neutral and closed.
rmmod v4l2loopback > "$O/VIRTUAL-RMMOD.txt" 2>&1
udevadm settle
[[ ! -e /dev/video90 && ! -e /dev/video91 && ! -d /sys/module/v4l2loopback ]]
wait_suspend
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$O/KERNEL-HEALTH.txt"
[[ ! -e "$O/front-normal.raw" && ! -e "$O/front-normal.nv12" ]]
done_ok=1
echo E004MC_NATIVE_RGB_SELECTOR_FRONT_REAR_UID1000=PASS
