#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
PREF=$NEW/ATTEMPT2-CAPTURE-PREFLIGHT.txt
READY=$NEW/RUNTIME-V4L2-0074-A2-WATCHER.ready
MARK=$NEW/ATTEMPT2-HELPER-CONSUMED.marker
RUN=$NEW/RUNTIME-V4L2-0074-A2-RUN.txt
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -qx 'STATUS=PASS' "$PREF" || fail capture_preflight
sudo -n test -f "$READY" || fail observer_not_ready
VIDEO=$(sed -n 's/^VIDEO=//p' "$PREF" | tail -1)
[ -n "$VIDEO" ] || fail video
D=$(cat "$DIAG")
case "$D" in *'seq=0 stage=0 name=idle fifo_seq=0'*'error=0'*'faulted=0'*) ;; *) fail rtcdm_not_idle;; esac
sudo -n test -r "$VIDEO" -a -w "$VIDEO" || fail video_privilege_regressed
( set -o noclobber; : >"$MARK" ) 2>/dev/null || fail helper_authorization_already_consumed
printf 'CONSUMED_TIME=%s\nVIDEO=%s\nPRIVILEGED_HELPER=true\n' "$(date -Ins)" "$VIDEO" >"$MARK"
set +e
sudo -n "$NEW/e003h-v4l2-six-frame" "$VIDEO" \
 "$NEW/RUNTIME-V4L2-0074-A2-QC10C-0.bin" \
 "$NEW/RUNTIME-V4L2-0074-A2-QC10C-1.bin" \
 "$NEW/RUNTIME-V4L2-0074-A2-QC10C-2.bin" \
 "$NEW/RUNTIME-V4L2-0074-A2-QC10C-3.bin" \
 "$NEW/RUNTIME-V4L2-0074-A2-QC10C-4.bin" \
 "$NEW/RUNTIME-V4L2-0074-A2-QC10C-5.bin" >"$RUN" 2>&1
RC=$?
printf 'HELPER_RC=%d\n' "$RC" >>"$RUN"
exit "$RC"
