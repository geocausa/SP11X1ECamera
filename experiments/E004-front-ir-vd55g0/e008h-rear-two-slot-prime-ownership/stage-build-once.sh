#!/usr/bin/env bash
set -euo pipefail

R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E="$R/experiments/E004-front-ir-vd55g0"
NT="$E/e004nt-rear-vfe1-4k-buffer-contract"
NU="$E/e004nu-rear-vfe1-ten-wm-ownership"
D="$E/e008d-rear-ten-wm-linux-dma-address-provider"
Z="$E/e007z-rear-ten-wm-consumed-iova-retirement"
H="$E/e008h-rear-two-slot-prime-ownership"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e008h-rear-two-slot-prime-ownership-build-fix1

cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
test "$HEAD_NOW" = "131506568acd703c62de352ef12e498fbb93eba4"

GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R" \
  "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden \
  --require-no-camera-process --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

"$H/verify.py"

test ! -e "$B" || { echo E008H_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
cp "$NT/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$NU/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$D/camss-vfe-e008d-rear-dma.inc" "$B/"
cp "$Z/camss-e007z-rear-retirement.inc" "$B/"
cp "$H/camss-vfe-e008h-rear-prime.inc" "$B/"

python3 - "$B/camss-vfe-680.c" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
needle='static int vfe680_x1e_group_from_event(u32 event_id)'
include=(
 '#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
 '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
 '#include "camss-vfe-e008d-rear-dma.inc"\n'
 '#include "camss-e007z-rear-retirement.inc"\n'
 '#include "camss-vfe-e008h-rear-prime.inc"\n\n'
)
s=p.read_text()
assert s.count(needle)==1
p.write_text(s.replace(needle,include+needle,1))
print("E008H_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E008H-CAMSS-BUILD.log" 2>&1 || {
  tail -n 240 "$B/E008H-CAMSS-BUILD.log" >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E008H-CAMSS-BUILD.log"; then
  echo E008H_W1_WARNING_OR_ERROR >&2
  exit 5
fi

vermagic="$(modinfo -F vermagic "$B/qcom-camss.ko")"
test "$vermagic" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
sha="$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
bytes="$(stat -c %s "$B/qcom-camss.ko")"

aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | grep -E \
  'e008h_rear_alloc_prime_pair|e008h_rear_bind_pair|e008h_rear_enable_slot0|e008h_rear_epoch0_retarget_slot1|e008h_rear_observe_consumed|e008h_rear_both_complete|e008h_rear_prime_recipe'

python3 - "$H/RESULT.json" "$H/BUILD-RESULT.json" "$B/qcom-camss.ko" "$sha" "$bytes" "$vermagic" <<'PY'
import json,sys
from pathlib import Path
rp,bp,mp,sha,bs,vm=sys.argv[1:]
d=json.load(open(rp))
d["classification"]="BUILD_ONLY_PASS"
d["build"]={
    "module_bytes":int(bs),
    "module_sha256":sha,
    "vermagic":vm,
    "w1_warnings_or_errors":0
}
Path(rp).write_text(json.dumps(d,indent=2)+"\n")
br={
    "schema":"E008H-build-result-v1",
    "status":"PASS",
    "module_path":mp,
    "module_bytes":int(bs),
    "module_sha256":sha,
    "vermagic":vm,
    "w1_warnings_or_errors":0,
    "module_installed":False,
    "module_loaded":False,
    "camera_runtime":False,
    "wm_enable_runtime":False,
    "rtcdm_submit_runtime":False,
    "golden_preserved":True
}
Path(bp).write_text(json.dumps(br,indent=2)+"\n")
PY

"$H/verify.py"
echo "E008H_BUILD_PASS bytes=$bytes sha256=$sha"
echo E008H_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_RUNTIME_CALLER
