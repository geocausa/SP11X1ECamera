#!/usr/bin/env bash
set -euo pipefail

R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E="$R/experiments/E004-front-ir-vd55g0"
SRC="$R/src/front-imx681/kernel/camss"
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e008n-rear-consumed-single-use-wrapper-build

Y5="$E/e005y-vfe1-shared-owner-csid1-wm16-observer"
NS="$E/e004ns-rear-csid1-ipp-offline"
NT="$E/e004nt-rear-vfe1-4k-buffer-contract"
NU="$E/e004nu-rear-vfe1-ten-wm-ownership"
Z7="$E/e007z-rear-ten-wm-consumed-iova-retirement"
A8="$E/e008a-rear-vfe1-bus-stop-csid-drain-contract"
D8="$E/e008d-rear-ten-wm-linux-dma-address-provider"
H8="$E/e008h-rear-two-slot-prime-ownership"
I8="$E/e008i-rear-csid1-irq-consumed-iova-observer"
J8="$E/e008j-rear-prebus-two-slot-order-adapter"
K8="$E/e008k-rear-complete-unreachable-runner"
L8="$E/e008l-rear-linux-command-dma-arena"
N8="$E/e008n-rear-consumed-single-use-wrapper"

A7="$E/e007a-rear-bpcabf411-calculated-provider"
B7="$E/e007b-rear-bfstats25-calculated-provider"
C7="$E/e007c-rear-period-cfg-transport-provider"
D7="$E/e007d-rear-register-provider-integration"
E7="$E/e007e-rear-bfstats25-dmi-provider"
F7="$E/e007f-rear-dmi-provider-integration"
I7="$E/e007i-rear-lsc-dmi-handoff"
Q7="$E/e007q-rear-gtm-clean-handoff"
S7="$E/e007s-rear-zero-stable-dmi-binding"
T7="$E/e007t-rear-gamma151-clean-provider"
U7="$E/e007u-rear-bpcabf411-clean-dmi"
V7="$E/e007v-rear-dsx101-clean-provider"
W7="$E/e007w-rear-period-cfg-semantic-provider"
X7="$E/e007x-rear-bhist16-startup-dmi"
Y7="$E/e007y-rear-full-startup-offline-materializer"

cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
test "$HEAD_NOW" = "5614006d997f5492eb3a97b232063c8f8ce64db1"

GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R" \
 "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden \
 --require-no-camera-process --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

"$Y7/verify.py"
"$Z7/verify.py"
"$A8/verify.py"
"$H8/verify.py"
"$I8/verify.py"
"$J8/verify.py"
"$K8/verify.py"
"$L8/verify.py"
"$N8/verify.py"

