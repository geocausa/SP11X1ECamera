#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FY' and s['status']=='PASS_CA6280_ENTRY_TO_COOKIE_PRODUCER_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==44
 assert s['CAD93C_call_executed'] and s['CA6280_entry_executed'] and s['CA6280_prologue_instruction_visits_per_case']==5 and s['CA6280_frame_bytes']==48 and s['CA6280_return_RVA']=='0xcad940'
 assert s['next_camera_source_RVA']=='0xca6294' and s['next_dependency_target_RVA']=='0x11d0' and s['next_dependency_kind']=='security_cookie_producer' and not s['next_dependency_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]: assert r[k]==sha(nm)
 assert not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_source_RVA']=='0xca6294' and not f['camera_frontier']['next_dependency_executed'] and n['experiment']=='E011FZ' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FY_PORTABLE_REVIEW','cases':4,'rejects':44,'next':'E011FZ'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
