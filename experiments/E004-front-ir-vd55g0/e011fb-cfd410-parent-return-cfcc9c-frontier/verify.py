#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');p=L(H/'PARENT-RETURN-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fa=ROOT/'experiments/E004-front-ir-vd55g0/e011fa-current-76byte-parent-cleanup/RESULT.json'
 assert s['status']=='PASS_CFD410_PARENT_RETURN_TO_CFCC9C_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1136
 assert s['CFD410_complete_return_qualified'] and s['CFD410_return_u32']==2 and not s['caller_resume_executed']
 assert s['current_UTF16_owner_bytes']==76 and s['current_UTF16_owner_released'] and s['no_original_reads_of_released_current_owner']
 assert s['next_source_RVA']=='0xcfcc9c' and s['inherited_E011FA_result_sha256']==sha(fa)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('parent_return_safe_sha256','PARENT-RETURN-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(H/nm)
 assert r['rejected_altered_contracts']==1136 and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert p['CFD410_complete_return_qualified'] and p['CFD410_return_u32']==2 and p['caller_return_target_RVA']=='0xcfcc9c' and not p['caller_resume_executed']
 assert p['nonvolatile_restore_qualified'] and p['caller_SP_restore_qualified'] and p['no_original_reads_of_released_owner_to_caller_frontier']
 assert f['camera_frontier']['source_RVA']=='0xcfcc9c' and not f['camera_frontier']['caller_instruction_executed']
 assert n['experiment']=='E011FC' and n['current_camera_frontier']['source_RVA']=='0xcfcc9c' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FB_PORTABLE_REVIEW','cases':4,'rejects':1136,'producer_rejects':264,'next':'E011FC'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
