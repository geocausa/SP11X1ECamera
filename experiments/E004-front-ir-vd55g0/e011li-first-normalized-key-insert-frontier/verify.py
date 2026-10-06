#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_FIRST_NORMALIZED_DESCRIPTOR_KEY_TO_INSERT_CALL_FRONTIER' and s['case_count']==4
assert s['descriptor_count_u32']==231 and s['descriptor_position_u32']==0 and s['source_descriptor_index_u32']==164 and s['top_level_length_u32']==40 and s['nested_length_u32']==16 and s['combined_key_length_u32']==56
assert s['key_buffer_SP_relative']=='0x1a0' and s['key_buffer_bytes']==128 and s['bounded_string_copy_calls']==2 and s['hash_u32']=='0x9f92cc38' and s['bucket_count_u32']==350 and s['bucket_index_u32']==280 and s['bucket_initially_null'] and s['empty_bucket_status_u32']==6
assert s['insert_call_RVA']=='0x5b8d50' and s['insert_target_RVA']=='0x5e83d8' and s['insert_call_x0_map_object'] and s['insert_call_x1_key_SP_relative']=='0x1a0' and s['insert_call_x2_value_SP_relative']=='0x10' and not s['insert_call_executed']
assert s['rejected_altered_contracts']==16 and s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and s['returned_to_Golden_Linux'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LJ' and n['expected_closure']['bucket_index_u32']==280 and n['expected_closure']['next_target_RVA']=='0x5e8740'
print(json.dumps({'status':'PASS_E011LI_PORTABLE_REVIEW','cases':4,'next':'E011LJ'},sort_keys=True))
