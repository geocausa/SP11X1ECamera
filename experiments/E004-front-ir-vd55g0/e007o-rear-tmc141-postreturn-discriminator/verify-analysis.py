#!/usr/bin/env python3
from pathlib import Path
import json, py_compile

D=Path(__file__).resolve().parent
prep=(D/"verify.py").read_text()
safe=json.load(open(D/"PRIVATE-VALIDATION-SAFE.json"))
res=json.load(open(D/"RESULT.json"))

assert safe["status"] == "PASS_POSTRETURN_DISCRIMINATOR"
assert safe["capture_complete"] is True
assert safe["calls_analyzed"] == 20
assert safe["changed_hits"] == [1,4,6,7,8,9]
assert safe["meaningful_settling_hits"] == [4,6,7,8,9]
assert safe["settling_src_changed_indices"] == [1,2]
assert safe["settling_dst_changed_indices"] == [1,2]
assert safe["post_triplets_matching_accepted_e007j_state"] == 18
assert safe["downstream_publication_rewrite_required"] is False
assert safe["missing_logic_location"] == "inside_CalculateAnchorKneePoints"
assert safe["rear_mode_specific_src_post_generator_branch"]["mode"] == "0x60800"
assert safe["rear_mode_specific_src_post_generator_branch"]["control_byte"] == "0x8244"
assert safe["rear_mode_specific_src_post_generator_branch"]["affected_src_indices"] == [1,2]
assert safe["rear_mode_specific_src_post_generator_branch"]["affected_dst_indices"] == []
assert safe["e007k_coefficient_port_revalidation"]["exact_requests"] == 12
assert safe["e007k_coefficient_port_revalidation"]["total_requests"] == 15
assert safe["e007k_coefficient_port_revalidation"]["mismatch_requests"] == [4,7,8]
assert safe["raw_capture_values_emitted"] is False

assert res["classification"] == "WINDOWS_ORACLE_OFFLINE_ANALYSIS_PASS"
assert res["downstream_publication_rewrite_required"] is False
assert res["missing_logic_location"] == "TMC141Interpolation::CalculateAnchorKneePoints"
assert res["mode_specific_src_post_generator_indices"] == [1,2]
assert res["mode_specific_dst_post_generator_indices"] == []
assert res["family2_publication_blend_weights_zero"] is True
assert res["raw_windows_values_committed"] is False
assert res["linux_camera_runtime"] is False

py_compile.compile(str(D/"analyze-private.py"),doraise=True)
print("E007O_ANALYSIS_VERIFY_PASS calls=20 post_matches=18 settling_indices=1,2")
print("downstream_rewrite=false missing_logic=CalculateAnchorKneePoints")
