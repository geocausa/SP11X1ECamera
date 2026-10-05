#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HE' and s['status']=='PASS_1370762_BYTE25_TO_CA9590_LOOP_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['source_RVA']=='0x1370762' and s['source_u8']==37 and s['source_s8']==37 and s['source_read_RVA']=='0xca984c' and s['source_read_executed']
 assert s['pointer_after_RVA']=='0x1370763' and s['pointer_store_executed'] and s['receiver_plus_0x39_u8']==37 and s['receiver_byte_store_executed']
 assert s['branch_RVA']=='0xca9858' and s['nonzero_branch_taken'] and s['next_camera_source_RVA']=='0xca9590' and not s['next_camera_source_executed']
 assert s['retained_source_pointer_RVA']=='0x1370763' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['source_u8']==37 and x['pointer_after_RVA']=='0x1370763' and x['nonzero_branch_taken'] and not x['target_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HF' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['branch']['target_executed'] and n['experiment']=='E011HF' and n['expected_lookup']['second_table_RVA']=='0xf8b230' and not n['expected_lookup']['second_table_read_executed']
 return {'status':'PASS_E011HE_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011HF'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
