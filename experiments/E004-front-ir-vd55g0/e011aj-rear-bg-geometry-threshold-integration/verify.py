#!/usr/bin/env python3
"""Check committed BG integration aggregates and source/build locks."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
s=json.loads((D/"INTEGRATION-SAFE.json").read_text())
a=json.loads((D/"BG-SAFE.json").read_text())
b=json.loads((D/"BUILD-SAFE.json").read_text())
r=json.loads((D/"RESULT.json").read_text())
assert s["status"]=="PASS_BG_GEOMETRY_THRESHOLD_FULL_PROVIDER_PRIVATE_PARITY"
assert a["status"]=="PASS_ORIGINAL_BG_GEOMETRY_THRESHOLD_DIFFERENTIAL"
assert a["bound_clean_C_outputs"] and not a["input_authority_is_retained_registers"]
assert s["native_geometry_differential"]==a["compiler_runs"]
assert {x["compiler"] for x in a["compiler_runs"]}=={"gcc","clang"}
assert all(x["original_cases_exact"]==2056 and x["original_fields_exact"]==20560 for x in a["compiler_runs"])
assert {x["compiler"] for x in s["compiler_runs"]}=={"gcc","clang"}
for x in s["compiler_runs"]:
    assert x["status"]=="PASS" and x["assertions"]==509427
    assert (x["negative_cases"],x["af_negative_cases"],x["scalar_negative_cases"],
        x["scalar_producer_negative_cases"],x["bg_negative_cases"],x["bg_producer_negative_cases"])==(32,61,69,69,90,14)
    assert x["register_writes"]==[714,705,504,345] and x["dmi_slots"]==[17,16,10,3]
    assert x["dmi_payload_bytes"]==36152 and not x["cold_bf_gamma_emitted"]
assert s["source_schedule"]==[0,1,1,1]
assert s["bg_geometry_threshold_register_instances_exact"]==36
assert [x["geometry_threshold_registers_exact"] for x in s["bg_phase_comparison"]]==[18,18,0,0]
assert [x["exact_scalar_registers"] for x in s["scalar_phase_comparison"]]==[8,8,8,2]
assert s["remaining_mismatches_by_phase"]==[3,5,3,0] and s["remaining_semantic_register_mismatches"]==11
assert [x["host_fixture_other_register_mismatch_count"] for x in s["phase_comparison"]]==[3,5,3,0]
assert [x["remaining_fixture_mismatch_families"] for x in s["phase_comparison"]]==[
    {"AEC_BE_STATS17":1,"AWB_BG_STATS17":1,"RS_STATS14":1},
    {"AEC_BE_STATS17":1,"AWB_BG_STATS17":1,"RS_STATS14":3},{"RS_STATS14":3},{}]
assert s["source_adaptive_payload_matches"]=={"lsc_selector_slots_exact":4,"gtm_slots_exact":4,"gic_alias_slots_exact":3}
for p in s["bf_phase_comparison"]:
    for x in p["bf_payloads"]:assert x["matching_bytes"]==x["payload_bytes"]
for lock in s["source_locks"]:
    assert hashlib.sha256((ROOT/lock["path"]).read_bytes()).hexdigest()==lock["sha256"]
assert s["other_fields_and_caller_tags_preserved"] and s["atomic_rejection_preserves_all_bases"]
for key in ("complete_source_produced_e008o_composition_closed","vfe1_wm16_retirement_closed",
            "native_rear_linux_runtime_allowed","runtime_actions_performed","private_values_or_generated_packet_bytes_exported"):
    assert not s[key]
assert b["status"]=="PASS_ISOLATED_ARM64_W1_BUILD" and b["warnings"]==0
assert b["module_bytes"]==14765856 and b["module_sha256"]=="a763e03440cf2fce81a89e338b90867cd3df5fbea4129492e8d8535e049bab71"
assert hashlib.sha256((D/"camss-e011aj-startup-bg-bind.inc").read_bytes()).hexdigest()==b["bg_binder_source_sha256"]
for key in ("user_space_float_producer_in_kernel","installed","loaded","hardware_actions","native_rear_runtime_allowed"):assert not b[key]
assert r["isolated_arm64_build"]==b
assert all(r[k]==v for k,v in s.items())
print("E011AJ_BG_GEOMETRY_THRESHOLD_FULL_INTEGRATION_SOURCE_BUILD_LOCK_PASS")
print("BG_geometry_threshold=36/36; remaining_statistics_differences=11; complete_bootstrap=OPEN; WM16=OPEN; native_rear_runtime=DENIED")
