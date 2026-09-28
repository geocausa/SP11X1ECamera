#!/usr/bin/env python3
"""Source-derived E009b DMI versus private same-SP11 originals; aggregates only."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE.parent / "e008u-rear-bf-roi-geometry-audit/audit-private.py"
TUNING = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
TUNING_SHA = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
DEC = REPO / "experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py"

def import_file(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

audit = import_file(SOURCE, "e009b_source")
decoder = import_file(DEC, "e009b_chromatix")
tuning = TUNING.read_bytes()
assert hashlib.sha256(tuning).hexdigest() == TUNING_SHA
header = decoder.parse_header(tuning)
records, _ = decoder.parse_symbol_table(tuning, header["sections"][0], header["sections"][1])
haf = decoder.data_bytes(tuning, header["sections"][1], records[0xB6])
fractions = struct.unpack_from("<2f", haf, 0x28)
assert all(abs(v - 0.25) < 1e-6 for v in fractions)
with tempfile.TemporaryDirectory(prefix="e009b-source-") as tmp:
    binary = str(Path(tmp) / "offline-roi")
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    str(HERE / "offline-roi.c"), "-o", binary],
                   cwd=HERE, check=True, capture_output=True)
    generated = subprocess.check_output([binary], cwd=HERE)
assert len(generated) == 4 * 300
observed = audit.observed()
expected = {f"startup{i}": generated[i * 300:(i + 1) * 300] for i in range(4)}
expected["steady_ac8"] = expected["startup2"]
results = {}
for label, clean in expected.items():
    actual = observed[label]
    c, a = audit.decode(clean), audit.decode(actual)
    results[label] = {"matching_bytes": sum(x == y for x, y in zip(clean, actual)),
                      "matching_fields": {key: sum(x[key] == y[key] for x, y in zip(c, a))
                                          for key in audit.FIELDS}}
for label in ("startup0", "startup2", "startup3", "steady_ac8"):
    assert results[label]["matching_bytes"] == 300
    assert all(n == 25 for n in results[label]["matching_fields"].values())
assert results["startup1"]["matching_bytes"] == 250
assert all(results["startup1"]["matching_fields"][k] == 0 for k in ("left", "top"))
assert all(results["startup1"]["matching_fields"][k] == 25
           for k in audit.FIELDS if k not in ("left", "top"))
safe = {"schema": "E009B-settled-source-forward-v1",
        "classification": "PACKET0_2_3_STEADY_300_OF_300_PACKET1_POSITION_OPEN",
        "selected_haf_fraction_source_verified": True,
        "source_derived_normal_roi_geometry": True,
        "compared": results,
        "packet1_request_stage_source_closed": False,
        "native_rear_isp_runtime_authorized": False,
        "captured_values_or_hashes_emitted": False}
(HERE / "RESULT.json").write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n")
print("E009B_PRIVATE_FORWARD_PASS packet0/2/3/steady 300/300, packet1 250/300")
