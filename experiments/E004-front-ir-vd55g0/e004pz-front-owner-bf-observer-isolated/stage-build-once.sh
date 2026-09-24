#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Single-use isolated ARM64 CAMSS candidate. NO module install/load or stream.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e004pz-front-owner-bf-observer-isolated"
N="$R/experiments/E004-front-ir-vd55g0"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pz-front-owner-bf-observer-build
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden \
 --require-no-camera-process \
 --expect-head 82c52a1bdcf5330177662a6678191ce21c3be4d6 \
 --expect-origin 82c52a1bdcf5330177662a6678191ce21c3be4d6
python3 - "$SRC" <<'PY'
from pathlib import Path
import hashlib,sys
src=Path(sys.argv[1])
checks={
"camss.h":"da2941a9d2afa6250773c682027fc70512e32daa69a9478cb372ecaa74be37c0",
"camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
"camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
"camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208"}
for name,sha in checks.items():
 assert hashlib.sha256((src/name).read_bytes()).hexdigest()==sha, ("accepted source changed",name)
print("E004PZ_ACCEPTED_CAMSS_FOUR_SOURCE_SHA_PASS")
PY
test ! -e "$B" || { echo E004PZ_BUILD_ATTEMPT_ALREADY_CONSUMED >&2;exit 3; }
test -f "$HDR/include/generated/autoconf.h"
mkdir -- "$B"
# This unique attempt has now been consumed. If interrupted, AUDIT, do not replay.
cp -a "$SRC/." "$B/"
cp "$N/e004nr-rear-pix-kernel-source-profile/camss-e004nr-rear-profile.inc" "$B/"
cp "$N/e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$N/e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc" "$B/"
cp "$N/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc" "$B/"
cp "$N/e004nv-rear-six-group-bf-static/camss-vfe-e004nv-rear-six-group.inc" "$B/"
cp "$N/e004px-bf-owner-handoff-token-uniqueness-isolated/camss-vfe-e004pv-bf-owner-ring.inc" "$B/"
cp "$D/camss-e004pz-front-owner-observer.inc" "$B/"
python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])
def inject(filename,needle,replacement):
 path=b/filename
 text=path.read_text()
 assert text.count(needle)==1,("ambiguous accepted source anchor",filename,needle[:70],text.count(needle))
 assert text!=text.replace(needle,replacement,1)
 path.write_text(text.replace(needle,replacement,1))
# Copy only existing known compiled rear include stack, still UNWIRED and DENIED.
inject("camss.c","static int camss_x1e_pix_runner_validate(struct camss *camss,",
       '#include "camss-e004nr-rear-profile.inc"\n\nstatic int camss_x1e_pix_runner_validate(struct camss *camss,')
inject("camss-csid-680.c","static void __csid_configure_top(struct csid_device *csid)",
       '#include "camss-csid-e004ns-rear-ipp.inc"\n\nstatic void __csid_configure_top(struct csid_device *csid)')
inject("camss-vfe-680.c","static int vfe680_x1e_group_from_event(u32 event_id)",
       '#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
       '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
       '#include "camss-vfe-e004nv-rear-six-group.inc"\n'
       '#include "camss-vfe-e004pv-bf-owner-ring.inc"\n\n'
       'static int vfe680_x1e_group_from_event(u32 event_id)')
# Shared per-device front runner grant state accessible read-only in CSID IRQ.
inject("camss.h","struct camss {\n",
       '#include "camss-e004pz-front-owner-observer.inc"\n\n'
       'struct camss {\n'
       '\t/* E004pz front RUNNER scoped, not global VFE1 owner or rear arm. */\n'
       '\tstruct e004pz_front_observer e004pz_front_bf;\n')
inject("camss.c","\tatomic_set(&camss->ref_count, 0);\n",
       "\tatomic_set(&camss->ref_count, 0);\n"
       "\t/* An allocated camss object is initialized ONCE, before IRQ request. */\n"
       "\te004pz_front_observer_init(&camss->e004pz_front_bf);\n")
# Scope modifications to the real accepted custom front runner, NOT generic
# vfe_enable_v2 (which explicitly rejects X1E VFE1 PIX).
camss=b/"camss.c"
src=camss.read_text()
begin=src.index("static int camss_x1e_pix_runner_frames(")
end=src.index("static int camss_x1e_pix_runner_once(",begin)
part=src[begin:end]
def modify(old,new):
 global part
 assert part.count(old)==1,("ambiguous real front runner hook",old[:78],part.count(old))
 part=part.replace(old,new,1)
