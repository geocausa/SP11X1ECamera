#!/usr/bin/env bash
# Offline-only bounded multi-frame HLOS worker regression; no camera device I/O.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$ROOT/src/sp11-camera-hlos-worker"
CORE="$ROOT/src/sp11-camera-protected-worker"
ARCHIVE="$ROOT/experiments/E004-front-ir-vd55g0/e004fe-native-ir-frame-params/runtime/frames.bin"
TMP="$(mktemp -d /tmp/sp11-hlos-multiframe.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
[ "$(sha256sum "$ARCHIVE" | cut -d' ' -f1)" = 33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3 ] || {
    echo 'archived E004fe capture drift' >&2; exit 1;
}
CFLAGS=(-std=c11 -O2 -Wall -Wextra -Werror)
if [[ "${HLOS_SANITIZE:-0}" == 1 ]]; then
    CFLAGS=(-std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer)
    export ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
    export UBSAN_OPTIONS=halt_on_error=1
fi
clang "${CFLAGS[@]}" "$HERE/sp11-ir-rgb888-to-nv12.c" -o "$TMP/bridge"
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
clang "${CFLAGS[@]}" "$HERE/sp11-hlos-ir.c" "${SOURCES[@]}" -o "$TMP/worker"
python3 - "$ARCHIVE" "$TMP/bridge" "$TMP/worker" <<'PY'
from hashlib import sha256
from pathlib import Path
import subprocess
import sys

archive, bridge, worker = sys.argv[1:]
raw = Path(archive).read_bytes()
y = 644 * 604
nvbytes = y + y // 2
rgbbytes = 1936 * 604
assert len(raw) == 16 * rgbbytes
assert {sha256(raw[i:i+rgbbytes]).hexdigest() for i in range(0, len(raw), rgbbytes)} == {
    "baf8aef482c894c21c0c3f6dd818bce6181b9cb1dff78ff4a497ccf5cfd99b28"
}
def run(args, frame, ok=True):
    result = subprocess.run(args, input=frame, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if ok:
        assert result.returncode == 0, result.stderr.decode(errors="replace")
    else:
        assert result.returncode != 0 and not result.stdout, (
            args, result.returncode, result.stdout[:80], result.stderr[:120]
        )
    return result.stdout

nv = run([bridge], raw[:rgbbytes])
assert len(nv) == nvbytes and nv[y:] == bytes([128]) * (nvbytes-y)
baseline = run([worker], nv)
assert sha256(baseline).hexdigest() == "beb89bd8799fb43549d1ab1ade9135145e31651efcba4b8b72a8856dd4cdb7f9"
# The archive's actual 16 pattern frames are identical. Synthesize *offline*
# temporal variation to test frame independence; not an optical face fixture.
altered = bytes(255-v for v in nv[:y]) + nv[y:]
different = run([worker], altered)
assert baseline != different
parts = [altered if i % 4 == 1 else nv for i in range(16)]
input16 = b"".join(parts)
expected = b"".join(different if i % 4 == 1 else baseline for i in range(16))
output16 = run([worker, "--frames", "16"], input16)
assert output16 == expected
assert run([worker, "--frames", "16"], input16) == output16
print("HLOS_MULTIFRAME=PASS FRAMES=16 FRAME_INDEPENDENCE=PASS")
print("HLOS_MULTIFRAME_SHA256=" + sha256(output16).hexdigest())

failures = [
    ([worker, "--frames", "16"], input16[:-1]),
    ([worker, "--frames", "16"], input16 + b"\x00"),
    ([worker, "--frames", "16"], input16[:-nvbytes]),
    ([worker], input16),
    ([worker, "--frames", "0"], nv),
    ([worker, "--frames", "17"], input16),
    ([worker, "--frames", "abc"], nv),
    ([worker, "--frames", "-1"], nv),
    ([worker, "--frames", "2"], nv),
]
for args, data in failures:
    run(args, data, ok=False)
print("HLOS_MULTIFRAME_NEGATIVE=PASS CASES=9 PARTIAL_OUTPUT=NONE")
print("CAMERA_RUNTIME=NO ILLUMINATION=OFF FACE_AUTHENTICATION=NO")
PY
