#!/usr/bin/env bash
# E004kf: bounded real FRONT RAW10 RDI capture to direct NV12 GStreamer app; no rear/IR streaming.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kf
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$HW/modules/qcom-camss.ko
H=$R/experiments/E004-front-ir-vd55g0/e004kf-front-rdi-optical-native1080-one-shot
O=$D/output
MEDIA=
FRONT_RAW_STREAM_STARTED=0
START=0
done_ok=0
mkdir -p "$O"
at_exit() {
  rc=$?
  trap - EXIT
  if [ "$done_ok" -ne 1 ] && [ "$rc" -eq 0 ]; then rc=1; fi
  # No virtual module is loaded in this FIRST front-RDI evidence boot.
  [[ ! -e /dev/video90 && ! -e /dev/video91 && ! -d /sys/module/v4l2loopback ]] || rc=1
  if [ -n "$MEDIA" ]; then
    # Front C-PHY/RDI MUST be neutral on success AND on any failure/timeout.
    media-ctl -d "$MEDIA" -l '"msm_csid1":1 -> "msm_vfe0_rdi0":0 [0]' > "$O/FRONT-RDI-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]' > "$O/FRONT-PHY-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]' > "$O/FRONT-PIX-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]' > "$O/REAR-PHY-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]' > "$O/REAR-RDI-UNDO.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -p > "$O/FINAL-MEDIA.txt" 2>&1 || :
  fi
  dmesg | tail -n +$((START+1)) > "$O/DMESG.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then echo PASS_REAL_FRONT_RDI_RAW10_8_TO_GSTREAMER_NV12_1080P_NO_IR_NO_VIRTUAL > "$D/ATTEMPT-RESULT.txt"
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
grep -Fq 'sp11_camera_e004kf_front_rdi=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004kf-front-rdi' /proc/cmdline
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
[[ "$(sha256sum "$FRONT_BRIDGE" | awk '{print $1}')" == 3b4120431e0bc00429967dc476a24fc1edf5b2d082e12e814c1065bdf17724db ]]
[[ "$(sha256sum "$FRONT_APP" | awk '{print $1}')" == 38fe90ca920b31edb1dced7bb36874d29a7ebc129754220546410130a20c068e ]]
[[ "$(sha256sum "$FRONT_AUDIT" | awk '{print $1}')" == 9ef2bcc93b85ba8e1af3337f77d6e8dbe0d8a2bd23ea70793f84c293e7be14df ]]
[[ "$(sha256sum "$D/route-state.py" | awk '{print $1}')" == 91dbfe9b1ae299c69792e62efcc8cf2e2e0da665dc46d90743c64b83d5cec035 ]]
[[ "$(sha256sum "$D/validate-front-rdi.py" | awk '{print $1}')" == ad5592776eb77cb941b96763cb4cb3419cff95a3f2b62cca50cd526dbc643c8b ]]
grep -Fq 'E004KE_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KF_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
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
  echo E004KF_STOP_NO_COMPLETE_MEDIA_GRAPH_BEFORE_CAPTURE >&2
  exit 1
}
python3 "$H/discover-unified.py" --from-file "$O/ACCEPTED-MEDIA-GRAPH.txt" > "$O/UNIFIED.tmp" 2> "$O/UNIFIED-ERROR.txt" || {
  echo E004KF_UNIFIED_PARSER_REJECTED_ARCHIVED_CURRENT_GRAPH >&2
  exit 1
}
mv "$O/UNIFIED.tmp" "$O/UNIFIED.json"
[[ -s "$O/UNIFIED.json" ]]
MEDIA=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['media'])")
media-ctl -d "$MEDIA" -p > "$O/INITIAL-MEDIA.txt"
initial=$(/usr/bin/python3 "$D/route-state.py" "$O/INITIAL-MEDIA.txt")
case "$initial" in
  "E004KF_MEDIA_ROUTE=neutral "*) ;;
  "E004KF_MEDIA_ROUTE=rear-only "*)
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
    ;;
  *) echo "E004KF_REJECT_UNEXPECTED_INITIAL_MEDIA=$initial" >&2; exit 1 ;;
esac
media-ctl -d "$MEDIA" -p > "$O/FRONT-PRE-NEUTRAL.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FRONT-PRE-NEUTRAL.txt" --expect neutral
wait_suspend
FRONTSENSOR=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['front_sensor_entity'])")
FRONTSENSORDEV=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['front_sensor_device'])")
FRONTRDIVIDEO=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_video_device'])")
[[ "$FRONTSENSOR" == imx681\ * && -c "$FRONTSENSORDEV" && -c "$FRONTRDIVIDEO" ]]
# CRITICAL: this is a FRONT SENSOR on a generic RDI0 DMA, not the rear sensor.
# CSID1 pad 4 VFE1 PIX/QC10C remains OFF; IR and rear stay OFF.
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid1":1 -> "msm_vfe0_rdi0":0 [1]'
media-ctl -d "$MEDIA" -p > "$O/FRONT-RDI-ON-MEDIA.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FRONT-RDI-ON-MEDIA.txt" --expect front-rdi-only
media-ctl -d "$MEDIA" -V "\"$FRONTSENSOR\":0 [fmt:SRGGB10_1X10/3840x2160]" > "$O/FRONT-RDI-CONFIG.txt" 2>&1
for e in msm_csiphy2:0 msm_csiphy2:1 msm_csid1:0 msm_csid1:1 msm_vfe0_rdi0:0 msm_vfe0_rdi0:1; do
  IFS=: read -r entity pad <<< "$e"
  media-ctl -d "$MEDIA" -V "\"$entity\":$pad [fmt:SRGGB10_1X10/3840x2160]" >> "$O/FRONT-RDI-CONFIG.txt" 2>&1
