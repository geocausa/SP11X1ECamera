#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E004ns fresh isolated CAMSS ARM64 module build. NEVER install/load/reboot.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline
P=$R/experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HEADERS=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004ns-rear-csid-ipp-build/camss
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process \
 --expect-head ca5107448610a006b9f618836da42379982234dc \
 --expect-origin ca5107448610a006b9f618836da42379982234dc
test "$(sha256sum "$SRC/camss.c" | cut -d' ' -f1)" = 788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91
test "$(sha256sum "$SRC/camss-csid-680.c" | cut -d' ' -f1)" = 9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90
test "$(sha256sum "$D/camss-csid-e004ns-rear-ipp.inc" | cut -d' ' -f1)" = f145ec03045bf4e8a177011d52a44d6f56f9aff9fbd90fd4a6fc89200cf3f40f
test "$(sha256sum "$P/camss-e004nr-rear-profile.inc" | cut -d' ' -f1)" = 4c3e38cd2da75d758fcf595ae58cbc49122c96ca6f9b12e70d2692da9c06198d
test ! -e "$B" || { echo E004NS_STAGE_ALREADY_USED >&2; exit 3; }
test -f "$HEADERS/include/generated/autoconf.h"
mkdir -p "$B"
cp -a "$SRC/." "$B/"
cp "$P/camss-e004nr-rear-profile.inc" "$B/"
cp "$D/camss-csid-e004ns-rear-ipp.inc" "$B/"
python3 - "$B/camss.c" "$B/camss-csid-680.c" <<'PY'
from pathlib import Path
import sys
camss,csid=(Path(x) for x in sys.argv[1:])
old=camss.read_text()
needle="static int camss_x1e_pix_runner_validate(struct camss *camss,"
assert old.count(needle)==1 and 'camss-e004nr-rear-profile.inc' not in old
camss.write_text(old.replace(needle,'#include "camss-e004nr-rear-profile.inc"\n\n'+needle,1))
old=csid.read_text()
needle="static void __csid_configure_top(struct csid_device *csid)"
assert old.count(needle)==1 and 'camss-csid-e004ns-rear-ipp.inc' not in old
csid.write_text(old.replace(needle,'#include "camss-csid-e004ns-rear-ipp.inc"\n\n'+needle,1))
print("E004NS_STAGE_SOURCE_ONLY_CSID_REAR_MODE_AND_E004NR_REAR_GRAPH_INCLUDED_FRONT_UNCHANGED")
PY
make -C "$HEADERS" M="$B" W=1 -j4 > "$B/E004NS-CAMSS-BUILD.log" 2>&1 || {
 tail -n 115 "$B/E004NS-CAMSS-BUILD.log" >&2; echo E004NS_COMPILE_FAILED >&2; exit 4;
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
echo "E004NS_ISOLATED_ARM64_CAMSS_COMPILE_PASS bytes=$(stat -c %s "$B/qcom-camss.ko") sha256=$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)"
echo E004NS_NO_NEW_RUNTIME_CALLER_NOT_LOADED_INSTALLED_OR_ARMED
