#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GC' and s['status']=='PASS_TABLE_BYTE_01_TO_F8B222_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['first_table_RVA']=='0xf8b21b' and s['first_table_section']=='.rdata' and s['first_table_byte_u8']==1 and s['first_table_read_RVA']=='0xca95b8' and s['first_table_read_executed']
 assert s['parser_state_before_u8']==0 and s['scaled_state_u64']==9 and s['second_lookup_offset_u64']==18 and s['next_camera_source_RVA']=='0xca95d8' and s['next_dependency_read_RVA']=='0xf8b222' and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_source_RVA']=='0xca95d8' and not f['camera_frontier']['next_dependency_read_executed'] and n['experiment']=='E011GD' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011GC_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GD'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