done
v4l2-ctl -d "$FRONTRDIVIDEO" --set-fmt-video=width=3840,height=2160,pixelformat=pRAA >> "$O/FRONT-RDI-CONFIG.txt" 2>&1
v4l2-ctl -d "$FRONTRDIVIDEO" --get-fmt-video >> "$O/FRONT-RDI-CONFIG.txt" 2>&1
grep -q "Width/Height.*3840/2160" "$O/FRONT-RDI-CONFIG.txt"
grep -q "Pixel Format.*pRAA" "$O/FRONT-RDI-CONFIG.txt"
grep -q "Bytes per Line.*4800" "$O/FRONT-RDI-CONFIG.txt"
grep -q "Size Image.*10368000" "$O/FRONT-RDI-CONFIG.txt"
# No front test-pattern API exists. Real normal optical sensor frames are
# piped without creating front Bayer or NV12 files. Only bounded text logs.
FRONT_RAW_STREAM_STARTED=1
set +e
timeout --signal=TERM --kill-after=3s 48s bash -o pipefail -c '
 v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=8 --stream-to=- --verbose 2>"$2" |
   "$3" --frames 8 --idle-ms 6500 2>"$4" |
   "$5" --frames 8 2>"$6" |
   /usr/bin/python3 "$7" --frames 8 --require-distinct --idle-seconds 7 2>"$8"
' bash "$FRONTRDIVIDEO" "$O/FRONT-RDI-REAL-SOURCE.txt" \
  "$FRONT_AUDIT" "$O/FRONT-RDI-RAW-PIPE.txt" "$FRONT_BRIDGE" \
  "$O/FRONT-RDI-CONVERSION.txt" "$FRONT_APP" "$O/FRONT-1080P-GSTREAMER-APP.txt"
front_rc=$?
set -e
printf 'front_pipeline_rc=%s\n' "$front_rc" > "$O/FRONT-RDI-PIPE-RC.txt"
# Physical proof is only valid when the independent V4L2 data producer,
# exact RAW10 byte meter, Bayer demosaic and genuine appsink all pass.
[[ "$front_rc" -eq 0 ]] || { echo E004KF_FRONT_RAW_V4L2_TO_NV12_APP_FAIL_CLOSED >&2; exit 1; }
grep -Fq 'E004KF_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=8 FULL_FRAMES=8' "$O/FRONT-RDI-RAW-PIPE.txt"
grep -Fq 'BYTES_IN=82944000 BYTES_OUT=82944000 INCOMPLETE_TAIL_BYTES=0 TERMINATION=EOF' "$O/FRONT-RDI-RAW-PIPE.txt"
grep -Fq 'E004KE_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=8' "$O/FRONT-RDI-CONVERSION.txt"
grep -Fq 'E004KF_NV12_APPSRC_CONSUMER=PASS FRAMES=8 REQUESTED_FRAMES=8' "$O/FRONT-1080P-GSTREAMER-APP.txt"
grep -Fq 'SIZE=3110400 VIDEO=NV12_1920x1080_30' "$O/FRONT-1080P-GSTREAMER-APP.txt"
grep -Fq 'DISTINCT_PAYLOADS_VERIFIED=YES' "$O/FRONT-1080P-GSTREAMER-APP.txt"
/usr/bin/python3 "$D/validate-front-rdi.py" \
  "$O/FRONT-RDI-REAL-SOURCE.txt" "$O/FRONT-RDI-RAW-PIPE.txt" \
  "$O/FRONT-RDI-CONVERSION.txt" "$O/FRONT-1080P-GSTREAMER-APP.txt" \
  > "$O/FRONT-RDI-TEXT-VALIDATION.txt"
media-ctl -d "$MEDIA" -l '"msm_csid1":1 -> "msm_vfe0_rdi0":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
udevadm settle
wait_suspend
media-ctl -d "$MEDIA" -p > "$O/FINAL-NEUTRAL-MEDIA.txt"
/usr/bin/python3 "$D/route-state.py" "$O/FINAL-NEUTRAL-MEDIA.txt" --expect neutral
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$O/KERNEL-HEALTH.txt"
[[ ! -e "$O/front-normal.raw" && ! -e "$O/front-normal.nv12" ]]
done_ok=1
echo E004KF_REAL_FRONT_OPTICAL_RDI_RAW10_8_TO_REAL_GSTREAMER_NV12_1080P=PASS
