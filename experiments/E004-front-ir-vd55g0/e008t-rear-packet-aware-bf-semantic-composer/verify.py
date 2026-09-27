#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
GEN = HERE / "generate-e008t.py"
INC = HERE / "camss-vfe-e008t-rear-bf-semantic.inc"
SAFE = HERE / "SAFE-SOURCE-AUTHORITY.json"
HARNESS = HERE / "compile-check.c"
OUT = Path("/tmp/e008t-bf-semantic-check")

subprocess.run(["python3", str(GEN)], cwd=REPO, check=True)

safe = json.loads(SAFE.read_text())
assert safe["status"] == "PASS"
assert safe["bank_sequence"] == [0, 1, 0, 1]
assert safe["packet0"]["iir_shifts"] == [-3, 0]
assert safe["packet0"]["gamma_valid"] is False
assert safe["packet1_plus"]["iir_shifts"] == [3, 3]
assert safe["packet1_plus"]["gamma_valid"] is True
assert safe["final_bfstats_roi_adjustment_applied"] is False
assert safe["final_selector1_dmi_parity_claimed"] is False
assert safe["captured_windows_register_values_embedded"] is False
assert safe["captured_windows_dmi_bytes_embedded"] is False
assert safe["runtime_actions_performed"] is False

src = INC.read_text()
assert "e008t_rear_seed_bootstrap_bf" in src
assert "e008t_rear_seed_packet0_roi" in src
assert "e008t_rear_seed_normal_roi" in src
assert "private/e006" not in src
assert "E008T_HARDCODE_CORING_SCALAR" in src
assert "E008T_NORMAL_CORING_SCALAR" in src

subprocess.run([
    "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
    str(HARNESS), "-o", str(OUT)
], cwd=HERE, check=True)
subprocess.run([str(OUT)], check=True)
OUT.unlink(missing_ok=True)

print("E008T_VERIFY_PASS source_generation=pass host_semantic_harness=pass runtime=none")
