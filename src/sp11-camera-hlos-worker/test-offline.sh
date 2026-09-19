#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CORE="$ROOT/src/sp11-camera-protected-worker"
HERE="$ROOT/src/sp11-camera-hlos-worker"
ORACLE="$ROOT/experiments/E004-front-ir-vd55g0/e004dh-swab-exact-offline-port/oracle/windows-sync-oracle"
TMP="$(mktemp -d /tmp/sp11-hlos-ir-offline.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
INPUT="$ORACLE/input-644x604-nv12.bin"
EXPECTED="$ORACLE/windows-trustlet-sync-swasf-644x604-stable.bin"
[ "$(sha256sum "$INPUT" | cut -d' ' -f1)" = 1dbcc3b8f460565acd80b5efda6a8ef9457768ab2c977f91e2754c4f54abdb3d ] || { echo 'input oracle drift' >&2; exit 1; }
[ "$(sha256sum "$EXPECTED" | cut -d' ' -f1)" = 9ef2dc6179d6151910ff524e4821328ffddfdd151996463c08b904673688ccbf ] || { echo 'Windows oracle drift' >&2; exit 1; }
SOURCES=(
  "$CORE/sp11-parity-worker.c"
  "$CORE/sp11-swabf-reference.c"
  "$CORE/sp11-swasf-reference.c"
  "$CORE/sp11-swasf-windows-tuning.c"
  "$CORE/sp11-swasf-helpers.c"
  "$CORE/sp11-swasf-c230.c"
  "$CORE/sp11-swasf-c3e8.c"
  "$CORE/sp11-swasf-cd90.c"
)
clang -std=c11 -O2 -Wall -Wextra -Werror "$HERE/sp11-hlos-ir.c" "${SOURCES[@]}" -o "$TMP/sp11-hlos-ir"
"$TMP/sp11-hlos-ir" < "$INPUT" > "$TMP/output.bin"
python3 - "$TMP/output.bin" "$EXPECTED" <<'PY'
from pathlib import Path
import sys
actual, oracle = (Path(x).read_bytes() for x in sys.argv[1:])
y = 644 * 604
assert len(actual) == y + y // 2, "incorrect frame length"
assert actual[:y] == oracle[:y], "processed luma differs from Windows oracle"
assert actual[y:] == bytes([128]) * (y // 2), "non-neutral chroma tail"
print("HLOS_FULL_FRAME=PASS LUMA_DIFF=0 NEUTRAL_TAIL_DIFF=0")
PY
: > "$TMP/empty.bin"
head -c 100 "$INPUT" > "$TMP/short.bin"
cat "$INPUT" "$TMP/short.bin" > "$TMP/long.bin"
for bad in empty short long; do
  if "$TMP/sp11-hlos-ir" < "$TMP/$bad.bin" > "$TMP/$bad.out" 2> "$TMP/$bad.err"; then
    echo "unexpected acceptance of $bad frame" >&2
    exit 1
  fi
  [ ! -s "$TMP/$bad.out" ] || { echo "unexpected output for $bad frame" >&2; exit 1; }
done
echo 'HLOS_MALFORMED_INPUTS=PASS EMPTY_SHORT_LONG_REJECTED'
echo 'SP11_HLOS_IR_OFFLINE=PASS CAMERA_RUNTIME=NO AUTHENTICATION=NO'
