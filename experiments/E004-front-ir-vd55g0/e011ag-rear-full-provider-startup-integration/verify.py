#!/usr/bin/env python3
"""Check E011AG committed evidence without exporting private authority."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
R=D.parents[2]
s=json.loads((D/"INTEGRATION-SAFE.json").read_text())
b=json.loads((D/"BUILD-SAFE.json").read_text())
r=json.loads((D/"RESULT.json").read_text())
assert s["status"]=="PASS_FULL_REAL_PROVIDER_OFFLINE_INTEGRATION"
assert s["real_provider_include_count"]==34
assert s["full_recursive_e008o_validation_exercised"]
assert s["actual_e008l_layout_and_e007y_materializer_exercised"]
assert {x["compiler"] for x in s["compiler_runs"]}=={"gcc","clang"}
for run in s["compiler_runs"]:
    assert run["status"]=="PASS" and run["assertions"]==1872 and run["negative_cases"]==32
    assert run["register_writes"]==[714,705,504,345] and run["dmi_slots"]==[17,16,10,3]
    assert run["dmi_payload_bytes"]==36152 and not run["cold_bf_gamma_emitted"]
for provider in s["providers"]:
    assert hashlib.sha256((R/provider["path"]).read_bytes()).hexdigest()==provider["sha256"]
assert s["bpc_schedule"]==[0,1,2,2] and s["bpc_captured_startup_word_matches"]==21
assert s["source_adaptive_payload_matches"]=={"lsc_selector_slots_exact":4,"gtm_slots_exact":4,"gic_alias_slots_exact":3}
assert [x["host_fixture_other_register_mismatch_count"] for x in s["phase_comparison"]]==[11,27,11,2]
assert all(x["dmi_shape_exact"] for x in s["phase_comparison"])
assert s["period_comparison_uses_source_semantic_mask_0x1f"]
assert not s["complete_source_produced_e008o_composition_closed"]
assert not s["vfe1_wm16_retirement_closed"] and not s["native_rear_linux_runtime_allowed"]
assert not s["runtime_actions_performed"] and not s["private_values_or_generated_packet_bytes_exported"]
assert b["status"]=="PASS_ISOLATED_ARM64_W1_BUILD" and b["warnings"]==0
assert not b["installed"] and not b["loaded"] and not b["hardware_actions"]
assert hashlib.sha256((D/"camss-e011ag-startup-compose.inc").read_bytes()).hexdigest()==b["composer_source_sha256"]
assert r["status"]==s["status"] and r["isolated_arm64_build"]==b
assert not r["first_frame_source_gates_reopened"]
print("E011AG_FULL_REAL_PROVIDER_INTEGRATION_SOURCE_BUILD_LOCK_PASS")
print("complete_source_bootstrap=OPEN; hardware_retirement=OPEN; native_rear_runtime=DENIED")
