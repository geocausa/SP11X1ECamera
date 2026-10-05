#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HN' and s['status']=='PASS_1370764_BYTE25_REPEAT_CASE_TO_1370765_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==40
 assert s['source_RVA']=='0x1370764' and s['source_u8']==37 and s['source_read_executed'] and s['pointer_after_RVA']=='0x1370765' and s['receiver_plus_0x20_u32']==2
 assert s['first_table_RVA']=='0xf8b21b' and s['first_table_u8']==1 and s['second_table_RVA']=='0xf8b230' and s['second_table_u8']==1 and s['dispatch_entry_s32']==-52 and s['selected_case_RVA']=='0xca9718' and s['selected_case_executed'] and s['parser_state_after_u8']==1
 assert s['retained_source_pointer_RVA']=='0x1370765' and s['next_camera_source_RVA']=='0xca984c' and s['next_dependency_RVA']=='0x1370765' and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['source_u8']==37 and x['selected_case_executed'] and x['receiver_plus_0x20_u32']==2 and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HO' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['next_read']['executed'] and n['experiment']=='E011HO' and n['source_hint']['expected_u8']==115 and n['expected_helper_frontier']['dispatch_target_RVA']=='0xca9838'
 return {'status':'PASS_E011HN_PORTABLE_REVIEW','cases':4,'rejects':40,'next':'E011HO'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
