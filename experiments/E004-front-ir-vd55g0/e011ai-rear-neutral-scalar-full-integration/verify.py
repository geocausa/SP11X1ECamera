#!/usr/bin/env python3
"""Verify committed scalar arithmetic/integration evidence and source/build locks."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
s=json.loads((D/"INTEGRATION-SAFE.json").read_text())
a=json.loads((D/"SCALAR-SAFE.json").read_text())
b=json.loads((D/"BUILD-SAFE.json").read_text())
r=json.loads((D/"RESULT.json").read_text())
assert s["status"]=="PASS_CLEAN_SCALAR_FULL_PROVIDER_PRIVATE_PARITY"
assert a["status"]=="PASS_NATIVE_SOURCE_SCALAR_DIFFERENTIAL"
assert s["clean_C_production_is_binding_authority"] and a["bind_inputs_from_clean_C_production_not_native_outputs"]
assert s["source_scalar_schedule"]==[0,1,2,2] and s["source_scalar_calculations"]==3
assert s["live_input_recovery"]==a["private_recovery"]
assert s["native_scalar_differential"]==a["compiler_runs"]
assert {x["compiler"] for x in a["compiler_runs"]}=={"gcc","clang"}
assert all(x["native_cases_exact"]==1038 and x["scalar_fields_exact"]==10380 for x in a["compiler_runs"])
assert {x["compiler"] for x in s["compiler_runs"]}=={"gcc","clang"}
for x in s["compiler_runs"]:
    assert x["status"]=="PASS" and x["assertions"]==509118
    assert (x["negative_cases"],x["af_negative_cases"],x["scalar_negative_cases"],x["scalar_producer_negative_cases"])==(32,61,69,69)
    assert x["register_writes"]==[714,705,504,345] and x["dmi_slots"]==[17,16,10,3]
    assert x["dmi_payload_bytes"]==36152 and not x["cold_bf_gamma_emitted"]
assert s["scalar_register_instances_exact"]==26
assert [x["exact_scalar_registers"] for x in s["scalar_phase_comparison"]]==[8,8,8,2]
assert s["remaining_mismatches_by_phase"]==[3,19,3,0] and s["remaining_semantic_register_mismatches"]==25
assert [x["host_fixture_other_register_mismatch_count"] for x in s["phase_comparison"]]==[3,19,3,0]
assert all(set(x["remaining_fixture_mismatch_families"])<={
    "AEC_BE_STATS17","AWB_BG_STATS17","RS_STATS14"} for x in s["phase_comparison"])
assert s["source_adaptive_payload_matches"]=={"lsc_selector_slots_exact":4,"gtm_slots_exact":4,"gic_alias_slots_exact":3}
for p in s["bf_phase_comparison"]:
    for x in p["bf_payloads"]:assert x["matching_bytes"]==x["payload_bytes"]
for lock in s["source_locks"]:
    assert hashlib.sha256((ROOT/lock["path"]).read_bytes()).hexdigest()==lock["sha256"]
for key in ("cold_request_input_independently_observed","scalar_hold_phase3_derived_from_event_order",
            "non_scalar_fields_and_tags_preserved","invalid_source_or_late_packet_preserves_all_bases"):assert s[key]
for key in ("optional_wb_normalization_supported","other_bayer_policies_supported","floating_point_in_kernel",
            "complete_source_produced_e008o_composition_closed","vfe1_wm16_retirement_closed",
            "native_rear_linux_runtime_allowed","runtime_actions_performed","private_values_or_generated_packet_bytes_exported"):assert not s[key]
assert b["status"]=="PASS_ISOLATED_ARM64_W1_BUILD" and b["warnings"]==0
assert b["module_bytes"]==14758008 and b["module_sha256"]=="be35b2da4905b63549a4fef65f89f0299f46f4bc79404c7a720a278648113c5b"
assert hashlib.sha256((D/"camss-e011ai-startup-scalar-bind.inc").read_bytes()).hexdigest()==b["scalar_binder_source_sha256"]
for key in ("user_space_float_producer_in_kernel","installed","loaded","hardware_actions","native_rear_runtime_allowed"):assert not b[key]
assert r["isolated_arm64_build"]==b and not r["first_frame_source_gates_reopened"]
assert all(r[k]==v for k,v in s.items())
print("E011AI_CLEAN_NEUTRAL_SCALAR_FULL_INTEGRATION_SOURCE_BUILD_LOCK_PASS")
print("scalar_registers=26/26; remaining_statistics_differences=25; complete_bootstrap=OPEN; WM16=OPEN; native_rear_runtime=DENIED")
