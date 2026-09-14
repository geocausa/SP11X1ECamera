#!/usr/bin/env bash
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004ds-unified-rgb-ir-front-regression
O=$D/runtime-output
P=$D/package-root/usr/lib/sp11-front-imx681
CAMSS=$D/build/qcom-camss-ir-gated.ko; IRMOD=$D/build/sp11-vd55g0.ko; FRONTMOD=$D/build/imx681.ko; REARMOD=$D/build/ov13858-production.ko
"$D/runtime-preflight.sh"
IR=$(sed -n 's/^ir_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); REAR=$(sed -n 's/^rear_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); FRONT=$(sed -n 's/^front_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt")
[ ! -e "$O" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ]
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || exit 1
printf 'schema=sp11-camera-e004ds-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_CAMERA_MODULE_LOAD\ntime=%s\nboot_id=%s\nhead=%s\nretry=NO\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync; mkdir -p "$O"; BEFORE=$(sudo -n dmesg | wc -l)
on_fail(){ rc=$?; trap - ERR; sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/DMESG.txt" || true; sudo -n chown -R geoca:geoca "$O" 2>/dev/null||true; python3 - "$rc" "$D" <<'PY' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]);d=Path(sys.argv[2]);o={'schema':'sp11-camera-e004ds-attempt1-failure-v1','status':'FAIL_BOUNDED_NO_RETRY','exit_code':rc,'candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'head':subprocess.check_output(['git','-C','/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera','rev-parse','HEAD'],text=True).strip()};(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
PY
exit "$rc"; }
trap on_fail ERR
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$CAMSS" e004j_ir_dphy_windows_parity=1
sudo -n insmod "$REARMOD"; sudo -n insmod "$FRONTMOD" 'dyndbg=+p'; sudo -n insmod "$IRMOD"
for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ -L "$p/driver" ] && break; sleep 0.05; done; [ -L "$p/driver" ]; done
for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ "$(cat "$p/power/runtime_status" 2>/dev/null||true)" = suspended ] && break; sleep 0.05; done; [ "$(cat "$p/power/runtime_status")" = suspended ]; done
for _ in $(seq 1 100); do if ls /dev/media* >/dev/null 2>&1 && PYTHONDONTWRITEBYTECODE=1 "$D/discover-unified.py" > "$D/UNIFIED-DISCOVERY.json.tmp" 2>/dev/null; then mv "$D/UNIFIED-DISCOVERY.json.tmp" "$D/UNIFIED-DISCOVERY.json"; break; fi; sleep 0.1; done
[ -s "$D/UNIFIED-DISCOVERY.json" ]
eval "$(python3 - <<PY
import json,shlex
j=json.load(open('$D/UNIFIED-DISCOVERY.json'))
for k,n in [('MEDIA','media')]: print(k+'='+shlex.quote(j[n]))
PY
)"
media-ctl -d "$MEDIA" -p > "$D/LOAD-MEDIA.txt"
grep -Fq 'sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)' "$D/LOAD-MEDIA.txt"
grep -Fq -- '-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' "$D/LOAD-MEDIA.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$D/LOAD-MEDIA.txt" --expect neutral
sudo -n "$P/bin/front-imx681-discover.py" --json >/tmp/e004ds-front-discovery.json
python3 - <<PY
import json
u=json.load(open('$D/UNIFIED-DISCOVERY.json'));p=json.load(open('/tmp/e004ds-front-discovery.json'))
assert u['rear_sensor_entity'].startswith('ov13858 ') and u['front_sensor_entity'].startswith('imx681 ')
assert p['media']==u['media'] and p['csiphy_entity']=='msm_csiphy2' and p['csid_entity']=='msm_csid1' and p['pix_entity']=='msm_vfe1_pix'
PY
python3 - "$IR" "$REAR" "$FRONT" > "$O/PRE-STREAM-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_PRE_STREAM_SUSPEND=PASS')
PY
sudo -n env PYTHONDONTWRITEBYTECODE=1 "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow --build-dir "$P/build" --output-dir "$O/front1" > "$O/FRONT-F1.txt" 2>&1
echo FRONT_LAUNCHER_RC=0 >> "$O/FRONT-F1.txt"
media-ctl -d "$MEDIA" -p > "$O/ROUTE-FRONT-ON.txt"; PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/ROUTE-FRONT-ON.txt" --expect front-only
sleep 0.5
python3 - "$IR" "$REAR" "$FRONT" > "$O/POST-STREAM-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_POST_STREAM_SUSPEND=PASS')
PY
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/FINAL-NEUTRAL.txt"; PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/FINAL-NEUTRAL.txt" --expect neutral
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/DMESG.txt"; sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
echo 'E004DS_RUN=PASS FRONT_R27=27 FRAMES POST_G3=shadow REAR_STREAM=NO IR_STREAM=NO FINAL=NEUTRAL RETRY=NO'
