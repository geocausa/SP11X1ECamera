#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# HISTORICAL ONE-USE E005n fix1 build recipe. The build identity is consumed.
# Do not rerun or overwrite it; create a new experiment/build identity instead.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005n-vfe680-wm16-compgrp7-observer-isolated"
N="$R/experiments/E004-front-ir-vd55g0"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
FIRST=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005n-vfe680-wm16-compgrp7-observer-build
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005n-vfe680-wm16-compgrp7-observer-build-fix1

cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden   --require-no-camera-process   --expect-head 92d9b8d59f98726d83802ced1e539cfee9f6c0e7   --expect-origin 92d9b8d59f98726d83802ced1e539cfee9f6c0e7
test -d "$FIRST"
test ! -e "$FIRST/qcom-camss.ko"
test ! -e "$B" || { echo E005N_FIX1_BUILD_ALREADY_CONSUMED >&2; exit 3; }

python3 - "$SRC" <<'PY'
from pathlib import Path
import hashlib,sys
s=Path(sys.argv[1])
expected={
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
 "camss-vfe.h":"440b03e1d2701c311cddc6beeae70bccfea5f472f75790a1879167d66395e857",
 "camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
}
for n,w in expected.items():
    g=hashlib.sha256((s/n).read_bytes()).hexdigest()
    assert g==w,(n,g,w)
print("E005N_ACCEPTED_CAMSS_SOURCE_HASHES_PASS")
PY

mkdir -- "$B"
cp -a "$SRC/." "$B/"
cp "$N/e004nr-rear-pix-kernel-source-profile/camss-e004nr-rear-profile.inc" "$B/"
cp "$N/e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$N/e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$N/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$N/e004nv-rear-six-group-bf-static/camss-vfe-e004nv-rear-six-group.inc" "$B/"
cp "$D/camss-vfe-e005n-wm16-observer.inc" "$B/"
"$D/instrument.py" "$B"

make -C "$HDR" M="$B" W=1 -j4 > "$B/E005N-CAMSS-BUILD.log" 2>&1
test -s "$B/qcom-camss.ko"
! grep -E '(warning:|error:)' "$B/E005N-CAMSS-BUILD.log"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" =  '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
printf 'E005N_FIX1_BUILD_PASS bytes=%s sha256=%s\n'   "$(stat -c %s "$B/qcom-camss.ko")"   "$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
echo E005N_FIX1_NO_INSTALL_NO_LOAD
