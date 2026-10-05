#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GU' and s['status']=='PASS_CAD1F0_ZERO_COUNT_TO_SECOND_CAD1F0_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==44
 assert s['first_call_RVA']=='0xcab3ec' and s['first_target_RVA']=='0xcad1f0' and s['first_call_x2_u64']==0 and s['first_call_executed'] and s['zero_count_branch_RVA']=='0xcad214' and s['zero_count_branch_taken'] and not s['stream_slot_or_object_read_during_first_call']
 assert s['receiver_plus_0x28_u64']==0 and s['receiver_bit3_zero_branch_taken'] and s['receiver_plus_0x4c_u8']==0 and s['receiver_plus_0x4c_zero_branch_taken']
 assert s['stream_slot_receiver_relative']=='0x460' and s['stream_object_receiver_relative']=='-0x20'
 assert s['next_camera_source_RVA']=='0xcab58c' and s['next_call_target_RVA']=='0xcad1f0' and s['next_call_x0_receiver_relative']=='0x460' and s['next_call_x1_value_RVA']=='0x1370780' and s['next_call_x2_u64']==1 and s['next_call_x3_receiver_relative']=='0x20' and s['next_call_x4_receiver_relative']=='0x4c0' and not s['next_call_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==27 and x['zero_count_branch_taken'] and not x['stream_slot_read_during_first_call'] and x['receiver_bit3_zero_branch_taken'] and x['receiver_plus_0x4c_zero_branch_taken'] and not x['second_call_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GV' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['second_call_frontier']['x2_u64']==1 and not f['second_call_frontier']['call_executed'] and f['stream_pointer_authority']['slot_value_receiver_relative']=='-0x20'
 assert n['experiment']=='E011GV' and n['next_dependency']['pointer_load_RVA']=='0xcad218' and n['next_dependency']['object_field_read_RVA']=='0xcad21c' and not n['next_dependency']['object_field_read_executed']
 return {'status':'PASS_E011GU_PORTABLE_REVIEW','cases':4,'rejects':44,'next':'E011GV'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
