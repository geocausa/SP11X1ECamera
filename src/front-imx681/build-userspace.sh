#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$ROOT/build}"
R="$ROOT/userspace/runtime"
mkdir -p "$OUT"
cc -O2 -std=c11 -Wall -Wextra -Werror -fno-fast-math -ffp-contract=off -I"$R" \
  "$R/front-imx681-production-capture.c" "$R/gain-feed.c" "$R/continuous-db-schedule.c" \
  "$R/native-cap-release-policy.c" "$R/production-write-policy.c" \
  "$R/native-raw-control-join.c" "$R/native-raw-aec-loop.c" "$R/native-stats3a.c" \
  "$R/native-imx681-control.c" "$R/native-effective-analyzers.c" "$R/native-bhist-bank4.c" \
  "$R/native-aec-request-loop.c" "$R/native-internal-cap.c" "$R/native-final-exposure.c" \
  "$R/native-final-target.c" "$R/native-aec-tail.c" "$R/native-target-aggregate.c" \
  "$R/native-convergence.c" "$R/native-t681.c" "$R/native-aec-state.c" "$R/native-log103.c" \
  -pthread -lm -o "$OUT/front-imx681-capture"
cc -O2 -std=c11 -Wall -Wextra -Werror "$R/bootstrap-controls.c" -o "$OUT/front-imx681-bootstrap-controls"
printf 'FRONT_IMX681_USERSPACE_BUILD=PASS\n'
sha256sum "$OUT/front-imx681-capture" "$OUT/front-imx681-bootstrap-controls"
