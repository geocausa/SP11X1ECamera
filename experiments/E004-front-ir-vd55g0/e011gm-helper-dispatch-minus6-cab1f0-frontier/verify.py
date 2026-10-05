#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GM' and s['status']=='PASS_HELPER_DISPATCH_MINUS6_TO_CAB1F0_CASE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['helper_dispatch_table_base_RVA']=='0xcab65c' and s['helper_dispatch_index_u32']==50 and s['dispatch_entry_RVA']=='0xcab724' and s['dispatch_entry_s32']==-6
 assert s['dispatch_read_RVA']=='0xcab1c4' and s['dispatch_read_executed'] and s['dispatch_calc_base_RVA']=='0xcab208' and s['dispatch_scale']==4 and s['dispatch_target_RVA']=='0xcab1f0' and s['dispatch_branch_RVA']=='0xcab1d0' and s['dispatch_branch_executed'] and not s['selected_case_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7 and s['selected_case_helper_call_RVA']=='0xcab1f4' and s['selected_case_helper_target_RVA']=='0xcacdf8'
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==29 and x['dispatch_entry_s32']==-6 and x['dispatch_target_RVA']=='0xcab1f0' and not x['selected_case_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GN' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['helper_dispatch_frontier']['entry_s32']==-6 and f['helper_dispatch_frontier']['target_RVA']=='0xcab1f0' and not f['helper_dispatch_frontier']['selected_case_executed']
 assert n['experiment']=='E011GN' and n['current_camera_frontier']['selected_case_entry_RVA']=='0xcab1f0' and n['current_camera_frontier']['helper_call_RVA']=='0xcab1f4' and not n['current_camera_frontier']['helper_call_executed']
 return {'status':'PASS_E011GM_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GN'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
