#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E004nt isolated compile, never install/load/enable Golden or rear camera.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract
NR=$R/experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile
NS=$R/experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HEADERS=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nt-rear-4k-buffer-build/camss
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process \
 --expect-head 4684273a318856266b35d222de4e8cbf0240fb3c \
 --expect-origin 4684273a318856266b35d222de4e8cbf0240fb3c
test "$(sha256sum "$SRC/camss.c" | cut -d' ' -f1)" = 788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91
test "$(sha256sum "$SRC/camss-csid-680.c" | cut -d' ' -f1)" = 9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90
test "$(sha256sum "$SRC/camss-vfe-680.c" | cut -d' ' -f1)" = 99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208
test "$(sha256sum "$D/camss-vfe-e004nt-rear-4k-buffer.inc" | cut -d' ' -f1)" = 05a27b12384c1267787b193eb0d8d13abe57a4d189778dbe9a52490f180046e6
test "$(sha256sum "$NR/camss-e004nr-rear-profile.inc" | cut -d' ' -f1)" = 4c3e38cd2da75d758fcf595ae58cbc49122c96ca6f9b12e70d2692da9c06198d
test "$(sha256sum "$NS/camss-csid-e004ns-rear-ipp.inc" | cut -d' ' -f1)" = f145ec03045bf4e8a177011d52a44d6f56f9aff9fbd90fd4a6fc89200cf3f40f
test -f "$HEADERS/include/generated/autoconf.h"
test ! -e "$B" || { echo E004NT_STAGE_ALREADY_CONSUMED >&2; exit 3; }
mkdir -p "$B"
cp -a "$SRC/." "$B/"
cp "$NR/camss-e004nr-rear-profile.inc" "$B/"
cp "$NS/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$D/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
python3 - "$B/camss.c" "$B/camss-csid-680.c" "$B/camss-vfe-680.c" <<'PY'
from pathlib import Path
import sys
c,s,v=(Path(x) for x in sys.argv[1:])
edits=(
(c,'static int camss_x1e_pix_runner_validate(struct camss *camss,',
'#include "camss-e004nr-rear-profile.inc"\n\n'),
(s,'static void __csid_configure_top(struct csid_device *csid)',
'#include "camss-csid-e004ns-rear-ipp.inc"\n\n'),
(v,'static int vfe680_x1e_group_from_event(u32 event_id)',
'#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n\n'),
)
for p,needle,inc in edits:
 t=p.read_text()
 assert t.count(needle)==1 and inc not in t and not p.is_symlink()
 p.write_text(t.replace(needle,inc+needle,1))
print("E004NT_ISOLATED_FRONT_UNCHANGED_REAR_GRAPH_CSID_IPP_AND_4K_COHERENT_DMA_SURFACE_SOURCE_STAGED")
PY
make -C "$HEADERS" M="$B" W=1 -j4 > "$B/E004NT-CAMSS-BUILD.log" 2>&1 || {
 tail -n 110 "$B/E004NT-CAMSS-BUILD.log" >&2; echo E004NT_ISOLATED_COMPILE_FAILED >&2; exit 4;
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
echo "E004NT_ISOLATED_ARM64_CAMSS_COMPILE_PASS bytes=$(stat -c %s "$B/qcom-camss.ko") sha256=$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)"
echo E004NT_UNINSTALLED_UNLOADED_REAR_RUNTIME_UNCONDITIONALLY_DENIED
