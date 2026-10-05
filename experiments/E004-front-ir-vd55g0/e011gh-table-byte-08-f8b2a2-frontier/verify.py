#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GH' and s['status']=='PASS_TABLE_BYTE_08_TO_F8B2A2_SECOND_LOOKUP_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['first_table_RVA']=='0xf8b2b7' and s['first_table_byte_u8']==8 and s['first_table_read_RVA']=='0xca95b8' and s['first_table_read_executed']
 assert s['scaled_lookup_u64']==72 and s['parser_state_plus_0x24_u8']==1 and s['second_lookup_offset_u64']==146
 assert s['next_camera_source_RVA']=='0xca95d8' and s['next_dependency_read_RVA']=='0xf8b2a2' and s['next_dependency_bytes']==1 and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==7 and x['second_lookup_RVA']=='0xf8b2a2' and not x['second_table_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GI' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_dependency_read_RVA']=='0xf8b2a2' and not f['camera_frontier']['next_dependency_read_executed']
 assert n['experiment']=='E011GI' and n['current_camera_frontier']['source_RVA']=='0xca95d8' and n['current_camera_frontier']['dependency_read_RVA']=='0xf8b2a2' and not n['must_qualify_before_execution']['exact_value_known_publicly']
 return {'status':'PASS_E011GH_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GI'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
