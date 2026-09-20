#!/usr/bin/env bash
# E004iq: single boot-scoped, QC10C-only DMA safety regression.
# Root-only service reboots into preserved Golden on ANY service exit.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004iq
P=$D/stack/usr/lib/sp11-front-imx681
HW=$D/stack/usr/lib/sp11-camera-stack/hardware
CAND=$D/candidate/qcom-camss.ko
H=$R/experiments/E004-front-ir-vd55g0/e004iq-qc10c-dma-one-shot
O=$D/output
MEDIA=
START=0
done_ok=0
mkdir -p "$O"
at_exit() {
  rc=$?
  trap - EXIT
  if [ "$done_ok" -ne 1 ] && [ "$rc" -eq 0 ]; then rc=1; fi
  if [ -n "$MEDIA" ]; then
    media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]' > "$O/UNDO-1.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]' > "$O/UNDO-2.txt" 2>&1 || :
    media-ctl -d "$MEDIA" -p > "$O/FINAL-MEDIA.txt" 2>&1 || :
  fi
  dmesg | tail -n +$((START+1)) > "$O/DMESG.txt" 2>/dev/null || :
  if [ "$rc" -eq 0 ]; then echo PASS_27_QC10C_FRAMES > "$D/ATTEMPT-RESULT.txt"
  else echo "FAIL_RC=$rc ONE_SHOT_NO_RETRY" > "$D/ATTEMPT-RESULT.txt"; fi
  printf 'boot_id=%s\ncandidate_sha256=950ca403fc224873762001a013ec278bf93b041eb12e1ad7a0bd3687c86b4f56\n' \
    "$(cat /proc/sys/kernel/random/boot_id)" >> "$D/ATTEMPT-RESULT.txt" || :
  sync
  exit "$rc"
}
trap at_exit EXIT
[[ "$EUID" -eq 0 && "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
grep -Fq 'sp11_camera_e004iq_qc10c_dma_guard=1' /proc/cmdline
grep -Fq 'sp11_entry=7.1.5-sp11-camera-e004iq-qc10c-dma-guard' /proc/cmdline
grep -Fq 'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0' /proc/cmdline
env=$(grub-editenv /boot/grub/grubenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$env"
! grep -q '^next_entry=.' <<<"$env"
[[ ! -e "$D/ATTEMPT-CONSUMED" && ! -e /dev/media0 ]]
( set -o noclobber; printf 'boot_id=%s\nsingle_run=YES\n' \
  "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
START=$(dmesg | wc -l)
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d "/sys/module/$m" ]]; done
[[ "$(sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646 ]]
( cd "$D/stack"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 > "$O/PACKAGE-VERIFY.txt" )
[[ "$(sha256sum "$CAND" | awk '{print $1}')" == 950ca403fc224873762001a013ec278bf93b041eb12e1ad7a0bd3687c86b4f56 ]]
[[ "$(sha256sum "$HW/modules/imx681.ko" | awk '{print $1}')" == ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ]]
[[ "$(sha256sum "$HW/modules/ov13858.ko" | awk '{print $1}')" == 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ]]
[[ "$(sha256sum "$HW/modules/sp11-vd55g0.ko" | awk '{print $1}')" == 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(git -C "$R" rev-parse HEAD)" ]]
[[ "$(git -C "$R" rev-parse HEAD)" == "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
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
"$H/route-state.py" "$O/INITIAL-MEDIA.txt" --expect neutral
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
print('E004IQ_VALIDATION=PASS_27_QC10C_SHADOW_3_SENSORS_SUSPENDED')
PY
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/NEUTRAL-MEDIA.txt"
"$H/route-state.py" "$O/NEUTRAL-MEDIA.txt" --expect neutral
dmesg | tail -n +$((START+1)) > "$O/KERNEL-HEALTH.txt"
! grep -Eiq 'BUG:|Oops:|Kernel panic|Call trace:' "$O/KERNEL-HEALTH.txt"
done_ok=1
echo E004IQ_SINGLE_QC10C_REGRESSION=PASS
