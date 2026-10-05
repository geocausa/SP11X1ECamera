#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HB' and s['status']=='PASS_CAD1F0_EPILOGUE_TO_CAB62C_RETURN_VALUE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['epilogue_first_RVA']=='0xcad2a0' and s['epilogue_return_RVA']=='0xcad2b4' and s['epilogue_executed'] and s['return_target_RVA']=='0xcab590' and s['return_target_executed']
 assert s['receiver_plus_0x20_u32']==1 and s['receiver_plus_0x28_u32']==0 and not s['sign_branch_taken'] and s['bit2_zero_branch_taken']
 assert s['next_camera_source_RVA']=='0xcab62c' and s['next_return_value_u32']==1 and not s['next_return_value_store_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['epilogue_executed'] and x['return_target_executed'] and not x['sign_branch_taken'] and x['bit2_zero_branch_taken'] and not x['next_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HC' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['parent_branch']['target_executed'] and n['experiment']=='E011HC' and n['expected_helper_return']['target_RVA']=='0xca9840' and not n['expected_helper_return']['target_executed']
 return {'status':'PASS_E011HB_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011HC'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
