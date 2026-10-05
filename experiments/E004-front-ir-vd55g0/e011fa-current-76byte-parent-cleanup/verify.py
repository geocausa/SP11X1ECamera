#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');c=L(H/'PARENT-CLEANUP-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 ez=ROOT/'experiments/E004-front-ir-vd55g0/e011ez-cfd570-error-return-parent-frontier/RESULT.json'
 assert s['status']=='PASS_CURRENT_76BYTE_PARENT_CLEANUP_TO_PARENT_RESUME' and s['case_count']==4 and s['rejected_altered_contracts']==1112
 assert s['CFD570_return_u32']==2 and s['current_UTF16_owner_bytes']==76 and s['current_UTF16_owner_flag_u8']==1
 assert s['current_UTF16_owner_pointer_selected_exact'] and s['parent_cleanup_executed'] and s['original_CB1650_executed']
 assert s['owned_HeapFree_contract_executed'] and s['HeapFree_success_return_u32']==1 and s['current_UTF16_owner_released']
 assert s['no_original_reads_of_released_current_owner'] and s['old_74byte_geometry_negative_rejected'] and not s['older_E011CW_cleanup_geometry_reused']
 assert s['next_source_RVA']=='0xcfd52c' and s['inherited_E011EZ_result_sha256']==sha(ez)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('parent_cleanup_safe_sha256','PARENT-CLEANUP-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(H/nm)
 assert r['rejected_altered_contracts']==1112 and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert c['owner_flag_u8']==1 and c['current_owner_bytes']==76 and c['current_owner_released'] and c['HeapFree_success_return_u32']==1
 assert c['old_74byte_geometry_negative_rejected'] and c['no_original_reads_of_released_current_owner_to_frontier'] and not c['native_HeapFree_implementation_executed']
 assert f['camera_frontier']['source_RVA']=='0xcfd52c' and f['camera_frontier']['parent_return_target_RVA']=='0xcfcc9c' and not f['camera_frontier']['full_parent_return_qualified']
 assert n['experiment']=='E011FB' and n['current_camera_frontier']['source_RVA']=='0xcfd52c' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FA_PORTABLE_REVIEW','cases':4,'rejects':1112,'producer_rejects':264,'next':'E011FB'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
