#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_ZERO_SOURCE_SECOND_COPY_TO_1798508_FRONTIER' and s['case_count']==4 and s['source_first_u8']==0 and s['copy_call_RVA']=='0x5be498' and s['copied_bytes_including_nul']==1 and s['copy_return_u32']==0
assert s['next_camera_source_RVA']=='0x5be49c' and s['next_global_base_RVA']=='0x1798508' and not s['next_global_read_executed'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JH' and f['frontier']['global_base_RVA']=='0x1798508' and not f['frontier']['executed'] and len(n['dependencies'])==2
print(json.dumps({'status':'PASS_E011JG_PORTABLE_REVIEW','cases':4,'next':'E011JH'},sort_keys=True))
