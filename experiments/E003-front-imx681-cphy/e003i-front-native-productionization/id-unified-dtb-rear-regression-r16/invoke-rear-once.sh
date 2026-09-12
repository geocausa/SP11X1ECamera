#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/id-unified-dtb-rear-regression-r16
O=$D/runtime-output
[ -s "$D/DISCOVERY.json" ] || { echo 'FAIL: no discovery' >&2; exit 1; }
[ ! -e "$O" ] || { echo 'FAIL: runtime output exists' >&2; exit 1; }
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || { echo 'FAIL: attempt consumed' >&2; exit 1; }
eval "$(python3 - <<PY
import json,shlex
j=json.load(open('$D/DISCOVERY.json'))
for k,n in [('MEDIA','media'),('SENSOR','rear_sensor_entity'),('SENSORDEV','rear_sensor_device'),('VIDEO','rear_video_device'),('FRONTVIDEO','front_video_device')]: print(k+'='+shlex.quote(j[n]))
PY
)"
# Read-only route preflight before consuming the one-shot attempt.
PYTHONDONTWRITEBYTECODE=1 "$D/verify-rear-route.py" --mode pre --media "$MEDIA"
# Consume before any mutable link/format/control change.
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || { echo 'FAIL: consumed marker collision' >&2; exit 1; }
printf 'schema=sp11-camera-id-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_REAR_ROUTE_MUTATION\ntime=%s\nboot_id=%s\nhead=%s\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync
mkdir -p "$O"
on_fail() {
  rc=$?
  trap - ERR
  sudo -n dmesg -T | cat > "$D/DMESG.txt" || true
  python3 - "$rc" "$D" <<'PYE' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]); d=Path(sys.argv[2])
obj={'schema':'sp11-camera-id-attempt1-failure-v1','status':'FAIL_ID_UNIFIED_REAR_REGRESSION_AFTER_CONSUME','exit_code':rc,'candidate_consumed':True,'camera_stream_may_have_started':True,'front_stream_executed':False,'same_stream_retry_performed':False,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'head':subprocess.check_output(['git','-C',str(d.parents[3]),'rev-parse','HEAD'],text=True).strip()}
(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
PYE
  "$D/archive.sh" fail-unified-rear-r16 || true
  exit "$rc"
}
trap on_fail ERR
# Enable only the accepted rear mutable links. Front mutable route remains disabled.
media-ctl -d "$MEDIA" -l '"msm_csiphy1":1 -> "msm_csid0":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'
PYTHONDONTWRITEBYTECODE=1 "$D/verify-rear-route.py" --mode enabled --media "$MEDIA" | tee "$O/ROUTE-ENABLED.txt"
media-ctl -d "$MEDIA" -p > "$O/MEDIA-GRAPH-ENABLED.txt"
# Configure accepted rear format chain.
for spec in \
 "$SENSOR:0 [fmt:SGRBG10_1X10/4076x2806]" \
 'msm_csiphy1:0 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_csiphy1:1 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_csid0:0 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_csid0:1 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_vfe0_rdi0:0 [fmt:SGRBG10_1X10/4076x2806]' \
 'msm_vfe0_rdi0:1 [fmt:SGRBG10_1X10/4076x2806]'; do
  media-ctl -d "$MEDIA" -V "\"${spec%%:*}\":${spec#*:}" >> "$O/CONFIG.txt" 2>&1
done
v4l2-ctl -d "$VIDEO" --set-fmt-video=width=4076,height=2806,pixelformat=pgAA >> "$O/CONFIG.txt" 2>&1
printf 'front_video_forbidden=%s\n' "$FRONTVIDEO" >> "$O/CONFIG.txt"
# Accepted deterministic sensor pattern, one frame.
v4l2-ctl -d "$SENSORDEV" --set-ctrl=test_pattern=1
set +e
timeout 15s v4l2-ctl -d "$VIDEO" --stream-mmap=4 --stream-count=1 --stream-to="$O/colorbar.raw" --verbose > "$O/COLORBAR.txt" 2>&1
rc1=$?
set -e
v4l2-ctl -d "$SENSORDEV" --set-ctrl=test_pattern=0 || true
printf 'COLORBAR_RC=%d\n' "$rc1" >> "$O/COLORBAR.txt"
[ "$rc1" -eq 0 ] || false
[ "$(stat -c%s "$O/colorbar.raw")" -eq 14321824 ]
[ "$(sha256sum "$O/colorbar.raw"|awk '{print $1}')" = '6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346' ]
# Accepted normal bounded stream, no controls changed.
set +e
timeout 20s v4l2-ctl -d "$VIDEO" --stream-mmap=4 --stream-count=16 --stream-to=/dev/null --verbose > "$O/NORMAL16.txt" 2>&1
rc2=$?
set -e
printf 'NORMAL16_RC=%d\n' "$rc2" >> "$O/NORMAL16.txt"
sudo -n dmesg -T | cat > "$D/DMESG.txt"
[ "$rc2" -eq 0 ] || false
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
"$D/archive.sh" pass-unified-rear-r16
