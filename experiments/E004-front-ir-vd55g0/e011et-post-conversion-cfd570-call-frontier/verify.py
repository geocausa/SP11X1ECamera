#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['status']=='PASS_POST_CONVERSION_CFD570_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==772
 assert s['complete_CB76B0_return_qualified'] and s['post_conversion_parent_resume_qualified'] and s['CFD570_call_arguments_qualified'] and not s['CFD570_executed']
 assert s['next_source_RVA']=='0xcfd514' and s['next_call_target_RVA']=='0xcfd570'
 assert r['source_script_sha256']==sha(H/'source-private.py') and r['source_safe_sha256']==sha(H/'SOURCE-SAFE.json') and r['exact_API_output_safe_sha256']==sha(H/'EXACT-API-OUTPUT-SAFE.json')
 assert r['next_experiment']=='E011EU' and f['camera_frontier']['source_RVA']=='0xcfd514' and not f['camera_frontier']['CFD570_executed']
 assert n['experiment']=='E011EU' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011ET_PORTABLE_REVIEW','cases':4,'rejects':772,'next':'E011EU'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
