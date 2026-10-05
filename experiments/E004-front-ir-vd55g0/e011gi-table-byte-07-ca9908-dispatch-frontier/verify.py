#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GI' and s['status']=='PASS_TABLE_BYTE_07_TO_CA9908_DISPATCH_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['second_table_RVA']=='0xf8b2a2' and s['second_table_byte_u8']==7 and s['second_table_read_RVA']=='0xca95d8' and s['second_table_read_executed']
 assert s['parser_state_after_u8']==7 and s['parser_state_lt8_qualified'] and s['parser_state_le7_qualified'] and s['jump_table_base_RVA']=='0xca98ec' and s['jump_table_index_u32']==7
 assert s['next_camera_source_RVA']=='0xca95f4' and s['next_dependency_read_RVA']=='0xca9908' and s['next_dependency_bytes']==4 and s['next_dependency_signed'] and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==7 and x['jump_table_entry_RVA']=='0xca9908' and not x['dispatch_entry_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GJ' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['jump_table_index_u32']==7 and f['camera_frontier']['next_dependency_read_RVA']=='0xca9908' and not f['camera_frontier']['next_dependency_read_executed']
 assert n['experiment']=='E011GJ' and n['current_camera_frontier']['source_RVA']=='0xca95f4' and n['current_camera_frontier']['dependency_read_RVA']=='0xca9908' and not n['must_qualify_before_execution']['exact_value_known_publicly']
 return {'status':'PASS_E011GI_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GJ'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
