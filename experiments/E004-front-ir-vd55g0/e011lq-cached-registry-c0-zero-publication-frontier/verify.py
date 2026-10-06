#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_CACHED_REGISTRY_C0_ZERO_TO_FIRST_BASELINE_PUBLICATION_FRONTIER' and s['case_count']==4
assert s['post_map_call_RVA']=='0x5b8ddc' and s['post_map_helper_RVA']=='0x5b80a8' and s['post_map_helper_executed']
assert s['cached_pointer_RVA']=='0x1731880' and s['returned_registry_object_RVA']=='0x17a4230'
assert s['first_registry_field_offset']=='0xc0' and s['first_registry_field_u32']==0 and s['first_registry_field_read_RVA']=='0x5b8de4' and s['first_registry_field_read_executed']
assert s['publication_call_RVA']=='0x5b8df8' and s['publication_target_RVA']=='0x5b9f18' and s['publication_call_x0_object_RVA']=='0x17a7088' and s['publication_call_x1_SP_relative']=='0xd0' and s['publication_call_x2_SP_relative']=='0x14' and not s['publication_call_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['optional_ai_effects_followed'] and not s['native_rear_runtime_allowed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and s['returned_to_Golden_Linux']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LR' and n['current_frontier']['scalar_u32']==0 and n['expected_next']['resume_RVA']=='0x5b8dfc'
print(json.dumps({'status':'PASS_E011LQ_PORTABLE_REVIEW','cases':4,'next':'E011LR'},sort_keys=True))
