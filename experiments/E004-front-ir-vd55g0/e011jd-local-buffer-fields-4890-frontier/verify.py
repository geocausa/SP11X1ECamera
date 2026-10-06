#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent; L=lambda x:json.loads((H/x).read_text()); S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json'); r=L('RESULT.json'); f=L('FRONTIER-SAFE.json'); n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_LOCAL_AND_BUFFER_FIELDS_TO_4890_FRONTIER' and s['case_count']==4
assert s['clear_bytes']==1040 and s['local_plus_0x6c_before_u32']==0
assert s['buffer_plus_0x442c_u32']==s['buffer_plus_0x1c_u32']==s['buffer_plus_0x0c_u32']==0 and s['buffer_plus_0x20_u32']==134217728
assert s['local_plus_0x68_after_u32']==s['local_plus_0x6c_after_u32']==s['local_plus_0x470_after_u32']==0
assert s['next_camera_source_RVA']=='0x5be470' and not s['next_dependency_read_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==S(x)
assert r['next_experiment']=='E011JE' and f['frontier']['source_RVA']=='0x5be470' and not f['frontier']['executed'] and n['expected_frontier']['next_RVA']=='0x5be47c'
print(json.dumps({'status':'PASS_E011JD_PORTABLE_REVIEW','cases':4,'next':'E011JE'},sort_keys=True))
