#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n):return json.loads((H/n).read_text())
def S(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011HS' and s['status']=='PASS_CA9880_RETURN26_EPILOGUE_TO_CA634C_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==24
 assert s['return_load_RVA']=='0xca9880' and s['return_load_executed'] and s['return_w0_u32']==26 and s['epilogue_executed'] and s['saved_registers_restored'] and s['SP_restored_to_entry']
 assert s['next_camera_source_RVA']=='0xca634c' and not s['next_camera_source_executed']
 assert [x['axis'] for x in s['details']]==[0,1,40,1230] and all(x['instruction_visits']==7 and x['return_w0_u32']==26 and x['saved_registers_restored'] and not x['target_executed'] for x in s['details'])
 for k,nm in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(nm)
 assert r['next_experiment']=='E011HT' and not r['new_front_camera_starts'] and not r['new_rear_camera_starts'] and not r['new_reboots'] and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert not f['caller_frontier']['executed'] and n['experiment']=='E011HT' and n['expected_path']['next_read_RVA']=='0xca63d8'
 return {'status':'PASS_E011HS_PORTABLE_REVIEW','cases':4,'rejects':24,'next':'E011HT'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
