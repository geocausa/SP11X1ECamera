#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');c=L(H/'CED0D8-RETURN-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fg=ROOT/'experiments/E004-front-ir-vd55g0/e011fg-selected-lock-release-ced194-frontier/RESULT.json'
 assert s['status']=='PASS_CED0D8_ZERO_RETURN_TO_CED330_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1568
 assert s['CED0D8_complete_return_qualified'] and s['CED0D8_return_u64']==0 and s['CED0D8_return_target_RVA']=='0xced330'
 assert s['outer_result_pointer_SP_relative']==-1448 and not s['outer_result_store_executed'] and s['selected_object_lock_released']
 assert r['inherited_E011FG_result_sha256']==sha(fg)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('ced0d8_return_safe_sha256','CED0D8-RETURN-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert c['restored_return_target_RVA']=='0xced330' and c['CED0D8_return_u64']==0 and c['complete_CED0D8_return_qualified'] and c['selected_object_reads_after_release']==0
 assert f['camera_frontier']['source_RVA']=='0xced330' and f['camera_frontier']['x0_u64']==0 and not f['camera_frontier']['store_executed']
 assert n['experiment']=='E011FI' and n['current_camera_frontier']['outer_result_pointer_SP_relative']==-1448 and not n['native_rear_runtime_allowed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FH_PORTABLE_REVIEW','cases':4,'rejects':1568,'producer_rejects':264,'next':'E011FI'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
