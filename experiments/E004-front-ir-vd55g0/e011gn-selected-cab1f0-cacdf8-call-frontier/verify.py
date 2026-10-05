#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GN' and s['status']=='PASS_SELECTED_CAB1F0_CASE_TO_CACDF8_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==16
 assert s['case_entry_RVA']=='0xcab1f0' and s['case_prefix_executed'] and s['helper_call_RVA']=='0xcab1f4' and s['helper_target_RVA']=='0xcacdf8' and s['x0_selects_receiver'] and not s['helper_call_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7 and s['helper_first_receiver_read_RVA']=='0xcace10' and s['helper_first_receiver_read_offset']=='0x18' and not s['helper_receiver_pointer_value_qualified'] and s['helper_next_memory_read_RVA']=='0xcace28'
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==30 and x['x0_selects_receiver'] and not x['helper_call_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GO' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['x0_selects_receiver'] and not f['camera_frontier']['helper_call_executed'] and f['helper_source_frontier']['first_receiver_read_offset']=='0x18' and not f['helper_source_frontier']['receiver_pointer_value_qualified']
 assert n['experiment']=='E011GO' and n['next_dependency']['expected_initial_receiver_relative']=='0x648' and n['next_dependency']['memory_read_RVA']=='0xcace28' and not n['next_dependency']['read_executed']
 return {'status':'PASS_E011GN_PORTABLE_REVIEW','cases':4,'rejects':16,'next':'E011GO'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
