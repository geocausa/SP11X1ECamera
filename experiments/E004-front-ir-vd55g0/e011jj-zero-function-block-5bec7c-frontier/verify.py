#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_ZERO_FUNCTION_BLOCK_TO_5BEC7C_FRONTIER' and s['case_count']==4 and s['function_block_base_RVA']=='0x17a70d0' and s['all_seven_function_slots_zero'] and s['selected_mode_population_bypassed']
assert s['first_null_branch_RVA']=='0x5bea90' and s['branch_taken_to_RVA']=='0x5bec7c' and s['next_camera_source_RVA']=='0x5bec7c' and not s['next_instruction_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011JK' and f['frontier']['source_RVA']=='0x5bec7c' and not f['frontier']['executed']
print(json.dumps({'status':'PASS_E011JJ_PORTABLE_REVIEW','cases':4,'next':'E011JK'},sort_keys=True))
