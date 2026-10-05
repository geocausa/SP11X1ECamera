#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FV' and s['status']=='PASS_CAD868_X0_36_PREFIX_TO_16A2A84_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2584
 assert s['pins']['fv_cad868_prefix']==[0xcad868,0x50,'97422351811d9f2018cc2f09908cfb330b5eb52e644948e381a9d7b172a2a0df']
 assert s['CAD868_entry_executed'] and s['CAD868_entry_x0_u64']==36 and s['CAD868_prefix_instruction_visits']==72 and s['CAD868_exact_stack_write_chunks']==48 and s['CAD868_x5_zero_branch_taken']
 assert all(x['CAD868_entry_x0_u64']==36 and x['CAD868_prefix_instruction_visits']==18 and x['CAD868_exact_stack_write_chunks']==12 and x['rejected_altered_contracts']==646 for x in s['details'])
 assert s['next_source_RVA']=='0xcad8b8' and s['next_dependency_read_RVA']=='0x16a2a84' and s['next_dependency_bytes']==4 and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['older_E011DY_16a2a84_zero_is_loader_model_not_native'] and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_source_RVA']=='0xcad8b8' and not f['camera_frontier']['next_dependency_read_executed'] and n['experiment']=='E011FW'
 return {'status':'PASS_E011FV_PORTABLE_REVIEW','cases':4,'rejects':2584,'prefix_visits':72,'stack_writes':48,'next':'E011FW'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