modify("\tbool teardown_safe = true;\n",
       "\tbool teardown_safe = true;\n"
       "\tbool e004pz_front_granted = false;\n"
       "\te004pz_u64 e004pz_front_epoch = 0;\n")
modify("\t/* Same power owner used by the already-proven RDI video prepare path. */\n",
       "\t/* E004pz source-backed FRONT graph was validated above; acquire runner\n"
       "\t * scope before ANY camera power/start. This is NOT an asserted\n"
       "\t * shared front/rear VFE1 grant; unrelated streams remain unguarded.\n"
       "\t */\n"
       "\tret = e004pz_front_runner_begin(&camss->e004pz_front_bf, true,\n"
       "\t\t\t\t\t &e004pz_front_epoch);\n"
       "\tif (ret)\n"
       "\t\tgoto out_materialized;\n"
       "\te004pz_front_granted = true;\n\n"
       "\t/* Same power owner used by the already-proven RDI video prepare path. */\n")
modify('\t\tdev_err(camss->dev,\n'
       '\t\t\t"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\\n");\n'
       '\t\treturn ret ? ret : -EIO;',
       '\t\tdev_err(camss->dev,\n'
       '\t\t\t"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\\n");\n'
       '\t\tif (e004pz_front_granted)\n'
       '\t\t\t(void)e004pz_front_runner_end(&camss->e004pz_front_bf,\n'
       '\t\t\t\t\t e004pz_front_epoch, false);\n'
       '\t\treturn ret ? ret : -EIO;')
modify('out_free_inputs:\n\tkfree(materialized_next);',
       'out_free_inputs:\n'
       '\t/* Stop is safe only when the EXISTING runner proved safe teardown.\n'
       '\t * Failure pinned above; never clear a failed hardware stop here.\n'
       '\t */\n'
       '\tif (e004pz_front_granted) {\n'
       '\t\tint ownret = e004pz_front_runner_end(&camss->e004pz_front_bf,\n'
       '\t\t\t\t\t e004pz_front_epoch, teardown_safe);\n'
       '\t\tif (ownret && !ret)\n'
       '\t\t\tret = ownret;\n'
       '\t}\n'
       '\tkfree(materialized_next);')
camss.write_text(src[:begin]+part+src[end:])
inject("camss-csid-680.c",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n"
       "\t/* E004pz observes EXISTING latched+ACKed BUF_DONE only; no\n"
       "\t * second MMIO/ACK, BF FIFO8 pop or VB2/DMA completion.\n"
       "\t */\n"
       "\tif (csid->camss->res->version == CAMSS_X1E80100 &&\n"
       "\t    !csid_is_lite(csid) && csid->id == 1)\n"
       "\t\t(void)e004pz_observe_csid1_status(\n"
       "\t\t\t&csid->camss->e004pz_front_bf,\n"
       "\t\t\tcsid->phy.en_ipp && __csid_sp11_front_ipp_mode0(csid),\n"
       "\t\t\tbuf_done_val);\n")
print("E004PZ_ISOLATED_CAMSS_FRONT_RUNNER_GRANT_CS ID1_ISR_SINGLE_LATCH_NO_HW_CHANGES")
PY
make -C "$HDR" M="$B" W=1 -j4 > "$B/E004PZ-CAMSS-BUILD.log" 2>&1 || {
 tail -n 105 "$B/E004PZ-CAMSS-BUILD.log" >&2
 echo E004PZ_FIRST_ATTEMPT_COMPILE_FAILED_AUDIT_BEFORE_NEW_ID >&2
 exit 4
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
if grep -Ei '(warning:|error:)' "$B/E004PZ-CAMSS-BUILD.log";then
 echo E004PZ_W1_BUILD_WARNINGS_AUDIT_BEFORE_NEW_ID >&2
 exit 5
fi
printf 'E004PZ_ISOLATED_ARM64_W1_ZERO_WARNINGS bytes=%s sha256=%s\n' \
 "$(stat -c %s "$B/qcom-camss.ko")" \
 "$(sha256sum "$B/qcom-camss.ko" | cut -d' ' -f1)"
echo E004PZ_FRONT_ONLY_OBSERVER_NO_MODULE_INSTALL_LOAD_REAR_ARM_OR_NEW_IRQ_ACK
