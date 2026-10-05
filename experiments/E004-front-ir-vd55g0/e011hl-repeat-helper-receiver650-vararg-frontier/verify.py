#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HL' and s['status']=='PASS_REPEAT_CA9838_HELPER_TO_RECEIVER650_VARARG_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==40
 assert s['case_prefix_RVA']=='0xca9838' and s['case_prefix_executed'] and s['CAB178_entry_executed'] and s['helper_range_index_u32']==50 and s['helper_dispatch_entry_s32']==-6 and s['helper_selected_case_RVA']=='0xcab1f0' and s['helper_selected_case_executed']
 assert s['CACDF8_entry_executed'] and s['receiver_plus_0x18_before_relative']=='0x650' and s['receiver_plus_0x18_after_relative']=='0x658'
 assert s['next_camera_source_RVA']=='0xcace28' and s['next_dependency_receiver_relative']=='0x650' and s['next_dependency_bytes']==8 and not s['next_dependency_read_executed']
 assert s['retained_source_pointer_RVA']=='0x1370764' and s['retained_parser_state_u8']==7 and s['receiver_plus_0x20_u32']==1
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['helper_selected_case_RVA']=='0xcab1f0' and x['receiver_plus_0x18_after_relative']=='0x658' and not x['next_vararg_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HM' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['vararg_cursor']['read_executed'] and n['experiment']=='E011HM' and n['expected_source']['vararg_value_RVA']=='0x10f03b0' and n['expected_post_helper']['receiver_plus_0x20_u32']==2
 return {'status':'PASS_E011HL_PORTABLE_REVIEW','cases':4,'rejects':40,'next':'E011HM'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
