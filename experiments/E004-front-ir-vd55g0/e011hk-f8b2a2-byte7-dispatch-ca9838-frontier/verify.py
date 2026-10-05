#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HK' and s['status']=='PASS_F8B2A2_BYTE7_DISPATCH_PLUS20_TO_CA9838_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['second_table_RVA']=='0xf8b2a2' and s['second_table_u8']==7 and s['second_table_read_executed'] and s['parser_state_after_u8']==7
 assert s['dispatch_entry_RVA']=='0xca9908' and s['dispatch_entry_s32']==20 and s['dispatch_read_executed'] and s['dispatch_branch_RVA']=='0xca9600' and s['dispatch_branch_executed']
 assert s['next_camera_source_RVA']=='0xca9838' and not s['selected_target_executed'] and s['retained_source_pointer_RVA']=='0x1370764' and s['receiver_plus_0x20_u32']==1
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['second_table_u8']==7 and x['dispatch_entry_s32']==20 and x['selected_target_RVA']=='0xca9838' and not x['selected_target_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HL' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['dispatch']['target_executed'] and n['experiment']=='E011HL' and n['expected_vararg_frontier']['vararg_receiver_relative']=='0x650'
 return {'status':'PASS_E011HK_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011HL'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
