#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GG' and s['status']=='PASS_SOURCE_BYTE_73_TO_F8B2B7_LOOKUP_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['source_RVA']=='0x1370761' and s['source_byte_u8']==115 and s['source_byte_s8']==115 and s['source_read_RVA']=='0xca984c' and s['source_read_executed']
 assert s['source_pointer_advanced_RVA']=='0x1370762' and s['source_nonzero_branch_RVA']=='0xca9858' and s['source_nonzero_branch_taken']
 assert s['parser_control_plus_0x20_u32']==0 and s['parser_state_plus_0x24_u32']==1 and s['lookup_offset_u64']==166 and s['lookup_base_RVA']=='0xf8b211'
 assert s['next_camera_source_RVA']=='0xca95b8' and s['next_dependency_read_RVA']=='0xf8b2b7' and s['next_dependency_bytes']==1 and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==14 and x['lookup_RVA']=='0xf8b2b7' and not x['next_table_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GH' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['source_byte_u8']==115 and f['camera_frontier']['next_dependency_read_RVA']=='0xf8b2b7' and not f['camera_frontier']['next_dependency_read_executed']
 assert n['experiment']=='E011GH' and n['current_camera_frontier']['source_RVA']=='0xca95b8' and n['current_camera_frontier']['dependency_read_RVA']=='0xf8b2b7' and not n['must_qualify_before_execution']['exact_value_known_publicly']
 return {'status':'PASS_E011GG_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011GH'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
