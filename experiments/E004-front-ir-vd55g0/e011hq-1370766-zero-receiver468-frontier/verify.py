#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HQ' and s['status']=='PASS_1370766_ZERO_TO_RECEIVER468_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['source_RVA']=='0x1370766' and s['source_u8']==0 and s['source_read_executed'] and s['pointer_after_RVA']=='0x1370767' and s['receiver_plus_0x39_u8']==0
 assert not s['nonzero_branch_taken'] and s['parser_state_u8']==7 and not s['state_reject_branch_taken'] and s['receiver_plus_0x20_u32']==26
 assert s['next_camera_source_RVA']=='0xca986c' and s['next_dependency_receiver_relative']=='0x468' and s['next_dependency_bytes']==4 and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['source_u8']==0 and not x['nonzero_branch_taken'] and x['parser_state_u8']==7 and not x['state_reject_branch_taken'] and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HR' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['counter_frontier']['read_executed'] and n['experiment']=='E011HR' and n['expected_path']['counter_before_u32']==1 and n['expected_path']['target_RVA']=='0xca9880'
 return {'status':'PASS_E011HQ_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011HR'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
