#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GL' and s['status']=='PASS_CAB178_HELPER_TO_CAB724_SIGNED_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['helper_entry_RVA']=='0xcab178' and s['helper_entry_executed'] and s['helper_prefix_end_RVA']=='0xcab1c0' and s['helper_cookie_producer_RVA']=='0x11d0' and s['helper_cookie_producer_executed']
 assert s['receiver_retained'] and s['receiver_plus_0x39_read_RVA']=='0xcab1ac' and s['receiver_plus_0x39_u8']==115 and s['receiver_plus_0x39_s8']==115
 assert s['helper_range_index_u32']==50 and s['helper_range_upper_u32']==55 and s['helper_range_branch_RVA']=='0xcab1bc' and not s['helper_range_branch_taken'] and s['helper_dispatch_base_RVA']=='0xcab65c'
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert s['next_camera_source_RVA']=='0xcab1c4' and s['next_dependency_RVA']=='0xcab724' and s['next_dependency_bytes']==4 and s['next_dependency_signed'] and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==25 and x['receiver_byte_u8']==115 and x['range_index_u32']==50 and not x['next_dependency_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GM' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['receiver_plus_0x39_u8']==115 and f['camera_frontier']['range_index_u32']==50 and f['source_frontier']['next_dependency_RVA']=='0xcab724' and not f['source_frontier']['read_executed']
 assert n['experiment']=='E011GM' and n['current_camera_frontier']['helper_dispatch_read_RVA']=='0xcab1c4' and n['current_camera_frontier']['helper_dispatch_index_u32']==50 and n['next_dependency']['image_RVA']=='0xcab724'
 return {'status':'PASS_E011GL_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011GM'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
