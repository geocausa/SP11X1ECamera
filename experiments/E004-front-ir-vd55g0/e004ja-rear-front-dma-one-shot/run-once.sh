#!/usr/bin/env bash
# E004ja: bounded rear Bayer + front QC10C DMA-guard handoff regression.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004ja
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$D/candidate/qcom-camss.ko
H=$R/experiments/E004-front-ir-vd55g0/e004ja-rear-front-dma-one-shot
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
  if [ -n "$MEDIA" ]; then
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]' > "$O/REAR-UNDO-1.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]' > "$O/REAR-UNDO-2.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]' > "$O/UNDO-1.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]' > "$O/UNDO-2.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -p > "$O/FINAL-MEDIA.txt" 2>&1 || :
  fi
  dmesg | tail -n +$((START+1)) > "$O/DMESG.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then echo PASS_REAR8_FRONT27_QC10C_DMA_GUARD > "$D/ATTEMPT-RESULT.txt"
  else echo "FAIL_RC=$rc ONE_SHOT_NO_RETRY" > "$D/ATTEMPT-RESULT.txt"; fi
  printf 'boot_id=%s\ncandidate_sha256=4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d\n' \
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
grep -Fq 'sp11_camera_e004ja_two_rgb_dma_guard=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004ja-two-rgb-dma-guard' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$env"
grep -qx 'next_entry=' <<<"$env"
[[ ! -e "$D/ATTEMPT-CONSUMED" && ! -e /dev/media0 ]]
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' \
  "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
START=$(dmesg | wc -l)
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d "/sys/module/$m" ]]; done
[[ "$(sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646 ]]
( cd "$D/stack"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 > "$O/PACKAGE-VERIFY.txt" )
[[ "$(sha256sum "$CAND" | awk '{print $1}')" == 4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d ]]
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
for _ in $(seq 1 120); do
  if ls /dev/media* >/dev/null 2>&1 &&
     PYTHONDONTWRITEBYTECODE=1 "$H/discover-unified.py" > "$O/UNIFIED.tmp" 2>/dev/null; then
     mv "$O/UNIFIED.tmp" "$O/UNIFIED.json"; break
  fi
  sleep 0.05
done
[[ -s "$O/UNIFIED.json" ]]
MEDIA=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['media'])")
media-ctl -d "$MEDIA" -p > "$O/INITIAL-MEDIA.txt"
# CAMSS can expose both mutable rear links enabled at idle. E004iz
# proved this exact state on SP11. Reject partial/mixed/front states;
# explicitly neutralize ONLY the two known rear mutable links, and verify.
initial=$("$H/route-state.py" "$O/INITIAL-MEDIA.txt")
case "$initial" in
  "IF_ROUTE_STATE=neutral "*) ;;
  "IF_ROUTE_STATE=rear-only "*)
    media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
    media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
    ;;
  *) echo "E004JA_REJECT_UNEXPECTED_IDLE_GRAPH=$initial" >&2; exit 1 ;;
esac
media-ctl -d "$MEDIA" -p > "$O/INITIAL-NORMALIZED-MEDIA.txt"
"$H/route-state.py" "$O/INITIAL-NORMALIZED-MEDIA.txt" --expect neutral
wait_suspend
REARSENSOR=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_sensor_entity'])")
REARSENSORDEV=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_sensor_device'])")
REARVIDEO=$(python3 -c "import json;print(json.load(open('$O/UNIFIED.json'))['rear_video_device'])")
[[ "$REARSENSOR" == ov13858\ * && -c "$REARSENSORDEV" && -c "$REARVIDEO" ]]
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'
media-ctl -d "$MEDIA" -p > "$O/REAR-ON-MEDIA.txt"
"$H/route-state.py" "$O/REAR-ON-MEDIA.txt" --expect rear-only
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
# Eight bounded real rear optical frames, kept ONLY under root-private staging.
timeout 25s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=8 --stream-to="$O/rear-normal8.raw" --verbose > "$O/REAR-NORMAL8.txt" 2>&1
python3 - "$O/rear-normal8.raw" "$O/REAR-NORMAL8.txt" > "$O/REAR-VALIDATION.txt" <<'PY'
from pathlib import Path
import sys,re
raw=Path(sys.argv[1]);log=Path(sys.argv[2]).read_text()
assert raw.stat().st_size == 8*14321824,raw.stat().st_size
seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',log)]
assert seq==list(range(8)),seq
ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',log)]
assert len(ts)==8,ts
fps=7/(ts[-1]-ts[0])
assert 28.5 <= fps <=31.5,fps
print("E004JA_REAR_NORMAL_BAYER8=PASS sequences=0..7 fps=%.4f frames_private=YES"%fps)
PY
sleep 0.5
wait_suspend
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/BETWEEN-NEUTRAL.txt"
"$H/route-state.py" "$O/BETWEEN-NEUTRAL.txt" --expect neutral
wait_suspend
"$P/bin/front-imx681-discover.py" --json > "$O/FRONT-DISCOVERY.json"
python3 - "$O/UNIFIED.json" "$O/FRONT-DISCOVERY.json" <<'PY'
import json,sys
a,b=(json.load(open(f)) for f in sys.argv[1:])
assert a['media']==b['media']
assert (b['csiphy_entity'],b['csid_entity'],b['pix_entity'])==('msm_csiphy2','msm_csid1','msm_vfe1_pix')
assert b['proven_capture_fourcc']=='QC10C'
PY
"$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow \
  --build-dir "$P/build" --output-dir "$O/front" > "$O/FRONT-LAUNCHER.txt" 2>&1
media-ctl -d "$MEDIA" -p > "$O/FRONT-MEDIA.txt"
"$H/route-state.py" "$O/FRONT-MEDIA.txt" --expect front-only
sleep 0.5
wait_suspend
python3 - "$O/front" "$O/FRONT-LAUNCHER.txt" "$IR" "$REAR" "$FRONT" > "$O/VALIDATION.txt" <<'PY'
from pathlib import Path
import re,sys,hashlib
root=Path(sys.argv[1]);text=Path(sys.argv[2]).read_text()
seq=[int(x) for x in re.findall(r'DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)',text)]
assert seq==list(range(27)),seq
assert 'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1..27' in text and 'POLICY=shadow' in text
for i in range(27):
 f=root/f'QC10C-{i}.bin'
 assert f.stat().st_size==7778304,(i,f.stat().st_size)
 print(i,hashlib.sha256(f.read_bytes()).hexdigest())
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[3:])):
 assert (p/'power/runtime_status').read_text().strip()=='suspended',label
print('E004JA_VALIDATION=PASS_27_QC10C_SHADOW_3_SENSORS_SUSPENDED')
PY
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/NEUTRAL-MEDIA.txt"
"$H/route-state.py" "$O/NEUTRAL-MEDIA.txt" --expect neutral
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:|ILLUMINATION_ON|E004J_CSIPHY0_DPHY_WINDOWS_PARITY|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$O/KERNEL-HEALTH.txt"
done_ok=1
echo E004JA_SAME_BOOT_REAR8_FRONT27_QC10C_DMA_GUARD=PASS
