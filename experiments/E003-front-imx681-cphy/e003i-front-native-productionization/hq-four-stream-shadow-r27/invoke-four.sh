#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hq-four-stream-shadow-r27
P=$D/package-root/usr/lib/sp11-front-imx681
O=$D/runtime-output

launch_stream() {
  local stream_dir=$1
  local log=$2
  set +e
  /usr/bin/sudo -n env PYTHONDONTWRITEBYTECODE=1 \
    "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow \
    --build-dir "$P/build" --output-dir "$stream_dir" 2>&1 | cat >"$log"
  local rc=${PIPESTATUS[0]}
  set -e
  return "$rc"
}

run_one() {
  local n
  local stream_dir
  local log
  local rc
  n=${1:?stream number required}
  stream_dir="$O/stream$n"
  log="$O/RUN$n.txt"
  ( set -o noclobber; : > "$O/RUN${n}-CONSUMED.marker" ) 2>/dev/null || return 91
  printf 'TIME=%s\nSTREAM=%s\nPOLICY=shadow\n' "$(date -Ins)" "$n" > "$O/RUN${n}-CONSUMED.marker"
  if launch_stream "$stream_dir" "$log"; then rc=0; else rc=$?; fi
  printf 'LAUNCHER_RC=%d\n' "$rc" >> "$log"
  [ "$rc" -eq 0 ] || return "$rc"
  grep -q 'PROD_POST_G3_POLICY=shadow' "$log"
  grep -q 'STREAMOFF_OK' "$log"
  grep -q 'PROD_NATIVE_SCHEDULE_PASS .* POLICY=shadow CONTROL_IOCTLS=3 LATER_NATIVE_WRITES=0 ' "$log"
}

fail_stream() {
  local n=$1
  local rc=$2
  /usr/bin/sudo -n dmesg -T | cat > "$D/DMESG.txt"
  printf 'STATUS=STREAM%s_FAIL RC=%s\nTIME=%s\nABORT_LATER_STREAMS=YES\nPOLICY=shadow\n' "$n" "$rc" "$(date -Ins)" > "$D/POST.txt"
  "$D/archive.sh" "stream${n}-fail"
  return "$rc"
}

main() {
  local n rc
  mkdir -p "$O"
  for n in 1 2 3 4; do
    [ ! -e "$O/RUN${n}-CONSUMED.marker" ] || { echo "stream$n consumed" >&2; return 1; }
  done
  for n in 1 2 3 4; do
    if run_one "$n"; then rc=0; else rc=$?; fi
    [ "$rc" -eq 0 ] || { fail_stream "$n" "$rc"; return "$rc"; }
  done
  /usr/bin/sudo -n dmesg -T | cat > "$D/DMESG.txt"
  printf 'STATUS=STREAMS_COMPLETE\nTIME=%s\nSTREAM1=PASS\nSTREAM2=PASS\nSTREAM3=PASS\nSTREAM4=PASS\nPOLICY=shadow\n' "$(date -Ins)" > "$D/POST.txt"
  /usr/bin/sudo -n chown -R geoca:geoca "$O" || true
  PYTHONDONTWRITEBYTECODE=1 "$D/verify-four-streams.py"
  "$D/archive.sh" pass-four-stream-shadow
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
