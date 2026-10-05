#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HO' and s['status']=='PASS_1370765_BYTE73_TO_CA9838_HELPER_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==36
 assert s['source_RVA']=='0x1370765' and s['source_u8']==115 and s['source_read_executed'] and s['pointer_after_RVA']=='0x1370766' and s['receiver_plus_0x20_u32']==2
 assert s['first_table_RVA']=='0xf8b2b7' and s['first_table_u8']==8 and s['second_table_RVA']=='0xf8b2a2' and s['second_table_u8']==7 and s['dispatch_entry_RVA']=='0xca9908' and s['dispatch_entry_s32']==20 and s['parser_state_after_u8']==7
 assert s['retained_source_pointer_RVA']=='0x1370766' and s['next_camera_source_RVA']=='0xca9838' and not s['selected_target_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['source_u8']==115 and x['parser_state_after_u8']==7 and x['target_RVA']=='0xca9838' and not x['target_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HP' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['helper_frontier']['executed'] and n['experiment']=='E011HP' and n['expected_source']['vararg_value_RVA']=='0x13f1f28' and n['expected_source']['string_length_u64']==24
 return {'status':'PASS_E011HO_PORTABLE_REVIEW','cases':4,'rejects':36,'next':'E011HP'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
