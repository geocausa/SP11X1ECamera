#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27
P=$D/package-root/usr/lib/sp11-front-imx681
O=$D/runtime-output
S=$O/stream1
LOG=$O/RUN1.txt
[ -d /sys/module/qcom_camss ] && [ -d /sys/module/imx681 ]
[ ! -e "$O" ] || { echo 'FAIL: runtime output exists' >&2; exit 1; }
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || { echo 'FAIL: attempt already consumed' >&2; exit 1; }
mkdir -p "$O"
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || { echo 'FAIL: consumed marker collision' >&2; exit 1; }
printf 'schema=sp11-e003i-hy-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_STREAM_INVOKE\ntime=%s\nboot_id=%s\nhead=%s\npolicy=shadow\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync
set +e
/usr/bin/sudo -n env PYTHONDONTWRITEBYTECODE=1 \
  "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow \
  --build-dir "$P/build" --output-dir "$S" 2>&1 | cat > "$LOG"
rc=${PIPESTATUS[0]}
set -e
printf 'LAUNCHER_RC=%d\n' "$rc" >> "$LOG"
/usr/bin/sudo -n dmesg -T | cat > "$D/DMESG.txt"
/usr/bin/sudo -n chown -R geoca:geoca "$O" || true
if [ "$rc" -eq 0 ]; then
  printf 'STATUS=STREAM_COMPLETE\nTIME=%s\nPOLICY=shadow\nLAUNCHER_RC=0\n' "$(date -Ins)" > "$D/POST.txt"
  PYTHONDONTWRITEBYTECODE=1 "$D/verify-live.py"
  "$D/archive.sh" pass-production-one-stream-r27
else
  printf 'STATUS=STREAM_FAIL\nTIME=%s\nPOLICY=shadow\nLAUNCHER_RC=%d\nNO_RETRY=YES\n' "$(date -Ins)" "$rc" > "$D/POST.txt"
  "$D/archive.sh" fail-production-one-stream-r27
  exit "$rc"
fi
