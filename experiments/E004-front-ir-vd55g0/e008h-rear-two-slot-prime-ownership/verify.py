#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = ROOT/"experiments/E004-front-ir-vd55g0"

P = {
    "e008e": E/"e008e-rear-startup-order-windows-oracle/SAFE-ORDER.json",
    "e008f": E/"e008f-rear-startup-callsite-busid-oracle/SAFE-DETAIL.json",
    "e008g": E/"e008g-rear-startup-batch-static-correlation/RESULT.json",
    "e008d": E/"e008d-rear-ten-wm-linux-dma-address-provider/camss-vfe-e008d-rear-dma.inc",
    "e007z": E/"e007z-rear-ten-wm-consumed-iova-retirement/camss-e007z-rear-retirement.inc",
    "e004nt": E/"e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc",
    "e004nu": E/"e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc",
    "busdoc": ROOT/"experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/VFE1-BUS-UNREACHABLE-RECIPE.md",
}
HASH = {
    "e008e":"a636c16290f3778a520b5e378b285fdd46b95aeb7e5eecb108979f6d61dfbc3c",
    "e008f":"e472a4d14aefaa1a6569d80456d92a92d57d0f705d6dabcd9ee276d06d961c75",
    "e008g":"251294c86af44a57bd817c749c0f0d861c620536d8d63d7f5eee4a3492590706",
    "e008d":"ce5b180a3331f1f211a19cc9c75ed5f722f9303052e3a2a4117439168f9f3a46",
    "e007z":"e4b1cff066b18c6a254b6e0df9db1a91866804e57aa62420cb9b9ad030762ef2",
    "e004nt":"05a27b12384c1267787b193eb0d8d13abe57a4d189778dbe9a52490f180046e6",
    "e004nu":"ccbd1415e2e2c94e366b6c3c2ba636f272c868edbc7fef556e2a1b2b5b4c4f23",
    "busdoc":"fff9aabbcb99d769d0381198e1d71a36120356de90ecaea3ff008b2335d2cbbc",
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for k,p in P.items():
    assert sha(p) == HASH[k], (k, sha(p), HASH[k])

src = (HERE/"camss-vfe-e008h-rear-prime.inc").read_text()
res = json.loads((HERE/"RESULT.json").read_text())
e = json.loads(P["e008e"].read_text())
f = json.loads(P["e008f"].read_text())
g = json.loads(P["e008g"].read_text())
d = P["e008d"].read_text()
z = P["e007z"].read_text()
nt = P["e004nt"].read_text()
busdoc = P["busdoc"].read_text()

# Dynamic evidence: post-start address work exists before E008g packet2/BATCH2.
ev = e["events"]
i_done = ev.index("E008E EV ISP_START_DONE")
i_b2 = ev.index("E008E EV BATCH 2 COUNT=6")
between = ev[i_done + 1:i_b2]
assert len(between) == 8
assert all(x.startswith("E008E EV ADDR ") for x in between)

# E008g owns packet2 at first post-start Epoch0; exact scheduler puts BUS update first.
assert g["rear_startup_packets"][2]["e007y_packet"] == 2
assert g["rear_startup_packets"][2]["owner"] == "IFE_Epoch0_post_start"
assert g["epoch0_selector2"]["software_order"] == "IFE Epoch0 -> BUS IOVA update -> RT-CDM selector2 consume"
assert "update" in busdoc and "address-only" in busdoc

# Live E008f BUS resource order and rear-only BF identity.
expected_ids = ["3000","3001","3002","301c","3010","300f","300e","300c","300d"]
assert [x["id"] for x in f["bus_set"]] == expected_ids
assert all(x["arg"] == "1" for x in f["bus_set"])
assert f["bus_config_ids"] == ["3000"] + expected_ids
assert [x["id"] for x in f["initial_address_writes"]] == ["3000"] + expected_ids

for needle in [
    "#define E008H_REAR_SLOTS 2U",
    "static const u8 e008h_rear_program_wms[E007Z_REAR_WMS] = {",
    "0, 1, 2, 3, 11, 18, 12, 14, 13, 16,",
    "struct e008d_rear_dma_set dma[E008H_REAR_SLOTS];",
    "struct e007z_rear_frame frame[E008H_REAR_SLOTS];",
    "e008h_rear_validate_pair_disjoint",
    "e007z_rear_spans_overlap",
    "e008h_rear_build_binding",
    "e007z_rear_validate_binding",
    "e008d_rear_prepare_addresses_disabled",
    "e008h_rear_enable_slot0",
    "e008h_rear_epoch0_retarget_slot1",
    "e008h_rear_observe_consumed",
    "e008h_rear_both_complete",
    "pair->dma[0].full.in_flight = true;",
    "pair->dma[1].full.in_flight = true;",
    "return -EOPNOTSUPP;",
]:
    assert needle in src, needle

# Slot0 is preloaded disabled, then enabled, then rewritten/read back.
i_pre = src.index("e008d_rear_prepare_addresses_disabled(vfe, &pair->dma[0]")
i_enable_fn = src.index("e008h_rear_enable_slot0")
i_enable_write = src.index("cfg_now | VFE_BUS_WRITE_CLIENT_CFG_EN", i_enable_fn)
i_rewrite = src.index("e008h_rear_write_slot_addresses(vfe, pair, 0)", i_enable_write)
i_check = src.index("e008h_rear_check_slot_addresses(vfe, pair, 0, true)", i_rewrite)
assert i_pre < i_enable_fn < i_enable_write < i_rewrite < i_check

# Slot1 retarget is a complete address-only phase with no RT-CDM/CSID/sensor side effect.
m = re.search(r"static int __used\ne008h_rear_epoch0_retarget_slot1.*?\n}\n", src, re.S)
assert m
body = m.group(0)
assert "e008h_rear_write_slot_addresses(vfe, pair, 1)" in body
assert "e008h_rear_check_slot_addresses(vfe, pair, 1, true)" in body
for forbidden in ["rtcdm", "csid", "s_stream", "dma_free", "v4l2"]:
    assert forbidden not in body.lower(), forbidden

# Exact-I/O retirement is preserved. A not-yet-programmed slot cannot accept completion.
obs = re.search(r"static int __used\ne008h_rear_observe_consumed.*?\n}\n", src, re.S)
assert obs
obs = obs.group(0)
assert "programmed_image_iova != last_consumed_iova" in obs
assert "!pair->programmed[s]" in obs
assert "return -EPROTO;" in obs
assert "return -EALREADY;" in obs
assert "e007z_rear_observe" in obs
assert "e008h_rear_fault_ledgers" in obs

# Both-complete requires two programmed, active, fault-free and fully retired ledgers.
both = re.search(r"static bool __used\ne008h_rear_both_complete.*?\n}\n", src, re.S)
assert both
both = both.group(0)
assert "!pair->programmed[0] || !pair->programmed[1]" in both
assert "f->pending" in both and "f->faulted" in both

# No runtime-facing activation or unsafe free-after-MMIO path is supplied by E008h.
for forbidden in [
    "camss_rtcdm1_windows_start(",
    "csid680_x1e_front_ipp_enable(",
    "v4l2_subdev_call(",
    "dma_free_coherent(",
    "e007z_rear_release_ledger(",
]:
    assert forbidden not in src, forbidden
release_fn = re.search(r"static void\ne008h_rear_release_before_mmio.*?\n}\n", src, re.S)
assert release_fn and "e008d_rear_release_partial" in release_fn.group(0)

assert "VFE680_E004NT_REAR_TOTAL_BYTES" in nt and "0x00ff6000U" in nt
assert "struct e007z_rear_frame" in z and "u16 pending;" in z
assert "last_consumed_iova != frame->slot[idx].programmed_image_iova" in z
assert "independently_verified_bus_stopped" in z and "independently_verified_irqs_drained" in z
assert "e008d_rear_dma_alloc" in d and "e008d_rear_build_addresses" in d

assert res["classification"] in ("BUILD_ONLY_PENDING","BUILD_ONLY_PASS")
assert res["slots"] == 2
assert res["one_slot_private_bytes"] == 0x1369d00
assert res["two_slot_private_bytes"] == 0x26d3a00
assert res["wm_program_order"] == [0,1,2,3,11,18,12,14,13,16]
assert res["safe_free_authorized"] is False
assert res["runtime_call_site"] is False
assert res["linux_native_rear_isp_runtime_performed"] is False
assert res["module_installed_or_loaded"] is False

b = HERE/"BUILD-RESULT.json"
if b.exists():
    br = json.loads(b.read_text())
    assert res["classification"] == "BUILD_ONLY_PASS"
    assert br["status"] == "PASS"
    assert br["vermagic"] == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    assert br["w1_warnings_or_errors"] == 0
    assert br["module_installed"] is False
    assert br["module_loaded"] is False
    assert br["camera_runtime"] is False
    mod = Path(br["module_path"])
    assert mod.is_file()
    assert sha(mod) == br["module_sha256"]
    assert mod.stat().st_size == br["module_bytes"]
    nm = subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(mod)], text=True)
    for sym in [
        "e008h_rear_alloc_prime_pair",
        "e008h_rear_bind_pair",
        "e008h_rear_enable_slot0",
        "e008h_rear_epoch0_retarget_slot1",
        "e008h_rear_observe_consumed",
        "e008h_rear_both_complete",
        "e008h_rear_prime_recipe",
    ]:
        assert sym in nm, sym

print("E008h VERIFY PASS")
