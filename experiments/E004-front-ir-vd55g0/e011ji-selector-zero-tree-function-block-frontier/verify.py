#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_SELECTOR_ZERO_TREE_TO_FUNCTION_BLOCK_FRONTIER' and s['case_count']==4 and s['w20_u32']==s['w23_u32']==0 and s['selector_flags_zero']
assert s['decision_instruction_count']==29 and s['memory_reads_before_frontier']==s['memory_writes_before_frontier']==0 and s['next_camera_source_RVA']=='0x5bea80' and not s['next_dependency_read_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JJ' and f['frontier']['source_RVA']=='0x5bea80' and not f['frontier']['executed']
print(json.dumps({'status':'PASS_E011JI_PORTABLE_REVIEW','cases':4,'next':'E011JJ'},sort_keys=True))
