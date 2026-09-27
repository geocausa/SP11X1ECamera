#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
subprocess.run(["python3",str(D/"derive-authority.py")],check=True)
a=json.loads((D/"AUTHORITY-SAFE.json").read_text())
r=json.loads((D/"RESULT.json").read_text())
assert a["status"]=="PASS_PARTIAL_CLEAN_BF_AUTHORITY"
assert a["gamma"]["private_exact_matches"]==4
assert a["filter"]["private_exact_matches"]==34
assert a["filter"]["private_register_records_checked"]==35
assert a["coring"]["private_exact_matches"]==34
assert a["filter"]["startup_packet0_is_distinct"]
assert a["scope"]["does_not_close_25_roi_generator"]
assert not a["private_windows_register_values_emitted"]
assert not a["private_windows_dmi_bytes_emitted"]
assert not a["runtime_actions_performed"]
assert r["classification"]=="STATIC_AUTHORITY_PASS_PARTIAL_BF_BOOTSTRAP"
assert not r["native_rear_runtime_authorized"]
print("E008q VERIFY PASS")
