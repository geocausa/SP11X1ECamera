#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_COMPLETE_519_VENDOR_TAG_FLATTENING_TO_1040_TOTAL_FRONTIER' and s['case_count']==4
assert s['second_registry_call_RVA']=='0x5de948' and s['second_registry_target_RVA']=='0x5b80a8' and s['second_registry_call_executed'] and s['second_registry_resume_RVA']=='0x5de94c'
assert s['descriptor_count_u32']==231 and s['flattened_value_count_u32']==519 and len(s['flattened_values_sha256'])==64
assert s['caller_object_RVA']=='0x1733e20' and s['caller_total_offset']=='0x12c0' and s['caller_total_u32']==1040 and s['component_counts_u32']==[282,519,239]
assert s['stop_RVA']=='0x5de9e4' and not s['stop_executed'] and s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LZ' and n['expected_next']['standard_component_count_u32']==282
print(json.dumps({'status':'PASS_E011LY_PORTABLE_REVIEW','cases':4,'next':'E011LZ'},sort_keys=True))
