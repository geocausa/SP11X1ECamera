#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');c=L(H/'SELECTED-CLEANUP-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fe=ROOT/'experiments/E004-front-ir-vd55g0/e011fe-cfa9c0-error-branch-cc60e0-frontier/RESULT.json'
 ej=ROOT/'experiments/E004-front-ir-vd55g0/e011ej-slot3-stream-object-native-front-correlation/RESULT.json'
 ejss=ROOT/'experiments/E004-front-ir-vd55g0/e011ej-slot3-stream-object-native-front-correlation/SOURCE-SAFE.json'
 assert s['status']=='PASS_CC60E0_SELECTED_CLEANUP_TO_LOCK_RELEASE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1440
 assert s['CC60E0_executed'] and s['CC60E0_claim_old_u32']==0x2000 and s['CC60E0_claim_new_u32']==0
 assert s['source_runtime_atomic_flag_joined_u32']==0x80000000 and s['selected_object_cleanup_mutation_exact'] and s['selected_object_claim_cleared']
 assert s['selected_object_lock_retained_held_after_CC60E0'] and not s['CB3480_executed'] and s['next_source_RVA']=='0xced190' and s['next_call_target_RVA']=='0xcb3480'
 assert r['inherited_E011FE_result_sha256']==sha(fe) and r['inherited_E011EJ_result_sha256']==sha(ej) and r['inherited_E011EJ_source_safe_sha256']==sha(ejss)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('selected_cleanup_safe_sha256','SELECTED-CLEANUP-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert c['claim_old_u32']==0x2000 and c['claim_new_u32']==0 and c['selected_object_lock_retained_held_after_CC60E0'] and not c['CB3480_executed']
 assert not c['native_LSE_branch_qualified_by_E011FF'] and c['source_runtime_flag_handoff_not_native_startup_replay']
 assert f['camera_frontier']['source_RVA']=='0xced190' and f['camera_frontier']['call_target_RVA']=='0xcb3480' and not f['camera_frontier']['call_executed']
 assert n['experiment']=='E011FG' and n['current_camera_frontier']['selected_object_lock_retained_held'] and not n['native_rear_runtime_allowed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FF_PORTABLE_REVIEW','cases':4,'rejects':1440,'producer_rejects':264,'next':'E011FG'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
