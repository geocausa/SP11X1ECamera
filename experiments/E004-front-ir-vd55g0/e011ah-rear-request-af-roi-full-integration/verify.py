#!/usr/bin/env python3
"""Check the committed AF integration/build evidence and source locks."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
s=json.loads((D/"INTEGRATION-SAFE.json").read_text())
b=json.loads((D/"BUILD-SAFE.json").read_text())
r=json.loads((D/"RESULT.json").read_text())
assert s["status"]=="PASS_REQUEST_AF_ROI_FULL_PROVIDER_INTEGRATION"
assert {x["compiler"] for x in s["compiler_runs"]}=={"gcc","clang"}
for run in s["compiler_runs"]:
    assert run["status"]=="PASS" and run["assertions"]==508760
    assert run["negative_cases"]==32 and run["af_negative_cases"]==61
    assert run["af_axis_checks"]==16385 and run["af_map_checks"]==18157
    assert run["register_writes"]==[714,705,504,345] and run["dmi_slots"]==[17,16,10,3]
    assert run["dmi_payload_bytes"]==36152 and not run["cold_bf_gamma_emitted"]
for phase in s["bf_phase_comparison"]:
    payloads=phase["bf_payloads"]
    assert [x["selector"] for x in payloads]==([1] if phase["phase"]==0 else [1,2])
    assert payloads[0]["matching_bytes"]==payloads[0]["payload_bytes"]==300
    assert all(v==25 for v in payloads[0]["matching_fields"].values())
    if phase["phase"]:assert payloads[1]["matching_bytes"]==payloads[1]["payload_bytes"]==128
assert (s["bf_roi_slots_exact"],s["bf_roi_matching_bytes"])==(4,1200)
assert (s["bf_gamma_slots_exact"],s["bf_gamma_matching_bytes"])==(3,384)
assert s["neutral_control_phase1_roi_matching_bytes"]==250
assert s["source_adaptive_payload_matches"]=={"lsc_selector_slots_exact":4,"gtm_slots_exact":4,"gic_alias_slots_exact":3}
assert [p["host_fixture_other_register_mismatch_count"] for p in s["phase_comparison"]]==[11,27,11,2]
assert [p["bpc_present_words_exact"] for p in s["phase_comparison"]]==[7,7,7,0]
assert all(p["dmi_shape_exact"] for p in s["phase_comparison"])
for lock in s["source_locks"]:
    assert hashlib.sha256((ROOT/lock["path"]).read_bytes()).hexdigest()==lock["sha256"]
for key in ("binder_rejects_before_mutation","normal_roi_ids_flags_and_all_other_fields_preserved",
            "cold_packet_preserved_byte_for_byte","full_recursive_e008o_validation_exercised",
            "actual_e008l_layout_and_e007y_materializer_exercised"):assert s[key]
for key in ("first_normal_zoom_upstream_calculation_source_closed","live_af_to_rtcdm_packet_identity_directly_tagged",
            "complete_source_produced_e008o_composition_closed","vfe1_wm16_retirement_closed",
            "native_rear_linux_runtime_allowed","runtime_actions_performed",
            "private_values_or_generated_packet_bytes_exported"):assert not s[key]
assert b["status"]=="PASS_ISOLATED_ARM64_W1_BUILD" and b["warnings"]==0
assert b["module_bytes"]==14749232
assert b["module_sha256"]=="9f1de3bb49cbc47b8a8a8b52e8d8a59c97ea511781cd98107e0006aaa6ccf760"
assert hashlib.sha256((D/"camss-e011ah-request-af-roi.inc").read_bytes()).hexdigest()==b["af_roi_source_sha256"]
for key in ("installed","loaded","hardware_actions","native_rear_runtime_allowed"):assert not b[key]
assert r["isolated_arm64_build"]==b and not r["first_frame_source_gates_reopened"]
assert all(r[k]==v for k,v in s.items())
print("E011AH_REQUEST_AF_ROI_FULL_INTEGRATION_SOURCE_BUILD_LOCK_PASS")
print("BF_payload_replay=EXACT; complete_source_bootstrap=OPEN; WM16_retirement=OPEN; native_rear_runtime=DENIED")
