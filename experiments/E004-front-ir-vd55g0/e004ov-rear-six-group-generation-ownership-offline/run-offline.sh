#!/usr/bin/env bash
# E004ov standalone C11 source-only; no CAMSS build, install or camera access.
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$ROOT/experiments/E004-front-ir-vd55g0/e004ov-rear-six-group-generation-ownership-offline"
cd "$ROOT"
./tools/camera-overlap-guard.sh --require-golden --require-no-camera-process
test "$(git branch --show-current)" = experiment/e004-front-ir-vd55g0
work="$(mktemp -d /tmp/e004ov-only.XXXXXXXX)"
trap 'rm -rf -- "$work"' EXIT
cc -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
 "$D/test-rear-stop-ownership.c" -o "$work/test-native"
"$work/test-native"
cc -std=c11 -Wall -Wextra -Werror -pedantic -O1 -g \
 -fsanitize=address,undefined -fno-omit-frame-pointer \
 "$D/test-rear-stop-ownership.c" -o "$work/test-sanitized"
ASAN_OPTIONS=detect_leaks=1 "$work/test-sanitized"
echo PASS_E004OV_NO_SOURCE_HOOK_MODULE_INSTALL_BOOT_CAMERA_OR_GOLDEN_MUTATION
