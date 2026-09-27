#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

D=Path(__file__).resolve().parent
DLL=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"

assert hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
a=json.loads((D/"SAFE-SOURCE-LOCK.json").read_text())
r=json.loads((D/"RESULT.json").read_text())
assert a["status"]=="PASS"
assert a["bank_policy"]["normal_path_toggles_one_bank_state"]
assert a["bank_policy"]["roi_index_and_gamma_request_banks_written_equal"]
assert a["bank_policy"]["titan_hardware_bank_registers_consume_same_request_bank"]
assert all(a["config_producers"].values())
assert a["filter_shift_producers"]["lower_signed4_from_filter_offset_14c"]
assert a["filter_shift_producers"]["upper_signed4_from_filter_offset_2ec"]
assert not a["filter_shift_producers"]["numeric_shift_seed_closed"]
assert a["roi_policy"]["nonzero_roi_copies_upstream_af_config"]
assert a["roi_policy"]["accepted_25_roi_grid_owned_upstream_of_bfstats25"]
assert not a["roi_policy"]["accepted_25_roi_grid_generated_by_titan"]
assert not a["private_decompile_text_committed"]
assert not a["runtime_actions_performed"]
assert r["classification"]=="STATIC_SOURCE_CLOSURE_PASS"
assert not r["native_rear_runtime_authorized"]
print("E008r VERIFY PASS")
