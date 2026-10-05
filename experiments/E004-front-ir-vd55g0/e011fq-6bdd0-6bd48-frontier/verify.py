#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FQ' and s['status']=='PASS_6BDD0_TO_6BD48_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2040
 assert s['helper_6bdd0_executed'] and s['helper_6bdd0_dependency_callsite_RVA']=='0x6be08' and s['helper_6bdd0_dependency_target_RVA']=='0x6bd48' and not s['helper_6bd48_executed']
 assert (s['helper_x0_SP_relative'],s['helper_x1_u64'],s['helper_x2_u64'],s['helper_x3_RVA'],s['helper_x4_u64'],s['helper_x5_SP_relative'])==(-1392,640,18446744073709551615,'0x1370760',0,-1496)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FR' and f['camera_frontier']['source_RVA']=='0x6be08' and n['experiment']=='E011FR'
 return {'status':'PASS_E011FQ_PORTABLE_REVIEW','cases':4,'rejects':2040,'next':'E011FR'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
