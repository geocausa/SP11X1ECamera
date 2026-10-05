#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FP' and s['status']=='PASS_FORMATTER_WRAPPERS_TO_6BDD0_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2004
 assert s['wrapper_7ac38_executed'] and s['wrapper_7aca0_executed'] and s['nested_dependency_callsite_RVA']=='0x7acd8' and s['nested_dependency_target_RVA']=='0x6bdd0' and not s['nested_dependency_executed']
 assert (s['nested_x0_SP_relative'],s['nested_x1_u64'],s['nested_x2_u64'],s['nested_x3_RVA'],s['nested_x4_SP_relative'])==(-1392,640,18446744073709551615,'0x1370760',-1496)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FQ' and f['camera_frontier']['source_RVA']=='0x7acd8' and n['experiment']=='E011FQ'
 return {'status':'PASS_E011FP_PORTABLE_REVIEW','cases':4,'rejects':2004,'next':'E011FQ'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
