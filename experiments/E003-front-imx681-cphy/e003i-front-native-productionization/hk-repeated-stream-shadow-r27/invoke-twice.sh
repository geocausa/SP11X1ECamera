#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hk-repeated-stream-shadow-r27
P=$D/package-root/usr/lib/sp11-front-imx681
O=$D/runtime-output
mkdir -p "$O"
[ ! -e "$O/RUN1-CONSUMED.marker" ] && [ ! -e "$O/RUN2-CONSUMED.marker" ] || { echo consumed >&2; exit 1; }
run_one(){
 local n=$1 S=$O/stream$n LOG=$O/RUN$n.txt
 ( set -o noclobber; : > "$O/RUN${n}-CONSUMED.marker" ) 2>/dev/null || return 91
 printf 'TIME=%s\nSTREAM=%s\nPOLICY=shadow\n' "$(date -Ins)" "$n" > "$O/RUN${n}-CONSUMED.marker"
 set +e
 sudo -n env PYTHONDONTWRITEBYTECODE=1 "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow --build-dir "$P/build" --output-dir "$S" > "$LOG" 2>&1
 rc=$?
 set -e
 printf 'LAUNCHER_RC=%d\n' "$rc" >> "$LOG"
 [ "$rc" -eq 0 ] || return "$rc"
 grep -q 'PROD_POST_G3_POLICY=shadow' "$LOG"
 grep -q 'STREAMOFF_OK' "$LOG"
 grep -q 'PROD_NATIVE_SCHEDULE_PASS .* POLICY=shadow CONTROL_IOCTLS=3 LATER_NATIVE_WRITES=0 ' "$LOG"
}
run_one 1 || { rc=$?; sudo -n dmesg -T > "$D/DMESG.txt"; echo "STATUS=STREAM1_FAIL RC=$rc" > "$D/POST.txt"; "$D/archive.sh" stream1-fail; exit "$rc"; }
run_one 2 || { rc=$?; sudo -n dmesg -T > "$D/DMESG.txt"; echo "STATUS=STREAM2_FAIL RC=$rc" > "$D/POST.txt"; "$D/archive.sh" stream2-fail; exit "$rc"; }
sudo -n dmesg -T > "$D/DMESG.txt"
printf 'STATUS=STREAMS_COMPLETE\nTIME=%s\nSTREAM1=PASS\nSTREAM2=PASS\nPOLICY=shadow\n' "$(date -Ins)" > "$D/POST.txt"
sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-two-streams.py"
"$D/archive.sh" pass-two-stream-shadow
