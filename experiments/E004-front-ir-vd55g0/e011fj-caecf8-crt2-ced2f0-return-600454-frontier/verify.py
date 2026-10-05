#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');a=L(H/'CAECF8-CED2F0-RETURN-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fi=ROOT/'experiments/E004-front-ir-vd55g0/e011fi-ced330-zero-store-branch-caecf8-frontier/RESULT.json'
 assert s['status']=='PASS_CAECF8_CRT2_CED2F0_RETURN_TO_600454_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1680
 assert s['outer_CAECF8_complete_return_qualified'] and s['CED33C_CRT_error_load_u32']==2 and s['CED2F0_complete_return_qualified']
 assert s['CED2F0_return_u32']==2 and s['CED2F0_return_target_RVA']=='0x600454' and s['SP_relative_after_CED2F0_return']==-1456
 assert r['inherited_E011FI_result_sha256']==sha(fi)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('caecf8_ced2f0_return_safe_sha256','CAECF8-CED2F0-RETURN-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert a['thread_CRT_error_u32']==2 and a['CED33C_loaded_u32']==2 and a['saved_nonvolatile_frame_restored']
 assert a['CED2F0_return_target_RVA']=='0x600454' and a['SP_relative_after_CED2F0_return']==-1456
 assert f['camera_frontier']['source_RVA']=='0x600454' and f['camera_frontier']['incoming_return_u32']==2 and f['camera_frontier']['expected_nonzero_fallthrough_RVA']=='0x600458'
 assert n['experiment']=='E011FK' and n['current_camera_frontier']['source_RVA']=='0x600454' and not n['native_rear_runtime_allowed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FJ_PORTABLE_REVIEW','cases':4,'rejects':1680,'producer_rejects':264,'next':'E011FK'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
