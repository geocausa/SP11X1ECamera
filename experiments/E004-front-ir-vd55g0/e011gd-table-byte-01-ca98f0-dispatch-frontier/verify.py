#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GD' and s['status']=='PASS_TABLE_BYTE_01_TO_CA98F0_DISPATCH_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['second_table_RVA']=='0xf8b222' and s['second_table_byte_u8']==1 and s['second_table_read_RVA']=='0xca95d8' and s['second_table_read_executed'] and s['parser_state_after_u8']==1 and s['parser_state_lt8_qualified'] and s['parser_state_le7_qualified']
 assert s['jump_table_base_RVA']=='0xca98ec' and s['jump_table_index_u32']==1 and s['next_camera_source_RVA']=='0xca95f4' and s['next_dependency_read_RVA']=='0xca98f0' and s['next_dependency_bytes']==4 and s['next_dependency_signed'] and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert not r['new_front_camera_starts'] and not r['new_reboots'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert n['experiment']=='E011GE' and not f['camera_frontier']['next_dependency_read_executed']
 return {'status':'PASS_E011GD_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011GE'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
