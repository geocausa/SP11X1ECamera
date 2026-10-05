#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n):return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');w=L('WINDOWS-AUTHORITY-SAFE.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json')
 assert s['status']=='PASS_SOURCE_EXACT_CREATEFILEW_FAILURE_TO_GETLASTERROR_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==952
 assert s['CreateFileW_arguments_qualified'] and s['CreateFileW_executed_under_same_boot_exact_OS_contract'] and s['CreateFileW_invalid_handle_qualified']
 assert s['CreateFileW_last_error_authority']==3 and not s['exact_source_callsite_breakpoint_observed'] and s['invalid_handle_failure_branch_qualified']
 assert s['lowIO_record_active_cleared_on_failure'] and not s['GetLastError_executed'] and s['next_source_RVA']=='0xcfd6fc' and s['next_dependency_RVA']=='0xf7e468'
 assert w['same_boot_exact_OS_contract']['invalid_handle'] and w['same_boot_exact_OS_contract']['handle_signed']==-1 and w['same_boot_exact_OS_contract']['last_error']==3
 assert not w['same_boot_filesystem']['file_exists'] and not w['same_boot_filesystem']['parent_directory_exists'] and not w['live_debug_notes']['exact_source_callsite_breakpoint_observed']
 for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('windows_authority_safe_sha256','WINDOWS-AUTHORITY-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('exact_API_output_safe_sha256','EXACT-API-OUTPUT-SAFE.json'),('lowIO_lifetime_safe_sha256','LOWIO-LIFETIME-SAFE.json')]: assert r[k]==sha(nm)
 assert r['new_front_camera_starts']==3 and r['new_rear_camera_starts']==0 and r['new_reboots']==2 and r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
 assert r['next_experiment']=='E011EX' and f['camera_frontier']['source_RVA']=='0xcfd6fc' and not f['camera_frontier']['GetLastError_executed']
 assert n['experiment']=='E011EX' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EW_PORTABLE_REVIEW','cases':4,'rejects':952,'next':'E011EX'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