test ! -e "$B" || { echo E008N_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"

# Shared owner / CSID / VFE support.
cp "$Y5/camss-e005y-vfe1-owner-observer-fix3.inc" "$B/camss-e005y-vfe1-owner-observer.inc"
cp "$NS/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$NT/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$NU/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$D8/camss-vfe-e008d-rear-dma.inc" "$B/"
cp "$Z7/camss-e007z-rear-retirement.inc" "$B/"
cp "$A8/camss-csid-e008a-rear-quiesce.inc" "$B/"
cp "$A8/camss-vfe-e008a-rear-bus-stop.inc" "$B/"
cp "$H8/camss-vfe-e008h-rear-prime.inc" "$B/"
cp "$J8/camss-vfe-e008j-rear-prebus.inc" "$B/"
cp "$I8/camss-e008i-rear-observer.h" "$B/"
cp "$I8/camss-vfe-e008i-rear-status.inc" "$B/"
cp "$I8/camss-csid-e008i-rear-observer.inc" "$B/"
cp "$K8/camss-e008k-rear-bridge.h" "$B/"
cp "$K8/camss-e008k-rear-rtcdm-bridge.inc" "$B/"
cp "$K8/camss-csid-e008k-rear-bridge.inc" "$B/"
cp "$K8/camss-vfe-e008k-rear-runner.inc" "$B/"
cp "$L8/camss-vfe-e008l-rear-command-dma.inc" "$B/"
cp "$N8/camss-vfe-e008n-rear-single-use.inc" "$B/"

# E007y complete startup materializer dependency chain.
for f in \
 "$E/e006g-rear-rtcdm-materializer-skeleton/camss-e006g-rear-materializer.inc" \
 "$E/e006j-rear-steady-producer-binding-compile/camss-e006j-rear-register-bindings.inc" \
 "$E/e006m-rear-startup-producer-binding-compile/camss-e006m-rear-startup-bindings.inc" \
 "$E/e006o-rear-steady-singleton-provider-compile/camss-e006o-rear-steady-singletons.inc" \
 "$E/e006p-rear-crop-roundclamp-packers/camss-e006p-crop-roundclamp.inc" \
 "$E/e006q-rear-mnds23-packer/camss-e006q-mnds23.inc" \
 "$E/e006r-rear-cst12-tuning-packer/camss-e006r-cst12.inc" \
 "$E/e006s-rear-bc101-tuning-provider/camss-e006s-bc101.inc" \
 "$E/e006t-rear-disabled-small-iq-providers/camss-e006t-small-iq.inc" \
 "$E/e006u-rear-bhist16-provider/camss-e006u-bhist16.inc" \
 "$E/e006v-rear-rsstats14-packer/camss-e006v-rsstats14.inc" \
 "$E/e006w-rear-aecbe17-packer/camss-e006w-aecbe17.inc" \
 "$E/e006x-rear-tintlessbg17-packer/camss-e006x-tintlessbg17.inc" \
 "$E/e006y-rear-awbbg17-packer/camss-e006y-awbbg17.inc" \
 "$E/e006z-rear-clean-scalar-bank-providers/camss-e006z-clean-scalar-bank.inc" \
 "$A7/camss-e007a-bpcabf411.inc" \
 "$B7/camss-e007b-bfstats25.inc" \
 "$C7/camss-e007c-period-cfg.inc" \
 "$D7/camss-e007d-register-integration.inc" \
 "$E7/camss-e007e-bfstats25-dmi.inc" \
 "$F7/camss-e007f-dmi-integration.inc" \
 "$I7/camss-e007i-rear-lsc-handoff.inc" \
 "$Q7/camss-e007q-rear-gtm-handoff.inc" \
 "$S7/camss-e007s-zero-stable.inc" \
 "$T7/camss-e007t-gamma151.inc" \
 "$U7/camss-e007u-bpcabf411.inc" \
 "$V7/camss-e007v-dsx101.inc" \
 "$W7/camss-e007w-period-cfg.inc" \
 "$X7/camss-e007x-bhist16-startup-dmi.inc" \
 "$Y7/camss-e007y-rear-startup.inc"
do cp "$f" "$B/"; done

python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])

def inject(name, needle, replacement):
    p=b/name
    s=p.read_text()
    assert s.count(needle)==1,(name,needle[:100],s.count(needle))
    p.write_text(s.replace(needle,replacement,1))

# E005y shared owner is one per CAMSS device.
inject("camss.h", "struct camss {\n",
       '#include "camss-e005y-vfe1-owner-observer.inc"\n\n'
       'struct camss {\n'
       '\tstruct e005y_vfe1_owner e005y_vfe1_owner;\n')
inject("camss.c", "\tatomic_set(&camss->ref_count, 0);\n",
       "\tatomic_set(&camss->ref_count, 0);\n"
       "\te005y_vfe1_owner_init(&camss->e005y_vfe1_owner);\n")

# E008i shared type + bounded per-CSID history.
inject("camss-csid.h", '#include <media/v4l2-subdev.h>\n',
       '#include <media/v4l2-subdev.h>\n'
       '#include "camss-e008i-rear-observer.h"\n')
inject("camss-csid.h", '\tu32 x1e_buf_done_rs_count;\n',
       '\tu32 x1e_buf_done_rs_count;\n'
       '\tu64 e008i_rear_owner_epoch;\n'
       '\tu32 e008i_rear_epoch0_count;\n'
       '\tu32 e008i_rear_done_count;\n'
       '\tu32 e008i_rear_done_overflow;\n'
       '\tu32 e008i_rear_latch_errors;\n'
       '\tstruct e008i_rear_done_event e008i_rear_done[E008I_REAR_DONE_DEPTH];\n')

# CSID exact rear predicate/enable, observer, quiesce and E008k bridge.
inject("camss-csid-680.c",
       'static void csid_configure_stream(struct csid_device *csid, u8 enable)',
       '#include "camss-csid-e004ns-rear-ipp.inc"\n'
       '#include "camss-csid-e008i-rear-observer.inc"\n'
       '#include "camss-csid-e008a-rear-quiesce.inc"\n'
       '#include "camss-csid-e008k-rear-bridge.inc"\n\n'
       'static void csid_configure_stream(struct csid_device *csid, u8 enable)')

inject("camss-csid-680.c",
       '\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n',
       '\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n'
       '\tif (buf_done_val && csid_e004ns_rear_ipp_mode0(csid))\n'
       '\t\te008i_rear_latch_buf_done(csid, buf_done_val);\n')
