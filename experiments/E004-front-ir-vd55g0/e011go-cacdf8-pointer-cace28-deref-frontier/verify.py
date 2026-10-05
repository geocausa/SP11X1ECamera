#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GO' and s['status']=='PASS_CACDF8_RECEIVER_POINTER_TO_CACE28_DEREF_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['helper_entry_RVA']=='0xcacdf8' and s['helper_entry_executed'] and s['helper_prefix_end_RVA']=='0xcace24' and s['helper_frame_SP_relative_to_entry']==-48 and s['helper_frame_X29_relative_to_entry']==-48
 assert s['receiver_relative_to_CA6280_entry']==-1200 and s['receiver_plus_0x18_pointer_CA6280_SP_relative']==408 and s['receiver_plus_0x18_initial_receiver_relative']==1608 and s['receiver_plus_0x18_alignment_delta_u64']==0 and s['receiver_plus_0x18_updated_receiver_relative']==1616
 assert s['next_camera_source_RVA']=='0xcace28' and s['next_dependency_receiver_relative']==1608 and s['next_dependency_bytes']==8 and s['next_dependency_read_RVA']=='0xcace28' and not s['next_dependency_read_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==43 and x['receiver_plus_0x18_initial_receiver_relative']=='0x648' and x['receiver_plus_0x18_updated_receiver_relative']=='0x650' and not x['next_memory_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GP' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['receiver_plus_0x18_initial_receiver_relative']=='0x648' and f['source_frontier']['next_memory_read_RVA']=='0xcace28' and not f['source_frontier']['read_executed']
 assert n['experiment']=='E011GP' and n['current_camera_frontier']['dependency_receiver_relative']=='0x648' and n['known_downstream_source']['call_frontier_RVA']=='0xcace48'
 return {'status':'PASS_E011GO_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GP'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
