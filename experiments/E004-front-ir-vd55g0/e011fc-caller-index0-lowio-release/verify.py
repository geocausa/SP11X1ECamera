#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');l=L(H/'LOWIO-RELEASE-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fb=ROOT/'experiments/E004-front-ir-vd55g0/e011fb-cfd410-parent-return-cfcc9c-frontier/RESULT.json'
 assert s['status']=='PASS_CALLER_INDEX0_LOWIO_RELEASE_TO_CFCCE4_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1168
 assert s['caller_resume_executed'] and s['caller_return_store_u32']==2 and s['caller_cleanup_flag_u32']==1 and s['caller_index_u32']==0
 assert s['lowIO_record0_active_clear_qualified'] and s['lowIO_record0_lock_released'] and s['CC08C0_executed']
 assert s['current_UTF16_owner_released'] and s['no_original_reads_of_released_current_owner'] and s['next_source_RVA']=='0xcfcce4'
 assert s['inherited_E011FB_result_sha256']==sha(fb)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('lowio_release_safe_sha256','LOWIO-RELEASE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]: assert r[k]==sha(H/nm)
 assert r['rejected_altered_contracts']==1168 and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert l['cleanup_flag_u32']==1 and l['index_u32']==0 and l['record0_lock_released'] and l['record0_lock_depth_at_frontier']==0
 assert l['record_active_before_clear_u8']==l['record_active_after_clear_u8']==0 and l['record_active_clear_idempotent']
 assert f['camera_frontier']['source_RVA']=='0xcfcce4' and f['camera_frontier']['lowIO_record0_lock_depth']==0 and not f['camera_frontier']['full_CFCC18_return_qualified']
 assert n['experiment']=='E011FD' and n['current_camera_frontier']['source_RVA']=='0xcfcce4' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FC_PORTABLE_REVIEW','cases':4,'rejects':1168,'producer_rejects':264,'next':'E011FD'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
