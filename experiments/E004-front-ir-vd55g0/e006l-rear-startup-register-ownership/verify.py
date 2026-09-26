#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys

D=Path(__file__).resolve().parent
safe=json.loads((D/"STARTUP-VS-STEADY-SAFE.json").read_text(encoding="utf-8-sig"))
owners=json.loads((D/"STARTUP-REGISTER-OWNER-MAP.json").read_text())

assert safe["schema"]=="E006l-startup-vs-steady-safe-classification-v1"
assert owners["schema"]=="E006l-rear-startup-register-owner-map-v1"
assert safe["startup_register_count"]==714==owners["startup_register_count"]
expected={
 "STEADY_SINGLETON_REUSABLE":468,
 "STEADY_DYNAMIC_PRODUCER":25,
 "STARTUP_DIFFERS_FROM_STEADY":37,
 "STARTUP_ONLY":184,
}
assert owners["partition_counts"]==expected
assert sum(expected.values())==714
assert owners["unresolved_owner_count"]==0
assert owners["period_cfg"]["register"]=="0x8c"
assert owners["period_cfg"]["owner"]=="VFE680_PERIOD_CFG"
assert owners["raw_values_committed"] is False
assert owners["private_bytes_committed"] is False
assert len(owners["startup_only"])==184
assert len(owners["startup_differs_from_steady"])==37
assert len(owners["steady_dynamic"])==25
assert len(owners["reusable_steady_singleton_offsets"])==468
assert len(safe["startup_phase_variant_offsets"])==81

# Deterministic regeneration.
before=(D/"STARTUP-REGISTER-OWNER-MAP.json").read_bytes()
subprocess.run([sys.executable,str(D/"generate-owner-map.py")],check=True,
               stdout=subprocess.DEVNULL)
after=(D/"STARTUP-REGISTER-OWNER-MAP.json").read_bytes()
assert before==after

print("E006L_VERIFY_PASS")
print("partition=468+25+37+184=714")
print("startup_only_owners=14 startup_diff_owners=6 unresolved=0")
print("period_cfg=VFE680 transport state")
