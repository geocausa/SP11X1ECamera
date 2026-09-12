#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ie-unified-front-production-r27
P=$D/package-root/usr/lib/sp11-front-imx681
O=$D/runtime-output
S=$O/stream1
LOG=$O/RUN1.txt
[ -d /sys/module/qcom_camss ] && [ -d /sys/module/imx681 ] && [ -d /sys/module/ov13858 ]
[ ! -e "$O" ] || { echo 'FAIL: runtime output exists' >&2; exit 1; }
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || { echo 'FAIL: attempt already consumed' >&2; exit 1; }
MEDIA=$(python3 -c "import json;print(json.load(open('$D/UNIFIED-DISCOVERY.json'))['media'])")
PYTHONDONTWRITEBYTECODE=1 "$D/verify-rear-disabled.py" --media "$MEDIA"
mkdir -p "$O"
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || { echo 'FAIL: consumed marker collision' >&2; exit 1; }
printf 'schema=sp11-camera-ie-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_STREAM_INVOKE\ntime=%s\nboot_id=%s\nhead=%s\npolicy=shadow\nrear_stream_authorized=NO\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync
on_fail() {
  rc=$?
  trap - ERR
  /usr/bin/sudo -n dmesg -T | cat > "$D/DMESG.txt" || true
  /usr/bin/sudo -n chown -R geoca:geoca "$O" 2>/dev/null || true
  python3 - "$rc" "$D" <<'PYE' || true
import json,sys,subprocess
from pathlib import Path
rc=int(sys.argv[1]); d=Path(sys.argv[2])
obj={'schema':'sp11-camera-ie-attempt1-failure-v1','status':'FAIL_IE_UNIFIED_FRONT_AFTER_CONSUME','exit_code':rc,'candidate_consumed':True,'camera_stream_may_have_started':True,'rear_stream_executed':False,'same_stream_retry_performed':False,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'head':subprocess.check_output(['git','-C',str(d.parents[3]),'rev-parse','HEAD'],text=True).strip()}
(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
PYE
  "$D/archive.sh" fail-unified-front-r27 || true
  exit "$rc"
}
trap on_fail ERR
# shellcheck disable=SC2024
/usr/bin/sudo -n env PYTHONDONTWRITEBYTECODE=1 \
  "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow \
  --build-dir "$P/build" --output-dir "$S" > "$LOG" 2>&1
printf 'LAUNCHER_RC=0\n' >> "$LOG"
/usr/bin/sudo -n dmesg -T | cat > "$D/DMESG.txt"
/usr/bin/sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-rear-disabled.py" --media "$MEDIA" | tee "$O/REAR-ROUTE-POST.txt"
printf 'STATUS=STREAM_COMPLETE\nTIME=%s\nPOLICY=shadow\nLAUNCHER_RC=0\nREAR_STREAM=NO\n' "$(date -Ins)" > "$D/POST.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
trap - ERR
"$D/archive.sh" pass-unified-front-r27
