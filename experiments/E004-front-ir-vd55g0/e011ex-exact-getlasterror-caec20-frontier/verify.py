#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 ew=ROOT/'experiments/E004-front-ir-vd55g0/e011ew-source-exact-createfilew-failure-branch/RESULT.json'
 assert s['status']=='PASS_EXACT_GETLASTERROR_TO_CAEC20_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==984
 assert s['GetLastError_executed'] and s['GetLastError_return_qualified'] and s['GetLastError_return_u32']==3 and not s['CAEC20_executed']
 assert s['next_source_RVA']=='0xcfd700' and s['next_call_target_RVA']=='0xcaec20' and s['lowIO_record_active_cleared_on_failure'] and s['lowIO_record0_lock_retained_held']
 assert s['inherited_E011EW_result_sha256']==sha(ew)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(H/nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['source_RVA']=='0xcfd700' and f['camera_frontier']['GetLastError_return_u32']==3 and not f['camera_frontier']['CAEC20_executed']
 assert f['evidence_boundary']['current_unicode_owner_bytes']==76 and f['evidence_boundary']['older_E011CW_cleanup_owner_bytes']==74 and not f['evidence_boundary']['older_cleanup_geometry_joined']
 assert n['experiment']=='E011EY' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EX_PORTABLE_REVIEW','cases':4,'rejects':984,'next':'E011EY'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
