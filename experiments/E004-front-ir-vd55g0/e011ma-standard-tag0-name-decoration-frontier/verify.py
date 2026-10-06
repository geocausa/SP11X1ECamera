#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_STANDARD_TAG0_NAME_DECORATION_TO_NUMERIC_RECORD_FRONTIER' and s['case_count']==4
assert s['standard_tag_u32']==0 and s['name_helper_call_RVA']=='0x5dea14' and s['name_helper_RVA']=='0x5e07b0'
assert s['resolved_name']=='ColorCorrectionMode' and s['destination_record_RVA']=='0x17350e0' and s['destination_offset']=='0x3c' and s['destination_capacity_u32']==128
assert s['name_decoration_only'] and s['numeric_record_bytes_untouched'] and s['resume_RVA']=='0x5dea18' and not s['resume_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011MB'
print(json.dumps({'status':'PASS_E011MA_PORTABLE_REVIEW','cases':4,'next':'E011MB'},sort_keys=True))
