#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GS' and s['status']=='PASS_CACE94_LENGTH1_RETURN_TO_CAB288_X22_WRITE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['result_store_RVA']=='0xcace94' and s['result_store_executed'] and s['receiver_plus_0x48_u32']==1 and s['helper_return_RVA']=='0xcaceac' and s['helper_return_target_RVA']=='0xcab1f8' and s['helper_return_u8']==1
 assert s['common_resume_RVA']=='0xcab274' and not s['truth_zero_branch_taken'] and s['receiver_plus_0x38_u8']==0 and not s['receiver_nonzero_branch_taken'] and s['receiver_plus_0x28_low_u32']==0
 assert s['x22_source_RVA']=='0xcab19c' and s['x22_is_helper_local_SP'] and s['x22_local_qword0_s64']==-2 and s['next_camera_source_RVA']=='0xcab288' and s['next_write_offset']=='0x8' and s['next_write_bytes']==2 and not s['next_write_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==13 and x['receiver_plus_0x48_u32']==1 and x['x22_helper_local_relative']==0 and not x['first_x22_write_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GT' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['x22_authority']['is_helper_local_SP'] and not f['x22_authority']['write_executed']
 assert n['experiment']=='E011GT' and n['expected_call_frontier']['call_RVA']=='0xcab3ec' and n['expected_call_frontier']['x4_receiver_relative']=='0x4c0'
 return {'status':'PASS_E011GS_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011GT'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
