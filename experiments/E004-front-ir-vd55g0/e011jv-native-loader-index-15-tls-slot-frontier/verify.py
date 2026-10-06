#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NATIVE_LOADER_INDEX_15_TLS_SLOT_WRITE_FRONTIER" and s["case_count"]==4
assert s["native_loader_index_u32"]==s["native_loader_index_before_reader_start_u32"]==s["native_loader_index_after_successful_reader_start_u32"]==15 and s["native_loader_index_stable_across_successful_front_reader_start"]
assert s["loader_index_read_RVA"]=="0xce7a90" and s["loader_index_cell_RVA"]=="0x16a3740" and s["x18_tls_array_offset_u64"]=="0x58" and s["loader_slot_stride_u64"]==8
assert s["published_epoch_u32"]=="0x80000043" and s["tls_epoch_store_RVA"]=="0xce7aa4" and s["tls_epoch_store_offset_u64"]=="0x10"
assert s["next_camera_source_RVA"]=="0xce7aa8" and s["next_release_import_RVA"]=="0xf7e518" and s["next_release_call_RVA"]=="0xce7ab0" and not s["next_release_call_executed"]
assert s["new_front_camera_starts"]==1 and s["new_rear_camera_starts"]==0 and s["new_reboots"]==4 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JW" and f["windows_oracle"]["native_value_before_reader_start_u32"]==f["windows_oracle"]["native_value_after_successful_reader_start_u32"]==15
assert n["retained_state"]["loader_index_u32"]==15 and n["retained_state"]["srw_lock_held"] and not n["expected_next_frontier"]["wake_call_executed"]
print(json.dumps({"status":"PASS_E011JV_PORTABLE_REVIEW","cases":4,"next":"E011JW"},sort_keys=True))
