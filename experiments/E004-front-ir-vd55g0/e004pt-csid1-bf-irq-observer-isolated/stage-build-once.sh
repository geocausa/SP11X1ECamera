#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E004pt one-use isolated ARM64 CAMSS compile; never install or load module.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e004pt-csid1-bf-irq-observer-isolated"
N="$R/experiments/E004-front-ir-vd55g0"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden \
  --require-no-camera-process \
  --expect-head 376c172430783b07300d4af780a1fe870982d154 \
  --expect-origin 376c172430783b07300d4af780a1fe870982d154
python3 - "$SRC" "$D" <<'PY'
import pathlib,hashlib,sys
src=pathlib.Path(sys.argv[1]); stage=pathlib.Path(sys.argv[2])
expected={
"camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
"camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
"camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
"camss-csid.h":"bd8f68b623f2e8e5a2c624fdd8ce7a901c7fc11fa35a2efbd04f8273fca3aee2"}
for filename,want in expected.items():
 got=hashlib.sha256((src/filename).read_bytes()).hexdigest()
 assert got==want,("accepted-source-changed",filename,got)
assert (stage/"camss-csid-e004pt-bf-observer.inc").is_file()
print("E004PT_ACCEPTED_ORIGINAL_CAMSS_HASHES_PASS")
PY
test -f "$HDR/include/generated/autoconf.h"
test ! -e "$B" || { echo E004PT_BUILD_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
# The newly created build folder is an atomic one-shot identity. On any
# interruption it must be audited and never blindly overwritten/replayed.
cp -a "$SRC/." "$B/"
cp "$N/e004nr-rear-pix-kernel-source-profile/camss-e004nr-rear-profile.inc" "$B/"
cp "$N/e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$N/e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$N/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$N/e004nv-rear-six-group-bf-static/camss-vfe-e004nv-rear-six-group.inc" "$B/"
cp "$D/camss-csid-e004pt-bf-observer.inc" "$B/"
python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])
def inject(filename,old,new):
 p=b/filename
 text=p.read_text()
 assert text.count(old)==1,(filename,"unexpected accepted source anchor")
 assert new not in text
 p.write_text(text.replace(old,new,1))
inject("camss.c",
       "static int camss_x1e_pix_runner_validate(struct camss *camss,",
       '#include "camss-e004nr-rear-profile.inc"\n\nstatic int camss_x1e_pix_runner_validate(struct camss *camss,')
inject("camss-csid-680.c",
       "static void __csid_configure_top(struct csid_device *csid)",
       '#include "camss-csid-e004ns-rear-ipp.inc"\n\nstatic void __csid_configure_top(struct csid_device *csid)')
inject("camss-vfe-680.c",
       "static int vfe680_x1e_group_from_event(u32 event_id)",
       '#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
       '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
       '#include "camss-vfe-e004nv-rear-six-group.inc"\n\n'
       "static int vfe680_x1e_group_from_event(u32 event_id)")
inject("camss-csid.h", "#include <linux/clk.h>",
       "#include <linux/atomic.h>\n#include <linux/clk.h>")
inject("camss-csid.h", "\tu32 x1e_buf_done_rs_count;\n",
       "\tu32 x1e_buf_done_rs_count;\n"
       "\t/* E004pt observation ONLY. Not a FIFO/WM16/DMA completion counter. */\n"
       "\tatomic64_t x1e_e004pt_bf_observations;\n"
       "\tu32 x1e_e004pt_bf_last_status;\n")
inject("camss-csid-680.c",
       "/*\n * csid_isr - CSID module interrupt service routine\n",
       '#include "camss-csid-e004pt-bf-observer.inc"\n\n'
       "/*\n * csid_isr - CSID module interrupt service routine\n")
inject("camss-csid-680.c",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n"
       "\t/* Only reuse the ALREADY-LATCHED status; no additional MMIO/ACK. */\n"
       "\te004pt_observe_csid1_bf_irq(csid, buf_done_val);\n")
inject("camss-csid-680.c",
       "static void csid_subdev_init(struct csid_device *csid) {}",
       "static void csid_subdev_init(struct csid_device *csid)\n"
       "{\n"
       "\tatomic64_set(&csid->x1e_e004pt_bf_observations, 0);\n"
       "\tWRITE_ONCE(csid->x1e_e004pt_bf_last_status, 0);\n"
       "}")
print("E004PT_ISOLATED_CAMSS_COPY_INSTRUMENTED_NO_ACCEPTED_SOURCE_MUTATION")
PY
# Compile exclusively in new SP11-local build directory; no insmod, depmod,
# modprobe, boot, kernel installation, camera open or IRQ/MMIO access.
make -C "$HDR" M="$B" W=1 -j4 > "$B/E004PT-CAMSS-BUILD.log" 2>&1 || {
 tail -n 90 "$B/E004PT-CAMSS-BUILD.log" >&2
 echo E004PT_ISOLATED_ARM64_COMPILE_FAILED >&2
 exit 4
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | \
 grep ' csid680_e004pt_bf_status_observations$'
printf 'E004PT_ISOLATED_ARM64_CAMSS_BUILD_PASS bytes=%s sha256=%s\n' \
 "$(stat -c %s "$B/qcom-camss.ko")" \
 "$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
echo E004PT_NO_REAR_RUNTIME_ENABLE_NO_MODULE_INSTALL_LOAD_NO_GOLDEN_CHANGE
