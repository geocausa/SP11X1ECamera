#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GQ' and s['status']=='PASS_CA65A8_ZERO_TO_F5E3E0_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==40
 assert s['leaf_call_RVA']=='0xcace48' and s['leaf_target_RVA']=='0xca65a8' and s['leaf_executed'] and s['leaf_input_x0_u64']==36 and s['leaf_input_w1_u32']==115 and s['leaf_input_w2_u32']==0 and s['leaf_return_u8']==0
 assert s['zero_result_branch_RVA']=='0xcace54' and s['zero_result_branch_taken'] and s['x20_nonzero_branch_RVA']=='0xcace7c' and s['x20_nonzero_branch_taken'] and s['receiver_plus_0x4c_u8']==0
 assert s['next_camera_source_RVA']=='0xcace90' and s['next_call_target_RVA']=='0xf5e3e0' and s['next_call_x0_RVA']=='0x1370780' and s['next_call_x1_u64']==0x7fffffff and not s['next_call_executed']
 assert s['next_dependency_read_RVA']=='0x1370780' and s['next_dependency_bytes']==16 and not s['next_dependency_read_executed'] and s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==70 and x['leaf_return_u8']==0 and x['zero_result_branch_taken'] and x['x20_nonzero_branch_taken'] and not x['next_call_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GR' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['leaf_return_u8']==0 and f['camera_frontier']['next_call_RVA']=='0xcace90' and not f['camera_frontier']['next_call_executed'] and not f['source_frontier']['read_executed']
 assert n['experiment']=='E011GR' and n['next_dependency']['image_RVA']=='0x1370780' and n['stop_frontier']['resume_RVA']=='0xcace94' and not n['stop_frontier']['store_executed']
 return {'status':'PASS_E011GQ_PORTABLE_REVIEW','cases':4,'rejects':40,'next':'E011GR'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
