#!/usr/bin/env bash
# Offline bounded capture-format-to-worker integration; no device or emitter I/O.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$ROOT/src/sp11-camera-hlos-worker"
CORE="$ROOT/src/sp11-camera-protected-worker"
ARCHIVE="$ROOT/experiments/E004-front-ir-vd55g0/e004fe-native-ir-frame-params/runtime/frames.bin"
TMP="$(mktemp -d /tmp/sp11-hlos-bridge16.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
[ "$(sha256sum "$ARCHIVE" | cut -d' ' -f1)" = 33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3 ] || {
    echo "archived E004fe capture drift" >&2; exit 1;
}
FLAGS=(-std=c11 -O2 -Wall -Wextra -Werror)
if [[ "${HLOS_SANITIZE:-0}" == 1 ]]; then
    FLAGS=(-std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer)
    export ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
    export UBSAN_OPTIONS=halt_on_error=1
fi
clang "${FLAGS[@]}" "$HERE/sp11-ir-rgb888-to-nv12.c" -o "$TMP/bridge"
clang "${FLAGS[@]}" "$HERE/sp11-hlos-ir.c" \
 "$CORE/sp11-parity-worker.c" "$CORE/sp11-swabf-reference.c" \
 "$CORE/sp11-swasf-reference.c" "$CORE/sp11-swasf-windows-tuning.c" \
 "$CORE/sp11-swasf-helpers.c" "$CORE/sp11-swasf-c230.c" \
 "$CORE/sp11-swasf-c3e8.c" "$CORE/sp11-swasf-cd90.c" -o "$TMP/worker"
python3 - "$ARCHIVE" "$TMP/bridge" "$TMP/worker" <<'PY'
from pathlib import Path
from hashlib import sha256
import subprocess, sys
source, bridge, worker = sys.argv[1:]
raw = Path(source).read_bytes()
rgb_len, ylen = 1936*604, 644*604
nv_len = ylen + ylen//2
assert len(raw) == 16*rgb_len
assert {sha256(raw[i:i+rgb_len]).hexdigest()
        for i in range(0, len(raw), rgb_len)} == {
    "baf8aef482c894c21c0c3f6dd818bce6181b9cb1dff78ff4a497ccf5cfd99b28"
}
def run(cmd, payload, success=True):
    r = subprocess.run(cmd, input=payload, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=False)
    if success:
        assert r.returncode == 0, (cmd, r.stderr.decode(errors="replace"))
    else:
        assert r.returncode != 0 and not r.stdout, (
            cmd, r.returncode, r.stdout[:32], r.stderr[:120])
    return r.stdout

reference = run([bridge], raw[:rgb_len])
assert len(reference) == nv_len
multi = run([bridge, "--frames", "16"], raw)
assert multi == reference*16
expected = run([worker, "--frames", "16"], multi)
per_frame = run([worker], reference)
assert expected == per_frame*16
# Actual 16-frame archived libcamera output through both bounded executables.
p = subprocess.Popen([bridge, "--frames", "16"], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
frames, bridge_err = p.communicate(raw, timeout=25)
assert p.returncode == 0 and frames == multi, bridge_err
p = subprocess.Popen([worker, "--frames", "16"], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
processed, worker_err = p.communicate(frames, timeout=35)
assert p.returncode == 0 and processed == expected, worker_err
print("HLOS_RGB888_TO_WORKER_16=PASS FRAMES=16 OUTPUT_SHA256="+sha256(processed).hexdigest())

bad = bytearray(raw)
bad[-rgb_len + 1] ^= 1     # final frame has non-neutral RGB component
padding = bytearray(raw)
padding[-rgb_len + 644*3] ^= 1  # final frame row padding not zero
failures = [
    ([bridge, "--frames", "16"], raw[:-1]),
    ([bridge, "--frames", "16"], raw + b"\x00"),
    ([bridge, "--frames", "16"], bytes(bad)),
    ([bridge, "--frames", "16"], bytes(padding)),
    ([bridge, "--frames", "15"], raw),
    ([bridge], raw),
    ([bridge, "--frames", "0"], reference),
    ([bridge, "--frames", "17"], raw),
    ([bridge, "--frames", "abc"], reference),
    ([bridge, "--frames", "-1"], reference),
]
for cmd, payload in failures:
    run(cmd, payload, success=False)
print("HLOS_RGB888_BRIDGE_NEGATIVE=PASS CASES=10 PARTIAL_OUTPUT=NONE")
print("CAMERA_RUNTIME=NO ILLUMINATION=OFF FACE_AUTHENTICATION=NO")
PY
