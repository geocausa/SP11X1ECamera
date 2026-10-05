#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011GA' and s['status']=='PASS_CA94E8_OWNED_RECEIVER_PREFIX_TO_1370760_BYTE_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==40
 assert s['CA6348_call_executed'] and s['CA94E8_entry_executed'] and s['current_path_instruction_visits_per_case']==26 and s['CA94E8_frame_bytes']==64 and s['CA94E8_return_RVA']=='0xca634c'
 assert s['owned_receiver_counter_before_u32']==0 and s['owned_receiver_counter_after_u32']==1 and s['owned_receiver_parser_state_cleared'] and s['selected_source_pointer_RVA']=='0x1370760'
 assert s['next_camera_source_RVA']=='0xca984c' and s['next_dependency_read_RVA']=='0x1370760' and s['next_dependency_bytes']==1 and s['next_dependency_signed'] and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_source_RVA']=='0xca984c' and not f['camera_frontier']['next_dependency_read_executed'] and n['experiment']=='E011GB' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011GA_PORTABLE_REVIEW','cases':4,'rejects':40,'next':'E011GB'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
