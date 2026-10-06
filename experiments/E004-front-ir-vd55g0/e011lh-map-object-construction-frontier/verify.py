#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_5E81B8_MAP_OBJECT_TO_CALLER_STORE_FRONTIER' and s['case_count']==4 and s['call_executed']
assert s['helper_object_bytes']==64 and s['entry_array_count_u32']==350 and s['entry_array_bytes']==2800 and s['entry_array_exactly_cleared']
assert s['helper_field_plus_0_u32']==350 and s['helper_field_plus_0x4_f32_bits']=='0x3f800000' and s['helper_field_plus_0x8_u32']==128 and s['helper_field_plus_0xc_u32']==4 and s['helper_field_plus_0x30_u64']==132
assert s['helper_return_nonzero'] and s['caller_store_executed'] and s['next_branch_RVA']=='0x5b8bcc' and not s['next_branch_executed'] and s['rejected_altered_contracts']==16
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LI' and n['expected_first_key']['bucket_index_u32']==120
print(json.dumps({'status':'PASS_E011LH_PORTABLE_REVIEW','cases':4,'next':'E011LI'},sort_keys=True))
