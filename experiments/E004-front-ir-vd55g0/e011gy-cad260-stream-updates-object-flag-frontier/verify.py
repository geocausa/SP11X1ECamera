#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GY' and s['status']=='PASS_CAD260_STREAM_UPDATES_TO_OBJECT_FLAG_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['object_qword0_before_receiver_relative']=='0x6b0' and s['object_qword0_after_receiver_relative']=='0x6b1' and s['pointer_store_RVA']=='0xcad26c' and s['pointer_store_executed']
 assert s['object_count_before_u64']==0 and s['object_count_after_u64']==1 and s['count_store_RVA']=='0xcad27c' and s['count_store_executed']
 assert s['slot_reload_RVA']=='0xcad280' and s['slot_reload_executed'] and s['next_camera_source_RVA']=='0xcad284' and s['next_dependency_receiver_relative']=='-0x8' and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==9 and x['object_count_after_u64']==1 and not x['flag_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011GZ' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['object_flag_frontier']['read_executed'] and n['experiment']=='E011GZ' and n['source_hint']['expected_flag_u8']==0 and n['expected_branch_frontier']['next_read_RVA']=='0xcad294'
 return {'status':'PASS_E011GY_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011GZ'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
