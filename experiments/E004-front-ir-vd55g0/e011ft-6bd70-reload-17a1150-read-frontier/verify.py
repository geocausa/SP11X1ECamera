#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FT' and s['status']=='PASS_6BD70_RELOAD_PREFIX_TO_17A1150_READ_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2320
 assert s['consumer_reload_prefix_executed'] and s['consumer_exact_stack_reads']==24 and all(x['consumer_exact_stack_reads']==6 for x in s['details']) and s['consumer_tuple_restored_exact']
 assert s['pins']['ft_6bd70_reload_prefix']==[0x6bd70,0x1c,'56a262397e36d6ab68c1acad6a140252ee72c1b541acca395edcbd48b25abc42']
 assert s['next_source_RVA']=='0x6bd8c' and s['next_dependency_read_RVA']=='0x17a1150' and s['next_dependency_bytes']==8 and not s['next_dependency_read_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['older_E011DY_zero_is_loader_model_not_native'] and r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011FU' and f['camera_frontier']['source_RVA']=='0x6bd8c' and n['experiment']=='E011FU'
 return {'status':'PASS_E011FT_PORTABLE_REVIEW','cases':4,'rejects':2320,'next':'E011FU'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
