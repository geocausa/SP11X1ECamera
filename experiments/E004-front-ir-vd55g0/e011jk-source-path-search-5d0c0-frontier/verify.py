#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_SOURCE_PATH_SEARCH_TO_5D0C0_FRONTIER' and s['case_count']==4 and s['source_bytes_including_nul']==97 and s['source_first_backslash_offset']==2 and s['source_last_backslash_offset']==74
assert s['search_return_source_offset']==74 and s['log_path_x4_source_offset']==75 and s['next_call_RVA']=='0x5bec98' and s['next_call_target_RVA']=='0x5d0c0' and s['next_call_x0_u64']==131072 and not s['next_call_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JL' and f['frontier']['target_RVA']=='0x5d0c0' and not f['frontier']['executed']
print(json.dumps({'status':'PASS_E011JK_PORTABLE_REVIEW','cases':4,'next':'E011JL'},sort_keys=True))
