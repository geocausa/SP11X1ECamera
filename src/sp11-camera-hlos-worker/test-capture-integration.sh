#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$ROOT/src/sp11-camera-protected-worker"
BRIDGE="$ROOT/src/sp11-camera-hlos-worker"
CAPTURE="$ROOT/experiments/E004-front-ir-vd55g0/e004fe-native-ir-frame-params/runtime/frames.bin"
TMP="$(mktemp -d /tmp/sp11-ir-capture-integration.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

[ "$(sha256sum "$CAPTURE" | cut -d' ' -f1)" = 33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3 ] || {
    echo 'E004fe archive hash changed: refusing to run' >&2; exit 1;
}
clang -std=c11 -O2 -Wall -Wextra -Werror "$BRIDGE/sp11-ir-rgb888-to-nv12.c" -o "$TMP/bridge"
CORE=(
    "$SRC/sp11-parity-worker.c"
    "$SRC/sp11-swabf-reference.c"
    "$SRC/sp11-swasf-reference.c"
    "$SRC/sp11-swasf-windows-tuning.c"
    "$SRC/sp11-swasf-helpers.c"
    "$SRC/sp11-swasf-c230.c"
    "$SRC/sp11-swasf-c3e8.c"
    "$SRC/sp11-swasf-cd90.c"
)
clang -std=c11 -O2 -Wall -Wextra -Werror "$BRIDGE/sp11-hlos-ir.c" "${CORE[@]}" -o "$TMP/worker"

python3 - "$CAPTURE" "$TMP" <<'PY'
from pathlib import Path
import hashlib, sys
capture = Path(sys.argv[1]).read_bytes()
out = Path(sys.argv[2])
stride, width, height = 1936, 644, 604
frame_len = stride * height
assert len(capture) == frame_len * 16, "unexpected archived capture length"
hashes = {hashlib.sha256(capture[i:i+frame_len]).hexdigest()
          for i in range(0, len(capture), frame_len)}
assert hashes == {"baf8aef482c894c21c0c3f6dd818bce6181b9cb1dff78ff4a497ccf5cfd99b28"}, "archived frame hashes differ from E004fe"
frame = capture[:frame_len]
out.joinpath("rgb-frame.bin").write_bytes(frame)
expected_y = bytearray()
for row in range(height):
    line = frame[row*stride:(row+1)*stride]
    for x in range(width):
        assert line[3*x] == line[3*x+1] == line[3*x+2], "input is not neutral monochrome"
        expected_y.append(line[3*x])
    assert line[width*3:] == bytes(stride-width*3), "nonzero padding in archived frame"
assert min(expected_y) == 15 and max(expected_y) == 212
out.joinpath("expected-nv12.bin").write_bytes(expected_y + bytes([128])*(width*height//2))
print("E004FE_ARCHIVED_CAPTURE=PASS FRAMES=16 NEUTRAL=YES")
PY

"$TMP/bridge" < "$TMP/rgb-frame.bin" > "$TMP/bridge-nv12.bin"
cmp "$TMP/bridge-nv12.bin" "$TMP/expected-nv12.bin"
"$TMP/worker" < "$TMP/bridge-nv12.bin" > "$TMP/processed-nv12.bin"
"$TMP/bridge" < "$TMP/rgb-frame.bin" | "$TMP/worker" > "$TMP/pipeline-nv12.bin"
cmp "$TMP/processed-nv12.bin" "$TMP/pipeline-nv12.bin"

python3 - "$TMP/processed-nv12.bin" "$TMP/expected-nv12.bin" <<'PY'
from pathlib import Path
import hashlib, sys
actual, inp = (Path(p).read_bytes() for p in sys.argv[1:])
y = 644 * 604
assert len(actual) == len(inp) == y + y//2
assert actual[y:] == bytes([128])*(y//2), "worker output has unexpected chroma"
assert min(actual[:y]) < max(actual[:y]), "processor returned a flat pattern"
print("ARCHIVED_RGB888_TO_HLOS_WORKER=PASS OUTPUT_SHA256=" + hashlib.sha256(actual).hexdigest())
PY

# Reject malformed frames and unexpected colour/padding rather than processing wrong buffers.
python3 - "$TMP" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
data = bytearray(p.joinpath("rgb-frame.bin").read_bytes())
p.joinpath("short.bin").write_bytes(data[:-1])
p.joinpath("long.bin").write_bytes(data + bytes([0]))
data[1] ^= 1
p.joinpath("coloured.bin").write_bytes(data)
data[1] ^= 1
data[644*3] ^= 1
p.joinpath("padding.bin").write_bytes(data)
PY
for kind in short long coloured padding; do
    if "$TMP/bridge" < "$TMP/$kind.bin" > "$TMP/$kind.out" 2> "$TMP/$kind.err"; then
        echo "format bridge accepted $kind input" >&2; exit 1
    fi
    [ ! -s "$TMP/$kind.out" ] || { echo "format bridge emitted partial $kind output" >&2; exit 1; }
done
echo 'IR_FORMAT_BRIDGE_REJECTION=PASS SHORT_LONG_COLOUR_PADDING'
echo 'CAMERA_RUNTIME=NO ILLUMINATION=OFF AUTHENTICATION=NO'
