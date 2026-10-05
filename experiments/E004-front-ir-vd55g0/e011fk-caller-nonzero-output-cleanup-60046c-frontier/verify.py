#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(p):return json.loads(Path(p).read_text())
def check():
 s=L(H/'SOURCE-SAFE.json');r=L(H/'RESULT.json');a=L(H/'CALLER-CLEANUP-SAFE.json');f=L(H/'FRONTIER-SAFE.json');n=L(H/'NEXT-SOURCE.json')
 fj=ROOT/'experiments/E004-front-ir-vd55g0/e011fj-caecf8-crt2-ced2f0-return-600454-frontier/RESULT.json'
 assert s['status']=='PASS_CALLER_NONZERO_RETURN_OUTPUT_CLEANUP_TO_60046C_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1732
 assert s['caller_nonzero_return_branch_qualified'] and s['caller_x20_cleared'] and s['caller_output_slot_zero_store_executed'] and s['caller_x20_zero_branch_qualified']
 assert s['next_source_RVA']=='0x60046c' and s['next_dependency_RVA']=='0x160a218' and s['next_dependency_bytes']==8
 assert r['inherited_E011FJ_result_sha256']==sha(fj)
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('caller_cleanup_safe_sha256','CALLER-CLEANUP-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==sha(H/nm)
 assert a['incoming_return_u32']==2 and a['output_store_executed'] and a['output_store_bytes']==8 and a['output_store_value_u64']==0 and not a['next_dependency_read_executed']
 assert f['camera_frontier']['source_RVA']=='0x60046c' and f['camera_frontier']['dependency_RVA']=='0x160a218' and not f['camera_frontier']['read_executed']
 assert n['experiment']=='E011FL' and n['current_camera_frontier']['dependency_RVA']=='0x160a218' and not n['native_rear_runtime_allowed']
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 return {'status':'PASS_E011FK_PORTABLE_REVIEW','cases':4,'rejects':1732,'producer_rejects':264,'next':'E011FL'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
