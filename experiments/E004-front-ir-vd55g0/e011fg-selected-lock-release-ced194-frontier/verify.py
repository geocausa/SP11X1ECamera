#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');l=L(H/'LOCK-RELEASE-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 ff=ROOT/'experiments/E004-front-ir-vd55g0/e011ff-cc60e0-selected-cleanup-lock-release-frontier/RESULT.json'
 cw=ROOT/'experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/RESULT.json'
 assert s['status']=='PASS_SELECTED_LOCK_RELEASE_TO_CED194_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1496
 assert s['CB3480_executed'] and s['selected_object_lock_release_executed'] and s['selected_object_lock_released']
 assert s['next_source_RVA']=='0xced194' and s['CC60E0_claim_new_u32']==0 and s['no_original_reads_of_released_current_owner']
 assert r['inherited_E011FF_result_sha256']==sha(ff) and r['inherited_E011CW_result_sha256']==sha(cw)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('lock_release_safe_sha256','LOCK-RELEASE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert l['release_callsite_RVA']=='0xced190' and l['release_wrapper_RVA']=='0xcb3480' and l['selected_object_lock_released_after_owned_contract']
 assert l['owned_LeaveCriticalSection_contract_executed'] and not l['native_mutex_bytes_or_concurrency_qualified']
 assert f['camera_frontier']['source_RVA']=='0xced194' and f['camera_frontier']['selected_object_lock_released'] and not f['complete_CED0D8_return_qualified']
 assert n['experiment']=='E011FH' and n['current_camera_frontier']['selected_object_lock_released'] and not n['native_rear_runtime_allowed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FG_PORTABLE_REVIEW','cases':4,'rejects':1496,'producer_rejects':264,'next':'E011FH'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
