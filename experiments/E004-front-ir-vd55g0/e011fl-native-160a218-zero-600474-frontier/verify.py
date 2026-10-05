#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
    s=L('SOURCE-SAFE.json'); r=L('RESULT.json'); w=L('WINDOWS-SAFE.json'); f=L('FRONTIER-SAFE.json'); n=L('NEXT-SOURCE.json')
    assert s['experiment']=='E011FL' and s['status']=='PASS_NATIVE_160A218_ZERO_TO_600474_FRONTIER'
    assert s['case_count']==4 and s['rejected_altered_contracts']==1768
    assert s['native_dependency_value_qualified'] and s['native_160a218_value_u64']==0
    assert s['native_160a218_before_reader_start_u64']==0 and s['native_160a218_after_successful_reader_start_u64']==0
    assert not s['exact_60046c_native_instruction_breakpoint_observed'] and not s['bit16_set'] and not s['bit16_branch_taken']
    assert s['next_source_RVA']=='0x600474' and not s['next_dependency_read_executed']
    assert w['native_value_before_reader_start_u64']==0 and w['native_value_after_successful_reader_start_u64']==0
    assert w['reader_format']=='NV12' and w['reader_width']==1920 and w['reader_height']==1080 and w['reader_start_status']=='Success'
    assert not w['exact_60046c_native_instruction_breakpoint_observed'] and not w['tested_bit_set'] and not w['expected_original_branch_taken']
    for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('windows_safe_sha256','WINDOWS-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]: assert r[k]==sha(nm)
    assert r['new_front_camera_starts']==1 and r['new_rear_camera_starts']==0 and r['new_reboots']==1
    assert r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed']
    assert r['next_experiment']=='E011FM' and f['camera_frontier']['source_RVA']=='0x600474' and not f['camera_frontier']['next_dependency_read_executed']
    assert n['experiment']=='E011FM' and not n['native_rear_runtime_allowed']
    return {'status':'PASS_E011FL_PORTABLE_REVIEW','cases':4,'rejects':1768,'next':'E011FM'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
