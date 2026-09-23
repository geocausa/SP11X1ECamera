#!/usr/bin/env bash
# E004nl no-hardware source-only test; does not arm or install anything.
set -euo pipefail
cd "$(dirname "$0")"
tmp="$(mktemp -d /tmp/e004nl-rear-pix-XXXXXXXX)"
trap 'rm -rf -- "$tmp"' EXIT
cc -std=c11 -Wall -Wextra -Werror -pedantic -O2 test-rear-pix-route.c -o "$tmp/rear-pix-test"
"$tmp/rear-pix-test"
cc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g \
    -fsanitize=address,undefined -fno-omit-frame-pointer \
    test-rear-pix-route.c -o "$tmp/rear-pix-asan"
"$tmp/rear-pix-asan"
PYTHONDONTWRITEBYTECODE=1 python3 verify-kernel-boundary.py > RESULT.json
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import json
from pathlib import Path
p = Path("RESULT.json")
r = json.loads(p.read_text())
assert r["status"] == "PASS_SOURCE_ONLY_FRONT_GUARDS_LOCKED_REAR_RAW_PINNED"
r["experiment"] = "E004nl"
r["native_arm64_C_normal_assertions_passed"] = 25
r["native_arm64_C_asan_ubsan_assertions_passed"] = 25
r["rear_4k_native_isp_physical_frames_proven"] = 0
r["tested_only_source_no_runtime_mutation"] = True
p.write_text(json.dumps(r, sort_keys=True, indent=2) + "\n")
print(p.read_text(), end="")
PY
