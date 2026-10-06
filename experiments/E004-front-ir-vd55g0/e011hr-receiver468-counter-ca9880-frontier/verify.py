#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HR' and s['status']=='PASS_RECEIVER468_COUNTER1_TO_CA9880_RETURN_LOAD_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['counter_receiver_relative']=='0x468' and s['counter_before_u32']==1 and s['counter_read_executed'] and s['counter_after_u32']==2 and s['counter_store_executed'] and s['branch_equal_taken']
 assert s['receiver_plus_0x20_u32']==26 and s['next_camera_source_RVA']=='0xca9880' and s['next_return_load_receiver_relative']=='0x20' and not s['next_return_load_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['counter_before_u32']==1 and x['counter_after_u32']==2 and x['branch_equal_taken'] and not x['target_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HS' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['return_load_frontier']['executed'] and n['experiment']=='E011HS' and n['expected_return']['target_RVA']=='0xca634c'
 return {'status':'PASS_E011HR_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011HS'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
