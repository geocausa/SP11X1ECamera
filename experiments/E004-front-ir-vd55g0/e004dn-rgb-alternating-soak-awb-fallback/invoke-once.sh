#!/usr/bin/env bash
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dn-rgb-alternating-soak-awb-fallback
P=$D/package-root/usr/lib/sp11-front-imx681
O=$D/runtime-output
[ -s "$D/UNIFIED-DISCOVERY.json" ] || { echo 'FAIL: no unified discovery' >&2; exit 1; }
[ ! -e "$O" ] || { echo 'FAIL: runtime output exists' >&2; exit 1; }
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || { echo 'FAIL: attempt consumed' >&2; exit 1; }
eval "$(python3 - <<PY
import json,shlex
j=json.load(open('$D/UNIFIED-DISCOVERY.json'))
for k,n in [('MEDIA','media'),('REARSENSOR','rear_sensor_entity'),('REARSENSORDEV','rear_sensor_device'),('REARVIDEO','rear_video_device')]: print(k+'='+shlex.quote(j[n]))
PY
)"
media-ctl -d "$MEDIA" -p > /tmp/e004dn-route-pre.txt
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" /tmp/e004dn-route-pre.txt --expect neutral
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || exit 1
printf 'schema=sp11-camera-e004dn-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_FIRST_ROUTE_MUTATION\ntime=%s\nboot_id=%s\nhead=%s\nlegs=rear,front,rear,front,rear,front\nretry=NO\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync; mkdir -p "$O"
on_fail(){ rc=$?; trap - ERR; sudo -n dmesg -T | cat > "$D/DMESG.txt" || true; sudo -n chown -R geoca:geoca "$O" 2>/dev/null||true; python3 - "$rc" "$D" <<'PYE' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]);d=Path(sys.argv[2]);obj={'schema':'sp11-camera-e004dn-attempt1-failure-v1','status':'FAIL_E004DN_RGB_ALTERNATING_SOAK_AFTER_CONSUME','exit_code':rc,'candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'head':subprocess.check_output(['git','-C','/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera','rev-parse','HEAD'],text=True).strip()};(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
PYE
exit "$rc"; }
trap on_fail ERR
route_snapshot(){ media-ctl -d "$MEDIA" -p > "$O/$1.txt"; PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/$1.txt" --expect "$2"; }
rear_on(){ media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'; media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'; }
rear_off(){ media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [0]'; media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'; }
front_off(){ media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'; media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'; }
rear_config(){ local out=$1; : > "$out"; for spec in "$REARSENSOR:0 [fmt:SGRBG10_1X10/4076x2806]" 'msm_csiphy1:0 [fmt:SGRBG10_1X10/4076x2806]' 'msm_csiphy1:1 [fmt:SGRBG10_1X10/4076x2806]' 'msm_csid0:0 [fmt:SGRBG10_1X10/4076x2806]' 'msm_csid0:1 [fmt:SGRBG10_1X10/4076x2806]' 'msm_vfe0_rdi0:0 [fmt:SGRBG10_1X10/4076x2806]' 'msm_vfe0_rdi0:1 [fmt:SGRBG10_1X10/4076x2806]'; do entity=${spec%%:*}; rest=${spec#*:}; media-ctl -d "$MEDIA" -V "\"$entity\":$rest" >> "$out" 2>&1; done; v4l2-ctl -d "$REARVIDEO" --set-fmt-video=width=4076,height=2806,pixelformat=pgAA >> "$out" 2>&1; }
rear_suspend(){ python3 - <<'PY'
from pathlib import Path
p=[x for x in Path('/sys/bus/i2c/devices').glob('*-0010') if (x/'name').exists() and (x/'name').read_text().strip()=='ov13858'];assert len(p)==1,p;st=(p[0]/'power/runtime_status').read_text().strip();assert st=='suspended',st;print('REAR_RUNTIME_SUSPEND=PASS')
PY
}
front_suspend(){ python3 - <<'PY'
from pathlib import Path
p=[x for x in Path('/sys/bus/i2c/devices').glob('*-0010') if (x/'name').exists() and (x/'name').read_text().strip()=='imx681'];assert len(p)==1,p;st=(p[0]/'power/runtime_status').read_text().strip();assert st=='suspended',st;print('FRONT_RUNTIME_SUSPEND=PASS')
PY
}
rear_leg(){ local n=$1; rear_on; route_snapshot "ROUTE-R${n}-ON" rear-only; rear_config "$O/REAR-R${n}-CONFIG.txt"; if [ "$n" = 1 ]; then v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=1; timeout 15s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=1 --stream-to="$O/rear-colorbar.raw" --verbose > "$O/REAR-COLORBAR.txt" 2>&1; echo COLORBAR_RC=0 >> "$O/REAR-COLORBAR.txt"; v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0; [ "$(stat -c%s "$O/rear-colorbar.raw")" -eq 14321824 ]; [ "$(sha256sum "$O/rear-colorbar.raw"|awk '{print $1}')" = 6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346 ]; fi; timeout 15s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=8 --stream-to=/dev/null --verbose > "$O/REAR-R${n}-NORMAL8.txt" 2>&1; echo NORMAL8_RC=0 >> "$O/REAR-R${n}-NORMAL8.txt"; sleep 0.5; rear_suspend > "$O/REAR-R${n}-SUSPEND.txt"; rear_off; route_snapshot "NEUTRAL-AFTER-R${n}" neutral; }
front_leg(){ local n=$1; sudo -n env PYTHONDONTWRITEBYTECODE=1 "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow --build-dir "$P/build" --output-dir "$O/front${n}" > "$O/FRONT-F${n}.txt" 2>&1; echo FRONT_LAUNCHER_RC=0 >> "$O/FRONT-F${n}.txt"; route_snapshot "ROUTE-F${n}-ON" front-only; sleep 0.5; front_suspend > "$O/FRONT-F${n}-SUSPEND.txt"; front_off; route_snapshot "NEUTRAL-AFTER-F${n}" neutral; }
rear_leg 1
front_leg 1
rear_leg 2
front_leg 2
rear_leg 3
front_leg 3
route_snapshot FINAL-NEUTRAL neutral
python3 - <<'PY' > "$O/FINAL-SUSPEND.txt"
from pathlib import Path
for name in ('ov13858','imx681'):
 p=[x for x in Path('/sys/bus/i2c/devices').glob('*-0010') if (x/'name').exists() and (x/'name').read_text().strip()==name];assert len(p)==1,(name,p);st=(p[0]/'power/runtime_status').read_text().strip();assert st=='suspended',(name,st);print(name.upper()+'_FINAL_SUSPEND=PASS')
PY
sudo -n dmesg -T | cat > "$D/DMESG.txt"; sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
echo 'E004DN_INVOKE=PASS LEGS=6 TRANSITIONS=5 FINAL=NEUTRAL RETRY=NO'
