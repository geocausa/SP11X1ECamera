#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json, py_compile

D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e007k_coeff",D/"tmc141-coeff.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

# Structural source-lock.
assert len(m.tmc141_coeff([0,1,2,3,4,5,6],[0,1,2,3,4,5,6])) == 15
assert len(m.pack_coeff([0,1,2,3,4,5,6],[0,1,2,3,4,5,6])) == 60

r=json.load(open(D/"RESULT.json"))
assert r["coefficient_helper_address"] == "0x1809276e8"
assert r["anchor_solver_address"] == "0x1809255f0"
assert r["request_state_assembler_address"] == "0x180923b90"
assert r["gtm_family"] == 2
assert r["gtm_src_offset"] == "0x5104"
assert r["gtm_dst_offset"] == "0x5120"
assert r["gtm_coef_offset"] == "0x51b0"
assert r["gtm_domain_offset"] == "0x6228"
assert r["private_coefficient_exact_requests"] == 12
assert r["private_coefficient_total_requests"] == 15
assert r["private_coefficient_mismatch_requests"] == [4,7,8]
assert r["private_coefficient_mismatch_indices"] == [8]
assert r["coefficient_clean_port_bit_exact_complete"] is False
assert r["coefficient_independent_dynamic_state"] is False
assert r["coefficient_structurally_derived_from_src_dst"] is True
assert r["raw_windows_values_committed"] is False
py_compile.compile(str(D/"tmc141-coeff.py"),doraise=True)
print("E007K_VERIFY_PASS family=2 coef=structurally-derived clean_port_exact=12/15")
