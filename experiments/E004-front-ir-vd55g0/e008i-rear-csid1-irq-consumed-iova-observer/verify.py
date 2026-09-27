#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = ROOT/"experiments/E004-front-ir-vd55g0"

P = {
    "e004ns": E/"e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc",
    "e004nq": E/"e004nq-rear-physical-mmio-5phase/README.md",
    "e007z": E/"e007z-rear-ten-wm-consumed-iova-retirement/camss-e007z-rear-retirement.inc",
    "csidc": ROOT/"src/front-imx681/kernel/camss/camss-csid-680.c",
    "csidh": ROOT/"src/front-imx681/kernel/camss/camss-csid.h",
    "vfec": ROOT/"src/front-imx681/kernel/camss/camss-vfe-680.c",
    "vfeh": ROOT/"src/front-imx681/kernel/camss/camss-vfe.h",
}
HASH = {
    "e004ns":"f145ec03045bf4e8a177011d52a44d6f56f9aff9fbd90fd4a6fc89200cf3f40f",
    "e004nq":"123657b2afd1f7ad76977429ea3cdacf02740a6ad7af24138cb59866e81118c0",
    "e007z":"e4b1cff066b18c6a254b6e0df9db1a91866804e57aa62420cb9b9ad030762ef2",
    "csidc":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
    "csidh":"bd8f68b623f2e8e5a2c624fdd8ce7a901c7fc11fa35a2efbd04f8273fca3aee2",
    "vfec":"5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec",
    "vfeh":"b2a39f1d2310e072eccd50db00fb0aae13357a99807be778b4edd4cc7f429374",
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for k,p in P.items():
    assert sha(p) == HASH[k], (k, sha(p), HASH[k])

hdr = (HERE/"camss-e008i-rear-observer.h").read_text()
vfe = (HERE/"camss-vfe-e008i-rear-status.inc").read_text()
csid = (HERE/"camss-csid-e008i-rear-observer.inc").read_text()
stage = (HERE/"stage-build-once.sh").read_text()
res = json.loads((HERE/"RESULT.json").read_text())
z = P["e007z"].read_text()
nq = P["e004nq"].read_text()
base_csid = P["csidc"].read_text()

assert "#define E008I_REAR_DONE_DEPTH" in hdr and "16U" in hdr
assert "#define E008I_REAR_BUF_DONE_MASK" in hdr and "0x000002f1U" in hdr
assert "struct e008i_rear_done_event" in hdr
assert "u32 addr_status0[E008I_REAR_WMS];" in hdr

assert "0x000002F1" in nq and "0x0001FFFF" in nq
for group in [0,4,5,6,7,9]:
    assert f".comp_group = {group}" in z
assert "{ .wm = 16, .comp_group = 7" in z

assert "static const u8 e008i_rear_wm[E008I_REAR_WMS]" in vfe
assert "0, 1, 2, 3, 11, 12, 13, 14, 16, 18" in vfe
assert "0, 0, 0, 0, 4, 4, 5, 6, 7, 9" in vfe
assert "VFE680_X1E_BUS_ADDR_STATUS0" in vfe
assert "readl_relaxed" in vfe
assert "writel" not in vfe

for needle in [
    "e008i_rear_latch_buf_done",
    "e008i_rear_latch_ipp",
    "csid680_e008i_rear_reset",
    "synchronize_irq(csid->irq)",
    "csid680_e008i_rear_poll_next_epoch0",
    "csid680_e008i_rear_poll_done",
    "csid680_e008i_rear_done_event",
    "READ_ONCE(csid->e008i_rear_owner_epoch)",
    "n >= E008I_REAR_DONE_DEPTH",
    "smp_wmb();",
    "smp_rmb();",
    "return -EOVERFLOW;",
    "return -EOPNOTSUPP;",
]:
    assert needle in csid, needle
assert "writel" not in csid
assert "readl" not in csid
assert "vfe680_e008i_rear_snapshot_addr_status0" in csid

# Baseline front-only latch excludes rear, proving why a distinct observer is needed.
assert "if (buf_done_val && __csid_sp11_front_ipp_mode0(csid))" in base_csid
assert "if (ipp_val && __csid_sp11_front_ipp_mode0(csid))" in base_csid
assert "if (ipp_val & CSID_IPP_CAMIF_EPOCH0)" in base_csid
assert "#define\t\tCSID_BUF_DONE_VIDEO" in base_csid
assert "#define\t\tCSID_BUF_DONE_RS" in base_csid
assert "BIT(7)" not in "\n".join(
    line for line in base_csid.splitlines()
    if "CSID_BUF_DONE_" in line
)

# Stage must hook only the already-read statuses and add no extra CSID ACK.
for needle in [
    'writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);',
    'e008i_rear_latch_buf_done(csid, buf_done_val);',
    'e008i_rear_latch_ipp(csid, ipp_val);',
    '#include "camss-csid-e004ns-rear-ipp.inc"',
    '#include "camss-csid-e008i-rear-observer.inc"',
    '#include "camss-vfe-e008i-rear-status.inc"',
    'struct e008i_rear_done_event e008i_rear_done[E008I_REAR_DONE_DEPTH];',
]:
    assert needle in stage, needle

assert res["classification"] in ("BUILD_ONLY_PENDING","BUILD_ONLY_PASS")
assert res["rear_tracked_buf_done_mask"] == "0x000002f1"
assert res["tracked_groups"] == [0,4,5,6,7,9]
assert res["wm_order"] == [0,1,2,3,11,12,13,14,16,18]
assert res["extra_irq_ack_added"] is False
assert res["runtime_call_site"] is False
assert res["module_installed_or_loaded"] is False
assert res["linux_camera_runtime_performed"] is False

b = HERE/"BUILD-RESULT.json"
if b.exists():
    br = json.loads(b.read_text())
    assert res["classification"] == "BUILD_ONLY_PASS"
    assert br["status"] == "PASS"
    assert br["vermagic"] == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    assert br["w1_warnings_or_errors"] == 0
    assert br["module_installed"] is False and br["module_loaded"] is False
    assert br["camera_runtime"] is False and br["reboot_performed"] is False
    mod = Path(br["module_path"])
    assert mod.is_file() and sha(mod) == br["module_sha256"]
    assert mod.stat().st_size == br["module_bytes"]

    bdir = Path(br["build_dir"])
    staged = (bdir/"camss-csid-680.c").read_text()
    isr_start = staged.index("static irqreturn_t csid_isr")
    isr = staged[isr_start:staged.index("static void csid_subdev_reg_update", isr_start)]
    clear = "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);"
    assert isr.count(clear) == 1
    assert isr.index(clear) < isr.index("e008i_rear_latch_buf_done(csid, buf_done_val);")
    assert isr.index("ipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);") < isr.index("e008i_rear_latch_ipp(csid, ipp_val);")
    assert isr.index("e008i_rear_latch_ipp(csid, ipp_val);") < isr.index("writel(ipp_val, csid->base + CSID_IPP_IRQ_CLEAR);")

    nm = subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(mod)], text=True)
    for sym in [
        "csid680_e008i_rear_reset",
        "csid680_e008i_rear_epoch0_seq",
        "csid680_e008i_rear_poll_next_epoch0",
        "csid680_e008i_rear_done_event",
        "vfe680_e008i_rear_snapshot_addr_status0",
    ]:
        assert sym in nm, sym

print("E008i VERIFY PASS")
