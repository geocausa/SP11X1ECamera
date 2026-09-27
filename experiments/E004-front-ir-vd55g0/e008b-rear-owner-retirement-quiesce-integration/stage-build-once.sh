#!/usr/bin/env bash
set -euo pipefail

R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E="$R/experiments/E004-front-ir-vd55g0"
Y5="$E/e005y-vfe1-shared-owner-csid1-wm16-observer"
Z7="$E/e007z-rear-ten-wm-consumed-iova-retirement"
A8="$E/e008a-rear-vfe1-bus-stop-csid-drain-contract"
B8="$E/e008b-rear-owner-retirement-quiesce-integration"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e008b-rear-owner-retirement-quiesce-integration-build

cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R"   "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden   --require-no-camera-process --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

"$Z7/verify.py"
"$A8/verify.py"
"$B8/verify.py"

test ! -e "$B" || { echo E008B_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
cp "$Y5/camss-e005y-vfe1-owner-observer-fix3.inc" "$B/camss-e005y-vfe1-owner-observer.inc"
cp "$Z7/camss-e007z-rear-retirement.inc" "$B/"
cp "$A8/camss-csid-e008a-rear-quiesce.inc" "$B/"
cp "$A8/camss-vfe-e008a-rear-bus-stop.inc" "$B/"
cp "$B8/camss-e008b-rear-integration.inc" "$B/"

python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])

def inject(name, needle, repl):
    p=b/name
    s=p.read_text()
    assert s.count(needle)==1,(name,needle,s.count(needle))
    p.write_text(s.replace(needle,repl,1))

inject(
    "camss-csid-680.c",
    "static void __csid_configure_top(struct csid_device *csid)",
    '#include "camss-csid-e008a-rear-quiesce.inc"\n\n'
    "static void __csid_configure_top(struct csid_device *csid)"
)
inject(
    "camss-vfe-680.c",
    "static const u8 vfe680_x1e_windows_bus_client_order[] = {",
    '#include "camss-vfe-e008a-rear-bus-stop.inc"\n\n'
    "static const u8 vfe680_x1e_windows_bus_client_order[] = {"
)
inject(
    "camss.c",
    "static int camss_x1e_pix_runner_validate(struct camss *camss,",
    '#include "camss-e005y-vfe1-owner-observer.inc"\n'
    '#include "camss-e007z-rear-retirement.inc"\n'
    '#include "camss-e008b-rear-integration.inc"\n\n'
    "static int camss_x1e_pix_runner_validate(struct camss *camss,"
)
print("E008B_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E008B-CAMSS-BUILD.log" 2>&1 || {
  tail -n 220 "$B/E008B-CAMSS-BUILD.log" >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E008B-CAMSS-BUILD.log"; then
  echo E008B_W1_WARNING_OR_ERROR >&2
  exit 5
fi
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" =   '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
sha="$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
bytes="$(stat -c %s "$B/qcom-camss.ko")"
echo "E008B_BUILD_PASS bytes=$bytes sha256=$sha"
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" |   grep -E 'e008b_rear_observe_snapshot|e008b_rear_quiesce_and_prove|e008b_rear_integration_recipe|csid680_e008a_rear_quiesce|vfe680_e008a_rear_bus_stop'
echo E008B_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_DMA_RELEASE_NO_RTCDM_SUBMIT_NO_LEDGER_RELEASE
