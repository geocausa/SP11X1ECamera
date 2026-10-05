#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');w=L('WINDOWS-SAFE.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FW' and s['status']=='PASS_NATIVE_16A2A84_ZERO_BRANCH_TO_16072D8_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==2620
 assert s['pins']['fw_cad8b8_zero_branch_prefix']==[0xcad8b8,0x10,'7dbe9cf939b0e222e8d5594e2c8c8cf43ac4f9f7cbf2225d2741b6315b48ea09']
 assert s['native_16a2a84_value_u32']==0 and s['native_16a2a84_authority_joined'] and s['CAD8B8_dependency_read_executed'] and not s['CAD8BC_nonzero_branch_taken']
 assert s['FW_original_source_instruction_visits']==16 and s['next_source_RVA']=='0xcad8c8' and s['next_dependency_read_RVA']=='0x16072d8' and s['next_dependency_bytes']==16 and not s['next_dependency_read_executed']
 assert w['authority']=='bounded_same_boot_SP7_KDNET_process_context_front_only' and w['dependency_RVA']=='0x16a2a84' and w['dependency_bytes']==4 and w['native_value_before_reader_start_u32']==w['native_value_after_successful_reader_start_u32']==0 and w['same_process_context_across_reads'] and w['same_module_base_across_reads'] and w['reader_start_status']=='Success'
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('windows_safe_sha256','WINDOWS-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]:assert r[k]==sha(nm)
 assert r['source_read_RVA']=='0xcad8b8' and r['source_read_executed_under_qualified_native_value'] and not r['nonzero_branch_taken'] and r['next_camera_source_RVA']=='0xcad8c8' and not r['next_dependency_read_executed']
 assert r['new_front_camera_starts']==1 and r['new_rear_camera_starts']==0 and r['new_reboots']==1 and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 cf=f['camera_frontier'];assert cf['source_read_executed'] and not cf['nonzero_branch_taken'] and cf['next_source_RVA']=='0xcad8c8' and cf['next_dependency_read_RVA']=='0x16072d8' and not cf['next_dependency_read_executed']
 assert f['older_E011DY_16072d8_file_initial_pair_is_not_native_runtime_authority'] and n['experiment']=='E011FX' and n['current_camera_frontier']['source_RVA']=='0xcad8c8' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FW_PORTABLE_REVIEW','cases':4,'rejects':2620,'native_16a2a84':0,'source_visits':16,'next':'E011FX'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
