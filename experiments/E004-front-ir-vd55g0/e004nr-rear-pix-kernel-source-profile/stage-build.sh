#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E004nr source-pinned ISOLATED kernel module build; never load/install/reboot.
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
HERE="$REPO/experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile"
SOURCE=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src
HEADERS=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nr-rear-pix-profile-build-v2/camss
CAMSS="$SOURCE/drivers/media/platform/qcom/camss"
EXPECTED_BASE=788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91
EXPECTED_HEADER=4c3e38cd2da75d758fcf595ae58cbc49122c96ca6f9b12e70d2692da9c06198d

cd "$REPO"
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
test "$(sha256sum "$CAMSS/camss.c" | awk '{print $1}')" = "$EXPECTED_BASE"
test "$(sha256sum "$HERE/camss-e004nr-rear-profile.inc" | awk '{print $1}')" = "$EXPECTED_HEADER"
test -f "$HEADERS/Makefile" && test -f "$HEADERS/include/generated/autoconf.h"
test -f "$HERE/RESULT.json" || test -f "$REPO/experiments/E004-front-ir-vd55g0/e004nq-rear-physical-mmio-5phase/RESULT.json"
if test -e "$B"; then echo "E004NR_BUILD_ALREADY_EXISTS_DO_NOT_REUSE" >&2; exit 3; fi
mkdir -p "$B"
cp -a "$CAMSS/." "$B/"
cp "$HERE/camss-e004nr-rear-profile.inc" "$B/"
python3 - "$B/camss.c" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
needle='static int camss_x1e_pix_runner_validate(struct camss *camss,'
assert s.count(needle)==1
assert '#include "camss-e004nr-rear-profile.inc"' not in s
s=s.replace(needle,
            '#include "camss-e004nr-rear-profile.inc"\n\n'+needle,1)
p.write_text(s)
print('E004NR_FRONT_RUNNER_BODY_PRESERVED_SOURCE_ONLY_REAR_INCLUDE_INJECTED')
PY
echo "E004NR_COMPILE_BEGIN E004NR_ONLY_STAGED_CAMSS_SOURCE NOT_INSTALLED"
make -C "$HEADERS" M="$B" W=1 -j4 > "$B/E004NR-CAMSS-BUILD.log" 2>&1 || {
  tail -n 100 "$B/E004NR-CAMSS-BUILD.log" >&2
  echo E004NR_COMPILE_FAIL >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
echo "E004NR_ISOLATED_CAMSS_MODULE_COMPILE_PASS size=$(stat -c %s "$B/qcom-camss.ko") sha256=$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)"
echo 'E004NR_NOT_INSTALLED_NOT_LOADED_NOT_BOOTED_REAR_RUNTIME_DENIED'
