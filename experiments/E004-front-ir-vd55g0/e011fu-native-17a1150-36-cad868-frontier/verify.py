#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json');w=L('WINDOWS-SAFE.json')
 assert s['experiment']=='E011FU' and s['status']=='PASS_NATIVE_17A1150_36_READ_TO_CAD868_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2356
 assert s['pins']['fu_6bd8c_native_read']==[0x6bd8c,4,'804d03f908bc3ddb2251c0ed80a5a8cbc44c4cc964797d091910bd46b232670a']
 assert w['dependency_RVA']=='0x17a1150' and w['dependency_bytes']==8 and w['native_value_before_reader_start_u64']==w['native_value_after_successful_reader_start_u64']==36
 assert w['reader_start_status']=='Success' and w['same_process_context_across_reads'] and w['same_module_base_across_reads'] and w['older_E011DY_loader_model_zero_rejected_as_native_authority']
 assert s['native_17a1150_value_u64']==36 and s['dependency_read_executed'] and all(x['dependency_read_executed'] and x['native_17a1150_value_u64']==36 for x in s['details'])
 assert s['next_source_RVA']=='0x6bd90' and s['next_call_target_RVA']=='0xcad868' and not s['next_dependency_executed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('windows_safe_sha256','WINDOWS-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert not r['exact_6bd8c_native_instruction_breakpoint_observed'] and r['original_6bd8c_instruction_executed_under_qualified_native_value'] and r['source_exact_dependency_read_value_u64']==36
 assert r['new_front_camera_starts']==1 and r['new_rear_camera_starts']==0 and r['new_reboots']==1 and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['next_source_RVA']=='0x6bd90' and not f['camera_frontier']['next_call_executed'] and n['experiment']=='E011FV'
 return {'status':'PASS_E011FU_PORTABLE_REVIEW','cases':4,'rejects':2356,'native_value':36,'next':'E011FV'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
