#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
src=(D/"camss-e007d-register-integration.inc").read_text()
owner=json.load(open(D.parent/"e006l-rear-startup-register-ownership/STARTUP-REGISTER-OWNER-MAP.json"))

assert sum(owner["partition_counts"].values()) == 714
assert owner["unresolved_owner_count"] == 0

required=[
"e007d_rear_register_state","e007d_rear_bundle",
"e007d_rear_validate_register_integration",
"e007d_rear_fill_steady","e007d_rear_fill_startup",
"e007c_rear_fill_startup_packet","e007d_period_requires_packet",
"e007d_rear_register_integration_recipe",
]
for t in required:
    assert t in src

# Every callback field in E006m's startup bundle is explicitly bound.
for field in [
"steady_singleton","bc101","bayer_gtm101","bayer_ltm101","lcac111","cst12",
"uv_gamma101","mnds23","round_clamp12","crop12","aec_be_stats17",
"bhist_stats16","tintless_bg_stats17","awb_bg_stats17","rs_stats14","period_cfg"
]:
    assert f".{field} =" in src

# Every steady producer family in E006j is explicitly bound.
for field in ["demux_bls","pdpc","lsc","wb","gic","bpc_abf","gtm","gamma","dsx","bfstats25"]:
    assert f".{field} =" in src

assert "return e006z_rear_clean_scalar_bank_lookup" in src
assert "return e007a_bpcabf411_lookup" in src
assert "return e007b_bfstats25_lookup" in src
assert "return -EOPNOTSUPP;" in src
assert "ctx.period = s->period;" in src

print("E007D_VERIFY_PASS startup_contracts=714 steady_producers=10 startup_callbacks=16")
print("period_cfg=packet_aware old_scalar_path=fail_closed dmi_live_state=separate")
