#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json');life=L('LOWIO-LIFETIME-SAFE.json')
 assert s['status']=='PASS_STARTUP_LOWIO_LIFETIME_JOIN_CFD570_PREFIX' and s['case_count']==4 and s['rejected_altered_contracts']==820
 assert s['startup_lowIO_lifetime_join_qualified'] and s['startup_lowIO_state_unchanged_to_CFD570_entry'] and s['startup_lowIO_count']==64
 assert s['CFD570_executed'] and s['CFD0B0_parser_return_qualified'] and not s['CC08E8_executed'] and s['next_source_RVA']=='0xcfd5e8'
 assert life['status']=='PASS_SOURCE_LOWIO_LIFETIME_TO_FIRST_CFD570_CALL' and life['startup_lowIO_state_survives_to_joined_camera_frontier_under_owned_lifecycle_contract']
 for k,fname in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('lowIO_lifetime_safe_sha256','LOWIO-LIFETIME-SAFE.json'),('exact_API_output_safe_sha256','EXACT-API-OUTPUT-SAFE.json')]:assert r[k]==sha(H/fname)
 assert r['next_experiment']=='E011EV' and f['camera_frontier']['source_RVA']=='0xcfd5e8' and not f['camera_frontier']['CC08E8_executed']
 assert n['experiment']=='E011EV' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EU_PORTABLE_REVIEW','cases':4,'rejects':820,'next':'E011EV'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
