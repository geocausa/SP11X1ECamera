#!/usr/bin/env python3
"""Private same-SP11 aggregate check. Never emit captured DMI bytes/hashes."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
parent = here.parent / "e008u-rear-bf-roi-geometry-audit"
spec = importlib.util.spec_from_file_location("e008u_audit", parent / "audit-private.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

with tempfile.TemporaryDirectory(prefix="e008w-host-") as temp:
    binary = Path(temp) / "roi"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    str(here / "offline-roi.c"), "-o", str(binary)],
                   cwd=here, check=True, capture_output=True)
    generated = subprocess.check_output([str(binary)], cwd=here)
assert len(generated) == 1200
actual = audit.observed()
assert generated[:300] == actual["startup0"]
fields = ("left", "top", "width", "height", "rid", "oid", "merge", "eob", "type")
mismatch = {}
for i in (1, 2, 3):
    label = f"startup{i}"
    a = audit.decode(generated[300*i:300*(i+1)])
    b = audit.decode(actual[label])
    mismatch[label] = {k: sum(x[k] != y[k] for x, y in zip(a,b)) for k in fields}
    assert mismatch[label]["width"] == 0
    assert any(mismatch[label][k] for k in ("left", "top", "height"))
safe = {
    "schema": "E008W-bf-width-source-slice-v1",
    "classification": "OFFLINE_NORMAL_WIDTH_EXACT_OTHER_GEOMETRY_OPEN",
    "packet0_bytes_exact": 300,
    "normal_width_records_exact": 75,
    "normal_field_mismatch_counts": mismatch,
    "full_packet1_to_3_selector1_parity": False,
    "captured_values_or_hashes_emitted": False,
    "runtime_actions_performed": False,
}
(here / "RESULT.json").write_text(json.dumps(safe, indent=2, sort_keys=True)+"\n")
print("E008W_PRIVATE_AUDIT_PASS normal width 75/75 exact; remaining geometry open")
