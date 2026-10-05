#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HF' and s['status']=='PASS_CA9590_STATE7_TO_F8B230_SECOND_LOOKUP_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['receiver_plus_0x20_u32']==1 and s['source_byte_u8']==37 and s['first_table_RVA']=='0xf8b21b' and s['first_table_u8']==1 and s['first_table_read_executed']
 assert s['parser_state_before_u8']==7 and s['scaled_first_table_u64']==9 and s['second_lookup_offset_u64']==32
 assert s['next_camera_source_RVA']=='0xca95d8' and s['next_dependency_RVA']=='0xf8b230' and s['next_dependency_bytes']==1 and not s['next_dependency_read_executed']
 assert s['retained_source_pointer_RVA']=='0x1370763'
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['first_table_u8']==1 and x['parser_state_before_u8']==7 and x['second_table_RVA']=='0xf8b230' and not x['second_table_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HG' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['second_lookup_frontier']['read_executed'] and n['experiment']=='E011HG' and n['source_hint']['expected_u8']==1 and n['expected_dispatch']['selected_target_RVA']=='0xca9718'
 return {'status':'PASS_E011HF_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011HG'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
