#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FN' and s['status']=='PASS_LOOP_COUNTER_SECOND_X23_TO_600424_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1904
 assert s['loop_counter_before_u32']==2 and s['loop_counter_after_decrement_u32']==1 and s['loop_back_taken'] and s['loop_back_target_RVA']=='0x600418'
 assert s['second_iteration_entered'] and s['second_x23_before_RVA']=='0x10f03a8' and s['second_x23_read_value_RVA']=='0x1370780' and s['second_x23_after_RVA']=='0x10f03b0'
 assert s['second_x23_table_entry_sha256']=='f21f688470a8c5fa55d98e4d5a653b527282349e85882e6709a4284b0c7f2fdf' and s['next_source_RVA']=='0x600424'
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FO' and f['camera_frontier']['source_RVA']=='0x600424' and n['experiment']=='E011FO'
 return {'status':'PASS_E011FN_PORTABLE_REVIEW','cases':4,'rejects':1904,'next':'E011FO'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
