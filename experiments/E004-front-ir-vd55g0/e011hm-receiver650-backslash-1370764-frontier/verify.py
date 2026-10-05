#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HM' and s['status']=='PASS_RECEIVER650_VARARG_BACKSLASH_TO_1370764_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==40
 assert s['vararg_receiver_relative']=='0x650' and s['vararg_value_RVA']=='0x10f03b0' and s['vararg_read_RVA']=='0xcace28' and s['vararg_read_executed'] and s['string_first_u8']==92 and s['string_first_zero_offset']==1 and s['string_length_u64']==1
 assert s['stream_qword0_before_receiver_relative']=='0x6b1' and s['stream_qword0_after_receiver_relative']=='0x6b2' and s['stream_count_before_u64']==1 and s['stream_count_after_u64']==2
 assert s['receiver_plus_0x20_before_u32']==1 and s['receiver_plus_0x20_after_u32']==2 and s['destination_new_byte_receiver_relative']=='0x6b1' and s['destination_new_byte_u8']==92 and s['helper_return_u32']==1
 assert s['retained_parser_state_u8']==7 and s['retained_source_pointer_RVA']=='0x1370764' and s['next_camera_source_RVA']=='0xca984c' and s['next_dependency_RVA']=='0x1370764' and not s['next_dependency_read_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['vararg_value_RVA']=='0x10f03b0' and x['string_first_u8']==92 and x['stream_count_after_u64']==2 and x['receiver_plus_0x20_after_u32']==2 and not x['next_read_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HN' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['next_read']['executed'] and n['experiment']=='E011HN' and n['source_hint']['expected_u8']==37 and n['expected_next_frontier']['pointer_RVA']=='0x1370765'
 return {'status':'PASS_E011HM_PORTABLE_REVIEW','cases':4,'rejects':40,'next':'E011HN'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
