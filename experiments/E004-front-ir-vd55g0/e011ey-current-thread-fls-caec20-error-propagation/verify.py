#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');f=L(H/'FRONTIER-SAFE.json');t=L(H/'THREAD-AUTHORITY-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 ex=ROOT/'experiments/E004-front-ir-vd55g0/e011ex-exact-getlasterror-caec20-frontier/RESULT.json';cv=ROOT/'experiments/E004-front-ir-vd55g0/e011cv-original-slot-thread-producer/RESULT.json';cw=ROOT/'experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/RESULT.json'
 assert s['status']=='PASS_CURRENT_THREAD_FLS_CAEC20_ERROR_PROPAGATION' and s['case_count']==4 and s['rejected_altered_contracts']==1020
 assert s['thread_producer_invalid_API_requests_rejected']==264 and s['CAEC20_executed'] and s['CAEC20_error3_to_thread_OS3_CRT2_qualified']
 assert s['thread_owner_matches_current_CRT_next_allocation'] and s['native_FlsGetValue2_original_instructions_executed']
 assert s['current_UTF16_owner_bytes']==76 and not s['current_UTF16_owner_released'] and not s['older_E011CW_cleanup_geometry_reused']
 assert s['next_source_RVA']=='0xcfd704' and s['next_branch_target_RVA']=='0xcfd5dc'
 assert s['inherited_E011EX_result_sha256']==sha(ex) and s['inherited_E011CV_result_sha256']==sha(cv) and s['inherited_E011CW_result_sha256']==sha(cw)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('thread_authority_safe_sha256','THREAD-AUTHORITY-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(H/nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert t['error_mapping']=={'input_Win32':3,'thread_OS':3,'thread_CRT':2} and t['current_UTF16_owner_bytes']==76 and not t['older_E011CW_cleanup_geometry_reused']
 assert f['camera_frontier']['source_RVA']=='0xcfd704' and f['camera_frontier']['next_internal_call_target_RVA']=='0xcaecf8'
 assert n['experiment']=='E011EZ' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EY_PORTABLE_REVIEW','cases':4,'rejects':1020,'producer_rejects':264,'next':'E011EZ'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
