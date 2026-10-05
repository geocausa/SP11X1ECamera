#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GX' and s['status']=='PASS_F5D480_ONE_BYTE_COPY_TO_CAD260_STREAM_UPDATE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==28
 assert s['copy_call_RVA']=='0xcad25c' and s['copy_target_RVA']=='0xf5d480' and s['copy_call_executed'] and s['copied_bytes']==1
 assert s['copy_source_RVA']=='0x1370780' and s['copy_source_u8']==46 and s['copy_source_read_executed']
 assert s['copy_destination_receiver_relative']=='0x6b0' and s['copy_destination_after_u8']==46 and s['copy_destination_write_executed']
 assert s['next_camera_source_RVA']=='0xcad260' and s['next_stream_pointer_update_RVA']=='0xcad268' and s['next_stream_count_update_RVA']=='0xcad27c' and not s['stream_update_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['source_u8']==46 and x['destination_after_u8']==46 and x['copied_bytes']==1 and not x['stream_update_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(nm)
 assert r['next_experiment']=='E011GY' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['resume_frontier']['stream_update_executed'] and n['experiment']=='E011GY' and n['next_dependency']['flag_read_RVA']=='0xcad284' and not n['next_dependency']['flag_read_executed']
 return {'status':'PASS_E011GX_PORTABLE_REVIEW','cases':4,'rejects':28,'next':'E011GY'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
