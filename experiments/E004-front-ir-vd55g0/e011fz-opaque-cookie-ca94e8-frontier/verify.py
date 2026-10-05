#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FZ' and s['status']=='PASS_OPAQUE_COOKIE_TO_CA94E8_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==48
 assert s['cookie_producer_executed'] and s['cookie_producer_instruction_visits_per_case']==6 and s['cookie_global_RVA']=='0x1607000' and s['cookie_read_bytes']==8 and not s['cookie_native_value_qualified'] and s['cookie_contract']=='opaque_process_cookie_value'
 assert s['cookie_encoded_stack_formula_qualified'] and s['cookie_control_flow_independent_to_next_frontier'] and s['current_path_instruction_visits_per_case']==38
 assert s['CA6280_resume_RVA']=='0xca6298' and s['CA6280_setup_complete_through_RVA']=='0xca6344' and s['next_camera_source_RVA']=='0xca6348' and s['next_call_target_RVA']=='0xca94e8' and not s['next_call_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['cookie_contract']['native_value_qualified'] and f['camera_frontier']['next_source_RVA']=='0xca6348' and not f['camera_frontier']['next_call_executed'] and n['experiment']=='E011GA' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FZ_PORTABLE_REVIEW','cases':4,'rejects':48,'next':'E011GA'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
