#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E006o compile-only: no install/load/camera/boot/MMIO/RT-CDM runtime.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
G="$R/experiments/E004-front-ir-vd55g0/e006g-rear-rtcdm-materializer-skeleton"
J="$R/experiments/E004-front-ir-vd55g0/e006j-rear-steady-producer-binding-compile"
L="$R/experiments/E004-front-ir-vd55g0/e006l-rear-startup-register-ownership"
M="$R/experiments/E004-front-ir-vd55g0/e006m-rear-startup-producer-binding-compile"
O="$R/experiments/E004-front-ir-vd55g0/e006o-rear-steady-singleton-provider-compile"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e006o-rear-singleton-build

cd "$R"
HEAD_NOW="$(git rev-parse HEAD)"
ORIGIN_NOW="$(git rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process \
  --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

python3 - "$SRC" <<'PY'
from pathlib import Path
import hashlib,sys
src=Path(sys.argv[1])
pins={
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss.h":"da2941a9d2afa6250773c682027fc70512e32daa69a9478cb372ecaa74be37c0",
 "Makefile":"5ffdb6c8e88b946e27f1f03a7588d290f416098dc99b0659658593a60c920bc7",
}
for n,sha in pins.items():
    got=hashlib.sha256((src/n).read_bytes()).hexdigest()
    assert got==sha,(n,got,sha)
print("E006O_ACCEPTED_SOURCE_PINS_PASS")
PY

"$G/verify-e006g.py"
"$J/verify-e006j.py"
"$L/verify.py"
"$M/verify-e006m.py"
"$O/verify-e006o.py"

test ! -e "$B" || { echo E006O_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
for f in \
 "$G/camss-e006g-rear-materializer.inc" \
 "$J/camss-e006j-rear-register-bindings.inc" \
 "$M/camss-e006m-rear-startup-bindings.inc" \
 "$O/camss-e006o-rear-steady-singletons.inc"
do cp "$f" "$B/"; done

python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1]); p=b/"camss.c"; s=p.read_text()
needle="static int camss_x1e_pix_runner_validate(struct camss *camss,"
assert s.count(needle)==1
inject=(
 '#include "camss-e006g-rear-materializer.inc"\n'
 '#include "camss-e006j-rear-register-bindings.inc"\n'
 '#include "camss-e006m-rear-startup-bindings.inc"\n'
 '#include "camss-e006o-rear-steady-singletons.inc"\n\n'
)
p.write_text(s.replace(needle,inject+needle,1))
print("E006O_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E006O-CAMSS-BUILD.log" 2>&1 || {
  tail -n 180 "$B/E006O-CAMSS-BUILD.log" >&2
  echo E006O_BUILD_FAILED_CONSUMED >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E006O-CAMSS-BUILD.log"; then
  echo E006O_W1_WARNINGS_CONSUMED >&2
  exit 5
fi
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

sha=$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)
bytes=$(stat -c %s "$B/qcom-camss.ko")
printf 'E006O_BUILD_PASS bytes=%s sha256=%s\n' "$bytes" "$sha"
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | \
 grep -E 'e006[gjmo]_rear_(materializer_recipe|binding_recipe|startup_binding_recipe|steady_singleton_recipe|steady_singleton_lookup|singletons)' || true
echo E006O_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_RTCDM_SUBMIT
