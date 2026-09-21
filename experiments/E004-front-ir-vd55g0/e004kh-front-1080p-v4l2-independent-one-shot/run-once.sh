#!/usr/bin/env bash
# E004kh: bounded real FRONT RAW10 RDI capture to direct NV12 GStreamer app; no rear/IR streaming.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kh
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$HW/modules/qcom-camss.ko
H=$R/experiments/E004-front-ir-vd55g0/e004kh-front-1080p-v4l2-independent-one-shot
O=$D/output
MEDIA=
FRONT_RAW_STREAM_STARTED=0
LOOP_MOD=$D/v4l2loopback.ko
LOOP_DEV=/dev/video91
publisher_pid=
START=0
done_ok=0
mkdir -p "$O"
at_exit() {
  rc=$?
  trap - EXIT
  if [ "$done_ok" -ne 1 ] && [ "$rc" -eq 0 ]; then rc=1; fi
  # A bounded publisher cannot survive an early failure or a delayed reboot.
  if [ -n "${publisher_pid:-}" ]; then
    kill -TERM "$publisher_pid" >/dev/null 2>&1 || :
    wait "$publisher_pid" >/dev/null 2>&1 || :
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
  if [ "$rc" -eq 0 ]; then echo PASS_FRONT_IMX681_RAW72_TO_STANDARD_NV12_1080P_VIDEO91_INDEPENDENT_READER24_APP24_NO_IR > "$D/ATTEMPT-RESULT.txt"
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
grep -Fq 'sp11_camera_e004kh_front_webcam=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004kh-front-webcam' /proc/cmdline
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
[[ "$(sha256sum "$FRONT_BRIDGE" | awk '{print $1}')" == 8e810a80366844a46ec83348d8a019172dfe6c364ae5f6f112d477ab823b90a2 ]]
[[ "$(sha256sum "$FRONT_APP" | awk '{print $1}')" == e165491ea22bcc4c452ea03073525662293c30ff3c274c67c4c6d4872e1c6b0a ]]
[[ "$(sha256sum "$FRONT_AUDIT" | awk '{print $1}')" == 2524c3588db803e052d28eef755149b8a9ffd0773954a804e1cc92d0ac70786f ]]
FRONT_NV12_AUDIT=$D/bridge/front-nv12-1080p-pipe-audit
[[ -f "$LOOP_MOD" && ! -L "$LOOP_MOD" && "$(sha256sum "$LOOP_MOD" | awk '{print $1}')" == 2307cabcde97ab9cca7166ded1c974a9378e2ec99b8b8b07afb7213b7bc5aad4 ]]
[[ "$(modinfo -F vermagic "$LOOP_MOD")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ -f "$FRONT_NV12_AUDIT" && ! -L "$FRONT_NV12_AUDIT" && "$(sha256sum "$FRONT_NV12_AUDIT" | awk '{print $1}')" == 8160bf78849bf5dac08394f1dc8b935af5399447a79d72e89e141297fc67fdf5 ]]
grep -Fq 'E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
[[ "$(sha256sum "$D/route-state.py" | awk '{print $1}')" == 84aa7e9b3a4960fd113320138e509b4e28026a7ae4462c31732f709d8c201498 ]]
[[ "$(sha256sum "$D/validate-front-rdi.py" | awk '{print $1}')" == 934fb0aea58c8996ec9edd1e9581c3ce83d7c48cff0ba8ae10923c4877ec95f4 ]]
grep -Fq 'E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
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
  echo E004KH_STOP_NO_COMPLETE_MEDIA_GRAPH_BEFORE_CAPTURE >&2
  exit 1
}
python3 "$H/discover-unified.py" --from-file "$O/ACCEPTED-MEDIA-GRAPH.txt" > "$O/UNIFIED.tmp" 2> "$O/UNIFIED-ERROR.txt" || {
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
FRONTSENSOR=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['front_sensor_entity'])")
FRONTSENSORDEV=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['front_sensor_device'])")
FRONTRDIVIDEO=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['front_rdi_video_device'])")
[[ "$FRONTSENSOR" == imx681\ * && -c "$FRONTSENSORDEV" && -c "$FRONTRDIVIDEO" ]]
# CRITICAL: this is a FRONT SENSOR on a generic RDI0 DMA, not the rear sensor.
# CSID1 pad 4 VFE1 PIX/QC10C remains OFF; IR and rear stay OFF.
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [1]'
media-ctl -d "$MEDIA" -p > "$O/FRONT-RDI-ON-MEDIA.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FRONT-RDI-ON-MEDIA.txt" --expect front-rdi-only
media-ctl -d "$MEDIA" -V "\"$FRONTSENSOR\":0 [fmt:SRGGB10_1X10/3840x2160]" > "$O/FRONT-RDI-CONFIG.txt" 2>&1
for e in msm_csiphy2:0 msm_csiphy2:1 msm_csid1:0 msm_csid1:1 msm_vfe1_rdi0:0 msm_vfe1_rdi0:1; do
  IFS=: read -r entity pad <<< "$e"
  media-ctl -d "$MEDIA" -V "\"$entity\":$pad [fmt:SRGGB10_1X10/3840x2160]" >> "$O/FRONT-RDI-CONFIG.txt" 2>&1
