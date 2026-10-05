#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');c=L(H/'CFCC18-RETURN-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fc=ROOT/'experiments/E004-front-ir-vd55g0/e011fc-caller-index0-lowio-release/RESULT.json'
 assert s['status']=='PASS_CFCC18_ERROR_RETURN_TO_CFA9C0_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1212
 assert s['CFCC18_complete_error_return_qualified'] and s['CFCC18_return_u32']==2 and not s['outer_caller_resume_executed']
 assert s['lowIO_record0_lock_released'] and s['current_UTF16_owner_released'] and s['no_original_reads_of_released_current_owner'] and s['next_source_RVA']=='0xcfa9c0'
 assert s['inherited_E011FC_result_sha256']==sha(fc)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('cfcc18_return_safe_sha256','CFCC18-RETURN-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert r['rejected_altered_contracts']==1212 and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert c['CFCC18_complete_error_return_qualified'] and c['return_value_u32']==2 and c['caller_return_target_RVA']=='0xcfa9c0' and not c['outer_caller_resume_executed']
 assert c['lowIO_global7_lock_depth']==c['lowIO_record0_lock_depth']==0 and c['no_original_reads_of_released_unicode_owner']
 assert f['camera_frontier']['source_RVA']=='0xcfa9c0' and f['camera_frontier']['nonzero_branch_target_RVA']=='0xcfa99c' and not f['camera_frontier']['caller_instruction_executed']
 assert n['experiment']=='E011FE' and n['current_camera_frontier']['source_RVA']=='0xcfa9c0' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FD_PORTABLE_REVIEW','cases':4,'rejects':1212,'producer_rejects':264,'next':'E011FE'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
