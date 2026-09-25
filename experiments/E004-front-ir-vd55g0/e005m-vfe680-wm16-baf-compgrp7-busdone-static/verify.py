#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
Q = Path("/home/geoca/.cache/qualcomm-camera-driver")
QHDR = Q / "camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h"
QBUS = Q / "camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c"
K = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src")
KVFE = K / "drivers/media/platform/qcom/camss/camss-vfe-680.c"

Q_COMMIT = "82ac3a671a5b0a4e3b3ac4519208af1d37a93eb6"
QHDR_SHA = "a31f6fe84cbd2b544fe504e9099ea6adc6bbe846628999742d9fb6024add2505"
QBUS_SHA = "dbe53691b46f912d59a5848a7c3e039601088430fd2e3efc992d9100dcc36b44"
KVFE_SHA = "99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208"

def req(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError("E005M_FAIL_CLOSED " + msg)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def has(text: str, pattern: str, msg: str) -> None:
    req(re.search(pattern, text, re.S) is not None, msg)

def main() -> None:
    req(subprocess.check_output(["git", "-C", str(Q), "rev-parse", "HEAD"], text=True).strip() == Q_COMMIT,
        "Qualcomm source revision")
    req(sha(QHDR) == QHDR_SHA, "VFE680 header hash")
    req(sha(QBUS) == QBUS_SHA, "VFE bus v3 hash")
    req(sha(KVFE) == KVFE_SHA, "accepted SP11 VFE680 hash")

    h = QHDR.read_text()
    b = QBUS.read_text()
    k = KVFE.read_text()

    # Exact VFE680 BUS IRQ map.
    for needle in (
        ".mask_reg_offset   = 0x00000C18",
        ".clear_reg_offset  = 0x00000C20",
        ".status_reg_offset = 0x00000C28",
        ".mask_reg_offset   = 0x00000C1C",
        ".clear_reg_offset  = 0x00000C24",
        ".status_reg_offset = 0x00000C2C",
        ".global_irq_cmd_offset    = 0x00000C30",
        ".global_clear_bitmask     = 0x00000001",
        ".support_consumed_addr = true",
    ):
        req(needle in h, "missing VFE680 register contract: " + needle)

    # Client 16 must be STATS_BAF in both descriptor and register table,
    # and must map to comp group 7 with exact WM16 offsets.
    has(h, r'\.wm_id\s*=\s*16,\s*\.desc\s*=\s*"STATS_BAF"', "WM16 STATS_BAF descriptor")
    has(h, r"/\* BUS Client 16 STATS BAF \*/.*?\.cfg\s*=\s*0x00001E00.*?"
           r"\.addr_status_0\s*=\s*0x00001E70.*?"
           r"\.comp_group\s*=\s*CAM_VFE_BUS_VER3_COMP_GRP_7",
        "WM16 register/comp-group block")

    # VFE680 defines one comp-done bit per group; group 7 therefore BIT(7).
    has(h, r"\.num_comp_grp\s*=\s*17.*?\.comp_done_mask\s*=\s*\{.*?"
           r"BIT\(0\).*?BIT\(1\).*?BIT\(2\).*?BIT\(3\).*?"
           r"BIT\(4\).*?BIT\(5\).*?BIT\(6\).*?BIT\(7\)",
        "comp group 7 BIT(7)")

    # C3C/C40 are frame-header configuration entries in the exact VFE680
    # common map, while C20/C24 above are the IRQ clears.
    has(h, r"\.if_frameheader_cfg\s*=\s*\{\s*0x00000C34,\s*0x00000C38,\s*"
           r"0x00000C3C,\s*0x00000C40,\s*0x00000C44", "C3C/C40 frameheader semantics")

    # Hardware completion must test the comp-done mask before reading the
    # selected WM's consumed-address register.
    has(b, r"status_0\s*=.*?CAM_IFE_IRQ_BUS_VER3_REG_STATUS0.*?"
           r"if \(status_0 & resource_data->comp_done_mask\).*?"
           r"last_consumed_addr\s*=\s*cam_io_r_mb\(.*?"
           r"wm_rsrc_data->hw_regs->addr_status_0",
        "top-half comp-done -> consumed-address contract")
    for needle in (
        "bufdone_evt_info.res_id = vfe_out->res_id",
        "bufdone_evt_info.comp_grp_id = comp_grp_id",
        "bufdone_evt_info.last_consumed_addr = evt_payload->last_consumed_addr",
        "CAM_ISP_HW_EVENT_DONE",
    ):
        req(needle in b, "bottom-half event field: " + needle)

    # Accepted SP11 source still cannot supply this witness.
    has(k, r"static irqreturn_t vfe_isr\(int irq, void \*dev\)\s*\{\s*return IRQ_HANDLED;\s*\}",
        "accepted ISR remains no-op")
    for needle in (
        "#define VFE_BUS_IRQn_MASK(vfe, n)",
        "#define VFE_BUS_IRQn_CLEAR(vfe, n)",
        "#define VFE_BUS_IRQn_STATUS(vfe, n)",
        "#define VFE_BUS_IRQ_GLOBAL_CLEAR(vfe)",
    ):
        req(needle in k, "accepted SP11 VFE680 canonical BUS register macro " + needle)

    # Cross-check earlier project evidence but do not promote it.
    nv = json.loads((ROOT / "experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/BF-RESULT.json").read_text())
    req(nv["BF_static_dispatch"]["BF_group_client_resource_port"] == "0x300d", "Windows BF resource port")
    req(nv["BF_static_dispatch"]["queue_group_index"] == 8, "Windows BF FIFO group8")
    req(nv["BF_event_live_during_OEM_rear_recording_observed"] is False, "Windows BF remains not live-proven")

    pi = json.loads((ROOT / "experiments/E004-front-ir-vd55g0/e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline/RESULT.json").read_text())
    req(pi["accepted_native_VFE680_ISR_implements_WM16_BUS_IRQ_retirement"] is False,
        "parent native completion remains absent")
    req(pi["native_rear_VFE1_WM16_generation_matched_DMA_IOMMU_safe_retirement_proven"] is False,
        "parent no retirement")

    l = json.loads((ROOT / "experiments/E004-front-ir-vd55g0/e005l-original-group3-stat-aggregate-key-tag-export-static/RESULT.json").read_text())
    req(l["same_frame_fifo8_nonnull_wm16_match_proven"] is False, "E005l no same-frame FIFO8/WM16 match")
    req(l["native_rear_hardware_isp_runtime_authorized"] is False, "E005l rear denied")

    saved = json.loads((HERE / "RESULT.json").read_text())
    req(saved["vfe680_wm_id"] == 16 and saved["vfe680_wm_comp_group"] == 7, "saved WM/comp-group")
    req(saved["vfe680_comp_group7_done_mask"] == "BIT(7)", "saved done mask")
    req(saved["qualcomm_c3c_c40_are_if_frameheader_cfg_entries"] is True, "saved C3C/C40 semantics")
    req(saved["c3c_c40_are_canonical_vfe680_bus_irq_clear_offsets"] is False, "no false clear mapping")
    req(saved["linux_live_vfe1_bus_status0_bit7_observed_for_rear"] is False, "no live promotion")
    req(saved["linux_native_wm16_dma_iommu_safe_retirement_proven"] is False, "no DMA promotion")
    req(saved["native_rear_hardware_isp_runtime_authorized"] is False, "rear runtime denied")

    print("PASS_E005M_VFE680_WM16_STATS_BAF_COMPGRP7_BIT7_CONSUMED_ADDR_CONTRACT_STATIC_ONLY_REAR_DENIED")

if __name__ == "__main__":
    main()
