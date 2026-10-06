#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_STANDARD_TAG0_NUMERIC_RECORD_TO_SECOND_STANDARD_ITERATION_FRONTIER' and s['case_count']==4
assert s['standard_tag_u32']==0 and s['record_RVA']=='0x17350e0' and s['record_stride_bytes']==168
assert s['record_index_u32']==0 and s['record_source_class_u32']==0 and s['category_pointer_RVA']=='0x1014012' and s['tag_id_u32']==0
assert s['element_bytes_u32']==1 and s['type_u8']==0 and s['element_count_u32']==1 and s['sentinel_u32']==0xffffffff and s['aggregate_bytes_u32']==1
assert s['numeric_record_complete'] and s['second_standard_iteration_RVA']=='0x5dea00' and not s['second_standard_iteration_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011MC'
print(json.dumps({'status':'PASS_E011MB_PORTABLE_REVIEW','cases':4,'next':'E011MC'},sort_keys=True))
