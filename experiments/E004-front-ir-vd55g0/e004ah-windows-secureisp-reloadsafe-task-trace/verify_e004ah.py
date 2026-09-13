#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys

D = Path(__file__).resolve().parent
raw = D / "E004AH-COLD2_TRACE.log"
norm = D / "E004AH-COLD2_TRACE.utf8.txt"
holder = D / "E004AH-COLD2-IR-HOLDER.txt"
gold = D / "POST-RETURN-GOLDEN.txt"
result = json.loads((D / "RESULT.json").read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

errors = []
if raw.stat().st_size != 33928:
    errors.append(f"raw bytes {raw.stat().st_size} != 33928")
if sha(raw) != "8891648f2152eec937567bd2736e33573912f70a04ba0292f83a4bf748636df6":
    errors.append("raw KD sha mismatch")
if sha(norm) != "12d302c6b394ded5e01cf91dd05c6e4839ae142325b36674dd0ce3751f459c52":
    errors.append("normalized KD sha mismatch")
if sha(holder) != "b5720f34cfaa6d98498ab14cd827518a1bae1b111e27c457cc13813c90a8bf7f":
    errors.append("holder sha mismatch")

t = norm.read_text(errors="replace")
h = holder.read_text()
g = gold.read_text()

for anchor in [
    "Base Address: fffff8037c6d0000",
    "Unload module qccamsecureisp8380.sys at fffff803`7c6d0000",
    "Base Address: fffff803813d0000",
    "===E004AH_COLD2_L2_VALIDATE===",
    "qccamsecureisp8380+0x3350:",
    "qccamsecureisp8380+0x4a90:",
    "qccamsecureisp8380+0x24f0:",
    "cmp         w1,#0x2E",
    "qccamsecureisp8380+0x1b08:",
    "===E004AH_COLD2_POSTSTOP_STATE===",
    "===E004AH_COLD2_END_NO_SECUREISP_TASK_HITS===",
]:
    if anchor not in t:
        errors.append(f"missing KD anchor: {anchor}")

runtime = re.findall(r"^E004AH_C2(?:_L2)?_(?:OP|TASK|FNTABLE|SECURECFG)\s+.*$", t, re.M)
if runtime:
    errors.append("unexpected accepted runtime markers: " + repr(runtime[:4]))

if "E004_IR_ROUTE_START_STATUS=Success" not in h:
    errors.append("holder StartAsync not successful")
if "E004_IR_ROUTE_ACQUIRED=12" not in h:
    errors.append("holder did not acquire 12 frames")
if len(re.findall(r"^E004_IR_ROUTE_FRAME n=", h, re.M)) != 12:
    errors.append("holder frame-line count != 12")
if "E004_IR_ROUTE_STOP_PASS" not in h:
    errors.append("holder StopAsync not successful")

for anchor in [
    "status=RETURNED_GOLDEN_FULLIO_V19C",
    "saved_entry=sp11-audio-fullio-v19c",
    "next_entry=",
    "sp11_entry=7.1.5-sp11-fullio-v19c",
]:
    if anchor not in g:
        errors.append(f"missing Golden anchor: {anchor}")

if result["accepted_runtime_hits"] != {
    "outer_operation_dispatcher": 0,
    "companion_send_helper": 0,
    "lane_protection_dispatcher": 0,
    "config_secure_camera": 0,
}:
    errors.append("RESULT runtime-hit table changed")

if errors:
    print("E004ah VERIFY: FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("E004ah VERIFY: PASS")
print(" - two SecureISP loads captured; load2 RVAs live-validated")
print(" - exact IR holder: StartAsync success, 12 real frames, StopAsync success")
print(" - zero accepted qccamsecureisp control-ABI runtime hits")
print(" - returned to protected Golden FullIO v19c")
