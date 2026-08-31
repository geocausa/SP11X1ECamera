#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate
VIDEO=${1:-/dev/video7}
TRIGGER=/sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
OUT=$NEW/RUNTIME-MODE2-0054-QC10C.bin
RUNLOG=$NEW/RUNTIME-MODE2-0054-RUN.txt
POST=$NEW/RUNTIME-MODE2-0054-POST.txt
DMESG=$NEW/RUNTIME-MODE2-0054-DMESG.txt
HASHES=$NEW/RUNTIME-MODE2-0054-HASHES.txt
STAGES=$NEW/RUNTIME-MODE2-0054-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-MODE2-0054-WATCHER.ready
AUTH=$NEW/AUTHORIZATION.json
HELPER=$NEW/e003h-pix-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
[ -f "$AUTH" ] || fail 'authorization file absent'
python3 - "$AUTH" "$HEAD" "$REPO" <<'PY'
import json,subprocess,sys
p,head,repo=sys.argv[1:]; x=json.load(open(p)); assert x.get('accepted') is True and x.get('runtime_authorized') is True
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',x['package_commit'],head])
assert x['execution_contract']['boot_count']==1 and x['execution_contract']['root_helper_invocation_count']==1 and x['execution_contract']['same_boot_retry'] is False
PY
grep -q 'sp11_camera_e003h_mode2_0054=1' /proc/cmdline || fail 'not 0054 candidate boot'
sudo -n test -w "$TRIGGER" || fail 'trigger absent/not writable by root'
[ -r "$DIAG" ] || fail 'diagnostic observer absent'
[ -c "$VIDEO" ] || fail 'video node absent'
sudo -n test -f "$READY" || fail 'watcher READY marker absent'
sudo -n grep -q '^READY$' "$READY" || fail 'watcher not ready'
grep -q 'name=idle' "$DIAG" || fail 'RT-CDM diagnostic not idle before RUN'
[ ! -e "$OUT" ] || fail 'output path already exists'
[ ! -e "$RUNLOG" ] || fail 'RUN log already exists; refusing retry'
: > "$RUNLOG"
{ echo "START=$(date -Ins)"; echo "VIDEO=$VIDEO"; echo "TRIGGER=$TRIGGER"; echo "HEAD=$HEAD"; echo 'HELPER_INVOCATION_COUNT=1'; } >> "$RUNLOG"
sync
set +e
sudo -n "$HELPER" "$VIDEO" "$TRIGGER" "$OUT" >> "$RUNLOG" 2>&1
RC=$?
set -e
{ echo "RUN_RC=$RC"; echo "END=$(date -Ins)"; } >> "$RUNLOG"
{
 echo "RUN_RC=$RC"; echo "POST_TIME=$(date -Ins)"; echo -n 'LIVE_DIAG='; cat "$DIAG" 2>&1 || true
 S=$(basename "$(readlink -f /sys/bus/i2c/drivers/imx681/*-0010 2>/dev/null | head -1)"); echo "SENSOR=$S"
 [ -n "$S" ] && echo "SENSOR_PM=$(cat "/sys/bus/i2c/devices/$S/power/runtime_status" 2>/dev/null || true)"
 echo "CAMSS_PM=$(cat /sys/bus/platform/devices/acb7000.isp/power/runtime_status 2>/dev/null || true)"
 if [ -f "$OUT" ]; then stat -c 'QC10C_BYTES=%s' "$OUT"; sha256sum "$OUT"; else echo 'QC10C_OUTPUT=absent'; fi
 echo 'WATCHER:'; sudo -n cat "$STAGES" 2>/dev/null || true
} > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|CSID1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 800 > "$DMESG" || true
sha256sum "$RUNLOG" "$POST" "$DMESG" > "$HASHES"
if sudo -n test -f "$STAGES"; then sudo -n sha256sum "$STAGES" >> "$HASHES"; fi
sync
echo "ARCHIVED_RC=$RC"
sudo -n systemctl reboot
