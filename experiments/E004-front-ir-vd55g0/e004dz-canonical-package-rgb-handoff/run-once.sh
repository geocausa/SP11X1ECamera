#!/usr/bin/env bash
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff
O=$D/runtime-output
HW=/usr/lib/sp11-camera-stack/hardware
P=/usr/lib/sp11-front-imx681
CAMSS=$HW/modules/qcom-camss.ko; IRMOD=$HW/modules/sp11-vd55g0.ko; FRONTMOD=$HW/modules/imx681.ko; REARMOD=$HW/modules/ov13858.ko
"$D/runtime-preflight.sh"
IR=$(sed -n 's/^ir_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); REAR=$(sed -n 's/^rear_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); FRONT=$(sed -n 's/^front_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt")
[ "$(sha256sum "$CAMSS"|awk '{print $1}')" = 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]
[ "$(sha256sum "$IRMOD"|awk '{print $1}')" = 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ]
[ "$(sha256sum "$FRONTMOD"|awk '{print $1}')" = ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ]
[ "$(sha256sum "$REARMOD"|awk '{print $1}')" = 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ]
[ ! -e "$O" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ]
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || exit 1
printf 'schema=sp11-camera-e004dz-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_CAMERA_MODULE_LOAD\ntime=%s\nboot_id=%s\nhead=%s\nretry=NO\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync; mkdir -p "$O"; BEFORE=$(sudo -n dmesg | wc -l)
on_fail(){ rc=$?; trap - ERR; sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/DMESG.txt" || true; sudo -n chown -R geoca:geoca "$O" 2>/dev/null||true; python3 - "$rc" "$D" <<'PY' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]);d=Path(sys.argv[2]);o={'schema':'sp11-camera-e004dz-attempt1-failure-v1','status':'FAIL_BOUNDED_NO_RETRY','exit_code':rc,'candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'head':subprocess.check_output(['git','-C','/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera','rev-parse','HEAD'],text=True).strip()};(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
PY
exit "$rc"; }
trap on_fail ERR
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$CAMSS" e004j_ir_dphy_windows_parity=1
sudo -n insmod "$REARMOD"; sudo -n insmod "$FRONTMOD" 'dyndbg=+p'; sudo -n insmod "$IRMOD"
for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ -L "$p/driver" ] && break; sleep 0.05; done; [ -L "$p/driver" ]; done
wait_suspend(){ local p; for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ "$(cat "$p/power/runtime_status" 2>/dev/null||true)" = suspended ] && break; sleep 0.05; done; [ "$(cat "$p/power/runtime_status")" = suspended ]; done; }
wait_suspend
for _ in $(seq 1 100); do if ls /dev/media* >/dev/null 2>&1 && PYTHONDONTWRITEBYTECODE=1 "$D/discover-unified.py" > "$D/UNIFIED-DISCOVERY.json.tmp" 2>/dev/null; then mv "$D/UNIFIED-DISCOVERY.json.tmp" "$D/UNIFIED-DISCOVERY.json"; break; fi; sleep 0.1; done
[ -s "$D/UNIFIED-DISCOVERY.json" ]
eval "$(python3 - <<PY
import json,shlex
j=json.load(open('$D/UNIFIED-DISCOVERY.json'))
for k,n in [('MEDIA','media'),('REARSENSOR','rear_sensor_entity'),('REARSENSORDEV','rear_sensor_device'),('REARVIDEO','rear_video_device')]: print(k+'='+shlex.quote(j[n]))
PY
)"
media-ctl -d "$MEDIA" -p > "$D/LOAD-MEDIA.txt"
grep -Fq 'sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)' "$D/LOAD-MEDIA.txt"
grep -Fq -- '-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' "$D/LOAD-MEDIA.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$D/LOAD-MEDIA.txt" --expect neutral
[ "$(sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity)" = Y ]
python3 - "$IR" "$REAR" "$FRONT" > "$O/PRE-STREAM-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_PRE_STREAM_SUSPEND=PASS')
PY
route_snapshot(){ media-ctl -d "$MEDIA" -p > "$O/$1.txt"; PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/$1.txt" --expect "$2"; }
rear_on(){ media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'; media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'; }
rear_off(){ media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'; media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'; }
rear_config(){ : > "$O/REAR-CONFIG.txt"; for spec in "$REARSENSOR:0 [fmt:SGRBG10_1X10/4076x2806]" 'msm_csiphy1:0 [fmt:SGRBG10_1X10/4076x2806]' 'msm_csiphy1:1 [fmt:SGRBG10_1X10/4076x2806]' 'msm_csid0:0 [fmt:SGRBG10_1X10/4076x2806]' 'msm_csid0:1 [fmt:SGRBG10_1X10/4076x2806]' 'msm_vfe0_rdi0:0 [fmt:SGRBG10_1X10/4076x2806]' 'msm_vfe0_rdi0:1 [fmt:SGRBG10_1X10/4076x2806]'; do entity=${spec%%:*}; rest=${spec#*:}; media-ctl -d "$MEDIA" -V "\"$entity\":$rest" >> "$O/REAR-CONFIG.txt" 2>&1; done; v4l2-ctl -d "$REARVIDEO" --set-fmt-video=width=4076,height=2806,pixelformat=pgAA >> "$O/REAR-CONFIG.txt" 2>&1; }
rear_on; route_snapshot ROUTE-REAR-ON rear-only; rear_config
v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=1
timeout 15s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=1 --stream-to="$O/rear-colorbar.raw" --verbose > "$O/REAR-COLORBAR.txt" 2>&1; echo COLORBAR_RC=0 >> "$O/REAR-COLORBAR.txt"
v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0
[ "$(stat -c%s "$O/rear-colorbar.raw")" -eq 14321824 ]; [ "$(sha256sum "$O/rear-colorbar.raw"|awk '{print $1}')" = 6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346 ]
timeout 15s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=8 --stream-to=/dev/null --verbose > "$O/REAR-NORMAL8.txt" 2>&1; echo NORMAL8_RC=0 >> "$O/REAR-NORMAL8.txt"
sleep 0.5; wait_suspend
python3 - "$IR" "$REAR" "$FRONT" > "$O/POST-REAR-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_POST_REAR_SUSPEND=PASS')
PY
rear_off; route_snapshot BETWEEN-NEUTRAL neutral; wait_suspend
sudo -n "$P/bin/front-imx681-discover.py" --json > "$O/FRONT-DISCOVERY.json"
python3 - <<PY
import json
u=json.load(open('$D/UNIFIED-DISCOVERY.json'));p=json.load(open('$O/FRONT-DISCOVERY.json'))
assert p['media']==u['media'] and p['csiphy_entity']=='msm_csiphy2' and p['csid_entity']=='msm_csid1' and p['pix_entity']=='msm_vfe1_pix'
PY
sudo -n env PYTHONDONTWRITEBYTECODE=1 "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow --build-dir "$P/build" --output-dir "$O/front1" > "$O/FRONT-F1.txt" 2>&1
echo FRONT_LAUNCHER_RC=0 >> "$O/FRONT-F1.txt"
route_snapshot ROUTE-FRONT-ON front-only
sleep 0.5; wait_suspend
python3 - "$IR" "$REAR" "$FRONT" > "$O/POST-FRONT-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_POST_FRONT_SUSPEND=PASS')
PY
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'
route_snapshot FINAL-NEUTRAL neutral; wait_suspend
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/DMESG.txt"; sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
echo 'E004DZ_RUN=PASS PACKAGE=CANONICAL REAR=COLORBAR+NORMAL8 HANDOFF=NEUTRAL FRONT=R27 FINAL=NEUTRAL RETRY=NO'
