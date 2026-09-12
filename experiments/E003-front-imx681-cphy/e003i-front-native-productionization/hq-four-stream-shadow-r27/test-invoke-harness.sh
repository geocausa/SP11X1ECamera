#!/usr/bin/env bash
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
# shellcheck source=invoke-four.sh
source "$D/invoke-four.sh"
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
for n in 1 2 3 4; do run_one "$n"; done
for n in 1 2 3 4; do
  [ -s "$O/RUN${n}-CONSUMED.marker" ]
  grep -qx 'LAUNCHER_RC=0' <(tail -n1 "$O/RUN${n}.txt")
done
set +e
run_one 1 >/dev/null 2>&1
rc=$?
set -e
[ "$rc" -eq 91 ]
# Abort ordering test: later streams are not consumed when stream2 fails.
rm -rf "$O"; mkdir -p "$O"
launch_stream() {
  local stream_dir=$1 log=$2
  mkdir -p "$stream_dir"
  case "$stream_dir" in
    */stream2) printf '%s\n' 'synthetic failure' > "$log"; return 37 ;;
    *) printf '%s\n' 'PROD_POST_G3_POLICY=shadow' 'PROD_NATIVE_SCHEDULE_PASS X POLICY=shadow CONTROL_IOCTLS=3 LATER_NATIVE_WRITES=0 X' 'STREAMOFF_OK' > "$log"; return 0 ;;
  esac
}
run_one 1
set +e
run_one 2 >/dev/null 2>&1
rc=$?
set -e
[ "$rc" -eq 37 ]
[ -e "$O/RUN1-CONSUMED.marker" ] && [ -e "$O/RUN2-CONSUMED.marker" ]
[ ! -e "$O/RUN3-CONSUMED.marker" ] && [ ! -e "$O/RUN4-CONSUMED.marker" ]
echo 'HQ_INVOKE_HARNESS_SELFTEST=PASS STREAMS=4 REPEAT_MARKER_RC=91 ABORT_LATER=PASS CAMERA_ACCESS=NO'
