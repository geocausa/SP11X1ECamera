#!/usr/bin/env bash
set -euo pipefail

R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E="$R/experiments/E004-front-ir-vd55g0"
NS="$E/e004ns-rear-csid1-ipp-offline"
I="$E/e008i-rear-csid1-irq-consumed-iova-observer"
SRC="$R/src/front-imx681/kernel/camss"
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e008i-rear-csid1-irq-consumed-iova-observer-build

cd "$R"
HEAD_NOW="$(git -c safe.directory="$R" rev-parse HEAD)"
ORIGIN_NOW="$(git -c safe.directory="$R" rev-parse origin/experiment/e004-front-ir-vd55g0)"
test "$HEAD_NOW" = "$ORIGIN_NOW"
test "$HEAD_NOW" = "50ea4bd61a0732da13bfe1d2d588590764191fd1"

GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0="$R" \
  "$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden \
  --require-no-camera-process --expect-head "$HEAD_NOW" --expect-origin "$ORIGIN_NOW"

"$I/verify.py"

test ! -e "$B" || { echo E008I_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
cp "$NS/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$I/camss-e008i-rear-observer.h" "$B/"
cp "$I/camss-vfe-e008i-rear-status.inc" "$B/"
cp "$I/camss-csid-e008i-rear-observer.inc" "$B/"

python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])

def inject(name, needle, replacement):
    p=b/name
    s=p.read_text()
    assert s.count(needle)==1,(name,needle,s.count(needle))
    p.write_text(s.replace(needle,replacement,1))

# Shared event type and prototypes, plus per-CSID bounded software history.
inject("camss-csid.h",
       '#include <media/v4l2-subdev.h>\n',
       '#include <media/v4l2-subdev.h>\n#include "camss-e008i-rear-observer.h"\n')
inject("camss-csid.h",
       '\tu32 x1e_buf_done_rs_count;\n',
       '\tu32 x1e_buf_done_rs_count;\n'
       '\t/* E008i rear-only bounded IRQ/VFE consumed-address history. */\n'
       '\tu64 e008i_rear_owner_epoch;\n'
       '\tu32 e008i_rear_epoch0_count;\n'
       '\tu32 e008i_rear_done_count;\n'
       '\tu32 e008i_rear_done_overflow;\n'
       '\tu32 e008i_rear_latch_errors;\n'
       '\tstruct e008i_rear_done_event e008i_rear_done[E008I_REAR_DONE_DEPTH];\n')

# Read-only VFE ADDR_STATUS0 sampler. No VFE write path is added.
inject("camss-vfe-680.c",
       'static const u8 vfe680_x1e_windows_bus_client_order[] = {',
       '#include "camss-e008i-rear-observer.h"\n'
       '#include "camss-vfe-e008i-rear-status.inc"\n\n'
       'static const u8 vfe680_x1e_windows_bus_client_order[] = {')

# Rear mode predicate/config source first, then rear software observer helpers.
inject("camss-csid-680.c",
       'static void csid_configure_stream(struct csid_device *csid, u8 enable)',
       '#include "camss-csid-e004ns-rear-ipp.inc"\n'
       '#include "camss-csid-e008i-rear-observer.inc"\n\n'
       'static void csid_configure_stream(struct csid_device *csid, u8 enable)')

# Consume the already-read/cleared BUF_DONE status. No new CSID ACK.
inject("camss-csid-680.c",
       '\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n',
       '\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n'
       '\tif (buf_done_val && csid_e004ns_rear_ipp_mode0(csid))\n'
       '\t\te008i_rear_latch_buf_done(csid, buf_done_val);\n')

# Consume the already-read IPP status before its existing clear.
inject("camss-csid-680.c",
       '\t\tipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);\n'
       '\t\tif (ipp_val && __csid_sp11_front_ipp_mode0(csid)) {',
       '\t\tipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);\n'
       '\t\tif (ipp_val && csid_e004ns_rear_ipp_mode0(csid))\n'
       '\t\t\te008i_rear_latch_ipp(csid, ipp_val);\n'
       '\t\tif (ipp_val && __csid_sp11_front_ipp_mode0(csid)) {')

print("E008I_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E008I-CAMSS-BUILD.log" 2>&1 || {
  tail -n 240 "$B/E008I-CAMSS-BUILD.log" >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E008I-CAMSS-BUILD.log"; then
  echo E008I_W1_WARNING_OR_ERROR >&2
  exit 5
fi

vermagic="$(modinfo -F vermagic "$B/qcom-camss.ko")"
test "$vermagic" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
sha="$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
bytes="$(stat -c %s "$B/qcom-camss.ko")"

aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | grep -E \
 'csid680_e008i_rear_|vfe680_e008i_rear_snapshot_addr_status0'

python3 - "$I/RESULT.json" "$I/BUILD-RESULT.json" "$B/qcom-camss.ko" "$B" "$sha" "$bytes" "$vermagic" <<'PY'
import json,sys
from pathlib import Path
rp,bp,mp,bd,sha,bs,vm=sys.argv[1:]
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
    "schema":"E008I-build-result-v1",
    "status":"PASS",
    "build_dir":bd,
    "module_path":mp,
    "module_bytes":int(bs),
    "module_sha256":sha,
    "vermagic":vm,
    "w1_warnings_or_errors":0,
    "module_installed":False,
    "module_loaded":False,
    "camera_runtime":False,
    "reboot_performed":False,
    "extra_csid_irq_ack_added":False,
    "golden_preserved":True
}
Path(bp).write_text(json.dumps(br,indent=2)+"\n")
PY

"$I/verify.py"
echo "E008I_BUILD_PASS bytes=$bytes sha256=$sha"
echo E008I_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_REBOOT
