#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_BUFFER_4890_ZERO_TO_3C28_FRONTIER' and s['case_count']==4 and s['buffer_plus_0x4890_u32']==0 and s['local_plus_0x474_after_u32']==0
assert s['next_camera_source_RVA']=='0x5be47c' and not s['next_source_formation_executed'] and s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JF' and f['frontier']['source_RVA']=='0x5be47c' and not f['frontier']['executed'] and n['expected_call']['target_RVA']=='0xcae7c0'
print(json.dumps({'status':'PASS_E011JE_PORTABLE_REVIEW','cases':4,'next':'E011JF'},sort_keys=True))
