#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

D = Path(__file__).resolve().parent

subprocess.run(["python3", str(D / "derive-source-lock.py")], check=True)
subprocess.run(["python3", str(D / "audit-private.py")], check=True)

source = json.loads((D / "SOURCE-DERIVATION-SAFE.json").read_text())
private = json.loads((D / "PRIVATE-VALIDATION-SAFE.json").read_text())
lock = json.loads((D / "SAFE-SOURCE-LOCK.json").read_text())
result = json.loads((D / "RESULT.json").read_text())

assert source["status"] == "PASS"
assert source["normal_all_mode_shift_pair"] == [3, 3]
assert source["haf_grid_count"] == [5, 5]
assert source["normal_gamma_enabled"]
assert not source["normal_scale_enabled"]
assert not source["normal_fir_enabled"]
assert source["normal_iir_enabled"]
assert not source["captured_windows_values_read"]
assert not source["runtime_actions_performed"]

assert private["status"] == "PASS"
assert private["packet0_hardcode_filter_exact_matches"] == 1
assert private["packet0_hardcode_shift_exact_matches"] == 1
assert private["packet0_hardcode_coring_exact_matches"] == 1
assert private["normal_shift_exact_matches"] == 34
assert private["roi_selector1_payloads_checked"] == 5
assert private["roi_selector1_all_300_bytes"]
assert private["gamma_phase_matches_source_policy"]
assert not private["captured_windows_register_values_emitted"]
assert not private["captured_windows_dmi_bytes_emitted"]

assert lock["status"] == "PASS_AF_BF_BOOTSTRAP_SOURCE_CLOSURE"
assert lock["packet0"]["iir_shifts"] == [-3, 0]
assert lock["normal_packet1_plus"]["iir_shifts"] == [3, 3]
assert lock["packet0"]["roi_count"] == 25
assert lock["normal_packet1_plus"]["roi_count"] == 25
assert not lock["scope"]["native_runtime_authorized"]

assert result["classification"] == "STATIC_AF_BAF_BOOTSTRAP_SOURCE_CLOSURE_PASS"
assert result["packet0_filter_seed_source_closed"]
assert result["packet0_coring_seed_source_closed"]
assert result["numeric_iir_shift_seed_closed"]
assert result["accepted_25_roi_semantic_seed_closed"]
assert result["per_packet_af_validity_seed_closed"]
assert not result["captured_windows_register_values_embedded"]
assert not result["captured_windows_dmi_bytes_embedded"]
assert not result["private_decompilation_embedded"]
assert not result["runtime_actions_performed"]
assert not result["native_rear_runtime_authorized"]

print("E008s VERIFY PASS")
