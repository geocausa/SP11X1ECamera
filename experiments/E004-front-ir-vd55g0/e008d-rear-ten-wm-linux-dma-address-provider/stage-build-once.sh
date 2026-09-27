#!/usr/bin/env bash
set -euo pipefail

R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E="$R/experiments/E004-front-ir-vd55g0"
NR="$E/e004nr-rear-pix-kernel-source-profile"
NS="$E/e004ns-rear-csid1-ipp-offline"
NT="$E/e004nt-rear-vfe1-4k-buffer-contract"
NU="$E/e004nu-rear-vfe1-ten-wm-ownership"
D="$E/e008d-rear-ten-wm-linux-dma-address-provider"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e008d-rear-ten-wm-linux-dma-address-build-fix1

cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R" \
  "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden \
  --require-no-camera-process --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

"$D/verify.py"

test ! -e "$B" || { echo E008D_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
cp "$NR/camss-e004nr-rear-profile.inc" "$B/"
cp "$NS/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$NT/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$NU/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$D/camss-vfe-e008d-rear-dma.inc" "$B/"

python3 - "$B/camss.c" "$B/camss-csid-680.c" "$B/camss-vfe-680.c" <<'PY'
from pathlib import Path
import sys
camss,csid,vfe=(Path(x) for x in sys.argv[1:])
for p,needle,include in (
 (camss,'static int camss_x1e_pix_runner_validate(struct camss *camss,',
  '#include "camss-e004nr-rear-profile.inc"\n\n'),
 (csid,'static void __csid_configure_top(struct csid_device *csid)',
  '#include "camss-csid-e004ns-rear-ipp.inc"\n\n'),
 (vfe,'static int vfe680_x1e_group_from_event(u32 event_id)',
  '#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
  '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
  '#include "camss-vfe-e008d-rear-dma.inc"\n\n')):
    s=p.read_text()
    assert s.count(needle)==1
    p.write_text(s.replace(needle,include+needle,1))
print("E008D_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E008D-CAMSS-BUILD.log" 2>&1 || {
  tail -n 220 "$B/E008D-CAMSS-BUILD.log" >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E008D-CAMSS-BUILD.log"; then
  echo E008D_W1_WARNING_OR_ERROR >&2
  exit 5
fi
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
  '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
sha="$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
bytes="$(stat -c %s "$B/qcom-camss.ko")"
echo "E008D_BUILD_PASS bytes=$bytes sha256=$sha"
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | \
  grep -E 'e008d_rear_dma_alloc|e008d_rear_prepare_addresses_disabled|e008d_rear_dma_free_unprepared|e008d_rear_dma_recipe'
echo E008D_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_WM_ENABLE_NO_RTCDM_SUBMIT
