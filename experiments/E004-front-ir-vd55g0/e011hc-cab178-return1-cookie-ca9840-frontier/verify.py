#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HC' and s['status']=='PASS_CAB178_RETURN1_COOKIE_TO_CA9840_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['return_value_RVA']=='0xcab62c' and s['return_value_u32']==1 and s['return_value_executed']
 assert s['cookie_checker_RVA']=='0x11f0' and s['cookie_checker_executed'] and s['cookie_axis_count']==4 and s['cookie_check_success_all_axes'] and not s['cookie_failure_executed']
 assert s['CAB178_return_RVA']=='0xcab658' and s['CAB178_return_executed'] and s['CAB178_saved_registers_restored']
 assert s['next_camera_source_RVA']=='0xca9840' and s['next_expected_w0_u32']==1 and not s['next_camera_source_executed']
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['return_value_u32']==1 and x['cookie_check_success'] and not x['cookie_failure_executed'] and x['saved_registers_restored'] and not x['return_target_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HD' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['caller_frontier']['executed'] and n['experiment']=='E011HD' and n['expected_path']['next_read_RVA']=='0xca984c' and not n['expected_path']['next_read_executed']
 return {'status':'PASS_E011HC_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011HD'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
