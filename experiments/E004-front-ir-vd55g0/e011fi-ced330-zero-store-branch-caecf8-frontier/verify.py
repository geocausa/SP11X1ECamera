#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');c=L(H/'CED330-STORE-BRANCH-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fh=ROOT/'experiments/E004-front-ir-vd55g0/e011fh-ced0d8-zero-return-ced330-frontier/RESULT.json'
 assert s['status']=='PASS_CED330_ZERO_STORE_BRANCH_TO_CAECF8_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1620
 assert s['outer_result_store_executed'] and s['outer_result_store_value_u64']==0 and s['outer_zero_branch_qualified']
 assert s['same_thread_error_authority_rejoined'] and s['same_thread_CRT_error_u32']==2 and s['next_source_RVA']=='0xcaecf8'
 assert r['inherited_E011FH_result_sha256']==sha(fh)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('ced330_store_branch_safe_sha256','CED330-STORE-BRANCH-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert c['source_RVA']=='0xced330' and c['store_executed'] and c['store_bytes']==8 and c['source_value_u64']==0
 assert c['zero_branch_qualified'] and c['call_target_RVA']=='0xcaecf8' and c['same_thread_CRT_error_u32']==2 and not c['new_outer_CAECF8_body_executed']
 assert f['camera_frontier']['source_RVA']=='0xcaecf8' and f['camera_frontier']['return_target_RVA']=='0xced33c' and f['camera_frontier']['same_thread_CRT_error_u32']==2
 assert n['experiment']=='E011FJ' and n['current_camera_frontier']['source_RVA']=='0xcaecf8' and not n['native_rear_runtime_allowed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FI_PORTABLE_REVIEW','cases':4,'rejects':1620,'producer_rejects':264,'next':'E011FJ'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
