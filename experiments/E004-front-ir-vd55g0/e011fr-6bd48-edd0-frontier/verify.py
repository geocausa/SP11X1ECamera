#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FR' and s['status']=='PASS_6BD48_TO_EDD0_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2184
 assert s['helper_6bd48_executed'] and s['helper_6bd48_entry_SP_relative']==-1696 and s['helper_6bd48_local_SP_relative']==-1776
 assert s['helper_6bd48_exact_local_save_chunks']==32 and all(x['helper_6bd48_exact_local_save_chunks']==8 for x in s['details'])
 assert s['next_source_RVA']=='0x6bd6c' and s['next_dependency_target_RVA']=='0xedd0' and not s['next_dependency_executed']
 pin=s['pins']['fr_6bd48_to_edd0_frontier'];assert pin==[0x6bd48,0x28,'c72f327d6d2a94edd03f07b62f077e9b4ec99deaeed16d5e6ce78bf069d90780']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['exact_local_save_chunks_per_case']==8 and r['exact_local_save_chunks_total']==32 and not r['dependency_executed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FS' and f['camera_frontier']['source_RVA']=='0x6bd6c' and n['experiment']=='E011FS'
 return {'status':'PASS_E011FR_PORTABLE_REVIEW','cases':4,'rejects':2184,'next':'E011FS'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
