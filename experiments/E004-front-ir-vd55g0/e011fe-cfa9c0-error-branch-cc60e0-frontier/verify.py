#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');c=L(H/'CFA968-RETURN-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fd=ROOT/'experiments/E004-front-ir-vd55g0/e011fd-cfcc18-error-return-cfa9c0-frontier/RESULT.json'
 assert s['status']=='PASS_CFA9C0_ERROR_BRANCH_TO_CC60E0_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1236
 assert s['CFA968_complete_error_return_qualified'] and s['CFA968_return_u64']==0 and s['CFA9C0_nonzero_branch_target_RVA']=='0xcfa99c'
 assert s['outer_zero_result_cleanup_branch_taken'] and s['selected_cleanup_pointer_exact'] and s['selected_object_lock_retained_held'] and s['selected_object_unchanged']
 assert not s['CC60E0_executed'] and s['next_source_RVA']=='0xced188' and s['next_call_target_RVA']=='0xcc60e0'
 assert s['current_UTF16_owner_released'] and s['no_original_reads_of_released_current_owner']
 assert r['inherited_E011FD_result_sha256']==sha(fd)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('cfa968_return_safe_sha256','CFA968-RETURN-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert c['branch_target_RVA']=='0xcfa99c' and c['zero_return_value_u64']==0 and c['CFA968_complete_error_return_qualified'] and c['selected_object_mutation_path_bypassed']
 assert f['camera_frontier']['source_RVA']=='0xced188' and f['camera_frontier']['call_target_RVA']=='0xcc60e0' and not f['camera_frontier']['call_executed']
 assert n['experiment']=='E011FF' and n['current_camera_frontier']['source_RVA']=='0xced188' and not n['native_rear_runtime_allowed']
 assert r['rejected_altered_contracts']==1236 and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FE_PORTABLE_REVIEW','cases':4,'rejects':1236,'producer_rejects':264,'next':'E011FF'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
