#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HA' and s['status']=='PASS_RECEIVER20_ZERO_TO_ONE_CAD1F0_EPILOGUE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['receiver20_producer_RVA']=='0xca6318' and s['receiver20_producer_executed'] and s['receiver_plus_0x20_before_u32']==0
 assert s['receiver20_read_RVA']=='0xcad294' and s['receiver20_read_executed'] and s['increment_RVA']=='0xcad298' and s['increment_u32']==1 and s['receiver20_store_RVA']=='0xcad29c' and s['receiver20_store_executed'] and s['receiver_plus_0x20_after_u32']==1
 assert s['next_camera_source_RVA']=='0xcad2a0' and s['epilogue_first_RVA']=='0xcad2a0' and not s['epilogue_executed'] and s['expected_return_target_RVA']=='0xcab590'
 assert s['retained_source_pointer_RVA']=='0x1370762' and s['retained_parser_state_u8']==7
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['receiver_plus_0x20_before_u32']==0 and x['receiver_plus_0x20_after_u32']==1 and not x['epilogue_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011HB' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['epilogue_frontier']['executed'] and n['experiment']=='E011HB' and n['expected_parent_branch']['target_RVA']=='0xcab62c' and not n['expected_parent_branch']['target_executed']
 return {'status':'PASS_E011HA_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011HB'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
