#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_ZERO_BUCKET_CHAIN_LOOKUP_TO_VALUE_ALLOC_FRONTIER' and s['case_count']==4 and s['bucket_index_u32']==280 and s['bucket_node_head_u64']==0 and s['lookup_return_u64']==0 and s['caller_x24_after_u64']==0
assert s['call_RVA']=='0x5e8488' and s['call_target_RVA']=='0x5e8740' and s['stop_RVA']=='0x5e84b0' and not s['stop_executed'] and s['rejected_altered_contracts']==12
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LL' and n['expected_closure']['key_storage_bytes']==132
print(json.dumps({'status':'PASS_E011LK_PORTABLE_REVIEW','cases':4,'next':'E011LL'},sort_keys=True))
