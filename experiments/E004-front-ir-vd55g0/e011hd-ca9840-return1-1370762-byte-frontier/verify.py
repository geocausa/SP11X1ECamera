#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HD' and s['status']=='PASS_CA9840_RETURN1_TO_1370762_BYTE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['input_w0_u32']==1 and s['uxtb_RVA']=='0xca9840' and s['uxtb_w8_u8']==1 and s['zero_branch_RVA']=='0xca9844' and not s['zero_branch_taken']
 assert s['pointer_reload_RVA']=='0xca9848' and s['pointer_reload_executed'] and s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert s['next_camera_source_RVA']=='0xca984c' and s['next_dependency_RVA']=='0x1370762' and s['next_dependency_bytes']==1 and s['next_dependency_signed'] and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['uxtb_w8_u8']==1 and not x['zero_branch_taken'] and x['pointer_RVA']=='0x1370762' and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HE' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['byte_frontier']['read_executed'] and n['experiment']=='E011HE' and n['source_hint']['expected_u8']==37 and n['expected_path']['target_RVA']=='0xca9590'
 return {'status':'PASS_E011HD_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011HE'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
