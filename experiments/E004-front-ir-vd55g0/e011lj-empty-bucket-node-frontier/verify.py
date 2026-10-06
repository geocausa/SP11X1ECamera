#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_EMPTY_BUCKET_NODE_PUBLICATION_TO_5E8740_CALL_FRONTIER' and s['case_count']==4
assert s['bucket_index_u32']==280 and s['bucket_node_allocation_bytes']==24 and s['bucket_node_zero_initialized'] and s['bucket_node_published']
assert s['next_call_RVA']=='0x5e8488' and s['next_target_RVA']=='0x5e8740' and not s['next_call_executed']
assert s['rejected_altered_contracts']==16 and s['new_front_camera_starts']==s['new_rear_camera_starts']==s['new_reboots']==0 and not s['new_kernel_build'] and s['returned_to_Golden_Linux'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LK' and n['expected_closure']['stop_RVA']=='0x5e84b0'
print(json.dumps({'status':'PASS_E011LJ_PORTABLE_REVIEW','cases':4,'next':'E011LK'},sort_keys=True))
