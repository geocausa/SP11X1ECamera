#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_COMPLETE_NORMALIZED_DESCRIPTOR_MAP_TO_5B8DDC_FRONTIER' and s['case_count']==4
assert s['descriptor_count_u32']==231 and s['nested_element_attempts_u32']==519 and s['unique_map_entries_u32']==517 and s['duplicate_key_attempts_u32']==2
assert s['used_bucket_count_u32']==268 and s['unique_collision_insertions_u32']==249 and s['maximum_chain_length_u32']==8
assert s['bucket_node_allocations_u32']==268 and s['value_node_allocations_u32']==517 and s['key_storage_allocations_u32']==517 and s['key_storage_bytes_u32']==132
assert s['all_unique_keys_and_first_values_exact'] and s['corrects_prior_350_entry_forecast'] and s['stop_RVA']=='0x5b8ddc' and not s['stop_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['optional_ai_effects_followed'] and not s['native_rear_runtime_allowed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and s['returned_to_Golden_Linux']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LQ' and n['expected_next']['publication_call_RVA']=='0x5b8df8' and not n['expected_next']['publication_call_executed']
print(json.dumps({'status':'PASS_E011LP_PORTABLE_REVIEW','cases':4,'next':'E011LQ'},sort_keys=True))
