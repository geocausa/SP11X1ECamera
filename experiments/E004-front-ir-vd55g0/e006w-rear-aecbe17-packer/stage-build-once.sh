#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E006w compile-only: no install/load/camera/boot/MMIO/RT-CDM runtime.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E=$R/experiments/E004-front-ir-vd55g0
G="$E/e006g-rear-rtcdm-materializer-skeleton"
J="$E/e006j-rear-steady-producer-binding-compile"
L="$E/e006l-rear-startup-register-ownership"
M="$E/e006m-rear-startup-producer-binding-compile"
O="$E/e006o-rear-steady-singleton-provider-compile"
P="$E/e006p-rear-crop-roundclamp-packers"
Q="$E/e006q-rear-mnds23-packer"
RR="$E/e006r-rear-cst12-tuning-packer"
S="$E/e006s-rear-bc101-tuning-provider"
T="$E/e006t-rear-disabled-small-iq-providers"
U="$E/e006u-rear-bhist16-provider"
V="$E/e006v-rear-rsstats14-packer"
W="$E/e006w-rear-aecbe17-packer"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e006w-rear-aecbe17-build

cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R"  "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process  --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

"$G/verify-e006g.py"
"$J/verify-e006j.py"
"$L/verify.py"
"$M/verify-e006m.py"
"$O/verify-e006o.py"
"$P/verify.py"
"$Q/verify.py"
"$RR/verify.py"
"$S/verify.py"
"$T/verify.py"
"$U/verify.py"
"$V/verify.py"
"$W/verify.py"
"$W/validate-private.py"

test ! -e "$B" || { echo E006W_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
for f in  "$G/camss-e006g-rear-materializer.inc"  "$J/camss-e006j-rear-register-bindings.inc"  "$M/camss-e006m-rear-startup-bindings.inc"  "$O/camss-e006o-rear-steady-singletons.inc"  "$P/camss-e006p-crop-roundclamp.inc"  "$Q/camss-e006q-mnds23.inc"  "$RR/camss-e006r-cst12.inc"  "$S/camss-e006s-bc101.inc"  "$T/camss-e006t-small-iq.inc"  "$U/camss-e006u-bhist16.inc"  "$V/camss-e006v-rsstats14.inc"  "$W/camss-e006w-aecbe17.inc"
do cp "$f" "$B/"; done

python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1]); p=b/"camss.c"; s=p.read_text()
needle="static int camss_x1e_pix_runner_validate(struct camss *camss,"
assert s.count(needle)==1
names=[
"camss-e006g-rear-materializer.inc",
"camss-e006j-rear-register-bindings.inc",
"camss-e006m-rear-startup-bindings.inc",
"camss-e006o-rear-steady-singletons.inc",
"camss-e006p-crop-roundclamp.inc",
"camss-e006q-mnds23.inc",
"camss-e006r-cst12.inc",
"camss-e006s-bc101.inc",
"camss-e006t-small-iq.inc",
"camss-e006u-bhist16.inc",
"camss-e006v-rsstats14.inc",
"camss-e006w-aecbe17.inc",
]
inject="".join(f'#include "{n}"\n' for n in names)+"\n"
p.write_text(s.replace(needle,inject+needle,1))
print("E006W_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E006W-CAMSS-BUILD.log" 2>&1 || {
  tail -n 180 "$B/E006W-CAMSS-BUILD.log" >&2
  echo E006W_BUILD_FAILED_CONSUMED >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E006W-CAMSS-BUILD.log"; then
  echo E006W_W1_WARNINGS_CONSUMED >&2
  exit 5
fi
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" =  '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

sha=$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)
bytes=$(stat -c %s "$B/qcom-camss.ko")
printf 'E006W_BUILD_PASS bytes=%s sha256=%s\n' "$bytes" "$sha"
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" |  grep -E 'e006w_aecbe(17_(lookup|validate|min_word)|_stats17_recipe)' || true
echo E006W_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_RTCDM_SUBMIT
