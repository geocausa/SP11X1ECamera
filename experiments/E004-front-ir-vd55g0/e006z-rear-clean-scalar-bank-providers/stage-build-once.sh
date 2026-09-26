#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E="$R/experiments/E004-front-ir-vd55g0"
W="$E/e006w-rear-aecbe17-packer"
X="$E/e006x-rear-tintlessbg17-packer"
Y="$E/e006y-rear-awbbg17-packer"
Z="$E/e006z-rear-clean-scalar-bank-providers"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e006z-rear-clean-scalar-bank-build
cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R"  "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process  --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"
for s in  "$E/e006g-rear-rtcdm-materializer-skeleton/verify-e006g.py"  "$E/e006j-rear-steady-producer-binding-compile/verify-e006j.py"  "$E/e006l-rear-startup-register-ownership/verify.py"  "$E/e006m-rear-startup-producer-binding-compile/verify-e006m.py"  "$E/e006o-rear-steady-singleton-provider-compile/verify-e006o.py"  "$E/e006p-rear-crop-roundclamp-packers/verify.py"  "$E/e006q-rear-mnds23-packer/verify.py"  "$E/e006r-rear-cst12-tuning-packer/verify.py"  "$E/e006s-rear-bc101-tuning-provider/verify.py"  "$E/e006t-rear-disabled-small-iq-providers/verify.py"  "$E/e006u-rear-bhist16-provider/verify.py"  "$E/e006v-rear-rsstats14-packer/verify.py"  "$W/verify.py" "$X/verify.py" "$X/validate-private.py" "$Y/verify.py" "$Y/validate-private.py" "$Z/verify.py" "$Z/validate-private.py"
do "$s"; done
test ! -e "$B" || { echo E006Z_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"; cp -a "$SRC/." "$B/"
for f in  "$E/e006g-rear-rtcdm-materializer-skeleton/camss-e006g-rear-materializer.inc"  "$E/e006j-rear-steady-producer-binding-compile/camss-e006j-rear-register-bindings.inc"  "$E/e006m-rear-startup-producer-binding-compile/camss-e006m-rear-startup-bindings.inc"  "$E/e006o-rear-steady-singleton-provider-compile/camss-e006o-rear-steady-singletons.inc"  "$E/e006p-rear-crop-roundclamp-packers/camss-e006p-crop-roundclamp.inc"  "$E/e006q-rear-mnds23-packer/camss-e006q-mnds23.inc"  "$E/e006r-rear-cst12-tuning-packer/camss-e006r-cst12.inc"  "$E/e006s-rear-bc101-tuning-provider/camss-e006s-bc101.inc"  "$E/e006t-rear-disabled-small-iq-providers/camss-e006t-small-iq.inc"  "$E/e006u-rear-bhist16-provider/camss-e006u-bhist16.inc"  "$E/e006v-rear-rsstats14-packer/camss-e006v-rsstats14.inc"  "$W/camss-e006w-aecbe17.inc" "$X/camss-e006x-tintlessbg17.inc" "$Y/camss-e006y-awbbg17.inc" "$Z/camss-e006z-clean-scalar-bank.inc"
do cp "$f" "$B/"; done
python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1]); p=b/"camss.c"; s=p.read_text()
needle="static int camss_x1e_pix_runner_validate(struct camss *camss,"
assert s.count(needle)==1
names=[
"camss-e006g-rear-materializer.inc","camss-e006j-rear-register-bindings.inc",
"camss-e006m-rear-startup-bindings.inc","camss-e006o-rear-steady-singletons.inc",
"camss-e006p-crop-roundclamp.inc","camss-e006q-mnds23.inc","camss-e006r-cst12.inc",
"camss-e006s-bc101.inc","camss-e006t-small-iq.inc","camss-e006u-bhist16.inc",
"camss-e006v-rsstats14.inc","camss-e006w-aecbe17.inc","camss-e006x-tintlessbg17.inc","camss-e006y-awbbg17.inc","camss-e006z-clean-scalar-bank.inc"]
inject="".join(f'#include "{n}"\n' for n in names)+"\n"
p.write_text(s.replace(needle,inject+needle,1))
print("E006Z_ISOLATED_SOURCE_INJECTION_PASS")
PY
make -C "$HDR" M="$B" W=1 -j4 > "$B/E006Z-CAMSS-BUILD.log" 2>&1 || { tail -n 180 "$B/E006Z-CAMSS-BUILD.log" >&2; exit 4; }
test -s "$B/qcom-camss.ko"
! grep -Ei '(warning:|error:)' "$B/E006Z-CAMSS-BUILD.log"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
sha=$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1); bytes=$(stat -c %s "$B/qcom-camss.ko")
echo "E006Z_BUILD_PASS bytes=$bytes sha256=$sha"
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | grep -E 'e006(z_rear_clean|y_awbbg|x_tintless_bg|w_aecbe)' || true
echo E006Z_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_RTCDM_SUBMIT
