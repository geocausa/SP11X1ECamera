#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json'); r=L('RESULT.json'); f=L('FRONTIER-SAFE.json'); n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GF' and s['status']=='PASS_SELECTED_CA9718_CASE_TO_1370761_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['case_entry_RVA']=='0xca9718' and s['case_last_RVA']=='0xca9728' and s['selected_case_executed'] and s['common_resume_RVA']=='0xca9848'
 assert s['owned_receiver_plus_0x38_u8']==0 and s['owned_receiver_plus_0x28_u64']==0 and s['owned_receiver_plus_0x30_u64']==0xffffffff and s['owned_receiver_plus_0x4c_u8']==0
 assert s['parser_state_u32_retained']==1 and s['retained_prior_source_byte_u8']==37 and s['retained_source_pointer_RVA']=='0x1370761'
 assert s['resume_pointer_load_RVA']=='0xca9848' and s['resume_pointer_load_executed'] and s['next_camera_source_RVA']=='0xca984c'
 assert s['next_dependency_read_RVA']=='0x1370761' and s['next_dependency_bytes']==1 and s['next_dependency_signed'] and not s['next_dependency_read_executed'] and s['source_memory_reads_during_case']==0
 assert len(s['details'])==4 and [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==6 and x['stop_RVA']=='0xca984c' and not x['next_source_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['experiment']=='E011GF' and r['status']==s['status'] and r['case_count']==4 and r['rejected_altered_contracts']==24 and r['next_experiment']=='E011GG'
 assert not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['selected_case_executed'] and f['camera_frontier']['common_resume_RVA']=='0xca9848' and f['camera_frontier']['retained_source_pointer_RVA']=='0x1370761' and f['camera_frontier']['next_source_RVA']=='0xca984c' and not f['camera_frontier']['next_dependency_read_executed']
 assert n['experiment']=='E011GG' and n['current_camera_frontier']['source_RVA']=='0xca984c' and n['current_camera_frontier']['source_pointer_RVA']=='0x1370761' and not n['current_camera_frontier']['source_read_executed'] and not n['must_qualify_before_execution']['exact_value_known_publicly']
 return {'status':'PASS_E011GF_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GG'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
