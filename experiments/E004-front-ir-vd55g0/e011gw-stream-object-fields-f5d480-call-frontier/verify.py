#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GW' and s['status']=='PASS_STREAM_OBJECT_FIELDS_TO_F5D480_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==36
 assert s['object_receiver_relative']=='-0x20' and s['object_qword0_receiver_relative']=='0x6b0' and s['object_plus_0x8_u64']==640 and s['object_plus_0x10_u64']==0
 assert s['object_field_read_RVA']=='0xcad21c' and s['object_field_read_executed'] and s['object_qword0_read_RVA']=='0xcad248' and s['object_qword0_read_executed']
 assert s['unequal_branch_RVA']=='0xcad224' and s['unequal_branch_taken'] and s['selected_copy_bytes_u64']==1
 assert s['next_camera_source_RVA']=='0xcad25c' and s['next_call_target_RVA']=='0xf5d480' and s['next_call_x0_receiver_relative']=='0x6b0' and s['next_call_x1_value_RVA']=='0x1370780' and s['next_call_x2_u64']==1 and not s['next_call_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==9 and x['unequal_branch_taken'] and not x['copy_call_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011GX' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['copy_call_frontier']['call_executed'] and n['experiment']=='E011GX' and n['source_dependency']['expected_u8']==46 and n['expected_resume_frontier']['RVA']=='0xcad260'
 return {'status':'PASS_E011GW_PORTABLE_REVIEW','cases':4,'rejects':36,'next':'E011GX'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
