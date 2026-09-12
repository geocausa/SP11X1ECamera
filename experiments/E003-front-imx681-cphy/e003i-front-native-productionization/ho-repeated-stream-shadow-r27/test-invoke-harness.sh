#!/usr/bin/env bash
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
# Source exact live harness without running main, then replace only the camera launcher function.
# The marker/variable/grep logic under test is the same function used live.
# shellcheck source=invoke-twice.sh
source "$D/invoke-twice.sh"
O="$T/runtime-output"
mkdir -p "$O"
launch_stream() {
  local stream_dir=$1
  local log=$2
  mkdir -p "$stream_dir"
  printf '%s\n' \
    'PROD_POST_G3_POLICY=shadow' \
    'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 POLICY=shadow CONTROL_IOCTLS=3 LATER_NATIVE_WRITES=0 LATER_SHADOW=23 POLICY_DISABLED_SHADOW=0 CAP_ACTIVE_SHADOW=21 UNCHANGED_SHADOW=0 ALREADY_APPLIED_SHADOW=0 HORIZON_SHADOW=2 PENDING=G27 APPLY_EFFECT_MAX=G27' \
    'STREAMOFF_OK' > "$log"
  return 0
}
run_one 1
run_one 2
[ -s "$O/RUN1-CONSUMED.marker" ]
[ -s "$O/RUN2-CONSUMED.marker" ]
grep -qx 'LAUNCHER_RC=0' <(tail -n1 "$O/RUN1.txt")
grep -qx 'LAUNCHER_RC=0' <(tail -n1 "$O/RUN2.txt")
set +e
run_one 1 >/dev/null 2>&1
rc=$?
set -e
[ "$rc" -eq 91 ]
[ ! -e "$O/stream1/QC10C-0.bin" ]
echo 'HO_INVOKE_HARNESS_SELFTEST=PASS STREAMS=2 REPEAT_MARKER_RC=91 CAMERA_ACCESS=NO'
