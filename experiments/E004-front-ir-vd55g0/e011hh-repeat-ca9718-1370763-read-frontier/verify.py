#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HH' and s['status']=='PASS_REPEAT_CA9718_CASE_TO_1370763_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['case_entry_RVA']=='0xca9718' and s['selected_case_executed'] and s['owned_receiver_plus_0x28_u64']==0 and s['owned_receiver_plus_0x30_u64']==4294967295 and s['owned_receiver_plus_0x38_u8']==0 and s['owned_receiver_plus_0x4c_u8']==0
 assert s['receiver_plus_0x20_u32_preserved']==1 and s['parser_state_u8_preserved']==1 and s['resume_pointer_load_executed'] and s['retained_source_pointer_RVA']=='0x1370763'
 assert s['next_camera_source_RVA']=='0xca984c' and s['next_dependency_RVA']=='0x1370763' and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['case_executed'] and x['receiver_plus_0x20_u32_preserved']==1 and x['parser_state_u8_preserved']==1 and x['pointer_RVA']=='0x1370763' and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HI' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['read_frontier']['read_executed'] and n['experiment']=='E011HI' and n['source_hint']['expected_u8']==115 and n['expected_first_lookup']['lookup_RVA']=='0xf8b2b7'
 return {'status':'PASS_E011HH_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011HI'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
