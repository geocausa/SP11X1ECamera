#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GJ' and s['status']=='PASS_DISPATCH_PLUS20_TO_CA9838_CASE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==16
 assert s['dispatch_index_u32']==7 and s['dispatch_entry_RVA']=='0xca9908' and s['dispatch_entry_s32']==20 and s['dispatch_read_RVA']=='0xca95f4' and s['dispatch_read_executed']
 assert s['dispatch_base_RVA']=='0xca97e8' and s['dispatch_scale']==4 and s['dispatch_target_RVA']=='0xca9838' and s['dispatch_branch_RVA']=='0xca9600' and s['dispatch_branch_executed'] and not s['selected_case_executed']
 assert s['next_camera_source_RVA']=='0xca9838' and s['selected_case_helper_call_RVA']=='0xca983c' and s['selected_case_helper_target_RVA']=='0xcab178'
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==4 and x['dispatch_target_RVA']=='0xca9838' and not x['selected_case_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GK' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['dispatch_target_RVA']=='0xca9838' and not f['camera_frontier']['selected_case_executed'] and f['camera_frontier']['selected_case_helper_target_RVA']=='0xcab178'
 assert n['experiment']=='E011GK' and n['current_camera_frontier']['source_RVA']=='0xca9838' and n['current_camera_frontier']['helper_call_RVA']=='0xca983c' and not n['current_camera_frontier']['helper_call_executed']
 return {'status':'PASS_E011GJ_PORTABLE_REVIEW','cases':4,'rejects':16,'next':'E011GK'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
