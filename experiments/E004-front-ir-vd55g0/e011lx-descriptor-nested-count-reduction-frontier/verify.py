#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_DESCRIPTOR_NESTED_COUNT_REDUCTION_TO_SECOND_REGISTRY_CALL_FRONTIER' and s['case_count']==4
assert s['registry_object_RVA']=='0x17a4230' and s['descriptor_count_u32']==231 and s['aggregate_nested_count_u32']==519
assert s['aggregate_store_RVA']=='0x5de93c' and s['caller_object_RVA']=='0x1733e20' and s['caller_total_offset']=='0x12c8'
assert s['preexisting_count_12c4_u32']==282 and s['preexisting_count_12cc_u32']==239 and s['combined_after_aggregate_u32']==1040
assert s['threshold_u32']==1200 and s['threshold_branch_to_second_helper'] and s['second_registry_call_RVA']=='0x5de948' and s['second_registry_target_RVA']=='0x5b80a8' and not s['second_registry_call_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LY' and n['expected_closure']['caller_total_u32']==1040
print(json.dumps({'status':'PASS_E011LX_PORTABLE_REVIEW','cases':4,'next':'E011LY'},sort_keys=True))
