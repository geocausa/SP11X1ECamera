#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FO' and s['status']=='PASS_SECOND_FORMATTER_ARGS_TO_60043C_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==1940
 assert s['second_formatter_callsite_RVA']=='0x60043c' and s['second_formatter_target_RVA']=='0x7ac38' and not s['second_formatter_call_executed']
 assert (s['second_formatter_x0_SP_relative'],s['second_formatter_x1_u64'],s['second_formatter_x2_RVA'],s['second_formatter_x3_RVA'],s['second_formatter_x4_RVA'],s['second_formatter_x5_RVA'])==(-1392,640,'0x1370760','0x1370780','0x10f03b0','0x13f1f28')
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FP' and f['camera_frontier']['source_RVA']=='0x60043c' and n['experiment']=='E011FP'
 return {'status':'PASS_E011FO_PORTABLE_REVIEW','cases':4,'rejects':1940,'next':'E011FP'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
