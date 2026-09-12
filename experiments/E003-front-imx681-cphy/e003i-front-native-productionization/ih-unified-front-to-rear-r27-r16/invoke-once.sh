#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ih-unified-front-to-rear-r27-r16
P=$D/package-root/usr/lib/sp11-front-imx681
O=$D/runtime-output
[ -s "$D/UNIFIED-DISCOVERY.json" ] || { echo 'FAIL: no unified discovery' >&2; exit 1; }
[ ! -e "$O" ] || { echo 'FAIL: runtime output exists' >&2; exit 1; }
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || { echo 'FAIL: attempt consumed' >&2; exit 1; }

eval "$(python3 - <<PY
import json,shlex
j=json.load(open('$D/UNIFIED-DISCOVERY.json'))
for k,n in [('MEDIA','media'),('REARSENSOR','rear_sensor_entity'),('REARSENSORDEV','rear_sensor_device'),('REARVIDEO','rear_video_device')]:
 print(k+'='+shlex.quote(j[n]))
PY
)"

media-ctl -d "$MEDIA" -p > "$D/ROUTE-PRE.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$D/ROUTE-PRE.txt" --expect neutral

( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || { echo 'FAIL: consumed marker collision' >&2; exit 1; }
printf 'schema=sp11-camera-ih-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_FIRST_ROUTE_MUTATION\ntime=%s\nboot_id=%s\nhead=%s\ndirection=front-to-rear\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync
mkdir -p "$O"

on_fail() {
  rc=$?
  trap - ERR
  sudo -n dmesg -T | cat > "$D/DMESG.txt" || true
  sudo -n chown -R geoca:geoca "$O" 2>/dev/null || true
  python3 - "$rc" "$D" <<'PYE' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]); d=Path(sys.argv[2])
obj={
 'schema':'sp11-camera-ih-attempt1-failure-v1',
 'status':'FAIL_IH_FRONT_TO_REAR_AFTER_CONSUME',
 'exit_code':rc,
 'candidate_consumed':True,
 'camera_stream_may_have_started':True,
 'direction':'front-to-rear',
 'same_stream_retry_performed':False,
 'same_boot_retry_performed':False,
 'golden_return_required':True,
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'head':subprocess.check_output(['git','-C',str(d.parents[3]),'rev-parse','HEAD'],text=True).strip(),
}
(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
PYE
  "$D/archive.sh" fail-front-to-rear-r27-r16 || true
  exit "$rc"
}
trap on_fail ERR

# Front target first. Launcher performs the two front link enables.
# shellcheck disable=SC2024
sudo -n env PYTHONDONTWRITEBYTECODE=1 "$P/bin/front-imx681-launcher.py" \
  --execute --post-g3-write-policy shadow --build-dir "$P/build" \
  --output-dir "$O/front" > "$O/FRONT-R27.txt" 2>&1
printf 'FRONT_LAUNCHER_RC=0\n' >> "$O/FRONT-R27.txt"

media-ctl -d "$MEDIA" -p > "$O/ROUTE-FRONT-ONLY.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/ROUTE-FRONT-ONLY.txt" --expect front-only

sleep 0.5
python3 - <<'PY' > "$O/FRONT-SUSPEND.txt"
from pathlib import Path
front=[p for p in Path('/sys/bus/i2c/devices').glob('*-0010') if (p/'name').exists() and (p/'name').read_text().strip()=='imx681']
assert len(front)==1,front
st=(front[0]/'power/runtime_status').read_text().strip()
assert st=='suspended',st
print('IH_FRONT_RUNTIME_SUSPEND=PASS')
PY

# Mandatory neutral handoff.
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/ROUTE-NEUTRAL-HANDOFF.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/ROUTE-NEUTRAL-HANDOFF.txt" --expect neutral

# Rear target only.
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'
media-ctl -d "$MEDIA" -p > "$O/ROUTE-REAR-ONLY.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/ROUTE-REAR-ONLY.txt" --expect rear-only

for spec in \
 "$REARSENSOR:0 [fmt:SGRBG10_1X10/4076x2806]" \
 'msm_csiphy1:0 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_csiphy1:1 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_csid0:0 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_csid0:1 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_vfe0_rdi0:0 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_vfe0_rdi0:1 [fmt:SGRBG10_1X10/4076x2806]'; do
  entity=$(printf '%s\n' "$spec" | cut -d: -f1)
  rest=$(printf '%s\n' "$spec" | cut -d: -f2-)
  media-ctl -d "$MEDIA" -V "\"$entity\":$rest" >> "$O/REAR-CONFIG.txt" 2>&1
done
v4l2-ctl -d "$REARVIDEO" --set-fmt-video=width=4076,height=2806,pixelformat=pgAA >> "$O/REAR-CONFIG.txt" 2>&1

v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=1
set +e
timeout 15s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=1 --stream-to="$O/rear-colorbar.raw" --verbose > "$O/REAR-COLORBAR.txt" 2>&1
rc1=$?
set -e
v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0 || true
printf 'COLORBAR_RC=%d\n' "$rc1" >> "$O/REAR-COLORBAR.txt"
[ "$rc1" -eq 0 ]
[ "$(stat -c%s "$O/rear-colorbar.raw")" -eq 14321824 ]
[ "$(sha256sum "$O/rear-colorbar.raw"|awk '{print $1}')" = '6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346' ]

set +e
timeout 20s v4l2-ctl -d "$REARVIDEO" --stream-mmap=4 --stream-count=16 --stream-to=/dev/null --verbose > "$O/REAR-NORMAL16.txt" 2>&1
rc2=$?
set -e
printf 'NORMAL16_RC=%d\n' "$rc2" >> "$O/REAR-NORMAL16.txt"
[ "$rc2" -eq 0 ]

sleep 0.5
python3 - <<'PY' > "$O/REAR-SUSPEND.txt"
from pathlib import Path
rear=[p for p in Path('/sys/bus/i2c/devices').glob('*-0010') if (p/'name').exists() and (p/'name').read_text().strip()=='ov13858']
assert len(rear)==1,rear
st=(rear[0]/'power/runtime_status').read_text().strip()
assert st=='suspended',st
print('IH_REAR_RUNTIME_SUSPEND=PASS')
PY

sudo -n dmesg -T | cat > "$D/DMESG.txt"
sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
"$D/archive.sh" pass-front-to-rear-r27-r16