done
v4l2-ctl -d "$FRONTRDIVIDEO" --set-fmt-video=width=3840,height=2160,pixelformat=pRAA >> "$O/FRONT-RDI-CONFIG.txt" 2>&1
v4l2-ctl -d "$FRONTRDIVIDEO" --get-fmt-video >> "$O/FRONT-RDI-CONFIG.txt" 2>&1
grep -q "Width/Height.*3840/2160" "$O/FRONT-RDI-CONFIG.txt"
grep -q "Pixel Format.*pRAA" "$O/FRONT-RDI-CONFIG.txt"
grep -q "Bytes per Line.*4800" "$O/FRONT-RDI-CONFIG.txt"
grep -q "Size Image.*10368000" "$O/FRONT-RDI-CONFIG.txt"
# The front RAW10 RDI hardware path is physically proven by E004kg. Unlike
# that candidate, E004kh MUST provide a standard ordinary front V4L2 node to
# a separately opened V4L2 reader/app. Never store actual optical pixels.
modprobe videodev
insmod "$LOOP_MOD" devices=1 video_nr=91 card_label=SP11-Front-Preview \
  exclusive_caps=0 max_buffers=8 max_openers=5
udevadm settle
[[ -c "$LOOP_DEV" ]]
v4l2-ctl -d "$LOOP_DEV" -D > "$O/FRONT-VIRTUAL-DEVICE.txt"
grep -Fq 'SP11-Front-Preview' "$O/FRONT-VIRTUAL-DEVICE.txt"
v4l2-ctl --list-devices > "$O/FRONT-VIRTUAL-DISCOVERY.txt"
grep -Fq 'SP11-Front-Preview' "$O/FRONT-VIRTUAL-DISCOVERY.txt"
PUBLISHER_START_NS=$(date +%s%N)
printf 'PUBLISHER_START_NS=%s\n' "$PUBLISHER_START_NS" > "$O/FRONT-PROCESS-EVENTS.txt"
(
 set +e
 timeout --signal=TERM --kill-after=3s 58s bash -o pipefail -c '
   v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=72 --stream-to=- --verbose 2>"$2" |
     "$3" --frames 72 --idle-ms 7000 2>"$4" |
     "$5" --frames 72 2>"$6" |
     gst-launch-1.0 -q fdsrc fd=0 blocksize=3110400 \
       ! rawvideoparse format=nv12 width=1920 height=1080 framerate=30/1 \
       ! "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1" \
       ! v4l2sink device="$7" sync=true qos=true max-lateness=-1 >"$8" 2>&1
 ' bash "$FRONTRDIVIDEO" "$O/REAL-FRONT-RAW72-CAPTURE.txt" \
   "$FRONT_AUDIT" "$O/FRONT-RAW72-BYTE-METER.txt" "$FRONT_BRIDGE" \
   "$O/FRONT-NV12-72-CONVERTER.txt" "$LOOP_DEV" "$O/FRONT-NV12-TO-VIRTUAL-PUBLISHER.txt"
 publisher_inner_rc=$?
 printf 'PUBLISHER_END_NS=%s\n' "$(date +%s%N)" > "$O/FRONT-PUBLISHER-DONE.txt"
 exit "$publisher_inner_rc"
) &
publisher_pid=$!
# Open the independent reader promptly after the FIRST advertised NV12
# 1920x1080 virtual format, with no dependence on synthetic caps FPS.
virtual_ready=0
for _ in $(seq 1 100); do
 if timeout 2s v4l2-ctl -d "$LOOP_DEV" --get-fmt-video > "$O/FRONT-VIRTUAL-FORMAT.txt" 2>/dev/null &&
    grep -q 'Width/Height.*1920/1080' "$O/FRONT-VIRTUAL-FORMAT.txt" &&
    grep -q 'Pixel Format.*NV12' "$O/FRONT-VIRTUAL-FORMAT.txt"; then
   virtual_ready=1; break
 fi
 kill -0 "$publisher_pid"
 sleep 0.05
