#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate
VIDEO=${1:-/dev/video7}
TRIGGER=/sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
RUN=$NEW/RUNTIME-CAMNOC-0055-RUN.txt
POST=$NEW/RUNTIME-CAMNOC-0055-POST.txt
DMESG=$NEW/RUNTIME-CAMNOC-0055-DMESG.txt
HASHES=$NEW/RUNTIME-CAMNOC-0055-HASHES.txt
CLOCK=$NEW/RUNTIME-CAMNOC-0055-CLOCK.txt
CREADY=$NEW/RUNTIME-CAMNOC-0055-CLOCK.ready
CSTOP=$NEW/RUNTIME-CAMNOC-0055-CLOCK.stop
STAGES=$NEW/RUNTIME-CAMNOC-0055-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-CAMNOC-0055-WATCHER.ready
OUT=$NEW/RUNTIME-CAMNOC-0055-QC10C.bin
HELPER=$NEW/e003h-pix-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'; git -C "$REPO" diff --quiet || fail 'tracked dirty'; git -C "$REPO" diff --cached --quiet || fail 'staged dirty'
grep -q 'sp11_camera_e003h_camnoc_0055=1' /proc/cmdline || fail 'not 0055 candidate'; sudo -n test -w "$TRIGGER" || fail 'trigger unavailable'; [ -c "$VIDEO" ] || fail 'video missing'; sudo -n grep -qx READY "$READY" || fail 'RT-CDM watcher not ready'; grep -q 'name=idle' "$DIAG" || fail 'RT-CDM not idle'; [ ! -e "$RUN" ] || fail 'RUN exists; retry forbidden'
rm -f "$CSTOP"; sudo -n test ! -e "$CLOCK"; sudo -n test ! -e "$CREADY"
sudo -n python3 "$NEW/camnoc-watch.py" "$CLOCK" --ready "$CREADY" --stop "$CSTOP" --max-seconds 15 & WPID=$!
for _ in $(seq 1 300); do sudo -n test -f "$CREADY" && break; sleep 0.01; done
sudo -n grep -qx READY "$CREADY" || { sudo -n kill "$WPID" 2>/dev/null || true; fail 'CAMNOC watcher not ready'; }
: > "$RUN"; { echo "START=$(date -Ins)"; echo "HEAD=$HEAD"; echo "VIDEO=$VIDEO"; echo 'HELPER_INVOCATION_COUNT=1'; echo 'CAMERA_PROGRAMMING_DELTA=0'; } >> "$RUN"; sync
trap 'sync; sudo -n systemctl reboot' EXIT
set +e; sudo -n "$HELPER" "$VIDEO" "$TRIGGER" "$OUT" >> "$RUN" 2>&1; RC=$?; set -e
{ echo "RUN_RC=$RC"; echo "END=$(date -Ins)"; } >> "$RUN"
touch "$CSTOP"; wait "$WPID" || true
MATCH=no; grep -q 'seen_live_300=1' "$CLOCK" && MATCH=yes
{
 echo "RUN_RC=$RC"; echo "WINDOWS_EXPECTED_CFG=0x00000203"; echo "WINDOWS_EXPECTED_BRANCH=0x00000001"; echo "WINDOWS_EXPECTED_RATE_HZ=300000000"; echo "LINUX_CAMNOC_MATCH_WINDOWS=$MATCH"; echo -n 'LIVE_DIAG='; cat "$DIAG" 2>&1 || true
 echo "CAMSS_PM=$(cat /sys/bus/platform/devices/acb7000.isp/power/runtime_status 2>/dev/null || true)"; echo 'CLOCK_SUMMARY:'; tail -n 8 "$CLOCK"; echo 'WATCHER:'; sudo -n cat "$STAGES" 2>/dev/null || true
 if [ -f "$OUT" ]; then stat -c 'QC10C_BYTES=%s' "$OUT"; sha256sum "$OUT"; else echo 'QC10C_OUTPUT=absent'; fi
} > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|CSID1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 900 > "$DMESG" || true
sha256sum "$RUN" "$POST" "$DMESG" "$CLOCK" > "$HASHES"; sudo -n test -f "$STAGES" && sudo -n sha256sum "$STAGES" >> "$HASHES" || true
sync; echo "ARCHIVED_RC=$RC CAMNOC_MATCH_WINDOWS=$MATCH"
