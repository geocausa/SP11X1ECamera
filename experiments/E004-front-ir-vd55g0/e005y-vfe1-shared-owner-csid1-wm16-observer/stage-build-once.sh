#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E005y isolated build only: no install/load/camera/boot/MMIO runtime.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005y-vfe1-shared-owner-csid1-wm16-observer"
N="$R/experiments/E004-front-ir-vd55g0"
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss
HDR=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005y-vfe1-shared-owner-observer-build

cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process \
  --expect-head 77d39e064aa0d32ab5f3a37f3a9e3b18a7cef70a --expect-origin 77d39e064aa0d32ab5f3a37f3a9e3b18a7cef70a

python3 - "$SRC" <<'PY'
from pathlib import Path
import hashlib,sys
src=Path(sys.argv[1])
pins={
 "camss.h":"da2941a9d2afa6250773c682027fc70512e32daa69a9478cb372ecaa74be37c0",
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
 "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
 "camss-vfe.h":""
}
for n,sha in list(pins.items()):
    if not sha:
        pins[n]=hashlib.sha256((src/n).read_bytes()).hexdigest()
for n,sha in pins.items():
    got=hashlib.sha256((src/n).read_bytes()).hexdigest()
    assert got==sha,(n,got,sha)
print("E005Y_ACCEPTED_SOURCE_PINS_PASS")
print("CAMSS_VFE_H_SHA="+pins["camss-vfe.h"])
PY

test ! -e "$B" || { echo E005Y_BUILD_ID_ALREADY_CONSUMED >&2; exit 3; }
mkdir -- "$B"
cp -a "$SRC/." "$B/"
cp "$N/e004nr-rear-pix-kernel-source-profile/camss-e004nr-rear-profile.inc" "$B/"
cp "$N/e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc" "$B/"
cp "$D/camss-e005y-vfe1-owner-observer.inc" "$B/"

python3 - "$B" <<'PY'
from pathlib import Path
import sys
b=Path(sys.argv[1])

def inject(name,needle,repl):
    p=b/name
    s=p.read_text()
    assert s.count(needle)==1,(name,needle[:80],s.count(needle))
    p.write_text(s.replace(needle,repl,1))

# Existing rear graph/profile remains source-only/denied.
inject("camss.c",
       "static int camss_x1e_pix_runner_validate(struct camss *camss,",
       '#include "camss-e004nr-rear-profile.inc"\n\n'
       'static int camss_x1e_pix_runner_validate(struct camss *camss,')

# Rear CSID1 route predicate/config source is available but remains unwired.
inject("camss-csid-680.c",
       "static void __csid_configure_top(struct csid_device *csid)",
       '#include "camss-csid-e004ns-rear-ipp.inc"\n\n'
       'static void __csid_configure_top(struct csid_device *csid)')

# Shared owner lives once per CAMSS device.
inject("camss.h",
       "struct camss {\n",
       '#include "camss-e005y-vfe1-owner-observer.inc"\n\n'
       'struct camss {\n'
       '\tstruct e005y_vfe1_owner e005y_vfe1_owner;\n')
inject("camss.c",
       "\tatomic_set(&camss->ref_count, 0);\n",
       "\tatomic_set(&camss->ref_count, 0);\n"
       "\te005y_vfe1_owner_init(&camss->e005y_vfe1_owner);\n")

# Compiler-visible VFE680 read-only WM16 status helper.
inject("camss-vfe.h",
       "\n#endif /* QC_MSM_CAMSS_VFE_H */\n",
       "\nu32 vfe680_e005y_wm16_addr_status0(struct vfe_device *vfe);\n"
       "\n#endif /* QC_MSM_CAMSS_VFE_H */\n")

inject("camss-vfe-680.c",
       "static const u8 vfe680_x1e_windows_bus_client_order[] = {",
       "u32 vfe680_e005y_wm16_addr_status0(struct vfe_device *vfe)\n"
       "{\n"
       "\tif (!vfe || !vfe->camss ||\n"
       "\t    vfe->camss->res->version != CAMSS_X1E80100 ||\n"
       "\t    vfe->id != 1 || vfe_is_lite(vfe))\n"
       "\t\treturn 0;\n"
       "\treturn readl_relaxed(vfe->base + VFE680_X1E_BUS_CLIENT_BASE +\n"
       "\t\t16 * VFE680_X1E_BUS_CLIENT_STRIDE + VFE680_X1E_BUS_ADDR_STATUS0);\n"
       "}\n\n"
       "static const u8 vfe680_x1e_windows_bus_client_order[] = {")

# Scope the existing custom FRONT runner under the shared owner.
p=b/"camss.c"
s=p.read_text()
a=s.index("static int camss_x1e_pix_runner_frames(")
z=s.index("static int camss_x1e_pix_runner_once(",a)
part=s[a:z]
def mod(old,new):
    global part
    assert part.count(old)==1,(old[:80],part.count(old))
    part=part.replace(old,new,1)

