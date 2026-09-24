#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E005b copy-only W1 ARM64 build against ACTUAL 27-frame PRODUCTION source.
# The earlier E005a older accepted-source build was RETIRED BEFORE BOOT.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot"
SRC="$R/src/front-imx681/kernel/camss"
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-observer-build
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden \
 --require-no-camera-process \
 --expect-head 73c990762d2aadde4aed3e7cc6d3700366b0c07b \
 --expect-origin 73c990762d2aadde4aed3e7cc6d3700366b0c07b
test -s "$R/experiments/E004-front-ir-vd55g0/e005a-front-bf-scalar-one-shot-isolated/UNARMED-RETIRE.txt"
python3 - "$SRC" "$D" <<'PY'
from pathlib import Path
import hashlib,sys
src=Path(sys.argv[1]);d=Path(sys.argv[2])
checks={
"camss.c":"117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95",
"camss.h":"0bc0ae6173ebc8c858d0f6117aebbc409d7f6fa4414a7df4b66119c83456371e",
"camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
"camss-vfe-680.c":"5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec"}
for name,want in checks.items():
 assert hashlib.sha256((src/name).read_bytes()).hexdigest()==want,("PRODUCTION_SOURCE_CHANGED",name)
assert "frame_limit < 1 || frame_limit > 27" in (src/"camss.c").read_text()
assert "e003h_pix_runtime_arm" not in (src/"camss.c").read_text()
assert hashlib.sha256((d/"camss-e004pz-front-owner-observer.inc").read_bytes()).hexdigest()=="0af6268f6a1f5603bc1a32e098bf5590048b911ab784fbe04cdb0cc9c5f85d0a"
print("E005B_PRODUCTION_27_FRAME_BASE_PREIMAGE_AND_EXACT_REVIEWED_OBSERVER_PASS")
PY
test -f "$HDR/include/generated/autoconf.h"
test ! -e "$B" || { echo E005B_SINGLE_USE_BUILD_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
# Path creation consumes attempt identity even on failure. NEVER replay this
# script or edit the prior failed/prepared candidate build.
cp -a "$SRC/." "$B/"
cp "$D/camss-e004pz-front-owner-observer.inc" "$B/"
python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])
def inject(name,old,new):
 p=b/name;s=p.read_text()
 assert s.count(old)==1,("NONUNIQUE_PRODUCTION_SOURCE_HOOK",name,old[:75],s.count(old))
 p.write_text(s.replace(old,new,1))
inject("camss.h","struct camss {\n",
       '#include "camss-e004pz-front-owner-observer.inc"\n\n'
       'struct camss {\n'
       '\t/* E005b: exact front custom runner scope, NOT global rear-owner grant. */\n'
       '\tstruct e004pz_front_observer e005b_front_bf;\n')
inject("camss.c","\tatomic_set(&camss->ref_count, 0);\n",
       "\tatomic_set(&camss->ref_count, 0);\n"
       "\te004pz_front_observer_init(&camss->e005b_front_bf);\n")
p=b/"camss.c";s=p.read_text()
begin=s.index("static int camss_x1e_pix_runner_frames(")
end=s.index("static int camss_x1e_pix_runner_once(",begin)
part=s[begin:end]
def mod(old,new):
 global part
 assert part.count(old)==1,("AMBIGUOUS_PRODUCTION_FRONT_RUNNER_HOOK",old[:75],part.count(old))
 part=part.replace(old,new,1)
mod("\tbool teardown_safe = true;\n",
    "\tbool teardown_safe = true;\n"
    "\tbool e005b_front_granted = false;\n"
    "\te004pz_u64 e005b_front_epoch = 0;\n")
mod("\t/* Same power owner used by the already-proven RDI video prepare path. */\n",
    "\t/* E005b: exact PRODUCTION front runner, after existing graph/capsule\n"
    "\t * verification and BEFORE pipeline power, CSID/IFE start or RT-CDM.\n"
    "\t * This is not a global front/rear VFE1 owner.\n"
    "\t */\n"
    "\tret = e004pz_front_runner_begin(&camss->e005b_front_bf,\n"
    "\t\t\t\t\t true, &e005b_front_epoch);\n"
    "\tif (ret)\n\t\tgoto out_materialized;\n"
    "\te005b_front_granted = true;\n\n"
    "\t/* Same power owner used by the already-proven RDI video prepare path. */\n")
