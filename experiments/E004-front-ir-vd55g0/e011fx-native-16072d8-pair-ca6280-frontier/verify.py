#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');w=L('WINDOWS-SAFE.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['experiment']=='E011FX' and s['status']=='PASS_NATIVE_16072D8_PAIR_TO_CA6280_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==32
 assert s['CAD8C8_executed'] and s['CAD8C8_read_bytes']==16 and s['native_qword0_image_RVA']=='0x1607180' and s['native_qword1_nonzero'] and not s['native_qword1_image_relative'] and s['native_qword1_absolute_value_redacted']
 assert s['source_prefix_first_RVA']=='0xcad8c8' and s['source_prefix_last_executed_RVA']=='0xcad938' and s['source_prefix_instruction_visits_per_case']==14
 assert s['next_camera_source_RVA']=='0xcad93c' and s['next_call_target_RVA']=='0xca6280' and not s['next_call_executed']
 assert w['authority']=='bounded_same_boot_SP7_KDNET_process_context_front_only' and w['dependency_RVA']=='0x16072d8' and w['dependency_bytes']==16
 assert w['qword0_before_image_RVA']==w['qword0_after_image_RVA']=='0x1607180' and w['qword1_before_nonzero'] and w['qword1_after_nonzero'] and not w['qword1_is_image_relative']
 assert w['same_pair_across_successful_front_reader_start'] and w['same_process_context_across_reads'] and w['same_module_base_across_reads'] and w['older_file_initial_qword1_rejected_as_native_current']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('windows_safe_sha256','WINDOWS-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]: assert r[k]==sha(nm)
 assert r['next_call_x0_u64']==36 and r['next_call_x1_SP_relative']==512 and r['next_call_x2_u64']==640 and r['next_call_x3_RVA']=='0x1370760' and r['next_call_x4_SP_relative']==16 and r['next_call_x5_SP_relative']==r['next_call_x6_SP_relative']==408
 assert r['new_front_camera_starts']==1 and r['new_rear_camera_starts']==0 and r['new_reboots']==2 and not r['new_kernel_build'] and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert f['camera_frontier']['source_read_executed'] and f['camera_frontier']['next_source_RVA']=='0xcad93c' and not f['camera_frontier']['next_call_executed']
 assert n['experiment']=='E011FY' and n['current_camera_frontier']['source_RVA']=='0xcad93c' and n['current_camera_frontier']['call_target_RVA']=='0xca6280' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011FX_PORTABLE_REVIEW','cases':4,'rejects':32,'next':'E011FY'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
