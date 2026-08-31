#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-clock-rate-0052-candidate
VIDEO=${1:-/dev/video7}
TRIGGER=/sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
OUT=$NEW/RUNTIME-CSIDCLK-0052-QC10C.bin
RUNLOG=$NEW/RUNTIME-CSIDCLK-0052-RUN.txt
POST=$NEW/RUNTIME-CSIDCLK-0052-POST.txt
DMESG=$NEW/RUNTIME-CSIDCLK-0052-DMESG.txt
HASHES=$NEW/RUNTIME-CSIDCLK-0052-HASHES.txt
STAGES=$NEW/RUNTIME-CSIDCLK-0052-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-CSIDCLK-0052-WATCHER.ready
AUTH=$NEW/AUTHORIZATION.json
HELPER=$NEW/e003h-pix-one-shot
CAMSS=$NEW/qcom-camss.ko
DTB=$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
SENSOR=$NEW/imx681.ko
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
[ -f "$AUTH" ] || fail 'authorization file absent'
python3 - "$AUTH" "$HEAD" "$REPO" <<'PY' || exit 1
import json,subprocess,sys
p,head,repo=sys.argv[1:]
x=json.load(open(p))
assert x.get('accepted') is True and x.get('runtime_authorized') is True
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',x['package_commit'],head])
assert x['execution_contract']['boot_count']==1
assert x['execution_contract']['root_helper_invocation_count']==1
assert x['execution_contract']['same_boot_retry'] is False
PY
grep -q 'sp11_camera_e003h_csidclk_0052=1' /proc/cmdline || fail 'not 0052 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-csidclk-0052/' /proc/cmdline || fail 'wrong BOOT_IMAGE'
[ "$(sha256sum "$CAMSS" | cut -d' ' -f1)" = 42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a ] || fail 'CAMSS hash drift'
[ "$(sha256sum "$DTB" | cut -d' ' -f1)" = 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f ] || fail 'DTB hash drift'
[ "$(sha256sum "$SENSOR" | cut -d' ' -f1)" = 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388 ] || fail 'sensor hash drift'
[ "$(sha256sum "$HELPER" | cut -d' ' -f1)" = d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09 ] || fail 'helper hash drift'
sudo -n test -w "$TRIGGER" || fail 'trigger absent/not writable by root'
[ -r "$DIAG" ] || fail 'diagnostic observer absent'
[ -c "$VIDEO" ] || fail 'video node absent'
sudo -n test -f "$READY" || fail 'watcher READY marker absent'
sudo -n grep -q '^READY$' "$READY" || fail 'watcher not ready'
grep -q 'name=idle' "$DIAG" || fail 'RT-CDM diagnostic not idle before RUN'
[ ! -e "$OUT" ] || fail 'output path already exists'
[ ! -e "$RUNLOG" ] || fail 'RUN log already exists; refusing retry'
: > "$RUNLOG"
{
  echo "START=$(date -Ins)"
  echo "VIDEO=$VIDEO"
  echo "TRIGGER=$TRIGGER"
  echo "HEAD=$HEAD"
  echo 'HELPER_INVOCATION_COUNT=1'
} >> "$RUNLOG"
sync
set +e
sudo -n "$HELPER" "$VIDEO" "$TRIGGER" "$OUT" >> "$RUNLOG" 2>&1
RC=$?
set -e
{
  echo "RUN_RC=$RC"
  echo "END=$(date -Ins)"
} >> "$RUNLOG"
{
  echo "RUN_RC=$RC"
  echo "POST_TIME=$(date -Ins)"
  echo -n 'LIVE_DIAG='; cat "$DIAG" 2>&1 || true
  S=$(basename "$(readlink -f /sys/bus/i2c/drivers/imx681/*-0010 2>/dev/null | head -1)")
  echo "SENSOR=$S"
  [ -n "$S" ] && echo "SENSOR_PM=$(cat "/sys/bus/i2c/devices/$S/power/runtime_status" 2>/dev/null || true)"
  echo "CAMSS_PM=$(cat /sys/bus/platform/devices/acb7000.isp/power/runtime_status 2>/dev/null || true)"
  if [ -f "$OUT" ]; then stat -c 'QC10C_BYTES=%s' "$OUT"; sha256sum "$OUT"; else echo 'QC10C_OUTPUT=absent'; fi
  echo 'WATCHER:'
  sudo -n cat "$STAGES" 2>/dev/null || true
} > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|CSID1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 700 > "$DMESG" || true
sha256sum "$RUNLOG" "$POST" "$DMESG" > "$HASHES"
if sudo -n test -f "$STAGES"; then sudo -n sha256sum "$STAGES" >> "$HASHES"; fi
sync
echo "ARCHIVED_RC=$RC"
sudo -n systemctl reboot
