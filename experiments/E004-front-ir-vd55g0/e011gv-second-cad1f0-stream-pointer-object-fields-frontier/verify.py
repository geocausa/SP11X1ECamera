#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GV' and s['status']=='PASS_SECOND_CAD1F0_STREAM_POINTER_TO_OBJECT_FIELDS_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['call_RVA']=='0xcab58c' and s['call_target_RVA']=='0xcad1f0' and s['call_executed'] and s['call_x2_u64']==1
 assert s['pointer_load_RVA']=='0xcad218' and s['pointer_slot_receiver_relative']=='0x460' and s['pointer_value_receiver_relative']=='-0x20' and s['pointer_load_executed']
 assert s['next_camera_source_RVA']=='0xcad21c' and s['next_dependency_first_receiver_relative']=='-0x18' and s['next_dependency_second_receiver_relative']=='-0x10' and s['next_dependency_bytes']==16 and not s['next_dependency_read_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==12 and x['pointer_load_executed'] and not x['object_field_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GW' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['stream_pointer']['value_receiver_relative']=='-0x20' and not f['object_field_frontier']['read_executed']
 assert n['experiment']=='E011GW' and n['current_camera_frontier']['read_RVA']=='0xcad21c' and n['expected_call_frontier']['call_RVA']=='0xcad25c' and not n['expected_call_frontier']['call_executed']
 return {'status':'PASS_E011GV_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011GW'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
