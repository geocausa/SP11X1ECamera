#!/usr/bin/env bash
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dp-unified-rgb-ir-receiver-coexistence
CAMSS=$D/build/qcom-camss-ir-gated.ko
IRMOD=$D/build/sp11-vd55g0.ko
HARNESS=$D/build/e004t_csiphy_readback_test.ko
FRONTMOD=$D/build/imx681.ko
REARMOD=$D/build/ov13858-production.ko
"$D/runtime-preflight.sh"
IR=$(sed -n 's/^ir_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); REAR=$(sed -n 's/^rear_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); FRONT=$(sed -n 's/^front_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt")
[ -n "$IR" ] && [ -n "$REAR" ] && [ -n "$FRONT" ]
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || { echo 'FAIL: attempt already consumed' >&2; exit 1; }
printf 'schema=sp11-camera-e004dp-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_CAMERA_MODULE_LOAD\ntime=%s\nboot_id=%s\nhead=%s\nretry=NO\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync
BEFORE=$(sudo -n dmesg | wc -l)
on_fail(){ rc=$?; trap - ERR; sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/RUNTIME-DMESG.txt" || true; python3 - "$rc" "$D" <<'PY' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]);d=Path(sys.argv[2]);o={'schema':'sp11-camera-e004dp-attempt1-failure-v1','status':'FAIL_BOUNDED_NO_RETRY','exit_code':rc,'candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'head':subprocess.check_output(['git','-C','/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera','rev-parse','HEAD'],text=True).strip()};(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
PY
exit "$rc"; }
trap on_fail ERR
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$CAMSS" e004j_ir_dphy_windows_parity=1
sudo -n insmod "$REARMOD"
sudo -n insmod "$FRONTMOD"
sudo -n insmod "$IRMOD"
for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ -L "$p/driver" ] && break; sleep 0.05; done; [ -L "$p/driver" ]; done
for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ "$(cat "$p/power/runtime_status" 2>/dev/null||true)" = suspended ] && break; sleep 0.05; done; [ "$(cat "$p/power/runtime_status")" = suspended ]; done
IRN=$(basename "$IR"); REARN=$(basename "$REAR"); FRONTN=$(basename "$FRONT")
IR_ENTITY="sp11-vd55g0 $IRN"; REAR_ENTITY="ov13858 $REARN"; FRONT_ENTITY="imx681 $FRONTN"
MEDIA=
for _ in $(seq 1 120); do
 for x in /dev/media*; do
  [ -e "$x" ] || continue
  T=/tmp/e004dp-media.txt
  if media-ctl -d "$x" -p > "$T" 2>/dev/null && grep -Fq "$IR_ENTITY (1 pad, 1 link, 0 routes)" "$T" && grep -Fq "$REAR_ENTITY (1 pad, 1 link, 0 routes)" "$T" && grep -Fq "$FRONT_ENTITY (1 pad, 1 link, 0 routes)" "$T"; then MEDIA=$x; cp "$T" "$D/MEDIA.txt"; break; fi
 done
 [ -n "$MEDIA" ] && break
 sleep 0.1
done
[ -n "$MEDIA" ]
# Immutable sensor links for all three cameras must coexist.
grep -Fq -- "-> \"msm_csiphy0\":0 [ENABLED,IMMUTABLE]" "$D/MEDIA.txt"
grep -Fq -- "-> \"msm_csiphy1\":0 [ENABLED,IMMUTABLE]" "$D/MEDIA.txt"
grep -Fq -- "-> \"msm_csiphy2\":0 [ENABLED,IMMUTABLE]" "$D/MEDIA.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$D/MEDIA.txt" --expect neutral
# CSIPHY0 downstream must also remain unlinked; the receiver harness independently rechecks it.
python3 - "$D/MEDIA.txt" <<'PY'
import re,sys
s=open(sys.argv[1],errors='replace').read();m=re.search(r'^- entity \d+: msm_csiphy0 \(.*?\)(.*?)(?=^- entity |\Z)',s,re.M|re.S);assert m,'missing csiphy0';b=m.group(1)
for ln in b.splitlines():
 if '-> "msm_csid' in ln: assert 'ENABLED' not in ln,ln
print('E004DP_IR_ROUTE=RECEIVER_ONLY_DOWNSTREAM_NONE')
PY
# Capture IR controls only; no stream command is present anywhere in this script.
IRSUB=
for n in /sys/class/video4linux/v4l-subdev*/name; do [ -r "$n" ] || continue; if grep -Fxq "$IR_ENTITY" "$n"; then IRSUB=/dev/$(basename "$(dirname "$n")"); break; fi; done
[ -n "$IRSUB" ]; v4l2-ctl -d "$IRSUB" --list-ctrls-menus > "$D/CONTROLS-IR.txt"
[ "$(sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity)" = Y ]
# Receiver-only action: no sensor stream callback, CSID stream or VFE stream.
sudo -n insmod "$HARNESS"
sleep 0.2
sudo -n rmmod e004t_csiphy_readback_test
for p in "$IR" "$REAR" "$FRONT"; do [ "$(cat "$p/power/runtime_status")" = suspended ]; done
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/RUNTIME-DMESG.txt"
{
 echo ir_client=$IRN; echo rear_client=$REARN; echo front_client=$FRONTN; echo media=$MEDIA
 echo ir_runtime_status=$(cat "$IR/power/runtime_status"); echo rear_runtime_status=$(cat "$REAR/power/runtime_status"); echo front_runtime_status=$(cat "$FRONT/power/runtime_status")
 echo camss_e004j_param=$(sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity)
 grep -E 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY|E004T_RECEIVER_PRECHECK|E004T_CSIPHY0_READBACK|E004T_CSIPHY0_MISMATCH|E004T_SENSOR_PM_CHANGED|E004T_RECEIVER_END' "$D/RUNTIME-DMESG.txt" || true
} > "$D/RECEIVER-READBACK.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
echo 'E004DP_RUN=PASS THREE_SENSORS_BOUND=YES RGB_ROUTE=NEUTRAL CSIPHY0=96/96 STREAMS=NO ILLUMINATION=NO SECUREISP=NO'
