#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GZ' and s['status']=='PASS_OBJECT_FLAG_ZERO_TO_RECEIVER20_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['flag_producer_store_RVA']=='0xca6300' and s['flag_producer_executed'] and s['object_flag_receiver_relative']=='-0x8' and s['object_flag_u8']==0
 assert s['flag_read_RVA']=='0xcad284' and s['flag_read_executed'] and not s['flag_nonzero_branch_taken'] and s['x22_u64']==s['x23_u64']==1 and not s['inequality_branch_taken']
 assert s['next_camera_source_RVA']=='0xcad294' and s['next_dependency_receiver_relative']=='0x20' and s['next_dependency_bytes']==4 and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['flag_u8']==0 and not x['flag_nonzero_branch_taken'] and not x['inequality_branch_taken'] and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HA' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['receiver20_frontier']['read_executed'] and n['experiment']=='E011HA' and n['source_hint']['expected_u32']==0 and n['expected_store_frontier']['expected_after_u32']==1
 return {'status':'PASS_E011GZ_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011HA'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
