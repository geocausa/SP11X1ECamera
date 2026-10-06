#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_ZERO_BACKED_PUBLICATION_TO_5F9724_EPILOGUE_FRONTIER" and s["case_count"]==4 and s["native_160a260_value_u64"]==0
assert s["publication_block_RVA"]=="0x160a1f0" and s["publication_ready_RVA"]=="0x160a270" and s["publication_ready_u32"]==1
assert s["secondary_publication_RVA"]=="0x16a3fe0" and s["secondary_publication_qword_u64"]==0 and s["secondary_publication_bitfield_RVA"]=="0x16a3fe8" and s["secondary_publication_bitfield_u32"]==0
assert s["next_camera_source_RVA"]=="0x5f9724" and not s["next_camera_source_executed"] and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IS" and f["frontier"]["source_RVA"]=="0x5f9724" and not f["frontier"]["executed"] and n["expected_frontier"]["architectural_return_RVA"]=="0x5f9420"
print(json.dumps({"status":"PASS_E011IR_PORTABLE_REVIEW","cases":4,"next":"E011IS"},sort_keys=True))
