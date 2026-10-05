#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');f=L(H/'FRONTIER-SAFE.json');e=L(H/'ERROR-RETURN-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 ey=ROOT/'experiments/E004-front-ir-vd55g0/e011ey-current-thread-fls-caec20-error-propagation/RESULT.json'
 assert s['status']=='PASS_CFD570_ERROR_RETURN_TO_PARENT_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1020
 assert s['CAECF8_executed'] and s['CAECF8_returned_current_thread_CRT_error_pointer'] and s['CFD570_complete_error_return_qualified'] and s['CFD570_return_u32']==2
 assert s['native_FlsGetValue2_original_instructions_executed'] and s['native_FlsGetValue2_total_reads']==36
 assert s['current_UTF16_owner_bytes']==76 and not s['current_UTF16_owner_released'] and not s['parent_cleanup_executed'] and not s['older_E011CW_cleanup_geometry_reused']
 assert s['next_source_RVA']=='0xcfd518' and s['next_dependency_source_RVA']=='0xcfd51c' and s['next_dependency_value_u8']==1
 assert s['inherited_E011EY_result_sha256']==sha(ey)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('error_return_safe_sha256','ERROR-RETURN-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(H/nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert e['CFD570_return_u32']==2 and e['current_UTF16_owner_bytes']==76 and not e['current_UTF16_owner_released']
 assert f['camera_frontier']['source_RVA']=='0xcfd518' and f['camera_frontier']['next_dependency_source_RVA']=='0xcfd51c' and f['camera_frontier']['candidate_cleanup_target_RVA']=='0xcb1650'
 assert n['experiment']=='E011FA' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EZ_PORTABLE_REVIEW','cases':4,'rejects':1020,'producer_rejects':264,'next':'E011FA'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
