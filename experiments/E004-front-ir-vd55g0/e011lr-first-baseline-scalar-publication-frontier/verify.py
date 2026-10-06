#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_FIRST_BASELINE_SCALAR_PUBLICATION_TO_SECOND_REGISTRY_GETTER_FRONTIER' and s['case_count']==4
assert s['publication_call_RVA']=='0x5b8df8' and s['publication_target_RVA']=='0x5b9f18' and s['publication_call_executed']
assert s['publication_container_RVA']=='0x17a7088' and s['scalar_u32']==0 and s['hash_algorithm']=='fnv1a64_4byte' and s['hash_u64']=='0x4d25767f9dce13f5' and s['bucket_mask_u64']==7 and s['bucket_index_u32']==5
assert s['value_node_allocation_bytes']==24 and s['value_node_zero_initialized'] and s['container_size_after_u64']==1 and s['output_inserted_u8']==1
assert s['resume_RVA']=='0x5b8dfc' and not s['resume_executed'] and s['next_registry_helper_RVA']=='0x5b80a8' and not s['next_registry_getter_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['optional_ai_effects_followed'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LS' and n['expected_closure']['additional_publication_calls_u32']==9 and n['expected_closure']['stop_RVA']=='0x5b8ef8'
print(json.dumps({'status':'PASS_E011LR_PORTABLE_REVIEW','cases':4,'next':'E011LS'},sort_keys=True))
