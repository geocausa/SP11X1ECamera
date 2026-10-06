#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_REMAINING_BASELINE_ZERO_SCALAR_PUBLICATIONS_TO_NATIVE_GATE_FRONTIER' and s['case_count']==4
assert s['additional_registry_getter_calls_u32']==9 and s['additional_publication_calls_u32']==9 and s['duplicate_publication_returns_u32']==9 and s['additional_value_node_allocations_u32']==0
assert s['publication_container_size_u64']==1 and s['total_baseline_publication_calls_u32']==10 and s['total_unique_publication_keys_u32']==1 and s['all_registry_scalars_u32']==0
assert len(s['registry_scalar_offsets'])==9 and s['stop_RVA']=='0x5b8ef8' and not s['stop_executed'] and s['next_native_gate_global_RVA']=='0x160a218'
assert s['product_scope']=='front_rear_rgb_parity' and not s['optional_ai_effects_followed'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LT' and n['accepted_native_authority']['RVA_0x1608858_u32']==1 and n['expected_closure']['branch_target_RVA']=='0x5b8fd0'
print(json.dumps({'status':'PASS_E011LS_PORTABLE_REVIEW','cases':4,'next':'E011LT'},sort_keys=True))
