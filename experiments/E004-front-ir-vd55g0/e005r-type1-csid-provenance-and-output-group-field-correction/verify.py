#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OEM = ROOT / "experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys"
SHA = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"

def req(v, msg):
    if not v: raise AssertionError("E005R_FAIL_CLOSED " + msg)

def main():
    req(OEM.is_file(), "OEM missing")
    req(hashlib.sha256(OEM.read_bytes()).hexdigest() == SHA, "OEM SHA")
    dis = subprocess.check_output(["llvm-objdump","-d","--no-show-raw-insn",str(OEM)], text=True, errors="replace")
    data = OEM.read_bytes()

    ph = json.loads((ROOT / "experiments/E004-front-ir-vd55g0/e004ph-original-type1-preparation-queue-status-provenance-static/RESULT.json").read_text())
    req(ph["original_type_one_B_preparation_input_is_separate_from_IFE_snapshot_A_wrapper"] is True, "queue separation")
    req(ph["old_direct_IFE_snapshot_TOP_status1_plus0x8_as_type1_BF_source_valid"] is False, "TOP1 superseded")
    req(ph["original_zero_mode_CSID_BUF_DONE_status_bit7_to_type1_BF0x0f_static_proven"] is True, "CSID BF provenance")
    req(ph["original_type_one_B_modezero_raw_register_window_word_offset"] == "0x8c", "CSID status offset")

    for pat in (
        r"140027fb0:.*mov\s+w24, #0x300d",
        r"140027fc4:.*ldr\s+w8, \[x10, #0x8\]",
        r"140027ff0:.*ldp\s+w9, w8, \[x10, #0x14\]",
        r"140027ffc:.*ldp\s+w4, w3, \[x10, #0x14\]",
    ):
        req(re.search(pat, dis) is not None, "WM update anchor " + pat)
    req(b"Write Master Update for PortId = %d: W = %d, H = %d" in data, "WM W/H diagnostic")
    req(b"Composite Group id of the group         = %d" in data, "composite diagnostic")

    for pat in (
        r"140016d9c:.*ldr\s+w2, \[x21, #0x8b0\]",
        r"140016dc0:.*ldr\s+w2, \[x21, #0x8b8\]",
        r"140016dd4:.*ldr\s+w2, \[x21, #0x8bc\]",
        r"140016de8:.*ldr\s+w2, \[x21, #0x8c0\]",
        r"140016dfc:.*ldr\s+w2, \[x21, #0x8c4\]",
    ):
        req(re.search(pat, dis) is not None, "output config anchor " + pat)

    q = json.loads((ROOT / "experiments/E004-front-ir-vd55g0/e005q-windows-live-oem-tophalf-bf-wm16-correlation/RESULT.json").read_text())
    req(q["run_consumed_no_retry"] is True, "E005q consumed")
    req(q["capture"]["launcher_acceptance_passed"] is False, "partial capture stays partial")
    req(q["live_scalar_counts"]["bf_event"] == 35, "BF count")
    req(q["live_scalar_counts"]["fifo8_nonnull"] == 35, "FIFO count")
    req(q["live_scalar_counts"]["matcher_nonnull"] == 35, "matcher count")
    req(q["live_scalar_counts"]["fifo_and_matcher_key_sequences_identical"] is True, "opaque key equality")
    req(q["live_scalar_counts"]["wm16_addr_status0_unique_values"] == 10, "WM16 live movement")
    req(q["live_scalar_counts"]["paired_wm16_samples_changed"] == 2, "asynchronous movement retained")
    req(q["live_scalar_counts"]["resource_0x300d_write_master_width"] == 25, "300d width")
    req(q["live_scalar_counts"]["resource_0x300d_write_master_height"] == 4, "300d height")
    req(q["not_proven"]["resource_0x300d_write_master_height_4_is_composite_group"] is True, "do not relabel height")

    d = json.loads((HERE / "RESULT.json").read_text())
    req(d["correction"]["e005p_top1_as_actual_type1_bf_source_superseded"] is True, "E005p correction")
    req(d["resource_0x300d"]["height_4_is_composite_group"] is False, "height != group")
    req(d["output_resource_config"]["composite_group_field_relative_to_container"] == "0x8c0", "group field")
    req(d["output_resource_config"]["live_resource_0x300d_composite_group_captured"] is False, "live group unknown")
    for v in d["not_proven"].values(): req(v is True, "unproven predicate")
    req(d["native_rear_hardware_isp_runtime_authorized"] is False, "rear denied")
    print("PASS_E005R_CSID_TYPE1_BF_PROVENANCE_RESTORED_300D_WH_NOT_GROUP_EXACT_GROUP_FIELD_SOURCE_LOCK_REAR_DENIED")

if __name__ == "__main__":
    main()
