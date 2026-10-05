#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GP' and s['status']=='PASS_CACE28_QWORD_1370780_TO_CA65A8_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==40
 assert s['formatter_x3_RVA']=='0x1370780' and s['formatter_wrapper_slot_retains_x3'] and s['receiver_dependency_relative']=='0x648' and s['dependency_value_RVA']=='0x1370780'
 assert s['dependency_read_RVA']=='0xcace28' and s['dependency_read_bytes']==8 and s['dependency_read_executed'] and s['receiver_plus_0x40_value_RVA']=='0x1370780'
 assert s['receiver_plus_0x39_u8']==115 and s['receiver_qword0_u64']==36 and s['receiver_plus_0x30_low_u32']==0xffffffff and s['receiver_plus_0x34_u32']==0 and s['selected_w21_u32']==0x7fffffff
 assert s['next_camera_source_RVA']=='0xcace48' and s['next_call_target_RVA']=='0xca65a8' and not s['next_call_executed'] and s['next_call_x0_u64']==36 and s['next_call_w1_u32']==115 and s['next_call_w2_u32']==0
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==51 and x['dependency_value_RVA']=='0x1370780' and x['selected_w21_u32']==0x7fffffff and not x['call_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GQ' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['source_authority']['dependency_value_RVA']=='0x1370780' and f['camera_frontier']['call_frontier_RVA']=='0xcace48' and not f['camera_frontier']['call_executed']
 assert n['experiment']=='E011GQ' and n['current_camera_frontier']['call_target_RVA']=='0xca65a8' and n['source_hint']['expected_downstream_call_RVA']=='0xcace90'
 return {'status':'PASS_E011GP_PORTABLE_REVIEW','cases':4,'rejects':40,'next':'E011GQ'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
