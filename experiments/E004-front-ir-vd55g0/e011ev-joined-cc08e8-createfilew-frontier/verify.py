#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['status']=='PASS_JOINED_CC08E8_CREATEFILEW_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==936
 assert s['CC08E8_executed'] and s['CC08E8_return_index']==0 and s['joined_lowIO_record0_selected_under_owned_fixture'] and not s['native_lowIO_record_selection_qualified']
 assert s['lowIO_global7_lock_released'] and s['lowIO_record0_lock_retained_held'] and s['CreateFileW_arguments_qualified'] and not s['CreateFileW_executed']
 assert s['next_source_RVA']=='0xcfd658' and s['next_dependency_RVA']=='0xf7e3b8'
 for k,fname in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('lowIO_lifetime_safe_sha256','LOWIO-LIFETIME-SAFE.json'),('exact_API_output_safe_sha256','EXACT-API-OUTPUT-SAFE.json')]:assert r[k]==sha(H/fname)
 assert r['next_experiment']=='E011EW' and f['camera_frontier']['source_RVA']=='0xcfd658' and not f['camera_frontier']['CreateFileW_executed']
 assert n['experiment']=='E011EW' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EV_PORTABLE_REVIEW','cases':4,'rejects':936,'next':'E011EW'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
