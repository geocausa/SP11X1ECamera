#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GB' and s['status']=='PASS_SOURCE_BYTE_25_TO_F8B21B_LOOKUP_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['source_RVA']=='0x1370760' and s['source_section']=='.rdata' and s['source_bytes']==1 and s['source_byte_u8']==s['source_byte_s8']==37 and s['source_read_RVA']=='0xca984c' and s['source_read_executed']
 assert s['source_pointer_advanced_RVA']=='0x1370761' and s['source_nonzero_branch_taken'] and s['parser_state_u32']==0 and s['lookup_index_u64']==10 and s['lookup_base_RVA']=='0xf8b211'
 assert s['next_camera_source_RVA']=='0xca95b8' and s['next_dependency_read_RVA']=='0xf8b21b' and s['next_dependency_bytes']==1 and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_source_RVA']=='0xca95b8' and not f['camera_frontier']['next_dependency_read_executed'] and n['experiment']=='E011GC' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011GB_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011GC'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
