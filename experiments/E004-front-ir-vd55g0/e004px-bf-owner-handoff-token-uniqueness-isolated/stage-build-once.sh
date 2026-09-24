#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E004pv one-use copied CAMSS ARM64 build; does NOT install/load/arm camera.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e004px-bf-owner-handoff-token-uniqueness-isolated"
N="$R/experiments/E004-front-ir-vd55g0"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004px-bf-owner-handoff-token-build
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden \
 --require-no-camera-process \
 --expect-head f26171114db27b48e4ca6348bbb8c6e9af0d8b57 \
 --expect-origin f26171114db27b48e4ca6348bbb8c6e9af0d8b57
python3 - "$SRC" <<'PY'
from pathlib import Path
import hashlib,sys
p=Path(sys.argv[1])
required={
"camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
"camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
"camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
"camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb"}
for file,expected in required.items():
 assert hashlib.sha256((p/file).read_bytes()).hexdigest()==expected,(file,"protected source changed")
print("E004PX_ACCEPTED_CAMSS_SOURCE_SHA_PASS")
PY
test -f "$HDR/include/generated/autoconf.h"
test ! -e "$B" || { echo E004PX_ATTEMPT_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
# Creation of this unique build path consumes the identity; on interruption,
# inspect it; NEVER rerun this script against a consumed ID.
cp -a "$SRC/." "$B/"
cp "$N/e004nr-rear-pix-kernel-source-profile/camss-e004nr-rear-profile.inc" "$B/"
cp "$N/e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$N/e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$N/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$N/e004nv-rear-six-group-bf-static/camss-vfe-e004nv-rear-six-group.inc" "$B/"
cp "$D/camss-vfe-e004pv-bf-owner-ring.inc" "$B/"
python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])
def inject(name,needle,prefix):
 path=b/name
 data=path.read_text()
 assert data.count(needle)==1 and prefix not in data,(name,"unexpected include boundary")
 path.write_text(data.replace(needle,prefix+needle,1))
inject("camss.c",
       "static int camss_x1e_pix_runner_validate(struct camss *camss,",
       '#include "camss-e004nr-rear-profile.inc"\n\n')
inject("camss-csid-680.c",
       "static void __csid_configure_top(struct csid_device *csid)",
       '#include "camss-csid-e004ns-rear-ipp.inc"\n\n')
inject("camss-vfe-680.c",
       "static int vfe680_x1e_group_from_event(u32 event_id)",
       '#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
       '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
       '#include "camss-vfe-e004nv-rear-six-group.inc"\n'
       '#include "camss-vfe-e004pv-bf-owner-ring.inc"\n\n')
print("E004PX_COPY_ONLY_NATIVE_QUEUE_H_INCLUDED_REAR_UNWIRED")
PY
make -C "$HDR" M="$B" W=1 -j4 > "$B/E004PX-CAMSS-BUILD.log" 2>&1 || {
 tail -n 90 "$B/E004PX-CAMSS-BUILD.log" >&2
 echo E004PX_ARM64_COMPILE_FAILED >&2
 exit 4
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
if grep -E '(warning:|error:)' "$B/E004PX-CAMSS-BUILD.log"; then
 echo E004PX_W1_HAS_WARNINGS >&2
 exit 5
fi
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | grep -E ' e004pv_(bf_(owner_begin|enqueue|confirm_and_pop|finish_stop)|rear_isp_runtime_authorize)$'
printf 'E004PX_ARM64_ISOLATED_W1_ZERO_WARNINGS bytes=%s sha256=%s\n' \
 "$(stat -c %s "$B/qcom-camss.ko")" \
 "$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)"
echo E004PX_NO_ISP_ARM_NO_MODULE_INSTALL_NO_LOAD_NO_IRQ_WRITE