mod("\tbool teardown_safe = true;\n",
    "\tbool teardown_safe = true;\n"
    "\tbool e005y_owner_granted = false;\n"
    "\tu64 e005y_owner_epoch = 0;\n")
mod("\t/* Same power owner used by the already-proven RDI video prepare path. */\n",
    "\t/* Exact FRONT graph has already been validated. Acquire the global\n"
    "\t * shared CSID1/VFE1 owner before any camera power/start.\n"
    "\t */\n"
    "\tret = e005y_vfe1_owner_acquire(&camss->e005y_vfe1_owner,\n"
    "\t\t\t\t       E005Y_VFE1_OWNER_FRONT, true,\n"
    "\t\t\t\t       &e005y_owner_epoch);\n"
    "\tif (ret)\n"
    "\t\tgoto out_materialized;\n"
    "\te005y_owner_granted = true;\n\n"
    "\t/* Same power owner used by the already-proven RDI video prepare path. */\n")
mod('\t\tdev_err(camss->dev,\n'
    '\t\t\t"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\\n");\n'
    '\t\treturn ret ? ret : -EIO;',
    '\t\tdev_err(camss->dev,\n'
    '\t\t\t"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\\n");\n'
    '\t\tif (e005y_owner_granted)\n'
    '\t\t\t(void)e005y_vfe1_owner_release(&camss->e005y_vfe1_owner,\n'
    '\t\t\t\tE005Y_VFE1_OWNER_FRONT, e005y_owner_epoch, false);\n'
    '\t\treturn ret ? ret : -EIO;')
mod('out_free_inputs:\n\tkfree(materialized_next);',
    'out_free_inputs:\n'
    '\tif (e005y_owner_granted) {\n'
    '\t\tint ownret = e005y_vfe1_owner_release(&camss->e005y_vfe1_owner,\n'
    '\t\t\tE005Y_VFE1_OWNER_FRONT, e005y_owner_epoch, teardown_safe);\n'
    '\t\tif (ownret && !ret)\n'
    '\t\t\tret = ownret;\n'
    '\t}\n'
    '\tkfree(materialized_next);')
p.write_text(s[:a]+part+s[z:])

# Correct CSID1 observer: consume existing latch/ACK, sample WM16 only for a
# still-current REAR owner + exact rear route. No retirement or extra ACK.
inject("camss-csid-680.c",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n",
       "\twritel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);\n"
       "\tif (csid->camss->res->version == CAMSS_X1E80100 &&\n"
       "\t    !csid_is_lite(csid) && csid->id == 1 &&\n"
       "\t    (buf_done_val & E005Y_CSID1_BF_BIT)) {\n"
       "\t\tbool front_now = csid->phy.en_ipp && __csid_sp11_front_ipp_mode0(csid);\n"
       "\t\tbool rear_now = csid_e004ns_rear_ipp_mode0(csid);\n"
       "\t\tu64 rear_epoch = 0;\n"
       "\t\tu32 wm16 = 0;\n"
       "\t\tbool sampled = e005y_vfe1_rear_sample_begin(\n"
       "\t\t\t&csid->camss->e005y_vfe1_owner, rear_now, &rear_epoch);\n"
       "\t\tif (sampled)\n"
       "\t\t\twm16 = vfe680_e005y_wm16_addr_status0(&csid->camss->vfe[1]);\n"
       "\t\t(void)e005y_vfe1_observe_bf(&csid->camss->e005y_vfe1_owner,\n"
       "\t\t\tfront_now, rear_now, buf_done_val, rear_epoch, sampled, wm16);\n"
       "\t}\n")

print("E005Y_ISOLATED_SOURCE_INJECTION_PASS")
PY

make -C "$HDR" M="$B" W=1 -j4 > "$B/E005Y-CAMSS-BUILD.log" 2>&1 || {
  tail -n 140 "$B/E005Y-CAMSS-BUILD.log" >&2
  echo E005Y_BUILD_FAILED_CONSUMED_AUDIT_BEFORE_NEW_ID >&2
  exit 4
}
test -s "$B/qcom-camss.ko"
if grep -Ei '(warning:|error:)' "$B/E005Y-CAMSS-BUILD.log"; then
  echo E005Y_W1_WARNINGS_CONSUMED_AUDIT_BEFORE_NEW_ID >&2
  exit 5
fi
test "$(modinfo -F vermagic "$B/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
printf 'E005Y_BUILD_PASS bytes=%s sha256=%s\n' "$(stat -c %s "$B/qcom-camss.ko")" "$(sha256sum "$B/qcom-camss.ko" | cut -d" " -f1)"
aarch64-linux-gnu-nm -a "$B/qcom-camss.ko" | grep -E 'e005y_vfe1|vfe680_e005y_wm16' | head -80
echo E005Y_BUILD_ONLY_NO_INSTALL_NO_LOAD_NO_CAMERA_NO_REAR_ARM
