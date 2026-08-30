#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
EXP=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
VIDEO=${1:-/dev/video7}
TRIGGER=/sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
OUT=$EXP/RUNTIME-PIX-POSTPROV-QC10C.bin
RUNLOG=$EXP/RUNTIME-PIX-POSTPROV-RUN-ACTUAL.txt
POST=$EXP/RUNTIME-PIX-POSTPROV-POST-ACTUAL.txt
DMESG=$EXP/RUNTIME-PIX-POSTPROV-DMESG-ACTUAL.txt
HASHES=$EXP/RUNTIME-PIX-POSTPROV-HASHES-ACTUAL.txt
STAGES=$EXP/RUNTIME-PIX-POSTPROV-RTCDM-STAGES-ACTUAL.txt
READY=$EXP/RUNTIME-PIX-POSTPROV-WATCHER-ACTUAL.ready
HELPER=$EXP/e003h-pix-one-shot
EXPECTED_CAMSS=7d8c8953f8c14e34d36e3d2352b3ea2581d66a5af777f061f6cd0951fcee1680
EXPECTED_DTB=019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f

fail() { echo "FAIL: $*" >&2; exit 1; }
[ "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
grep -q 'sp11_camera_e003h_pix_one_shot=1' /proc/cmdline || fail 'not candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-pix-one-shot/' /proc/cmdline || fail 'wrong BOOT_IMAGE'
[ "$(sha256sum "$ROOT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko" | cut -d' ' -f1)" = "$EXPECTED_CAMSS" ] || fail 'CAMSS hash drift'
[ "$(sha256sum "$EXP/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" | cut -d' ' -f1)" = "$EXPECTED_DTB" ] || fail 'DTB hash drift'
sudo -n test -w "$TRIGGER" || fail 'trigger absent/not writable by root context'
[ -r "$DIAG" ] || fail 'diagnostic observer absent'
[ -c "$VIDEO" ] || fail 'video node absent'
[ -f "$READY" ] || fail 'watcher READY marker absent'
sudo -n grep -q 'READY' "$READY" || fail 'watcher not ready'
grep -q 'name=idle' "$DIAG" || fail 'RT-CDM diagnostic not idle before RUN'
[ ! -e "$OUT" ] || fail 'output path already exists'
[ ! -e "$RUNLOG" ] || fail 'actual RUN log already exists; refusing retry'

# This file is intentionally created by the invoking user before sudo. The shell,
# not sudo, owns redirection; this avoids the root-owned-log failure that aborted
# the prior candidate boot before the helper executable was entered.
: > "$RUNLOG"
{
  echo "START=$(date -Ins)"
  echo "VIDEO=$VIDEO"
  echo "TRIGGER=$TRIGGER"
  echo "HEAD=$(git -C "$REPO" rev-parse HEAD)"
  echo "HELPER_INVOCATION_COUNT=1"
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
  if [ -f "$OUT" ]; then
    stat -c 'QC10C_BYTES=%s' "$OUT"
    sha256sum "$OUT"
  else
    echo 'QC10C_OUTPUT=absent'
  fi
  echo 'WATCHER:'
  sudo -n cat "$STAGES" 2>/dev/null || true
} > "$POST"

sudo -n dmesg -T | grep -Ei 'E003h|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 500 > "$DMESG" || true
sha256sum "$RUNLOG" "$POST" "$DMESG" > "$HASHES"
if sudo -n test -f "$STAGES"; then sudo -n sha256sum "$STAGES" >> "$HASHES"; fi
sync

echo "ARCHIVED_RC=$RC"
sudo -n systemctl reboot