done
[[ "$virtual_ready" -eq 1 ]]
printf 'VIRTUAL_FORMAT_READY_NS=%s\n' "$(date +%s%N)" >> "$O/FRONT-PROCESS-EVENTS.txt"
printf 'READER_START_NS=%s\n' "$(date +%s%N)" >> "$O/FRONT-PROCESS-EVENTS.txt"
set +e
timeout --signal=TERM --kill-after=3s 28s bash -o pipefail -c '
 v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=24 --stream-to=- --verbose 2>"$2" |
   "$3" --frames 24 --idle-ms 6000 2>"$4" |
   /usr/bin/python3 "$5" --frames 24 --require-distinct --idle-seconds 6 2>"$6"
' bash "$LOOP_DEV" "$O/INDEPENDENT-FRONT-VIDEO91-READER24.txt" \
 "$FRONT_NV12_AUDIT" "$O/INDEPENDENT-FRONT-NV12-METER24.txt" \
 "$FRONT_APP" "$O/INDEPENDENT-FRONT-GSTREAMER-APP24.txt"
reader_rc=$?
printf 'READER_END_NS=%s\n' "$(date +%s%N)" >> "$O/FRONT-PROCESS-EVENTS.txt"
wait "$publisher_pid"
publisher_rc=$?
publisher_pid=
if [[ -s "$O/FRONT-PUBLISHER-DONE.txt" ]]; then
 cat "$O/FRONT-PUBLISHER-DONE.txt" >> "$O/FRONT-PROCESS-EVENTS.txt"
else
 echo E004KH_MISSING_ACTUAL_PUBLISHER_COMPLETION_TIME >&2
fi
printf 'reader_rc=%s\npublisher_rc=%s\n' "$reader_rc" "$publisher_rc" > "$O/FRONT-PROCESS-RC.txt"
set -e
/usr/bin/python3 "$D/validate-front-rdi.py" \
 "$O/REAL-FRONT-RAW72-CAPTURE.txt" "$O/FRONT-RAW72-BYTE-METER.txt" \
 "$O/FRONT-NV12-72-CONVERTER.txt" "$O/INDEPENDENT-FRONT-VIDEO91-READER24.txt" \
 "$O/INDEPENDENT-FRONT-NV12-METER24.txt" "$O/INDEPENDENT-FRONT-GSTREAMER-APP24.txt" \
 --publisher-rc "$publisher_rc" --reader-rc "$reader_rc" \
 > "$O/FRONT-1080P-V4L2-TEXT-VALIDATION.txt"
[[ "$reader_rc" -eq 0 && "$publisher_rc" -eq 0 ]]
grep -Fq 'E004KH_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=72 FULL_FRAMES=72' "$O/FRONT-RAW72-BYTE-METER.txt"
grep -Fq 'E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=72' "$O/FRONT-NV12-72-CONVERTER.txt"
grep -Fq 'E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=24 FULL_FRAMES=24' "$O/INDEPENDENT-FRONT-NV12-METER24.txt"
grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=24 REQUESTED_FRAMES=24' "$O/INDEPENDENT-FRONT-GSTREAMER-APP24.txt"
grep -Fq 'DISTINCT_PAYLOADS_VERIFIED=YES' "$O/INDEPENDENT-FRONT-GSTREAMER-APP24.txt"
# Close every app/publisher before temporary loopback removal and media
# neutralization; NEVER modify the Golden modules or persistent boot defaults.
rmmod v4l2loopback > "$O/FRONT-VIRTUAL-RMMOD.txt" 2>&1
[[ ! -e "$LOOP_DEV" && ! -d /sys/module/v4l2loopback ]]
media-ctl -d "$MEDIA" -l '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
udevadm settle
wait_suspend
media-ctl -d "$MEDIA" -p > "$O/FINAL-NEUTRAL-MEDIA.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FINAL-NEUTRAL-MEDIA.txt" --expect neutral
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$O/KERNEL-HEALTH.txt"
[[ ! -e "$O/front-normal.raw" && ! -e "$O/front-normal.nv12" ]]
done_ok=1
echo E004KH_REAL_FRONT_1080P_STANDARD_V4L2_VIDEO91_INDEPENDENT_APP24=PASS
