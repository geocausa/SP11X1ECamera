#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DLL=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DECOMP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-private/e008r-bfstats25-static/BF-DECOMPILE.txt")
DLL_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"

assert hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
t=DECOMP.read_text()

need=[
 "FUNCTION=FUN_180a1d340 ENTRY=180a1d340",
 "CamX::BFStats25::CheckDependenceChange",
 "uVar28 = param_1[0x1d8a] ^ 1;",
 "*(char *)(param_2[0x1e4] + 0xd558) = (char)param_1[0x1d8a];",
 "*(char *)(param_2[0x1e4] + 0xd559) = (char)param_1[0x1d8a];",
 "gammaLUTBank = %d, ROIIndexLUTBank = %d",
 "if (piVar37[0xb07] == 0)",
 "FUN_180a1f4f8(piVar15,param_2,local_200 + 0x328)",
 "FUN_180f5d480(piVar15,piVar37 + 0x4b3,0x1978)",
 "FUN_180a1f578(piVar15,param_2,param_1 + 0x259)",
 "FUNCTION=FUN_180b4fc20 ENTRY=180b4fc20",
 "CamX::IFEBFStats25Titan680::PopulateLUTConfig",
 "(uVar10 ^ (int)param_2[6] << 9) & 0x200 ^ uVar10",
 "if ((int)param_2[5] != 1) goto LAB_180b4ff7c;",
 "*(int *)((longlong)param_2 + 0x2c) == 1",
 "(uVar10 ^ *piVar9 << 0xd) & 0x2000 ^ uVar10",
 "if (*(int *)(lVar5 + 0xd4) == 1)",
 "*(uint *)(lVar13 + 8) = *(uint *)(lVar13 + 8) | 0x10000;",
 "if (*(int *)(lVar5 + 0x110) == 1)",
 "*(uint *)(lVar13 + 8) = *(uint *)(lVar13 + 8) | 0x20000;",
 "if (*(int *)(lVar5 + 0x2b0) == 1)",
 "*(uint *)(lVar13 + 8) = *(uint *)(lVar13 + 8) | 0x200000;",
 "uVar10 = *(uint *)(lVar5 + 0x14c);",
 "iVar11 = *(int *)(lVar5 + 0x2ec);",
 "FUN_180b4f860(param_1,lVar5 + 0x150,1);",
 "FUN_180b4f860(param_1,lVar5 + 0x2f0,3);",
]
for x in need:
    assert x in t, x

# Titan680 consumes the same request-state bank byte for both hardware bank
# registers in this exact build. CheckDependence also writes d558/d559 from
# one toggled state and logs them as ROI-index/gamma LUT banks.
assert t.count("0xd558) & 1") >= 2

safe={
 "schema":"E008R-bfstats25-request-state-source-lock-v1",
 "status":"PASS",
 "driver_sha256":DLL_SHA,
 "source_functions":{
   "check_dependence_change_rva":"0xa1d340",
   "default_roi_helper_rva":"0xa1f4f8",
   "validate_adjust_roi_helper_rva":"0xa1f578",
   "titan_populate_lut_config_rva":"0xb4fc20",
   "titan_filter_tail_helper_rva":"0xb4f860"
 },
 "bank_policy":{
   "normal_path_toggles_one_bank_state":True,
   "roi_index_and_gamma_request_banks_written_equal":True,
   "titan_hardware_bank_registers_consume_same_request_bank":True,
   "startup_phase_parity_contract_consistent_with_policy":True
 },
 "config_producers":{
   "gamma_enable_from_request_gamma_valid":True,
   "luma_conversion_from_request_input_config":True,
   "scale_enable_from_request_scale_config":True,
   "fir_enable_from_filter_offset_d4_valid":True,
   "iir_group_a_enable_from_filter_offset_110_valid":True,
   "iir_group_b_enable_from_filter_offset_2b0_valid":True
 },
 "filter_shift_producers":{
   "lower_signed4_from_filter_offset_14c":True,
   "upper_signed4_from_filter_offset_2ec":True,
   "tail_group_a_from_filter_offset_150":True,
   "tail_group_b_from_filter_offset_2f0":True,
   "numeric_shift_seed_closed":False
 },
 "roi_policy":{
   "af_roi_count_field_observed":True,
   "zero_roi_uses_single_default_helper":True,
   "nonzero_roi_copies_upstream_af_config":True,
   "nonzero_roi_copy_bytes":"0x1978",
   "validate_adjust_boundary_helper_applied":True,
   "accepted_25_roi_grid_generated_by_titan":False,
   "accepted_25_roi_grid_owned_upstream_of_bfstats25":True
 },
 "private_decompile_text_committed":False,
 "captured_windows_register_values_emitted":False,
 "captured_windows_dmi_bytes_emitted":False,
 "runtime_actions_performed":False
}
(HERE/"SAFE-SOURCE-LOCK.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print("E008R_PRIVATE_SOURCE_LOCK_PASS")
