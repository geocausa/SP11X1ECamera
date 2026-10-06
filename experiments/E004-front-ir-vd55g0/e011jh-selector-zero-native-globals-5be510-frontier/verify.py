#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_SELECTOR_ZERO_NATIVE_GLOBALS_TO_5BE510_FRONTIER' and s['case_count']==4 and s['selector_byte1_u8']==s['selector_byte2_u8']==0 and s['selector_exact_source_materializations']==9 and s['selector_direct_writers_found']==0
assert s['native_160a218_u64']==0 and s['native_1608858_u32']==1 and s['branch_taken_to_RVA']=='0x5be510' and s['w20_u32']==s['w23_u32']==0 and not s['next_instruction_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JI' and f['frontier']['source_RVA']=='0x5be510' and not f['frontier']['executed'] and n['expected_frontier']['RVA']=='0x5bea80'
print(json.dumps({'status':'PASS_E011JH_PORTABLE_REVIEW','cases':4,'next':'E011JI'},sort_keys=True))
