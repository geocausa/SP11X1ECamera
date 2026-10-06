#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_ZERO_SOURCE_FIRST_COPY_TO_3E28_FRONTIER' and s['case_count']==4 and s['source_first_u8']==0 and s['copy_call_RVA']=='0x5be480' and s['copy_helper_RVA']=='0xcae7c0'
assert s['copy_capacity_u64']==512 and s['copy_count_s64']==-1 and s['copied_bytes_including_nul']==1 and s['copy_return_u32']==0 and s['next_camera_source_RVA']=='0x5be484' and not s['next_source_read_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JG' and f['frontier']['source_RVA']=='0x5be484' and not f['frontier']['executed'] and n['expected_call']['call_RVA']=='0x5be498'
print(json.dumps({'status':'PASS_E011JF_PORTABLE_REVIEW','cases':4,'next':'E011JG'},sort_keys=True))
