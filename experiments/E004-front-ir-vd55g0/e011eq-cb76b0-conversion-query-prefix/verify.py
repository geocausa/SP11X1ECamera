#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['status']=='PASS_CB76B0_CONVERSION_QUERY_PREFIX' and s['case_count']==4 and s['rejected_altered_contracts']==544
 assert s['CB76B0_nonempty_source_branch_qualified'] and s['CB8D88_mode_zero_dispatch_qualified'] and s['MultiByteToWideChar_query_arguments_qualified']
 assert not s['OS_conversion_call_executed'] and s['next_source_RVA']=='0xcb8dd0' and s['next_dependency_RVA']=='0xf7e2e8'
 assert r['source_script_sha256']==sha(H/'source-private.py') and r['source_safe_sha256']==sha(H/'SOURCE-SAFE.json') and r['next_experiment']=='E011ER'
 assert f['qualified']['source_input_bytes_including_NUL']==38 and f['qualified']['source_input_ascii'] and f['qualified']['source_input_NUL_terminated']
 assert f['camera_frontier']['query_arguments']['codepage']==0 and f['camera_frontier']['query_arguments']['flags']==9
 assert n['experiment']=='E011ER' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EQ_PORTABLE_REVIEW','cases':4,'rejects':544,'next':'E011ER'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
