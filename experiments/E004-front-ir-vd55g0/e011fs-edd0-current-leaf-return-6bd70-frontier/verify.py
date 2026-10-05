#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FS' and s['status']=='PASS_EDD0_CURRENT_LEAF_RETURN_6BD70_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2212
 assert s['EDD0_current_path_executed'] and s['EDD0_current_path_instruction_visits']==12 and all(x['EDD0_current_path_instruction_visits']==3 for x in s['details'])
 assert s['EDD0_return_RVA']=='0x6bd70' and s['EDD0_result_RVA']=='0x17a1150' and s['EDD0_ABI_preserved']
 assert s['pins']['fs_edd0_leaf']==[0xedd0,0x0c,'fccd30fe0400a87e1bee6601eac29919f8c78e65be18e9fabd5afa7982d92d44']
 assert s['next_source_RVA']=='0x6bd70' and s['next_dependency_read_RVA']=='0x17a1150' and s['next_dependency_bytes']==8 and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FT' and f['camera_frontier']['source_RVA']=='0x6bd70' and n['experiment']=='E011FT'
 return {'status':'PASS_E011FS_PORTABLE_REVIEW','cases':4,'rejects':2212,'next':'E011FT'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
