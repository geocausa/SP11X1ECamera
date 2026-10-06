#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def S(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json');assert s['experiment']=='E011HT' and s['status']=='PASS_CA634C_CALLER_BRANCH_TO_SP478_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==36
 assert s['bit0_zero_branch_taken'] and s['x21_u64']==0 and s['x21_zero_branch_taken'] and s['x19_u64']==640 and not s['x19_zero_branch_taken'] and s['frame_plus_0x10_u64']==0 and s['mismatch_branch_taken'] and s['zero_write_executed'] and s['zero_write_output_offset']==0 and s['w21_after_u32']==26
 assert s['next_camera_source_RVA']=='0xca63d8' and s['next_dependency_SP_relative']=='0x478' and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['mismatch_branch_taken'] and x['zero_write_output_offset']==0 and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(nm)
 assert r['next_experiment']=='E011HU' and not r['native_rear_runtime_allowed'] and not f['frame_frontier']['read_executed'] and n['expected_path']['frame_slot_u64']==0
 return {'status':'PASS_E011HT_PORTABLE_REVIEW','cases':4,'rejects':36,'next':'E011HU'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
