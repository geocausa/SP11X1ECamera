#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
KERNEL_BUILD="${KERNEL_BUILD:?set KERNEL_BUILD to the SP11 kernel build/header tree}"
OUT="${1:-$ROOT/build}"
mkdir -p "$OUT"
R="$ROOT/userspace/runtime"
cc -O2 -std=c11 -Wall -Wextra -Werror -fno-fast-math -ffp-contract=off -I"$R" \
  "$R/e003i-hc-caprelease-native-aec.c" "$R/gain-feed.c" "$R/continuous-db-schedule.c" "$R/native-cap-release-policy.c" \
  "$R/native-raw-control-join.c" "$R/native-raw-aec-loop.c" "$R/native-stats3a.c" \
  "$R/native-imx681-control.c" "$R/native-effective-analyzers.c" "$R/native-bhist-bank4.c" \
  "$R/native-aec-request-loop.c" "$R/native-internal-cap.c" "$R/native-final-exposure.c" \
  "$R/native-final-target.c" "$R/native-aec-tail.c" "$R/native-target-aggregate.c" \
  "$R/native-convergence.c" "$R/native-t681.c" "$R/native-aec-state.c" "$R/native-log103.c" \
  -pthread -lm -o "$OUT/front-imx681-capture-helper"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/camss" "$T/imx681"
cp -a "$ROOT/kernel/camss"/. "$T/camss/"
cp -a "$ROOT/kernel/imx681"/. "$T/imx681/"
make -C "$KERNEL_BUILD" M="$T/camss" clean >/dev/null
make -C "$KERNEL_BUILD" M="$T/camss" W=1 -j4 >/dev/null
make -C "$KERNEL_BUILD" M="$T/imx681" clean >/dev/null
make -C "$KERNEL_BUILD" M="$T/imx681" W=1 -j4 >/dev/null
cp "$T/camss/qcom-camss.ko" "$OUT/qcom-camss.ko"
cp "$T/imx681/imx681.ko" "$OUT/imx681.ko"
printf 'HF_BUILD=PASS\n'
sha256sum "$OUT/front-imx681-capture-helper" "$OUT/qcom-camss.ko" "$OUT/imx681.ko"
