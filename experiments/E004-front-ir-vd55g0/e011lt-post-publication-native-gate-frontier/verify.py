#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_POST_PUBLICATION_NATIVE_GATE_TO_TRACE_FLAG_FRONTIER' and s['case_count']==4
assert s['start_RVA']=='0x5b8ef8' and s['native_160a218_u64']==0 and s['native_1608858_u32']==1 and not s['bit16_branch_taken'] and s['second_global_nonzero_branch_taken']
assert s['branch_target_RVA']=='0x5b8fd0' and s['trace_flag_RVA']=='0x17a1180' and s['trace_flag_read_RVA']=='0x5b8fd0' and not s['trace_flag_read_executed']
assert s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and s['returned_to_Golden_Linux']
assert s['product_scope']=='front_rear_rgb_parity' and not s['optional_ai_effects_followed'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LU' and n['expected_closure']['branch_target_RVA']=='0x5b9034' and n['diagnostic_logging_non_blocking']
print(json.dumps({'status':'PASS_E011LT_PORTABLE_REVIEW','cases':4,'next':'E011LU'},sort_keys=True))
