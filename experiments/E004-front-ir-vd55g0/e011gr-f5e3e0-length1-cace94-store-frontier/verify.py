#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GR' and s['status']=='PASS_F5E3E0_SOURCE_BLOCK_LENGTH1_TO_CACE94_STORE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['source_block_RVA']=='0x1370780' and s['source_block_bytes']==16 and s['source_block_leading_u8']==46 and s['source_block_first_zero_offset']==1
 assert s['scan_call_RVA']=='0xcace90' and s['scan_target_RVA']=='0xf5e3e0' and s['scan_source_read_RVA']=='0xf5e3e8' and s['scan_source_read_bytes']==16 and s['scan_source_read_executed'] and s['scan_return_u64']==1
 assert s['next_camera_source_RVA']=='0xcace94' and s['receiver_result_offset']=='0x48' and not s['receiver_result_store_executed'] and s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==16 and x['source_block_first_zero_offset']==1 and x['scan_return_u64']==1 and not x['result_store_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['status']==s['status'] and r['next_experiment']=='E011GS' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['source_authority']['first_zero_offset']==1 and f['camera_frontier']['scan_return_u64']==1 and not f['camera_frontier']['result_store_executed']
 assert n['experiment']=='E011GS' and n['stop_frontier']['first_x22_write_RVA']=='0xcab288' and not n['stop_frontier']['write_executed']
 return {'status':'PASS_E011GR_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011GS'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
