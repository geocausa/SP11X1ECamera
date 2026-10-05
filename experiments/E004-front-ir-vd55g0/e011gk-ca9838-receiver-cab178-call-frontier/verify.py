#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GK' and s['status']=='PASS_CA9838_RECEIVER_TO_CAB178_CALL_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==16
 assert s['case_prefix_RVA']=='0xca9838' and s['case_prefix_executed'] and s['helper_call_RVA']=='0xca983c' and s['helper_target_RVA']=='0xcab178' and s['x0_selects_receiver'] and not s['helper_call_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_source_byte_u8']==115 and s['retained_parser_state_u8']==7
 assert s['helper_cookie_producer_RVA']=='0x11d0' and s['helper_range_index_u32']==50 and s['helper_next_dependency_read_RVA']=='0xcab1c4' and s['helper_next_dependency_RVA']=='0xcab724' and s['helper_next_dependency_bytes']==4 and s['helper_next_dependency_signed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==1 and x['x0_selects_receiver'] and not x['helper_call_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GL' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['x0_selects_receiver'] and not f['camera_frontier']['helper_call_executed'] and f['helper_source_frontier']['next_dependency_RVA']=='0xcab724' and not f['helper_source_frontier']['next_dependency_read_executed']
 assert n['experiment']=='E011GL' and n['current_camera_frontier']['helper_entry_RVA']=='0xcab178' and not n['current_camera_frontier']['helper_call_executed'] and n['next_dependency']['image_RVA']=='0xcab724' and not n['next_dependency']['read_executed']
 return {'status':'PASS_E011GK_PORTABLE_REVIEW','cases':4,'rejects':16,'next':'E011GL'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