mod('\t\tdev_err(camss->dev,\n'
    '\t\t\t"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\\n");\n'
    '\t\treturn ret ? ret : -EIO;',
    '\t\tdev_err(camss->dev,\n'
    '\t\t\t"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\\n");\n'
    '\t\tif (e005b_front_granted)\n'
    '\t\t\t(void)e004pz_front_runner_end(&camss->e005b_front_bf,\n'
    '\t\t\t\t\t e005b_front_epoch, false);\n'
    '\t\treturn ret ? ret : -EIO;')
mod('out_free_inputs:\n\tkfree(materialized_r27);',
    'out_free_inputs:\n'
    '\tif (e005b_front_granted) {\n'
    '\t\tint ownret = e004pz_front_runner_end(&camss->e005b_front_bf,\n'
    '\t\t\t\t\t e005b_front_epoch, teardown_safe);\n'
    '\t\t/* Scalar STATUS only, emitted ONCE after existing safe runner stop.\n'
    '\t\t * No per-frame WM16 IRQ/DMA/IOMMU claim; no log in ISR.\n'
    '\t\t */\n'
    '\t\tif (!ownret && teardown_safe && !ret)\n'
    '\t\t\tdev_info(camss->dev,\n'
    '\t\t\t\t \"E005B_FRONT_ONLY_BF_STATUS owner_epoch=%llu bf_count=%llu unattributed_lifetime=%llu safe_stop=1 dma_fence_proven=0 rear_runtime_authorized=0\\n\",\n'
    '\t\t\t\t (unsigned long long)e005b_front_epoch,\n'
    '\t\t\t\t (unsigned long long)READ_ONCE(camss->e005b_front_bf.session_front_bf_count),\n'
    '\t\t\t\t (unsigned long long)READ_ONCE(camss->e005b_front_bf.lifetime_unattributed_bf_count));\n'
    '\t\tif (ownret && !ret)\n'
    '\t\t\tret = ownret;\n'
    '\t}\n'
    '\tkfree(materialized_r27);')
p.write_text(s[:begin]+part+s[end:])
inject("camss-csid-680.c",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n"
       "\t/* E005b STATUS only: consume the SAME latched+ACKed CSID1 word;\n"
       "\t * do not ACK again, pop FIFO8, or complete a WM16/VB2 buffer.\n"
       "\t */\n"
       "\tif (csid->camss->res->version == CAMSS_X1E80100 &&\n"
       "\t    !csid_is_lite(csid) && csid->id == 1)\n"
       "\t\t(void)e004pz_observe_csid1_status(\n"
       "\t\t\t&csid->camss->e005b_front_bf,\n"
       "\t\t\tcsid->phy.en_ipp && __csid_sp11_front_ipp_mode0(csid),\n"
       "\t\t\tbuf_done_val);\n")
print("E005B_PRODUCTION_27_FRAME_SOURCE_FRONT_RUNNER_AND_SINGLE_CSID_IRQ_LATCH_INSTRUMENTED")
PY
make -C "$HDR" M="$B" W=1 -j4 > "$B/E005B-CAMSS-BUILD.log" 2>&1 || {
 tail -n 105 "$B/E005B-CAMSS-BUILD.log" >&2
 echo E005B_BUILD_FAILED_SINGLE_USE_ID_CONSUMED_DO_NOT_REPLAY >&2
 exit 4
}
test -s "$B/qcom-camss.ko"
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
if grep -Ei '(warning:|error:)' "$B/E005B-CAMSS-BUILD.log";then
 echo E005B_W1_WARNINGS_ATTEMPT_CONSUMED_DO_NOT_REPLAY >&2
 exit 5
fi
# No e003h module param in actual production source, unlike obsolete e005a.
! modinfo -p "$B/qcom-camss.ko" | grep -q e003h_pix_runtime_arm
printf 'E005B_ACTUAL_27_FRAME_PRODUCTION_CAMSS_ARM64_W1_ZERO_WARNINGS bytes=%s sha256=%s\n' \
 "$(stat -c %s "$B/qcom-camss.ko")" \
 "$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)"
echo E005B_MODULE_NOT_INSTALLED_LOADED_REAR_UNARMED