inject("camss-csid-680.c",
       '\t\tipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);\n'
       '\t\tif (ipp_val && __csid_sp11_front_ipp_mode0(csid)) {',
       '\t\tipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);\n'
       '\t\tif (ipp_val && csid_e004ns_rear_ipp_mode0(csid))\n'
       '\t\t\te008i_rear_latch_ipp(csid, ipp_val);\n'
       '\t\tif (ipp_val && __csid_sp11_front_ipp_mode0(csid)) {')

# camss.c bridge can use already-accepted static RT-CDM and media-link helpers.
inject("camss.c",
       'static int camss_x1e_pix_runner_validate(struct camss *camss,',
       '#include "camss-e008k-rear-rtcdm-bridge.inc"\n\n'
       'static int camss_x1e_pix_runner_validate(struct camss *camss,')

# All rear materializers/ownership live in the VFE680 TU so the runner can
# compose them without exporting internal provider types. The two native VFE
# helpers are defined later in this TU, so declare their exact signatures here.
inject("camss-vfe-680.c", '#include <linux/iopoll.h>\n',
       '#include <linux/iopoll.h>\n#include <linux/unaligned.h>\n')
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
"camss-e006x-tintlessbg17.inc",
"camss-e006y-awbbg17.inc",
"camss-e006z-clean-scalar-bank.inc",
"camss-e007a-bpcabf411.inc",
"camss-e007b-bfstats25.inc",
"camss-e007c-period-cfg.inc",
"camss-e007d-register-integration.inc",
"camss-e007e-bfstats25-dmi.inc",
"camss-e007f-dmi-integration.inc",
"camss-e007i-rear-lsc-handoff.inc",
"camss-e007q-rear-gtm-handoff.inc",
"camss-e007s-zero-stable.inc",
"camss-e007t-gamma151.inc",
"camss-e007u-bpcabf411.inc",
"camss-e007v-dsx101.inc",
"camss-e007w-period-cfg.inc",
"camss-e007x-bhist16-startup-dmi.inc",
"camss-e007y-rear-startup.inc",
"camss-vfe-e004nt-rear-4k-buffer.inc",
"camss-vfe-e004nu-rear-ten-wm.inc",
"camss-vfe-e008d-rear-dma.inc",
"camss-e007z-rear-retirement.inc",
"camss-vfe-e008h-rear-prime.inc",
"camss-vfe-e008j-rear-prebus.inc",
"camss-e008i-rear-observer.h",
"camss-vfe-e008i-rear-status.inc",
"camss-vfe-e008a-rear-bus-stop.inc",
"camss-vfe-e008l-rear-command-dma.inc",
"camss-vfe-e008k-rear-runner.inc",
"camss-vfe-e008n-rear-single-use.inc",
]
include=(
 'static void __iomem *vfe680_x1e_bus_reg(struct vfe_device *vfe, u8 client, u32 reg);\n'
 'static bool vfe680_x1e_dma_span_32bit(dma_addr_t dma, size_t size);\n\n' +
 ''.join(f'#include "{n}"\n' for n in names) + '\n')
inject("camss-vfe-680.c",
       'static const u8 vfe680_x1e_windows_bus_client_order[] = {',
       include+'static const u8 vfe680_x1e_windows_bus_client_order[] = {')

print("E008N_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E008N-CAMSS-BUILD.log" 2>&1 || {
 tail -n 280 "$B/E008N-CAMSS-BUILD.log" >&2
 exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E008N-CAMSS-BUILD.log"; then
 echo E008N_W1_WARNING_OR_ERROR >&2
 exit 5
fi
vermagic="$(modinfo -F vermagic "$B/qcom-camss.ko")"
test "$vermagic" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
sha="$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)"
bytes="$(stat -c %s "$B/qcom-camss.ko")"

aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | grep -E \
 'e008n_rear_run_once_unreachable|e008n_rear_single_use_recipe|e008l_rear_command_alloc|e008k_rear_run_unreachable'

python3 - "$N8/RESULT.json" "$sha" "$bytes" "$vermagic" <<'PY'
import json,sys
from pathlib import Path
p,sha,bs,vm=sys.argv[1:]
d=json.load(open(p))
d["classification"]="BUILD_ONLY_PASS"
d["build"]={
 "module_bytes":int(bs),
 "module_sha256":sha,
 "vermagic":vm,
 "w1_warnings_or_errors":0
}
Path(p).write_text(json.dumps(d,indent=2)+"\n")
PY

"$N8/verify.py"
echo "E008N_BUILD_PASS bytes=$bytes sha256=$sha"
echo E008N_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_REBOOT_NO_RUNTIME_CALL_SITE
