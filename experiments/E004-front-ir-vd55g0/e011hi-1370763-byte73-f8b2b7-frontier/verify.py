#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HI' and s['status']=='PASS_1370763_BYTE73_TO_F8B2B7_FIRST_LOOKUP_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['source_RVA']=='0x1370763' and s['source_u8']==115 and s['source_s8']==115 and s['source_read_executed'] and s['pointer_after_RVA']=='0x1370764'
 assert s['receiver_plus_0x39_u8']==115 and s['receiver_plus_0x20_u32']==1 and s['parser_state_u8']==1 and s['lookup_index_u64']==166 and s['lookup_base_RVA']=='0xf8b211'
 assert s['next_camera_source_RVA']=='0xca95b8' and s['next_dependency_RVA']=='0xf8b2b7' and s['next_dependency_bytes']==1 and not s['next_dependency_read_executed'] and s['retained_source_pointer_RVA']=='0x1370764'
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['source_u8']==115 and x['first_table_RVA']=='0xf8b2b7' and not x['first_table_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HJ' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['first_lookup_frontier']['read_executed'] and n['experiment']=='E011HJ' and n['source_hint']['expected_u8']==8 and n['expected_second_lookup']['second_table_RVA']=='0xf8b2a2'
 return {'status':'PASS_E011HI_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011HJ'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
