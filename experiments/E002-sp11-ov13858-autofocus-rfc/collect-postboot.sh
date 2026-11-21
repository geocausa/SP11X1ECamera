#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Read-only SP11 autofocus boot and media-graph evidence collection.
# Does not load drivers, move lenses, open/stream the sensor for capture,
# touch power rails, request suspend, reboot or modify boot state.
set -uo pipefail
expected='7.3.0-sp11-camera-rfc1+'
actual=$(uname -r)
if [[ "$actual" != "$expected" ]]; then
  echo "Wrong release: expected $expected, running $actual" >&2
  exit 2
fi
out=${1:-}
[[ -n "$out" && ! -e "$out" ]] || {
  echo "Provide a fresh absolute evidence-output directory" >&2
  exit 2
}
mkdir -p "$out" || exit 1
{
  date -u
  uname -a
  cat /proc/cmdline
  cat /sys/power/mem_sleep
  echo 'Firmware board model:'
  tr '\0' '\n' </proc/device-tree/model
  echo 'RPMh regulators (group/ID/compatible):'
  for p in /proc/device-tree/soc@0/rsc@17500000/regulators-*; do
    [[ -d "$p" ]] || continue
    printf '%s ' "${p##*/}"
    tr -d '\0' <"$p/qcom,pmic-id" 2>/dev/null
    printf ' '
    tr '\0' ' ' <"$p/compatible" 2>/dev/null
    echo
  done
  echo 'Exposed nodes:'
  ls -la /dev/video* /dev/media* /dev/v4l-subdev* 2>&1
  echo 'Boot next_entry:'
  command -v grub-editenv >/dev/null && grub-editenv /boot/grub/grubenv list
} >"$out/identity.txt" 2>&1
dmesg --color=never >"$out/dmesg.txt" 2>&1
cat /sys/kernel/debug/regulator/regulator_summary >"$out/regulator_summary.txt" 2>&1
if [[ -r /sys/kernel/debug/cmd-db ]]; then
  grep -Ei 'ldom6|ldob16' /sys/kernel/debug/cmd-db >"$out/cmd-db-camera.txt" 2>&1
fi
{
  v4l2-ctl --list-devices
  for d in /dev/v4l-subdev*; do
    [[ -e "$d" ]] || continue
    echo "===== $d ====="
    timeout 6 v4l2-ctl -d "$d" --all 2>&1 || true
    timeout 6 v4l2-ctl -d "$d" --list-ctrls 2>&1 || true
  done
} >"$out/v4l2-observation.txt" 2>&1
{
  for m in /dev/media*; do
    [[ -e "$m" ]] || continue
    echo "===== $m ====="
    timeout 8 media-ctl -d "$m" -p 2>&1 || true
  done
} >"$out/media-graph.txt" 2>&1
sha256sum "$out"/*.txt >"$out/SHA256SUMS"
printf 'Read-only evidence collected in %s\n' "$out"
