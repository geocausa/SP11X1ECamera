#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_STANDARD_METADATA_TABLE_FIRST_RECORD_TO_NAME_HELPER_FRONTIER' and s['case_count']==4
assert s['standard_component_count_u32']==282 and s['static_tag_table_RVA']=='0x10eda10' and len(s['static_tag_table_sha256'])==64 and s['first_standard_tag_u32']==0
assert s['record_array_RVA']=='0x17350e0' and s['record_stride_bytes']==168 and s['first_record_name_buffer_offset']=='0x3c'
assert s['first_name_helper_call_RVA']=='0x5dea14' and s['first_name_helper_target_RVA']=='0x5e07b0' and not s['first_name_helper_call_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011MA' and n['current_frontier']['standard_tag_u32']==0
print(json.dumps({'status':'PASS_E011LZ_PORTABLE_REVIEW','cases':4,'next':'E011MA'},sort_keys=True))
